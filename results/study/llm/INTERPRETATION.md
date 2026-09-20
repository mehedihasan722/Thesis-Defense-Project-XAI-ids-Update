# Completed LLM study: interpretation

All three immutable local models completed 400 unique source/target/row cases and 80 paired own-decision and detector-grounded explanations. Each source/target combination contains 100 class-balanced cases and 20 explanation pairs. Completion is an execution result, not evidence of useful detection.

## Classification collapse

Qwen and SmolLM2 predicted Benign for every evaluated case; TinyLlama predicted Attack for every case. On each 50/50 cohort, this gives accuracy and balanced accuracy of 0.5 and macro-F1 of approximately 0.333333. Benign-only predictions have zero false alarms but miss every attack. Attack-only predictions detect every attack but flag every benign case.

These findings apply to the tested frozen models, four-example prompts, rounded flow serialization and constrained label scoring. They do not establish that all LLM intrusion detection fails. Tokenizer compatibility tests and checkpoint verification do not rule out prompt sensitivity or label-token bias.

## Explanation evidence

Read [valid-output coverage](masking_coverage.csv) alongside [masking analysis](MASKING_ANALYSIS.md). A conditional score based on a few valid outputs does not characterize all generated explanations. Evidence-feature membership checks do not validate every prose claim. Named-versus-random masking is a model sensitivity proxy, not causal ground truth.

## Appropriate next research

Predefine a separate follow-up comparing label verbalizations, label-order permutations, input representations and prompt formats. Include constant-class baselines and independent development data. Keep this completed benchmark frozen; do not tune against its test outcomes and present the revised score as the original result. Larger models and fine-tuning require separate compute and evaluation designs.

The current deliverable is the completed, reproducible comparison, including negative findings. The thesis manuscript revision remains a separate task.
