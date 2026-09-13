# Matched-case LLM comparisons

Only complete 100-case runs are included. Each target cohort has 50 benign and 50 attack unique feature groups; these metrics are not comparable to population-prevalence 80000-case results. LLM scores normalize two label-token likelihoods and are not calibrated attack probabilities.

| Model | Source | Target | Macro-F1 | False alarm rate |
| --- | --- | --- | --- | --- |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | unsw | 0.333333 | 0.000000 |
| DecisionTree | unsw | unsw | 0.979992 | 0.040000 |
| RandomForest | unsw | unsw | 0.969997 | 0.040000 |
| XGBoost | unsw | unsw | 0.979992 | 0.000000 |
| SoftVoting | unsw | unsw | 0.969997 | 0.040000 |
| ShallowMLP | unsw | unsw | 0.979992 | 0.040000 |
| DeepMLP | unsw | unsw | 0.979992 | 0.040000 |
| FeatureCNN | unsw | unsw | 0.979992 | 0.040000 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | ids2018 | 0.333333 | 0.000000 |
| DecisionTree | unsw | ids2018 | 0.558638 | 0.200000 |
| RandomForest | unsw | ids2018 | 0.304163 | 0.200000 |
| XGBoost | unsw | ids2018 | 0.330357 | 0.100000 |
| SoftVoting | unsw | ids2018 | 0.285714 | 0.200000 |
| ShallowMLP | unsw | ids2018 | 0.526162 | 0.380000 |
| DeepMLP | unsw | ids2018 | 0.772633 | 0.400000 |
| FeatureCNN | unsw | ids2018 | 0.782135 | 0.400000 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | unsw | 0.333333 | 0.000000 |
| DecisionTree | ids2018 | unsw | 0.417193 | 0.060000 |
| RandomForest | ids2018 | unsw | 0.333333 | 0.000000 |
| XGBoost | ids2018 | unsw | 0.454365 | 0.000000 |
| SoftVoting | ids2018 | unsw | 0.396740 | 0.000000 |
| ShallowMLP | ids2018 | unsw | 0.374310 | 0.080000 |
| DeepMLP | ids2018 | unsw | 0.355178 | 0.000000 |
| FeatureCNN | ids2018 | unsw | 0.365804 | 0.040000 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | ids2018 | 0.333333 | 0.000000 |
| DecisionTree | ids2018 | ids2018 | 0.979992 | 0.000000 |
| RandomForest | ids2018 | ids2018 | 0.979992 | 0.000000 |
| XGBoost | ids2018 | ids2018 | 0.979992 | 0.000000 |
| SoftVoting | ids2018 | ids2018 | 0.979992 | 0.000000 |
| ShallowMLP | ids2018 | ids2018 | 0.979992 | 0.000000 |
| DeepMLP | ids2018 | ids2018 | 0.979992 | 0.000000 |
| FeatureCNN | ids2018 | ids2018 | 0.979992 | 0.000000 |

Explanation checks count valid JSON with 1-3 exact feature names and nonempty explanation text. Detector grounding checks only whether named features appear in supplied evidence; it does not validate every prose claim, usefulness or causal correctness. All raw outputs and failures remain in per-model cases.jsonl.
