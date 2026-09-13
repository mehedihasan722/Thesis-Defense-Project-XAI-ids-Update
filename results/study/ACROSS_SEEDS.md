# Across-seed detector results

Mean and sample standard deviation across completed training/split seeds. Three seeds are planned; rows with fewer seeds are explicitly incomplete. These are descriptive variations, not population confidence intervals. Binary transfer uses the same frozen source model; native multiclass taxonomies differ across datasets.

| Task | Source | Target | Model | Seeds | Macro-F1 mean | SD |
| --- | --- | --- | --- | --- | --- | --- |
| binary | ids2018 | ids2018 | DecisionTree | 3 | 0.948660 | 0.014405 |
| binary | ids2018 | ids2018 | DeepMLP | 3 | 0.984218 | 0.001305 |
| binary | ids2018 | ids2018 | FeatureCNN | 3 | 0.975451 | 0.014551 |
| binary | ids2018 | ids2018 | RandomForest | 3 | 0.985209 | 0.002886 |
| binary | ids2018 | ids2018 | ShallowMLP | 3 | 0.973199 | 0.003821 |
| binary | ids2018 | ids2018 | SoftVoting | 3 | 0.978489 | 0.010316 |
| binary | ids2018 | ids2018 | XGBoost | 3 | 0.984998 | 0.002113 |
| binary | ids2018 | unsw | DecisionTree | 3 | 0.462416 | 0.031582 |
| binary | ids2018 | unsw | DeepMLP | 3 | 0.516442 | 0.025625 |
| binary | ids2018 | unsw | FeatureCNN | 3 | 0.485328 | 0.003121 |
| binary | ids2018 | unsw | RandomForest | 3 | 0.487553 | 0.000596 |
| binary | ids2018 | unsw | ShallowMLP | 3 | 0.443366 | 0.091664 |
| binary | ids2018 | unsw | SoftVoting | 3 | 0.509509 | 0.011181 |
| binary | ids2018 | unsw | XGBoost | 3 | 0.515659 | 0.023287 |
| binary | unsw | ids2018 | DecisionTree | 3 | 0.511758 | 0.115282 |
| binary | unsw | ids2018 | DeepMLP | 3 | 0.436423 | 0.025593 |
| binary | unsw | ids2018 | FeatureCNN | 3 | 0.427407 | 0.035863 |
| binary | unsw | ids2018 | RandomForest | 3 | 0.436624 | 0.004797 |
| binary | unsw | ids2018 | ShallowMLP | 3 | 0.457482 | 0.028274 |
| binary | unsw | ids2018 | SoftVoting | 3 | 0.444514 | 0.005765 |
| binary | unsw | ids2018 | XGBoost | 3 | 0.462947 | 0.004971 |
| binary | unsw | unsw | DecisionTree | 3 | 0.966201 | 0.009066 |
| binary | unsw | unsw | DeepMLP | 3 | 0.962679 | 0.009335 |
| binary | unsw | unsw | FeatureCNN | 3 | 0.962122 | 0.009976 |
| binary | unsw | unsw | RandomForest | 3 | 0.970096 | 0.006066 |
| binary | unsw | unsw | ShallowMLP | 3 | 0.864295 | 0.172195 |
| binary | unsw | unsw | SoftVoting | 3 | 0.967897 | 0.008925 |
| binary | unsw | unsw | XGBoost | 3 | 0.975027 | 0.004996 |
| multiclass | ids2018 | ids2018 | DecisionTree | 3 | 0.677509 | 0.033662 |
| multiclass | ids2018 | ids2018 | DeepMLP | 3 | 0.573869 | 0.112182 |
| multiclass | ids2018 | ids2018 | FeatureCNN | 3 | 0.543784 | 0.046055 |
| multiclass | ids2018 | ids2018 | RandomForest | 3 | 0.717850 | 0.035766 |
| multiclass | ids2018 | ids2018 | ShallowMLP | 3 | 0.538362 | 0.104070 |
| multiclass | ids2018 | ids2018 | SoftVoting | 3 | 0.711064 | 0.024477 |
| multiclass | ids2018 | ids2018 | XGBoost | 3 | 0.705952 | 0.035548 |
| multiclass | unsw | unsw | DecisionTree | 3 | 0.523028 | 0.047693 |
| multiclass | unsw | unsw | DeepMLP | 3 | 0.400606 | 0.048683 |
| multiclass | unsw | unsw | FeatureCNN | 3 | 0.407409 | 0.002033 |
| multiclass | unsw | unsw | RandomForest | 3 | 0.546743 | 0.035371 |
| multiclass | unsw | unsw | ShallowMLP | 3 | 0.386476 | 0.043682 |
| multiclass | unsw | unsw | SoftVoting | 3 | 0.537922 | 0.024720 |
| multiclass | unsw | unsw | XGBoost | 3 | 0.495152 | 0.046697 |

## Scope

Reported training uses 200000 sampled rows per source/seed. Extremely rare attack categories may be absent from training or test; per-class files and the data manifest retain that support information. Timing is not a controlled benchmark and interrupted neural fits can have segment-only timing.

![Seed-42 transfer heatmap](figures/01_detection_transfer.png)

The heatmap shows seed 42 only; use the table above for across-seed variation.
