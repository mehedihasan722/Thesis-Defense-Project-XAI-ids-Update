"""
explainers.py — SHAP explainer selection, and the RQ5 tooling-bias question.

TreeSHAP is exact and fast, but only exists for tree ensembles. For a linear
model you must fall back to something else. That fallback is not a neutral
implementation detail: Hernandez et al. (2025) excluded their LSTM from SHAP
analysis because DeepExplainer does not support PyTorch RNNs, then trained
that same LSTM on SHAP-derived features anyway. Tool availability determined
which models got explained.

This module makes the fallback explicit and measurable.
"""

from __future__ import annotations

import time
import numpy as np
import shap
from sklearn.pipeline import Pipeline

from models import is_tree_model
from attribution import predicted_class_values


def get_shap_explainer(clf, background):
    """Return (explainer, kind). Kind is reported in results tables."""
    if is_tree_model(clf):
        return shap.TreeExplainer(clf), "TreeSHAP"

    if isinstance(clf, Pipeline):
        inner = clf.steps[-1][1]
        if inner.__class__.__name__ == "LogisticRegression":
            # LinearExplainer is exact for a linear model, but must see the
            # data in the space the model was fitted in — i.e. after scaling.
            scaler = clf.steps[0][1]
            bg_scaled = scaler.transform(background)
            return shap.LinearExplainer(inner, bg_scaled), "LinearSHAP"

    # Model-agnostic fallback (GaussianNB, MLP, anything else). Correct for
    # any model, but orders of magnitude slower — which is exactly the cost
    # the RQ5 tooling-bias chapter reports. Background is k-means summarised
    # to 25 centroids; without that reduction KernelSHAP is unusable here.
    bg = shap.kmeans(background, 25)
    return shap.KernelExplainer(clf.predict_proba, bg), "KernelSHAP"


def shap_ranking(explainer, kind, clf, x, label, n_features):
    """Feature indices ordered by |shap value|, plus elapsed seconds."""
    t0 = time.time()

    if kind == "LinearSHAP":
        scaler = clf.steps[0][1]
        xs = scaler.transform(x.reshape(1, -1))
        sv = explainer.shap_values(xs)
    else:
        sv = explainer.shap_values(x.reshape(1, -1))

    elapsed = time.time() - t0
    arr = predicted_class_values(sv, [label], n_features)[0]
    return [int(i) for i in np.argsort(-np.abs(arr))], elapsed
