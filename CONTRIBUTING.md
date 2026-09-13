# Contributing

Use issues for reproducible failures, bounded experiment proposals and result audits. The forms request the dataset, model, seed, commit and evidence needed to investigate. Use `codex/` branches for agent work and a gitmoji commit title with a detailed rationale and validation body.

## Validation

From the repository root, with the study runtime installed:

```powershell
.venv-study/Scripts/python.exe -m unittest discover -s study -p "test_*.py" -v
.venv-study/Scripts/python.exe -m unittest discover -s tests -v
.venv-study/Scripts/python.exe scripts/check_repository.py
```

GitHub Actions runs these dataset-free checks with the locked CPU environment. It does not rerun the full research matrix. Full experiment validation additionally requires the local datasets and prediction files.

## Research changes

Record changes to data, preprocessing, split assignment, seeds, metrics, prompt formats and dependencies in the study protocol. Keep historical outputs separate. Treat a dependency upgrade as an environment change: update the lock deliberately and verify compatibility before reusing saved checkpoints. Do not select a protocol solely because its result matches an expected relationship.

Save measured tables and analysis in Markdown, embed relevant figures, and retain source hashes and model revisions. Report incomplete runs and invalid explanations. Do not commit raw datasets, credentials, environments or fitted weights. The thesis report stays unchanged until the expanded study is ready for manuscript revision.
