# Completed executable study

All 84 detector configurations and 126 evaluation cells are complete and independently checked. All 14 RQ3 model pilots, source-only calibration, training-only imbalance comparison and three full local LLM runs with classification and explanations are complete. Valid LLM explanations have named-versus-random masking checks; invalid outputs remain in coverage denominators.

Results, tables and embedded figures are in results/study/RESULTS.md, ACROSS_SEEDS.md and the xai/, llm/, calibration/, imbalance/ and shift/ analysis files. The thesis report remains unchanged.

Limitations remain scientific, not hidden: small explanation cohorts, three small CPU LLMs, rounded flow serialization, masking distribution shifts and no temporal/analyst validation. Historical original probabilities replay, but exact old masks cannot be replayed because original rankings were not saved. Do not interpret inverse stability/faithfulness relationships as proof of falsification.
