# Training-only imbalance ablation

Same seed-42 group split and RF hyperparameters; change only class weights or training-row undersampling. Validation and test rows are untouched. Balanced-weight baseline reuses its completed checkpoint. No target-test model selection. Synthetic oversampling is deferred because integer/protocol fields need a justified mixed-feature synthesis policy.

| Source | Target | Variant | Train rows | Macro-F1 | False alarm rate |
| --- | --- | --- | --- | --- | --- |
| unsw | unsw | balanced_weights | 200000 | 0.964517 | 0.005494 |
| unsw | ids2018 | balanced_weights | 200000 | 0.437312 | 0.141218 |
| unsw | unsw | unweighted | 200000 | 0.970993 | 0.003026 |
| unsw | ids2018 | unweighted | 200000 | 0.306395 | 0.504417 |
| unsw | unsw | random_undersampling | 15588 | 0.960763 | 0.006351 |
| unsw | ids2018 | random_undersampling | 15588 | 0.335499 | 0.534840 |
| ids2018 | unsw | balanced_weights | 200000 | 0.487807 | 0.016118 |
| ids2018 | ids2018 | balanced_weights | 200000 | 0.981906 | 0.003098 |
| ids2018 | unsw | unweighted | 200000 | 0.490040 | 0.001584 |
| ids2018 | ids2018 | unweighted | 200000 | 0.982750 | 0.002522 |
| ids2018 | unsw | random_undersampling | 46528 | 0.487353 | 0.025806 |
| ids2018 | ids2018 | random_undersampling | 46528 | 0.981771 | 0.003156 |
