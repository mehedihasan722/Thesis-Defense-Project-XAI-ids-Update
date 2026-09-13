"""
run_rq1_stability.py — RQ1: does LIME return the same explanation twice?

    python run_rq1_stability.py --model RandomForest --n-instances 200

For each sampled test instance, LIME is run N_RUNS times under different
random seeds on an identical, frozen model. If the explainer were
deterministic every run would return the same ranking. It is not: LIME fits a
local surrogate to a random perturbation sample, so the ranking is a random
variable. This script measures its dispersion.

This runner measures repeated LIME rankings. It does not execute SHAP or
measure a SHAP repeatability ceiling.
"""
import argparse
import json
import sys
import time
import warnings
warnings.filterwarnings("ignore", message=".*valid feature names.*")
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import joblib
from joblib.externals import cloudpickle
import numpy as np
import pandas as pd
from lime.lime_tabular import LimeTabularExplainer

import config
from experiment import start_run, finish_run
from stability import rank_stability


N_RUNS = 10
LIME_SEEDS = [101, 202, 303, 404, 505, 606, 707, 808, 909, 1010]
BACKGROUND_N = 20_000      # rows LIME uses to learn feature distributions


def ranking_from_lime(exp, label, n_features) -> list[int]:
    """Feature indices ordered by |weight|, descending."""
    pairs = exp.as_map()[label]                    # [(feat_idx, weight), ...]
    pairs = sorted(pairs, key=lambda t: abs(t[1]), reverse=True)
    return [int(i) for i, _ in pairs]


