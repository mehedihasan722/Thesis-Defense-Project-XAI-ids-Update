# Change log

## 2026-09-13 - Restarted comparative study

- Begin a separate study from raw NF-UNSW-NB15-v2 and NF-CSE-CIC-IDS2018-v2 data. Preserve the original study as historical evidence.
- Add globally consistent feature-group partitions, streaming reservoir sampling, three seeds and cross-dataset duplicate checks.
- Add fresh tree baselines, shallow MLP, deep MLP and feature-axis CNN training with validation early stopping, checkpoint recovery and two-way binary transfer.
- Define classification and explanation experiments for three local instruction LLMs. Downloads are pinned to immutable revisions. LLM experiments are pending, not completed results.
- Validate partition invariance, reservoir selection, neural probabilities/serialization and false-alarm calculation: four new tests pass.

## Earlier September 2026 work preserved in this update

- Repair CPython 3.11 environment; correct three-model ensemble membership and SHAP class extraction.
- Introduce matched-target importance comparisons, paired masking controls, source/input manifests and group-aware final aggregation.
- Add LIME checkpoint recovery with a test of exact continuation; ten original protocol tests pass.
- Adapt thesis PDF generation to the supplied IIUC layout: A4, Times New Roman, front matter, five chapters, dotted contents and separate Roman/Arabic numbering. Final expanded manuscript is pending new results.

Each subsequent meaningful change is committed with a gitmoji title, detailed rationale, validation and known limitations, then pushed to the user-specified update repository.
