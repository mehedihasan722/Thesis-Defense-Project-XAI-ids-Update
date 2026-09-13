"""
models.py — detection layer.

Two things worth knowing:

1. SVM is wrapped in a Pipeline with StandardScaler. The scaler is fit inside
   the pipeline, so it sees training data only — scaling before the split
   would leak test statistics into training. Tree models need no scaling and
   are passed raw.

2. Soft voting is computed manually rather than with VotingClassifier, which
   refits every base estimator from scratch. Averaging predict_proba is the
   same mathematics at zero extra cost.
"""

from __future__ import annotations

import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

import config


def is_tree_model(clf) -> bool:
    """TreeSHAP only applies to tree ensembles. Anything else needs a
    different explainer — which is itself the RQ5 tooling-bias question."""
    from sklearn.pipeline import Pipeline as _P
    inner = clf.steps[-1][1] if isinstance(clf, _P) else clf
    return inner.__class__.__name__ in {
        "DecisionTreeClassifier", "RandomForestClassifier",
        "XGBClassifier", "ExtraTreesClassifier", "GradientBoostingClassifier",
    }


# Ordered by expected smoothness of the probability surface — the axis RQ1
# claims LIME stability tracks. Used to label results tables.
SURFACE_SMOOTHNESS = {
    "GaussianNB": "smooth, simple",
    "LogisticRegression": "smooth, linear",
    "MLP": "smooth, non-linear",
    "XGBoost": "averaged trees (200)",
    "RandomForest": "averaged trees (100)",
    "DecisionTree": "single tree, piecewise-constant",
}


def build_models(task: str, n_classes: int, seed: int = config.SEED,
                 include_svm: bool = True,
                 include_logreg: bool = False,
                 include_nb: bool = False,
                 include_mlp: bool = False) -> dict:
    common_tree = dict(random_state=seed, class_weight="balanced")

    models = {
        "DecisionTree": DecisionTreeClassifier(
            min_samples_leaf=5, max_depth=30, **common_tree,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, min_samples_leaf=5, max_depth=30,
            n_jobs=config.N_JOBS, **common_tree,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200, max_depth=8, learning_rate=0.1,
            subsample=0.8, colsample_bytree=0.8,
            n_jobs=config.N_JOBS, random_state=seed,
            tree_method="hist",
            objective="binary:logistic" if task == "binary" else "multi:softprob",
            num_class=None if task == "binary" else n_classes,
            eval_metric="logloss",
        ),
    }

    if include_logreg:
        # Not here to compete on macro-F1 — it will lose to the trees.
        # Its purpose is RQ1: a globally linear, perfectly smooth probability
        # surface is the control case for the claim that LIME stability
        # tracks surface smoothness. Prediction: Jaccard@5 near 1.0.
        models["LogisticRegression"] = Pipeline([
            ("scale", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=1000, C=1.0, class_weight="balanced",
                n_jobs=config.N_JOBS, random_state=seed,
                multi_class="multinomial" if task == "multiclass" else "auto",
            )),
        ])

    if include_nb:
        # Smooth Gaussian likelihoods, no learned decision boundary.
        # Weakest detector here by some margin — included as a smoothness
        # control for RQ1, not as a competitive baseline.
        models["GaussianNB"] = Pipeline([
            ("scale", StandardScaler()),
            ("nb", GaussianNB()),
        ])

    if include_mlp:
        # Smooth AND non-linear — fills the gap between LogisticRegression
        # and the tree ensembles on the smoothness axis. Also forces
        # KernelSHAP, which supplies the RQ5 cost comparison.
        models["MLP"] = Pipeline([
            ("scale", StandardScaler()),
            ("mlp", MLPClassifier(
                hidden_layer_sizes=(64, 32),
                activation="relu",
                max_iter=30,              # keep training time sane on 1.59M rows
                early_stopping=True,
                n_iter_no_change=3,
                batch_size=1024,
                random_state=seed,
            )),
        ])

    if include_svm:
        models["SVM"] = Pipeline([
            ("scale", StandardScaler()),
            ("svc", SVC(
                kernel="rbf",
                C=1.0,
                gamma="scale",
                class_weight="balanced",
                probability=True,      # required for soft voting; ~5x cost
                cache_size=1000,       # MB; larger = fewer kernel recomputes
                random_state=seed,
            )),
        ])

    return models


def soft_vote(probas: list[np.ndarray]) -> np.ndarray:
    """Mean of predict_proba matrices. All must share column order."""
    return np.mean(np.stack(probas, axis=0), axis=0)


class FrozenSoftVotingClassifier:
    """Serializable probability average of explicitly selected fitted models."""

    def __init__(self, members):
        if not members:
            raise ValueError('At least one fitted member is required')
        self.members = dict(members)
        self.classes_ = np.asarray(next(iter(members.values())).classes_)
        if any(not np.array_equal(m.classes_, self.classes_) for m in members.values()):
            raise ValueError('Ensemble members must share class column order')

    def predict_proba(self, X):
        return soft_vote([m.predict_proba(X) for m in self.members.values()])

    def predict(self, X):
        return self.classes_[self.predict_proba(X).argmax(axis=1)]
