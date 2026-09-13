"""
faithfulness.py — RQ2 metrics.

The question is not "do the top-k features suffice to build a model" — that
is feature selection, and retraining on a subset can recover performance from
correlated substitutes while the original explanation was wrong. The question
is whether THIS frozen model actually used them.

So: mask features on the input, never retrain, and measure what happens to
the prediction.

Comprehensiveness — mask the top-k. If the explanation is faithful the
predicted probability should fall sharply. Higher is better.

Sufficiency — keep ONLY the top-k, mask everything else. If the explanation
is faithful the probability should be largely retained. Higher is better.

Both are meaningless without the random-feature control: if masking k random
features drops the probability just as much, the explainer has told you
nothing.
"""

from __future__ import annotations

import numpy as np


def mask_features(x: np.ndarray, idx, baseline: np.ndarray) -> np.ndarray:
    """Replace the given feature indices with their training-set means."""
    xm = x.copy()
    xm[list(idx)] = baseline[list(idx)]
    return xm


def curves_for_instance(x, ranking, clf, baseline, label, ks) -> dict:
    """Comprehensiveness and sufficiency curves for one instance."""
    comp, suff = [], []
    all_idx = set(range(len(x)))

    for k in ks:
        top = ranking[:k]

        # comprehensiveness: remove the top-k
        comp.append(mask_features(x, top, baseline))

        # sufficiency: keep only the top-k
        rest = all_idx - set(top)
        suff.append(mask_features(x, rest, baseline))

    # One prediction batch preserves the exact perturbations while avoiding
    # twenty separate estimator/thread-pool launches per ranking.
    probabilities = clf.predict_proba(np.asarray(comp + suff))[:, label]
    return {"comprehensiveness": probabilities[:len(ks)].tolist(),
            "sufficiency": probabilities[len(ks):].tolist()}


def auc_over_k(values, p_original) -> float:
    """Normalised area under the curve.

    For comprehensiveness we report the DROP from the original probability,
    so higher = the masked features mattered more.
    """
    drops = [p_original - v for v in values]
    return float(np.mean(drops))


def auc_sufficiency(values, p_original) -> float:
    """Mean retained probability as a fraction of the original."""
    if p_original == 0:
        return 0.0
    return float(np.mean(values) / p_original)
