# Explanation masking checks

Only valid JSON explanations with 1–3 exact feature names enter masking evaluation. Invalid outputs remain failures in the coverage denominator; conditional masking scores do not describe invalid cases. A selected set is compared with three random sets of equal size, using a fixed source-training-background median. Original predicted class is fixed. LLM original scores must replay within 1e-4.

Named-feature removal advantage is a perturbation sensitivity proxy, not causal validity. Detector explanations are checked against the frozen XGBoost; own explanations against the generating LLM. These scores use different models and are not interchangeable.

| Model | Source | Target | Kind | Valid / total |
| --- | --- | --- | --- | --- |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | unsw | own | 0 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | unsw | detector | 2 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | ids2018 | own | 0 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | ids2018 | detector | 1 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | ids2018 | unsw | own | 0 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | ids2018 | unsw | detector | 2 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | ids2018 | ids2018 | own | 0 / 20 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | ids2018 | ids2018 | detector | 0 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | unsw | own | 0 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | unsw | detector | 13 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | ids2018 | own | 0 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | ids2018 | detector | 17 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | unsw | own | 13 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | unsw | detector | 16 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | ids2018 | own | 13 / 20 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | ids2018 | detector | 12 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | unsw | unsw | own | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | unsw | unsw | detector | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | unsw | ids2018 | own | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | unsw | ids2018 | detector | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ids2018 | unsw | own | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ids2018 | unsw | detector | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ids2018 | ids2018 | own | 0 / 20 |
| TinyLlama/TinyLlama-1.1B-Chat-v1.0 | ids2018 | ids2018 | detector | 0 / 20 |

## Conditional masking results

These means apply only to valid explanations. After excluding invalid outputs, the retained subset need not be class-balanced. Do not compare these conditional means without the coverage table.

| Model | Source | Target | Kind | Valid cases | Named-minus-random advantage |
| --- | --- | --- | --- | --- | --- |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | ids2018 | unsw | detector | 2 | 0.403604 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | ids2018 | detector | 1 | 0.080669 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | unsw | unsw | detector | 2 | 0.000009 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | ids2018 | detector | 12 | 0.133176 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | ids2018 | own | 13 | -0.011371 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | unsw | detector | 16 | 0.053784 |
| Qwen/Qwen2.5-0.5B-Instruct | ids2018 | unsw | own | 13 | -0.003809 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | ids2018 | detector | 17 | 0.026998 |
| Qwen/Qwen2.5-0.5B-Instruct | unsw | unsw | detector | 13 | 0.236691 |
