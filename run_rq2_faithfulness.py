"""
run_rq2_faithfulness.py — RQ2: is the explanation faithful to the model?

    python run_rq2_faithfulness.py --model RandomForest --n-instances 300

Compares three feature rankings on a FROZEN model:
  LIME      — the explainer under study
  TreeSHAP  — exact for tree models, the comparison arm
  Random    — the control, and the actual experiment

If LIME's comprehensiveness curve is not clearly above Random's, the
explanation is not identifying the features the model relies on. This protocol evaluates sensitivity under the selected masking baseline.
"""

from __future__ import annotations

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
import numpy as np
import pandas as pd
import shap
from lime.lime_tabular import LimeTabularExplainer

import config
from experiment import start_run, finish_run, bootstrap_mean_ci
from explainers import get_shap_explainer, shap_ranking
from faithfulness import curves_for_instance, auc_over_k, auc_sufficiency

KS = list(range(1, 11))
BACKGROUND_N = 20_000
LIME_SEED = 101


def lime_ranking(explainer, x, clf, label, n_features, num_samples):
    exp = explainer.explain_instance(
        x, clf.predict_proba, num_features=n_features,
        num_samples=num_samples, labels=(label,),
    )
    pairs = sorted(exp.as_map()[label], key=lambda t: abs(t[1]), reverse=True)
    return [int(i) for i, _ in pairs]


