# Expanded study: measured results

Partial snapshot: 40 completed evaluation cells. Planned classical/neural matrix: 84 fitted configurations, 126 evaluation cells. LLM and explanation-transfer results are not included until executed. No thesis report is generated.

Training uses capped samples after global encoded-feature group partitioning. Source-only preprocessing; frozen binary models are evaluated within and across datasets. Multiclass taxonomies remain dataset-specific. One seed is not a final multi-seed estimate.

| Task | Source | Target | Seed | Model | N | Macro-F1 | Balanced accuracy | False alarm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| binary | ids2018 | ids2018 | 42 | DecisionTree | 80000 | 0.958219 | 0.971669 | 0.016703 |
| binary | ids2018 | unsw | 42 | DecisionTree | 80000 | 0.493095 | 0.494467 | 0.074003 |
| binary | ids2018 | ids2018 | 42 | DeepMLP | 80000 | 0.985233 | 0.977544 | 0.000994 |
| binary | ids2018 | unsw | 42 | DeepMLP | 80000 | 0.497215 | 0.502600 | 0.002792 |
| binary | ids2018 | ids2018 | 42 | FeatureCNN | 80000 | 0.984814 | 0.977828 | 0.001369 |
| binary | ids2018 | unsw | 42 | FeatureCNN | 80000 | 0.486904 | 0.485450 | 0.050080 |
| binary | ids2018 | ids2018 | 42 | RandomForest | 80000 | 0.981906 | 0.977482 | 0.003098 |
| binary | ids2018 | unsw | 42 | RandomForest | 80000 | 0.487807 | 0.492940 | 0.016118 |
| binary | ids2018 | ids2018 | 42 | ShallowMLP | 80000 | 0.971515 | 0.973924 | 0.008517 |
| binary | ids2018 | unsw | 42 | ShallowMLP | 80000 | 0.484965 | 0.482527 | 0.072574 |
| binary | ids2018 | ids2018 | 42 | SoftVoting | 80000 | 0.986505 | 0.978874 | 0.000692 |
| binary | ids2018 | unsw | 42 | SoftVoting | 80000 | 0.517806 | 0.513925 | 0.000455 |
| binary | ids2018 | ids2018 | 42 | XGBoost | 80000 | 0.982817 | 0.977807 | 0.002637 |
| binary | ids2018 | unsw | 42 | XGBoost | 80000 | 0.528419 | 0.519599 | 0.000429 |
| binary | unsw | ids2018 | 42 | DecisionTree | 80000 | 0.631847 | 0.672656 | 0.170474 |
| binary | unsw | unsw | 42 | DecisionTree | 80000 | 0.965252 | 0.992280 | 0.005117 |
| binary | unsw | ids2018 | 42 | DeepMLP | 80000 | 0.462417 | 0.683662 | 0.573491 |
| binary | unsw | unsw | 42 | DeepMLP | 80000 | 0.962009 | 0.996615 | 0.006104 |
| binary | unsw | ids2018 | 42 | FeatureCNN | 80000 | 0.456107 | 0.663075 | 0.571315 |
| binary | unsw | unsw | 42 | FeatureCNN | 80000 | 0.958516 | 0.994403 | 0.006533 |
| binary | unsw | ids2018 | 42 | RandomForest | 80000 | 0.437312 | 0.438909 | 0.141218 |
| binary | unsw | unsw | 42 | RandomForest | 80000 | 0.964517 | 0.994922 | 0.005494 |
| binary | unsw | ids2018 | 42 | ShallowMLP | 80000 | 0.424836 | 0.566497 | 0.561098 |
| binary | unsw | unsw | 42 | ShallowMLP | 80000 | 0.955505 | 0.996043 | 0.007247 |
| binary | unsw | ids2018 | 42 | SoftVoting | 80000 | 0.437963 | 0.443831 | 0.121950 |
| binary | unsw | unsw | 42 | SoftVoting | 80000 | 0.966490 | 0.992544 | 0.004922 |
| binary | unsw | ids2018 | 42 | XGBoost | 80000 | 0.457450 | 0.475265 | 0.061062 |
| binary | unsw | unsw | 42 | XGBoost | 80000 | 0.969719 | 0.974980 | 0.002753 |
| multiclass | ids2018 | ids2018 | 42 | DecisionTree | 80000 | 0.714728 | 0.749833 | 0.293851 |
| multiclass | ids2018 | ids2018 | 42 | RandomForest | 80000 | 0.687490 | 0.730165 | 0.029472 |
| multiclass | ids2018 | ids2018 | 42 | ShallowMLP | 80000 | 0.529367 | 0.730141 | 0.488680 |
| multiclass | ids2018 | ids2018 | 42 | SoftVoting | 80000 | 0.734358 | 0.731579 | 0.004093 |
| multiclass | ids2018 | ids2018 | 42 | XGBoost | 80000 | 0.737529 | 0.731315 | 0.000288 |
| multiclass | unsw | unsw | 42 | DecisionTree | 80000 | 0.490975 | 0.578049 | 0.005689 |
| multiclass | unsw | unsw | 42 | DeepMLP | 80000 | 0.453811 | 0.683338 | 0.009520 |
| multiclass | unsw | unsw | 42 | FeatureCNN | 80000 | 0.406063 | 0.614733 | 0.011650 |
| multiclass | unsw | unsw | 42 | RandomForest | 80000 | 0.542520 | 0.626799 | 0.005896 |
| multiclass | unsw | unsw | 42 | ShallowMLP | 80000 | 0.429173 | 0.619271 | 0.009987 |
| multiclass | unsw | unsw | 42 | SoftVoting | 80000 | 0.540894 | 0.596652 | 0.005351 |
| multiclass | unsw | unsw | 42 | XGBoost | 80000 | 0.509012 | 0.483947 | 0.002429 |

## Analysis boundaries

Cross-dataset degradation measures the combined effect of domain differences under this protocol; it does not identify its cause. Explanation transfer requires separate stability, feature-ranking and random-controlled masking evaluations. Historical stability/faithfulness audit is in audit/ANALYSIS.md.

## Reproduction

Run `.venv-study/Scripts/python.exe -m study.run_training`, then `.venv-study/Scripts/python.exe -m study.summarize`. Only folders with complete.json contribute. Partial model outputs are excluded.
