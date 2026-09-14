# Study progress

The thesis report remains unchanged. Results, tables, figures and analysis are stored in Markdown.

Completed: all 84 detector configurations and 126 evaluation cells across both datasets and three seeds; independent probability, label, macro-F1 and confusion-matrix validation; all 14 RQ3 pilots; calibration, imbalance and feature-shift analyses. Figures are embedded in results/study/RESULTS.md.

The historical audit reproduces original probabilities for 483 cases per tree model. Exact old masking replay remains unavailable because the original rankings were not saved. An inverse stability/faithfulness association alone does not establish falsification.

Qwen is complete: 400 unique cases and 80 paired own/detector explanations verified. On 14 September 2026 at 14:44 UTC, the user requested concurrent execution. TinyLlama resumed from 328/400 cases and SmolLM2 was launched alongside it. Both evaluator processes were verified alive during startup; this does not yet establish completed inference. The concurrent supervisor runs finalization only after both exit successfully.

Remaining: complete the two remaining local LLM runs, then evaluate valid explanations against random masks, retain invalid-output coverage, regenerate matched tables and figures, run final checks and publish. Interrupted LLM runs resume saved cases. These are CPU jobs and can take hours.

The TinyLlama shared-prefix tokenizer correction is tested; equivalent single-token Qwen recovery is checked against the exact preserved legacy source. No outcomes are changed to force an expected relationship.

Git destination: update/main at https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update.git. Detailed gitmoji commits; raw datasets, environments and weights remain excluded.
