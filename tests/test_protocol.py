import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from attribution import predicted_class_values, probability_permutation_importance
from experiment import start_run, finish_run, bootstrap_mean_ci
from faithfulness import curves_for_instance, mask_features


class ProtocolTests(unittest.TestCase):
    def test_batched_masking_matches_individual_predictions(self):
        class Model:
            def predict_proba(self, X):
                p = 1 / (1 + np.exp(-np.asarray(X).sum(axis=1)))
                return np.column_stack([1 - p, p])
        x, baseline = np.array([1., 2., 3.]), np.zeros(3)
        ranking, ks = [2, 0, 1], [1, 2, 3]
        result = curves_for_instance(x, ranking, Model(), baseline, 1, ks)
        expected = [Model().predict_proba(mask_features(x, ranking[:k], baseline)[None, :])[0, 1] for k in ks]
        np.testing.assert_allclose(result['comprehensiveness'], expected)
        self.assertEqual(result['sufficiency'][-1], Model().predict_proba(x[None, :])[0, 1])

    def test_shap_selects_each_instances_class(self):
        values = np.arange(24).reshape(2, 3, 4)
        expected = np.stack([values[0, :, 3], values[1, :, 1]])
        np.testing.assert_array_equal(predicted_class_values(values, [3, 1], 3), expected)
        legacy = [values[:, :, c] for c in range(4)]
        np.testing.assert_array_equal(predicted_class_values(legacy, [3, 1], 3), expected)

    def test_shap_rejects_wrong_feature_axis(self):
        with self.assertRaises(ValueError):
            predicted_class_values(np.zeros((2, 4)), [0, 1], 3)

    def test_permutation_keeps_original_targets_and_ignores_unused_feature(self):
        class Model:
            def predict_proba(self, X):
                return np.column_stack([1 - X[:, 0], X[:, 0]])
        X = np.array([[0.1, 8], [0.9, 7], [0.2, 6], [0.8, 5]])
        mean, std = probability_permutation_importance(Model(), X, [0, 1, 0, 1], seed=3)
        self.assertGreater(mean[0], 0)
        self.assertEqual(mean[1], 0)
        self.assertEqual(std[1], 0)
        np.testing.assert_array_equal(X[:, 0], [0.1, 0.9, 0.2, 0.8])

    def test_run_directories_do_not_overwrite_and_track_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            first = start_run(folder, 'rq2', 'tree', 42, {})
            second = start_run(folder, 'rq2', 'tree', 42, {})
            self.assertNotEqual(first, second)
            self.assertEqual(json.loads((first / 'manifest.json').read_text())['status'], 'started')
            finish_run(first)
            self.assertEqual(json.loads((first / 'manifest.json').read_text())['status'], 'complete')

    def test_bootstrap_constant_effect_and_reproducibility(self):
        self.assertEqual(bootstrap_mean_ci([2, 2, 2], repeats=100), (2, 2))
        self.assertEqual(bootstrap_mean_ci([1, 2, 3], repeats=100),
                         bootstrap_mean_ci([1, 2, 3], repeats=100))


if __name__ == '__main__':
    unittest.main()
