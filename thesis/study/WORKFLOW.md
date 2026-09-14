# Experiment execution and interpretation workflow

1. Prepare both datasets using signed-log float32-equivalent feature groups shared across datasets and seeds. Keep raw data out of Git.
2. Run study.run_training for the 84 fitted configurations and 126 evaluation cells. Restart uses completed-model or neural-epoch checkpoints. Inspect logs after interruptions; a running status file alone is not proof a process remains alive.
3. Run study.run_xai for 14 frozen seed-42 models, each evaluated on two 20-case balanced unique-group cohorts. Preserve rankings, signs, controls and masking curves.
4. Run study.calibration and study.imbalance for source-only calibration and training-only imbalance extensions. These are seed-42 studies, not three-seed extensions.
5. Run study.run_llms sequentially for the three local models, with classification and explanations on fixed matched cohorts. Retain invalid outputs. The pilot is a separate output namespace and is not included in the 100-case benchmark.
6. Refresh study.summarize and study.summarize_llm after completed runs. Commit and push completed evidence and substantive code changes with detailed gitmoji commits.

## Interpretation safeguards

Stability, random-adjusted removal effect, sufficiency gap and classification quality are separate measures. Do not force their rankings to match. Domain shifts are descriptive under this protocol, not evidence of causation. Balanced explanation/LLM cohorts have different prevalence from full test samples.

Timing limitation: runs share CPU resources, so recorded times are operational observations, not controlled hardware benchmarks. Neural training times after epoch recovery cover the current execution segment, not necessarily all interrupted work; do not compare those as complete training costs. Classification and explanation outputs remain valid independently of this timing limitation.

The thesis report is intentionally unchanged until experiments and their analysis are complete. Completed and pending status must remain explicit in Markdown. Historical outputs remain separate from the restarted study.

## Concurrent execution amendment, 14 September 2026

At the user's explicit request, study.run_llms_parallel resumes TinyLlama and SmolLM2 concurrently and then runs study.finalize if both succeed. Start it only after confirming no existing evaluators or supervisors are active. Do not run it alongside study.run_llms. The evaluator, model precision, prompts and checkpoints are unchanged. Shared CPU and memory contention can affect wall-clock timings; previous sequential ETAs do not apply. Model-specific timestamped logs and process IDs are retained in local status.
