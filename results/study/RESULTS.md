# Expanded study: measured results

Partial snapshot: 12 completed evaluation cells. Planned classical/neural matrix: 84 fitted configurations, 126 evaluation cells. LLM and explanation-transfer results are not included until executed. No thesis report is generated.

Training uses capped samples after global encoded-feature group partitioning. Source-only preprocessing; frozen binary models are evaluated within and across datasets. Multiclass taxonomies remain dataset-specific. One seed is not a final multi-seed estimate.

| Task | Source | Target | Seed | Model | N | Macro-F1 | Balanced accuracy | False alarm rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| binary | unsw | ids2018 | 42 | DecisionTree | 80000 | 0.631847 | 0.672656 | 0.170474 |
| binary | unsw | unsw | 42 | DecisionTree | 80000 | 0.965252 | 0.992280 | 0.005117 |
| binary | unsw | ids2018 | 42 | DeepMLP | 80000 | 0.462417 | 0.683662 | 0.573491 |
| binary | unsw | unsw | 42 | DeepMLP | 80000 | 0.962009 | 0.996615 | 0.006104 |
| binary | unsw | ids2018 | 42 | RandomForest | 80000 | 0.437312 | 0.438909 | 0.141218 |
| binary | unsw | unsw | 42 | RandomForest | 80000 | 0.964517 | 0.994922 | 0.005494 |
| binary | unsw | ids2018 | 42 | ShallowMLP | 80000 | 0.424836 | 0.566497 | 0.561098 |
| binary | unsw | unsw | 42 | ShallowMLP | 80000 | 0.955505 | 0.996043 | 0.007247 |
| binary | unsw | ids2018 | 42 | SoftVoting | 80000 | 0.437963 | 0.443831 | 0.121950 |
| binary | unsw | unsw | 42 | SoftVoting | 80000 | 0.966490 | 0.992544 | 0.004922 |
| binary | unsw | ids2018 | 42 | XGBoost | 80000 | 0.457450 | 0.475265 | 0.061062 |
| binary | unsw | unsw | 42 | XGBoost | 80000 | 0.969719 | 0.974980 | 0.002753 |

## Analysis boundaries

Cross-dataset degradation measures the combined effect of domain differences under this protocol; it does not identify its cause. Explanation transfer requires separate stability, feature-ranking and random-controlled masking evaluations. Historical stability/faithfulness audit is in audit/ANALYSIS.md.

## Reproduction

Run `.venv-study/Scripts/python.exe -m study.run_training`, then `.venv-study/Scripts/python.exe -m study.summarize`. Only folders with complete.json contribute. Partial model outputs are excluded.
