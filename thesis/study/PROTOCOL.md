# New comparative study protocol

Requested on 13 September 2026. This study starts afresh from the two raw NetFlow v2 parquet releases. Earlier results remain historical and are not mixed into its tables.

## Questions and model families

1. Compare DecisionTree, RandomForest, XGBoost, three-tree soft voting, shallow MLP, deep MLP and a feature-axis 1D CNN on each dataset, for binary and native multiclass detection.
2. Evaluate binary transfer in both directions: UNSW to IDS2018 and IDS2018 to UNSW. Native attack classes are not assumed equivalent across datasets.
3. Evaluate Qwen2.5-0.5B-Instruct, TinyLlama-1.1B-Chat-v1.0 and SmolLM2-1.7B-Instruct as local frozen language-model classifiers and explanation generators. Report their sizes and exclude claims about frontier LLMs.
4. Compare feature-removal sensitivity against random controls. LLM explanation fluency alone is not evidence of fidelity; report malformed responses and grounding failures.

## Data and split rules

Use the shared numeric feature schema after identifier and target removal. Canonicalize to float64 and replace non-finite values by a fixed zero rule, recording affected counts. Encode signed log1p at float32 precision, then hash that common model-input representation to assign groups globally, including across datasets. This also keeps raw values that become equal through input rounding together. Split approximately 70/15/15 percent of feature groups. Never use test labels for scaling, thresholds, early stopping or model selection.

For CPU feasibility, take uniform row reservoir samples after assigning groups: at most 200,000 training, 40,000 validation and 80,000 test rows per dataset and seed. Preserve full-release row/class counts and report sampled class support. Sampling does not make the data balanced or guarantee rare-class coverage. Use seeds 42, 7 and 1337. These bounded experiments must not be described as training on every flow.

Use fixed signed log1p at float32 precision for every model. Fit additional neural-network standardization on training only. Use fixed neural architectures, maximum 20 epochs and validation-loss early stopping. Report learning curves and best epochs. The CNN operates on a fixed feature order, not a temporal sequence; no temporal claim follows from its name.

For LLMs, compare four-example prompts selected only from source training data, with both source directions on a fixed class-balanced subset of 100 seed-42 test cases per target dataset. Score constrained benign/attack label completions and disclose that their normalized likelihood is not a calibrated attack probability. Score the classical/neural models on the same subset in a separate table. Full-test and balanced-subset metrics must not be merged.

Generate and retain rationales on a fixed smaller subset for the LLM's own decision and for a detector decision with supplied local feature-removal evidence. Report outputs verbatim, valid-feature references and mask sensitivity relative to random, without treating a model's self-report as ground truth.

## Reporting

Macro-F1, balanced accuracy, precision, recall, average precision, false-alarm rate, confusion matrices, per-class support, runtime and across-seed variation. Audit exact-feature overlap and cross-dataset shift. Lock the protocol before inspecting new model results; changes must be recorded with reasons. Model downloads and run manifests record immutable revisions and hashes. All long stages are resumable.

Keep the supplied IIUC reference PDF format for the eventual revised manuscript. A completed artifact must distinguish measured results from pending experiments and scope limitations.

## Protocol correction before any successful new fit

The initial tree fit failed because some raw finite values exceed float32 range. Apply the common signed-log representation to trees as well as neural networks and rebuild group assignments at that input precision. Count extreme raw values in the dataset audit. No successful model result preceded this correction.

## Tokenizer compatibility correction before TinyLlama execution

TinyLlama encodes standalone 0 and 1 labels with a shared whitespace token followed by a digit. The evaluator appends that prefix before scoring suffix logits; its common likelihood cancels when normalizing the two full candidates. Empty-prefix Qwen and SmolLM2 behavior is unchanged. Tests verify prefix handling and normalization. The original scorer is preserved in llm_evaluate_single_token_v1.py; its signature exactly matches the earlier Qwen run. Only that known equivalent empty-prefix signature can migrate during recovery.
