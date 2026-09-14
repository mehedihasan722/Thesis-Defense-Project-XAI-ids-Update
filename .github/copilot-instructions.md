# Repository guidance for GitHub Copilot

This is a reproducible XAI intrusion-detection research project. Read README.md, PROGRESS.md, thesis/study/PROTOCOL.md and CONTRIBUTING.md before changing code. Use study/ for the restarted study; keep historical src/ and original results separate.

## Evidence and scope

Preserve raw predictions, failed outputs, invalid explanation coverage and run manifests. Never invent results or force stability and faithfulness rankings to agree. Distinguish case-level associations from model-level comparisons. Masking sensitivity is not causal ground truth.

The local datasets, fitted weights, prediction parquet files and LLM caches are excluded from Git. A cloud checkout cannot verify full scientific results without them. Report missing evidence explicitly. Do not download datasets or launch full training/LLM jobs as part of a routine code task. Local runs are already managed by a sequential runner; do not duplicate or interrupt them.

Do not change evaluator source, token handling, prompts, seeds, split rules or model revisions during a live run. Such changes can invalidate checkpoint signatures. For authorized protocol changes, record the amendment and preserve prior evidence.

Keep the thesis report unchanged unless the user explicitly requests its revision. Publish results and diagrams through Markdown, with sources and limitations.

## Setup and validation

Use Python 3.11. Install the locked CPU runtime in an isolated environment:

```sh
python -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r study/requirements.lock.txt
python -m pip check
python -m unittest discover -s study -p 'test_*.py' -v
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

Run these commands from the repository root using the environment's Python. Existing Windows runtime: .venv-study/Scripts/python.exe. GitHub CI uses Linux. Do not claim full experiment completion from these dataset-free tests.

## Delivery

Use a bounded issue and a focused pull request. Follow the repository PR template; include the problem, final behavior, relevant validation and limitations. Use detailed gitmoji commits. Avoid unrelated changes and do not merge automatically.

After a task is verified, update the associated issue with evidence and commit links. Close only after all acceptance criteria pass. Check actual processes and manifests before calling an experiment running or complete; stale status JSON is insufficient. Do not assert a cause for an interruption without evidence.
