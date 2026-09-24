# XAI intrusion detection: restarted comparative study

Mehedi Hasan (C213061) and Sazzadul Islam (C213066R), CSE, IIUC.

Development repository: https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update

## New study requested on 13 September 2026

The new study starts from raw NF-UNSW-NB15-v2 and NF-CSE-CIC-IDS2018-v2 releases. It compares classical models, shallow MLP, deep MLP, a feature-axis CNN, and three local instruction LLMs. LLMs were tested for both classification and explanations. Binary transfer is evaluated in both dataset directions; native multiclass results are evaluated separately.

The downloaded cleaned releases contain **1,986,745 UNSW flows** and **17,129,715 IDS2018 flows**. Both supply the same 39 retained predictive features after removing ports and targets. Dataset counts are measured from these files, not copied from the original-release website.

[Study protocol](thesis/study/PROTOCOL.md) records the model matrix, sampling, split rules and limitations before new model results are examined. [Change log](CHANGELOG.md) records implementation details. Every meaningful change uses a gitmoji commit with a detailed body and is pushed to this update repository.

[![Protocol CI](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/actions/workflows/protocol-ci.yml/badge.svg)](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/actions/workflows/protocol-ci.yml)

[Project Wiki](https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update/wiki) Â· [Contributing](CONTRIBUTING.md) Â· [Security](SECURITY.md) Â· [GitHub workflow](docs/GITHUB_WORKFLOW.md)

## Current status

- Both raw releases acquired and processed in batches.
- Three seeded, globally consistent feature-group splits prepared. Within-dataset and cross-dataset exact-feature overlap checks pass.
- Separate CPU PyTorch/Transformers environment installed.
- Fifteen study tests pass, covering splits, sampling, inference, metrics, masking, uncertainty and LLM tokenizer handling.
- All 84 detector configurations and 126 evaluation cells are complete and independently validated. All 1,200 LLM cases, final masking checks, 13 figures and 25 regression tests are complete; the current 109-page thesis preserves the original report and is available in [PDF](output/pdf/thesis_xai_ids_preserved.pdf) and [editable Word](output/docx/thesis_xai_ids_preserved.docx), with [23 separate added figures](results/study/preserved_report/README.md). See [LLM interpretation](results/study/llm/INTERPRETATION.md) for constant-class predictions and coverage limits.

For CPU feasibility, per dataset/seed caps are 200,000 training, 40,000 validation and 80,000 test flows, sampled uniformly after group assignment. These are bounded samples from the full releases. Rare-class support and sampling limitations must accompany results. The CNN's feature axis is not a temporal sequence.

LLM families: Qwen2.5-0.5B-Instruct, TinyLlama-1.1B-Chat-v1.0 and SmolLM2-1.7B-Instruct. These small local models do not represent frontier LLM performance. Downloads are pinned to immutable revisions; data and prompts are processed locally.

Measured results and embedded figures: [Results](results/study/RESULTS.md), [Across seeds](results/study/ACROSS_SEEDS.md), [RQ3](results/study/xai/ANALYSIS.md), [Figure index](results/study/figures/FIGURES.md). See [Progress](PROGRESS.md) for remaining execution.

## Run

```powershell
.venv-study/Scripts/python.exe -m pip install torch==2.8.0 --index-url https://download.pytorch.org/whl/cpu
.venv-study/Scripts/python.exe -m pip install -r study/requirements.txt
.venv-study/Scripts/python.exe study/download_dataset.py
.venv-study/Scripts/python.exe study/download_llms.py
.venv-study/Scripts/python.exe -m study.prepare
.venv-study/Scripts/python.exe -m unittest study.test_study -v
.venv-study/Scripts/python.exe -m study.run_training
```

Run from the repository root. The original `.venv` remains separate. Long neural runs save optimizer state and random-generator state after each epoch. Model metrics, class reports, confusion matrices and learning curves are saved under `results/study/`. Training status and logs record incomplete jobs explicitly.

Raw datasets, downloaded LLM weights, fitted checkpoints, large prediction files, environments and temporary renders are excluded from Git. Reproduce these locally using the scripts. Download sources and checksums are recorded in manifests.

## Thesis and historical evidence

The current revision starts from the original editable IIUC thesis. It retains all 25 original Word tables, 18 figure captions, 36 references, original media/styles and Appendices A and B; it adds 16 tables, 23 separately captioned figures, six references and Appendix C. The expanded sections incorporate completed results, RQ3, the historical audit, LLM failures and future work. The earlier shortened report is superseded. Original reference [28] remains unconfirmed and needs author review. See [revision notes and build instructions](docs/THESIS_REVISION.md). Author signatures and supervisor approval remain for the appropriate people to complete.

Older work is preserved in `results/final/`, the original scripts and `thesis/history/`. It includes a finding that 88.97% of original random-split test flows share retained features with training, which motivated the new globally group-disjoint design. Historical results must not be mixed into the restarted study's comparison tables.

Sources: [NetFlow dataset creators](https://staff.itee.uq.edu.au/marius/NIDS_datasets/), [cleaned IDS2018 release](https://www.kaggle.com/datasets/dhoogla/nfcsecicids2018v2), [Qwen](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct), [TinyLlama](https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0), [SmolLM2](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct).