def main(model_name: str, task: str, seed: int, n_instances: int,
         num_samples: int):
    t_all = time.time()

    # ---- load the FROZEN model and the exact Stage 2 split ---------------
    mpath = config.RESULTS_MODELS / f"{model_name}_{task}_seed{seed}.joblib"
    spath = config.RESULTS_MODELS / f"split_{task}_seed{seed}.json"
    if not mpath.exists():
        raise SystemExit(f"missing {mpath} — run run_baselines.py first")
    clf = joblib.load(mpath)
    meta = json.loads(spath.read_text())

    df = pd.read_parquet(config.DATA_PROCESSED / "unsw_clean.parquet")
    feature_names = meta["feature_names"]
    class_names = [str(c) for c in meta["class_names"]]
    n_features = len(feature_names)

    X = df[feature_names]
    y_raw = df[config.LABEL_BINARY if task == "binary" else config.LABEL_MULTI]
    test_idx = meta["test_index"]
    X_te, y_te = X.loc[test_idx], y_raw.loc[test_idx]
    X_tr = X.drop(index=test_idx)

    print(f"model={model_name}  task={task}  features={n_features}")
    print(f"test set: {len(X_te):,}")

    # ---- stratified instance sample --------------------------------------
    # Rare classes cap out at their own size: Worms has ~33 test flows, so
    # asking for 50 would silently give fewer. Take min() and report it.
    per_class = max(1, n_instances // y_te.nunique())
    picks = []
    for cls, grp in y_te.groupby(y_te):
        take = min(per_class, len(grp))
        picks.append(grp.sample(take, random_state=seed))
    sample_idx = pd.concat(picks).index
    print(f"sampled {len(sample_idx)} instances "
          f"({per_class} requested per class)")
    print(y_te.loc[sample_idx].value_counts().to_string())

    # ---- one explainer per seed, built once and reused --------------------
    run_dir = start_run(config.RESULTS_TABLES, "rq1", model_name, seed, {
        "task": task, "num_samples": num_samples, "lime_seeds": LIME_SEEDS,
        "sample_indices": [int(i) for i in sample_idx],
    })

    bg = X_tr.sample(min(BACKGROUND_N, len(X_tr)), random_state=seed)
    explainers = [
        LimeTabularExplainer(
            bg.values,
            feature_names=feature_names,
            class_names=class_names,
            discretize_continuous=True,
            random_state=s,
            mode="classification",
        )
        for s in LIME_SEEDS
    ]

    # ---- run --------------------------------------------------------------
    rows, times = [], []
    manifest_path = run_dir / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    candidates = sorted(run_dir.parent.glob(f'rq1_{model_name}_seed{seed}_*/checkpoint.joblib'), reverse=True)
    for checkpoint in candidates:
        previous = json.loads((checkpoint.parent / 'manifest.json').read_text())
        compatible = (
            previous['status'] != 'complete' and
            previous['parameters'] == manifest['parameters'] and
            previous.get('input_sha256') == manifest.get('input_sha256') and
            previous['python'] == manifest['python'] and
            previous['packages'] == manifest['packages'] and
            all(previous['source_sha256'].get(name) == manifest['source_sha256'].get(name)
                for name in ['run_rq1_stability.py', 'src/stability.py', 'src/models.py', 'config.py'])
        )
        if compatible:
            state = joblib.load(checkpoint)
            rows, times = state['rows'], state['times']
            explainers = cloudpickle.loads(state['explainers'])
            assert [r['instance'] for r in rows] == [int(i) for i in sample_idx[:len(rows)]]
            manifest['resumed_from'] = str(checkpoint.parent.relative_to(ROOT))
            manifest['resumed_instances'] = len(rows)
            manifest_path.write_text(json.dumps(manifest, indent=2))
            print(f'Resumed {len(rows)} instances with saved LIME random states.', flush=True)
            break
    for n, idx in enumerate(sample_idx[len(rows):], len(rows) + 1):
        x = X_te.loc[idx].values
        true_cls = y_te.loc[idx]
        pred_label = int(clf.predict(x.reshape(1, -1))[0])

        rankings = []
        for ex in explainers:
            t0 = time.time()
            exp = ex.explain_instance(
                x, clf.predict_proba,
                num_features=n_features,
                num_samples=num_samples,
                labels=(pred_label,),
            )
            times.append(time.time() - t0)
            rankings.append(ranking_from_lime(exp, pred_label, n_features))

        st = rank_stability(rankings, n_features)
        st.update({"instance": int(idx), "true_class": str(true_cls),
                   "pred_label": pred_label})
        rows.append(st)

        if n % 10 == 0 or n == len(sample_idx):
            temporary = run_dir / 'checkpoint.tmp.joblib'
            joblib.dump({'rows': rows, 'times': times, 'explainers': cloudpickle.dumps(explainers)}, temporary, compress=3)
            temporary.replace(run_dir / 'checkpoint.joblib')
            mj = np.mean([r["jaccard_at_5"] for r in rows])
            print(f"  [{n}/{len(sample_idx)}] running mean Jaccard@5 = {mj:.3f}"
                  f"   ({np.mean(times):.2f}s per explanation)", flush=True)

    res = pd.DataFrame(rows)

    # ---- outputs ----------------------------------------------------------
    out = run_dir / f"rq1_stability_{model_name}_{task}.csv"
    res.to_csv(out, index=False)

    summary = (res.groupby("true_class")
                  .agg(n=("jaccard_at_5", "size"),
                       jaccard5_mean=("jaccard_at_5", "mean"),
                       jaccard5_std=("jaccard_at_5", "std"),
                       jaccard10_mean=("jaccard_at_10", "mean"),
                       kendall_mean=("kendall_tau", "mean"))
                  .round(4)
                  .sort_values("jaccard5_mean"))
    s_out = run_dir / f"rq1_summary_{model_name}_{task}.csv"
    summary.to_csv(s_out)
    finish_run(run_dir)

    print("\n" + "=" * 70)
    print("RQ1 — LIME stability by attack class (lower = less stable)")
    print("=" * 70)
    print(summary.to_string())
    print(f"\noverall Jaccard@5 : {res['jaccard_at_5'].mean():.4f}")
    print(f"overall Jaccard@10: {res['jaccard_at_10'].mean():.4f}")
    print(f"overall Kendall t : {res['kendall_tau'].mean():.4f}")

    # Report measured local runtime without extrapolating deployment capacity.
    tot = np.sum(times)
    print(f"\nexplanations      : {len(times):,}")
    print(f"mean per expl.    : {np.mean(times):.3f}s  "
          f"(median {np.median(times):.3f}s)")
    print(f"total LIME time   : {tot/60:.1f} min")
    print(f"wall clock        : {(time.time()-t_all)/60:.1f} min")
    print(f"\nwrote {out}\nwrote {s_out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", dest="model_name", default="RandomForest")
    ap.add_argument("--task", choices=["binary", "multiclass"],
                    default="multiclass")
    ap.add_argument("--seed", type=int, default=config.SEED)
    ap.add_argument("--n-instances", type=int, default=200)
    ap.add_argument("--num-samples", type=int, default=5000,
                    help="LIME perturbation samples per explanation")
    main(**vars(ap.parse_args()))
