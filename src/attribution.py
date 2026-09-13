"""Select SHAP outputs without silently truncating mismatched arrays."""
import numpy as np


def predicted_class_values(values, labels, n_features):
    labels = np.asarray(labels, dtype=int)
    n = len(labels)
    # Older SHAP returns one (samples, features) array per class.
    arr = np.stack(values, axis=-1) if isinstance(values, list) else np.asarray(values)
    if arr.ndim == 3 and arr.shape[:2] == (n, n_features):
        return arr[np.arange(n), :, labels]
    # Binary single-output explainers report the positive-class attribution.
    # Its negative has the same absolute importance for the other class.
    if arr.shape == (n, n_features):
        return arr
    raise ValueError(f'Unexpected SHAP shape {arr.shape}; expected ({n}, {n_features}, classes)')


def probability_permutation_importance(clf, X, labels, repeats=10, seed=42):
    """Mean absolute change in each original predicted class's probability.

    Targets remain fixed after perturbation. This is a sensitivity measure,
    not the conventional permutation drop in a predictive performance score.
    """
    X = np.asarray(X, dtype=float)
    labels = np.asarray(labels, dtype=int)
    rows = np.arange(len(X))
    original = clf.predict_proba(X)[rows, labels]
    rng = np.random.default_rng(seed)
    scores = np.empty((X.shape[1], repeats))
    for feature in range(X.shape[1]):
        for repeat in range(repeats):
            perturbed = X.copy()
            perturbed[:, feature] = rng.permutation(X[:, feature])
            changed = clf.predict_proba(perturbed)[rows, labels]
            scores[feature, repeat] = np.abs(original - changed).mean()
    return scores.mean(axis=1), scores.std(axis=1)
