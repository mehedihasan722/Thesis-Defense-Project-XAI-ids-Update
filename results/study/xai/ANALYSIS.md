# RQ3 explanation-transfer analysis

Each row uses 20 balanced unique feature groups and a frozen seed-42 detector. LIME runs are first averaged within each instance. Percentile bootstrap intervals resample the 10 benign and 10 attack groups separately (5000 repeats), preserving the balanced cohort. They are conditional on this model and small cohort, not across-training-seed uncertainty or causal confidence intervals.

| Source | Target | Model | Jaccard@5 | LIME minus random drop | 95% bootstrap interval |
| --- | --- | --- | --- | --- | --- |
| ids2018 | unsw | DecisionTree | 0.5710 | 0.0261 | [-0.0422, 0.0980] |
| ids2018 | ids2018 | DecisionTree | 0.5427 | 0.0218 | [-0.0826, 0.1349] |
| ids2018 | unsw | DeepMLP | 0.6530 | -0.0253 | [-0.0599, -0.0038] |
| ids2018 | ids2018 | DeepMLP | 0.6063 | 0.0612 | [0.0086, 0.1227] |
| ids2018 | unsw | FeatureCNN | 0.5974 | 0.0588 | [-0.0093, 0.1401] |
| ids2018 | ids2018 | FeatureCNN | 0.6595 | -0.0036 | [-0.0575, 0.0447] |
| ids2018 | unsw | RandomForest | 0.6433 | 0.0031 | [-0.0079, 0.0164] |
| ids2018 | ids2018 | RandomForest | 0.6232 | -0.0066 | [-0.0257, 0.0181] |
| ids2018 | unsw | ShallowMLP | 0.7119 | -0.0519 | [-0.0898, -0.0121] |
| ids2018 | ids2018 | ShallowMLP | 0.6690 | 0.1142 | [0.0598, 0.1733] |
| ids2018 | unsw | SoftVoting | 0.5440 | 0.0145 | [-0.0137, 0.0471] |
| ids2018 | ids2018 | SoftVoting | 0.5177 | -0.0117 | [-0.0384, 0.0189] |
| ids2018 | unsw | XGBoost | 0.6853 | -0.0162 | [-0.0662, 0.0167] |
| ids2018 | ids2018 | XGBoost | 0.7238 | 0.0394 | [0.0092, 0.0820] |
| unsw | unsw | DecisionTree | 0.5240 | 0.3809 | [0.3381, 0.4281] |
| unsw | ids2018 | DecisionTree | 0.5960 | 0.0394 | [-0.0525, 0.1545] |
| unsw | unsw | DeepMLP | 0.7587 | 0.3043 | [0.1943, 0.3956] |
| unsw | ids2018 | DeepMLP | 0.7810 | 0.6057 | [0.4976, 0.7028] |
| unsw | unsw | FeatureCNN | 0.6645 | 0.3756 | [0.3202, 0.4172] |
| unsw | ids2018 | FeatureCNN | 0.7603 | 0.5199 | [0.4002, 0.6464] |
| unsw | unsw | RandomForest | 0.9778 | 0.3165 | [0.2938, 0.3395] |
| unsw | ids2018 | RandomForest | 0.9222 | -0.1338 | [-0.2034, -0.0476] |
| unsw | unsw | ShallowMLP | 0.8611 | 0.2813 | [0.1724, 0.3747] |
| unsw | ids2018 | ShallowMLP | 0.8833 | 0.1400 | [-0.0109, 0.2966] |
| unsw | unsw | SoftVoting | 0.7778 | 0.3628 | [0.3286, 0.3961] |
| unsw | ids2018 | SoftVoting | 0.8056 | -0.0395 | [-0.0898, 0.0370] |
| unsw | unsw | XGBoost | 0.5165 | 0.3922 | [0.3443, 0.4356] |
| unsw | ids2018 | XGBoost | 0.5706 | 0.0268 | [-0.0032, 0.0848] |

## Interpretation

Positive advantage means LIME-ranked masks reduce the original predicted-class score more than matched-size random masks, under the fixed source-median baseline. A confidence interval crossing zero does not establish superiority. Negative values and inverse stability relationships are preserved, not treated as errors to be removed. The 14-model comparison is exploratory; intervals are not multiplicity-adjusted.

Ranking absolute LIME weights can select both supporting and opposing evidence. Source-median replacements can leave the observed flow distribution. These limitations constrain the term faithfulness: this is a masking sensitivity proxy, not ground-truth explanation correctness.

![RQ3 domain shifts](../figures/03_explanation_transfer.png)

Arrows connect different domain cohorts, not paired instances.
