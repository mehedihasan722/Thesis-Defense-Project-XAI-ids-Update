"""Check grouping and model serialization assumptions used by final analysis."""
from pathlib import Path
import sys
import tempfile
import unittest

import joblib
from joblib.externals import cloudpickle
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from lime.lime_tabular import LimeTabularExplainer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'src'))
from build_final_results import clustered_ci
from models import FrozenSoftVotingClassifier


class FinalAnalysisTests(unittest.TestCase):
    def test_lime_checkpoint_preserves_next_explanation(self):
        X = np.random.RandomState(42).normal(size=(100, 3))
        clf = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X, X[:, 0] + X[:, 1] > 0)
        explainer = LimeTabularExplainer(X, random_state=101, mode='classification')
        kwargs = dict(num_features=3, num_samples=100, labels=(1,))
        explainer.explain_instance(X[0], clf.predict_proba, **kwargs)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'checkpoint.joblib'
            joblib.dump(cloudpickle.dumps(explainer), path, compress=3)
            restored = cloudpickle.loads(joblib.load(path))
        expected = explainer.explain_instance(X[1], clf.predict_proba, **kwargs).as_map()[1]
        actual = restored.explain_instance(X[1], clf.predict_proba, **kwargs).as_map()[1]
        np.testing.assert_allclose(actual, expected, rtol=0, atol=0)

    def test_cluster_interval_constant_effect(self):
        np.testing.assert_allclose(clustered_ci([.2, .2, .2], ['a', 'a', 'b'], repeats=100), [.2,.2])

    def test_ensemble_round_trip(self):
        X = np.array([[0],[1],[2],[3]])
        a = DecisionTreeClassifier(max_depth=1).fit(X,[0,0,1,1])
        b = DecisionTreeClassifier(max_depth=1).fit(X,[0,1,1,1])
        clf = FrozenSoftVotingClassifier({'a':a,'b':b})
        expected = (a.predict_proba(X)+b.predict_proba(X))/2
        np.testing.assert_allclose(clf.predict_proba(X), expected)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'model.joblib'
            joblib.dump(clf,path)
            np.testing.assert_allclose(joblib.load(path).predict_proba(X), expected)

    def test_ensemble_rejects_incompatible_class_order(self):
        X = np.array([[0],[1],[2],[3]])
        a = DecisionTreeClassifier().fit(X,[0,0,1,1])
        b = DecisionTreeClassifier().fit(X,[1,1,2,2])
        with self.assertRaises(ValueError):
            FrozenSoftVotingClassifier({'a':a,'b':b})


if __name__ == '__main__':
    unittest.main()
