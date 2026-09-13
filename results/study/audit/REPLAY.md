# Historical prediction replay

Replayed the original maximum class probability for every unique case in the three original RQ2 files using the currently available historical checkpoints. A matching original probability does not validate masked predictions: historical feature rankings were not stored in those CSVs. Full masking replay requires regenerating explanations under the exact historical configuration, whose provenance is incomplete.

| Model | Cases | Maximum absolute error | Errors above 1e-6 |
| --- | --- | --- | --- |
| DecisionTree | 483 | 1.11022302e-16 | 0 |
| RandomForest | 483 | 4.4408921e-16 | 0 |
| XGBoost | 483 | 1.11022302e-16 | 0 |
