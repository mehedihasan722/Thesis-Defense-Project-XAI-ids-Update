# Python environment verification

Verified 11 September 2026 in `D:\Test Thesis\thesis-xai-ids`.

## Repair

Installed workspace-local CPython 3.11.16 under `.python/` and repaired `.venv`
without deleting its installed scientific packages. Regenerated activation
scripts to remove the old `E:\Thesis\Project` path. Runtime/cache directories
are ignored by Git. No model retraining was performed.

```powershell
. .\.venv\Scripts\Activate.ps1
python --version
python -m pip check
python -m unittest discover -s tests -v
```

Alternatively, use `.\.venv\Scripts\python.exe` directly. Use `python -m pip`
instead of copied console launchers. The workspace-local Python directory must
remain available; moving the project requires regenerating the environment paths.

## Passed checks

- CPython 3.11.16 launches and PowerShell activation selects the project interpreter.
- NumPy 1.26.4, pandas, SciPy, scikit-learn 1.4.2, SHAP 0.45.1, LIME and
  XGBoost 2.0.3 import successfully.
- `python -m pip check`: no broken requirements.
- Five protocol unit tests passed.
- All six saved multiclass classifiers loaded and produced predictions for 25 rows.
- Frozen DT/RF/XGBoost ensemble matched manual probability averaging and survived
  a temporary joblib save/load round trip with unchanged predictions.
- DT/RF/XGBoost/LogisticRegression SHAP each returned a 39-feature ranking.
- DecisionTree RQ1, RQ2 and RQ4 completed end to end with 10 instances and
  100 perturbation samples. RQ1 used its ten default seeds; RQ2 used 101/202/303
  and mean masking. StandardScaler emitted only feature-name warnings during
  the direct SHAP compatibility check.

## Smoke-run evidence

Outputs are under `results/tables/runs/`:

- `rq1_DecisionTree_seed42_20260911T015908Z_f4621ead`
- `rq2_DecisionTree_seed42_20260911T015855Z_48f00e01`
- `rq4_DecisionTree_seed42_20260911T015909Z_17a4c1d6`

Each folder contains a completed manifest and result CSVs. Historical tables
were preserved. These small runs verify execution, not the thesis findings.
Full-scale revised experiments, fresh model training, median-mask runs and
KernelSHAP integration are not covered by this verification.
