# September 2026 thesis improvements

## Implemented

- Explicit, serializable three-tree soft voting with class-order validation.
- Predicted-class SHAP extraction across supported output shapes.
- RQ4 compares the same 300 cases and original predicted-class targets; probability-permutation sensitivity is named separately from score-based permutation importance.
- RQ2 uses three LIME seeds and paired mean/median masking evaluations with a random-feature control. Batched masked predictions preserve the individual-prediction result.
- Unique run directories, input/source hashes and completion manifests preserve revised evidence.
- A retained-feature overlap audit and three feature-group-disjoint detection splits address a limitation of the original random split.
- Final aggregation reports group-bootstrap intervals, group-average signed-rank tests, global multiplicity correction, class-level results and matched-instance associations.
- Results populate an editable manuscript and a PDF renderer following the supplied IIUC format.

## Verification and current execution

Ten protocol tests pass. Dependency consistency and saved-model loading have been verified. Group-disjoint detection has completed for all three seeds. Full revised explanation runs and additional random-split training are tracked in `results/final/suite_status.json`. Aggregation rejects incomplete suites and excludes small smoke runs.

The full voting-model protocol deliberately omits SHAP. It does not substitute a member's SHAP values for an explanation of the combined predictor. KernelSHAP integration for this predictor remains outside the selected evidence.

## Interpretation limits

The original seed-42 three-member ensemble macro-F1 is 0.6687. Historical six-member ensemble results are different evidence. The original random-flow split has 88.97% test-flow overlap with training in retained-feature representation; group-disjoint validation is therefore reported separately.

The revised manuscript does not claim preregistered mechanism falsification, a universal stability-faithfulness tradeoff, causal feature identification, cross-network validation or institutional approval. Historical RQ1 results retain explicit provenance. RQ3 remains future work.

## Reproduction caution

`run_baselines.py` replaces checkpoints for the specified seed. The resumable final suite avoids retraining seed 42. Preserve checkpoints before intentionally repeating a training run. Revised explanation outputs use unique directories.
