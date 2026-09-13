"""
run_baselines.py — Stage 2.

    python run_baselines.py --task binary
    python run_baselines.py --task multiclass

Trains DT, RF, XGBoost and a soft-voting ensemble, records timing, writes a
results table, and saves the fitted models. Those saved models are what RQ1
and RQ2 load — the faithfulness experiment requires a FROZEN model, so
nothing downstream may retrain.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

import config
from models import build_models, soft_vote, FrozenSoftVotingClassifier
from evaluation import evaluate, per_class_recall


def main(task: str, seed: int, no_svm: bool = False,
         logreg: bool = False, nb: bool = False, mlp: bool = False, ensemble_members=None):
    t_all = time.time()

    # ---- load the Stage 1 checkpoint -------------------------------------
    ckpt = config.DATA_PROCESSED / "unsw_clean.parquet"
    if not ckpt.exists():
        raise SystemExit("Run verify.py first — no checkpoint found.")
    df = pd.read_parquet(ckpt)
    print(f"loaded {len(df):,} flows, {df.shape[1] - 2} features")

    target = config.LABEL_BINARY if task == "binary" else config.LABEL_MULTI
    X = df.drop(columns=[config.LABEL_BINARY, config.LABEL_MULTI])
    y_raw = df[target]

    # XGBoost needs integer labels; keep the encoder for readable output
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    class_names = [c.item() if hasattr(c, "item") else c for c in le.classes_]
    benign_label = int(le.transform(["Benign"])[0]) if task == "multiclass" else 0
    print(f"task={task}  classes={class_names}")

    feature_names = list(X.columns)

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=seed, stratify=y
    )
    print(f"train={len(X_tr):,}  test={len(X_te):,}")

    # ---- train ------------------------------------------------------------
    models = build_models(task, n_classes=len(class_names), seed=seed,
                          include_svm=not no_svm,
                          include_logreg=logreg,
                          include_nb=nb, include_mlp=mlp)
    ensemble_members = ensemble_members or ["DecisionTree", "RandomForest", "XGBoost"]
    if len(set(ensemble_members)) != len(ensemble_members) or set(ensemble_members) - set(models):
        raise ValueError("Ensemble members must be unique enabled model names")
    rows, probas, timings = [], {}, {}

    for name, clf in models.items():
        print(f"\n--- {name} ---", flush=True)
        t0 = time.time()
        clf.fit(X_tr, y_tr)
        train_s = time.time() - t0
        print(f"  trained in {train_s:.1f}s", flush=True)

        t0 = time.time()
        proba = clf.predict_proba(X_te)
        infer_s = time.time() - t0
        latency_ms = infer_s / len(X_te) * 1000

        pred = proba.argmax(axis=1)
        probas[name] = proba

        m = evaluate(y_te, pred, proba, np.arange(len(class_names)),
                     benign_label, name)
        m["train_time_s"] = round(train_s, 1)
        m["inference_ms_per_flow"] = round(latency_ms, 5)
        rows.append(m)
        timings[name] = {"train_s": train_s, "infer_ms": latency_ms}
        print(f"  macro-F1 {m['macro_f1']:.4f}   FAR {m['false_alarm_rate']:.4%}")

        joblib.dump(clf, config.RESULTS_MODELS / f"{name}_{task}_seed{seed}.joblib")

    # ---- soft-voting ensemble --------------------------------------------
    print("\n--- SoftVotingEnsemble ---")
    ensemble = FrozenSoftVotingClassifier({name: models[name] for name in ensemble_members})
    joblib.dump(ensemble, config.RESULTS_MODELS / f"SoftVotingEnsemble_{task}_seed{seed}.joblib")
    ens_proba = soft_vote([probas[name] for name in ensemble_members])
    ens_pred = ens_proba.argmax(axis=1)
    m = evaluate(y_te, ens_pred, ens_proba, np.arange(len(class_names)),
                 benign_label, "SoftVotingEnsemble")
    m["train_time_s"] = round(sum(timings[name]["train_s"] for name in ensemble_members), 1)
    m["inference_ms_per_flow"] = round(sum(timings[name]["infer_ms"] for name in ensemble_members), 5)
    rows.append(m)
    print(f"  macro-F1 {m['macro_f1']:.4f}   FAR {m['false_alarm_rate']:.4%}")

    # ---- outputs ----------------------------------------------------------
    res = pd.DataFrame(rows)[[
        "model", "macro_f1", "macro_recall", "macro_precision", "pr_auc",
        "false_alarm_rate", "accuracy", "train_time_s", "inference_ms_per_flow",
    ]]
    out = config.RESULTS_TABLES / f"baselines_{task}_seed{seed}.csv"
    res.to_csv(out, index=False)
    print(f"\n{res.to_string(index=False)}")
    print(f"\nwrote {out}")

    if task == "multiclass":
        pcr = per_class_recall(y_te, ens_pred, class_names)
        p_out = config.RESULTS_TABLES / f"per_class_recall_{task}_seed{seed}.csv"
        pcr.to_csv(p_out, index=False)
        print(f"\n{pcr.to_string(index=False)}")
        print(f"wrote {p_out}")

    # test indices + metadata, so RQ1/RQ2 use the identical split
    meta = {
        "task": task, "seed": seed, "ensemble_members": ensemble_members,
        "class_names": class_names,
        "feature_names": feature_names,
        "benign_label": benign_label,
        "test_index": [int(i) for i in X_te.index],
    }
    with open(config.RESULTS_MODELS / f"split_{task}_seed{seed}.json", "w") as f:
        json.dump(meta, f)

    print(f"\ntotal {time.time() - t_all:.1f}s")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", choices=["binary", "multiclass"], default="binary")
    ap.add_argument("--seed", type=int, default=config.SEED)
    ap.add_argument("--no-svm", action="store_true",
                    help="skip SVM (much faster; required for multiclass "
                         "unless you have many hours)")
    ap.add_argument("--logreg", action="store_true",
                    help="add LogisticRegression (smooth, linear)")
    ap.add_argument("--nb", action="store_true",
                    help="add GaussianNB (smooth, simple)")
    ap.add_argument("--mlp", action="store_true",
                    help="add MLP (smooth, non-linear)")
    ap.add_argument("--ensemble-members", nargs="+", default=None,
                    help="Explicit enabled members; defaults to DecisionTree RandomForest XGBoost")
    main(**vars(ap.parse_args()))