def main(model_name: str, task: str, seed: int, n_instances: int,
         num_samples: int, lime_seeds=(101, 202, 303), masking="mean", skip_shap=False):
    t_all = time.time()
    if not lime_seeds or len(set(lime_seeds)) != len(lime_seeds):
        raise ValueError('Provide distinct LIME seeds')
    if n_instances < 1 or num_samples < 2:
        raise ValueError('n_instances must be positive and num_samples at least 2')
    rng = np.random.RandomState(seed)

    mpath = config.RESULTS_MODELS / f"{model_name}_{task}_seed{seed}.joblib"
    spath = config.RESULTS_MODELS / f"split_{task}_seed{seed}.json"
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

    # mean-imputation baseline, computed on TRAINING data only
    baseline = (X_tr.mean() if masking == "mean" else X_tr.median()).values.astype(float)

    print(f"model={model_name}  task={task}  features={n_features}")

    per_class = max(1, n_instances // y_te.nunique())
    picks = []
    for cls, grp in y_te.groupby(y_te):
        picks.append(grp.sample(min(per_class, len(grp)), random_state=seed))
    sample_idx = pd.concat(picks).index
    print(f"sampled {len(sample_idx)} instances")

    run_dir = start_run(config.RESULTS_TABLES, "rq2", model_name, seed, {
        "skip_shap": skip_shap, "task": task, "num_samples": num_samples, "lime_seeds": list(lime_seeds), "masking": masking,
        "sample_indices": [int(i) for i in sample_idx],
    })

    bg = X_tr.sample(min(BACKGROUND_N, len(X_tr)), random_state=seed)
    explainers = {
        ls: LimeTabularExplainer(
            bg.values, feature_names=feature_names, class_names=class_names,
            discretize_continuous=True, random_state=ls, mode="classification")
        for ls in lime_seeds
    }

    # TreeSHAP where available; LinearSHAP / KernelSHAP otherwise (RQ5)
    tree_expl, shap_kind = (None, None) if skip_shap else get_shap_explainer(clf, bg.values)
    print(f"SHAP variant: {shap_kind}")

    rows = []
    for n, idx in enumerate(sample_idx, 1):
        x = X_te.loc[idx].values.astype(float)
        label = int(clf.predict(x.reshape(1, -1))[0])
        p_orig = float(clf.predict_proba(x.reshape(1, -1))[0][label])


        rank_shap = None if skip_shap else shap_ranking(tree_expl, shap_kind, clf, x, label, n_features)[0]

        for ls, explainer in explainers.items():
            rank_lime = lime_ranking(explainer, x, clf, label, n_features, num_samples)
            rank_rand = list(rng.permutation(n_features))
            ranks = [("LIME", rank_lime), ("Random", rank_rand)]
            if not skip_shap:
                ranks.append((shap_kind, rank_shap))
            for tag, rank in ranks:
                c = curves_for_instance(x, rank, clf, baseline, label, KS)
                rows.append({
                    "instance": int(idx), "lime_seed": ls,
                    "true_class": str(y_te.loc[idx]), "explainer": tag,
                    "p_original": p_orig,
                    "comprehensiveness_auc": auc_over_k(c["comprehensiveness"], p_orig),
                    "sufficiency_auc": auc_sufficiency(c["sufficiency"], p_orig),
                    **{f"comp_k{k}": v for k, v in zip(KS, c["comprehensiveness"])},
                    **{f"suff_k{k}": v for k, v in zip(KS, c["sufficiency"])},
                })

        if n % 25 == 0 or n == len(sample_idx):
            print(f"  [{n}/{len(sample_idx)}]", flush=True)

    res = pd.DataFrame(rows)
    out = run_dir / f"rq2_faithfulness_{model_name}_{task}.csv"
    res.to_csv(out, index=False)

    instance_means = res.groupby(["instance", "explainer"], as_index=False).mean(numeric_only=True)
    summary = (instance_means.groupby("explainer")
                  .agg(n=("comprehensiveness_auc", "size"),
                       comp_auc_mean=("comprehensiveness_auc", "mean"),
                       comp_auc_std=("comprehensiveness_auc", "std"),
                       suff_auc_mean=("sufficiency_auc", "mean"),
                       suff_auc_std=("sufficiency_auc", "std"))
                  .round(4))
    s_out = run_dir / f"rq2_summary_{model_name}_{task}.csv"
    summary.to_csv(s_out)

    print("\n" + "=" * 72)
    print("RQ2 — faithfulness (comprehensiveness: higher = better)")
    print("=" * 72)
    print(summary.to_string())

    lime_c = summary.loc["LIME", "comp_auc_mean"]
    rand_c = summary.loc["Random", "comp_auc_mean"]
    shap_c = None if skip_shap else summary.loc[shap_kind, "comp_auc_mean"]
    print(f"\nLIME vs Random    : {lime_c:.4f} vs {rand_c:.4f} "
          f"(ratio {lime_c/rand_c if rand_c else float('nan'):.2f}x)")
    if not skip_shap:
        print(f"{shap_kind} vs Random: {shap_c:.4f} vs {rand_c:.4f} "
          f"(ratio {shap_c/rand_c if rand_c else float('nan'):.2f}x)")

    # paired Wilcoxon: is LIME actually better than random on the same instances?
    from scipy.stats import wilcoxon
    piv = res.pivot_table(index="instance", columns="explainer",
                          values="comprehensiveness_auc")
    comparisons = []
    comparison_methods = ["LIME"] if skip_shap else ["LIME", shap_kind]
    for a in comparison_methods:
        delta = (piv[a] - piv["Random"]).to_numpy()
        low, high = bootstrap_mean_ci(delta, seed=seed)
        if np.all(delta == 0):
            st, p = 0.0, 1.0
        else:
            st, p = wilcoxon(delta, alternative="greater")
        comparisons.append({"explainer": a, "n_instances": len(delta),
                            "mean_paired_difference": float(delta.mean()),
                            "ci95_low": low, "ci95_high": high,
                            "wilcoxon_alternative": "greater", "p_value": p,
                            "p_bonferroni": min(1.0, len(comparison_methods) * p)})
    pd.DataFrame(comparisons).to_csv(run_dir / "paired_comparisons.csv", index=False)
    print(pd.DataFrame(comparisons).to_string(index=False))

    finish_run(run_dir)
    print(f"\nwall clock {(time.time()-t_all)/60:.1f} min")
    print(f"wrote {out}\nwrote {s_out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", dest="model_name", default="RandomForest")
    ap.add_argument("--task", choices=["binary", "multiclass"],
                    default="multiclass")
    ap.add_argument("--seed", type=int, default=config.SEED)
    ap.add_argument("--n-instances", type=int, default=300)
    ap.add_argument("--num-samples", type=int, default=5000)
    ap.add_argument("--lime-seeds", type=int, nargs="+", default=[101, 202, 303])
    ap.add_argument("--masking", choices=["mean", "median"], default="mean")
    ap.add_argument("--skip-shap", action="store_true", help="Evaluate LIME and random only; explicitly recorded")
    main(**vars(ap.parse_args()))
