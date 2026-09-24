# Thesis defense presentation

[Editable PowerPoint](../output/presentation/thesis_defense.pptx) · [PDF](../output/presentation/thesis_defense.pdf)

28 slides: 24 main slides including questions, and four backup slides. Eleven charts are native editable PowerPoint charts with embedded data workbooks. Each figure has its own slide. Speaker notes document sources and interpretation limits. Suggested rehearsal target: 20–25 minutes before questions.

The original title, authors and RQ1–RQ4 structure are retained. The LLM work is a separate extension. Results come from saved study evidence, without new model training or changes to the thesis report. Chart workbooks retain six decimals and labels show three decimals (integer counts for coverage). Detection plots show means, with per-model seed SD in notes and in the full report.

## Slide outline and speaker notes

### 1. Evaluating the Reliability of Explainable AI in Ensemble-Based Intrusion Detection Systems

Original title and authors from thesis/reference/original_thesis.docx. Expanded work includes neural baselines, transfer and LLMs.

### 2. The research problem

Source: preserved thesis, expanded introduction and results. Predictive relevance refers to a masking proxy, not causal truth.

### 3. Research questions

Original RQ numbering preserved. RQ4 is historical LIME/TreeSHAP agreement. The LLM classification and explanation study is a separate extension.

### 4. Research gap and contribution

Scope of this study, not an exhaustive claim of novelty. Do not claim the first systematic study. The unverified historical reference [28] is not used to substantiate novelty.

### 5. Datasets and shared representation

Source: thesis/manuscript.md, expanded methods. Cleaned release sizes differ from per-fit sampling caps. Attack taxonomies are not assumed equivalent.

### 6. Evaluation protocol

Source: expanded methods. Signed-log float32 representation and consistent global feature-group hashing. No chronological split. Caps apply per dataset and seed, not the full release.

### 7. Model comparison

Seven families x two datasets x two tasks x three seeds = 84 fits. Binary models evaluate both domains and native multiclass models evaluate their own domain. Feature CNN convolves tabular feature positions, not time.

### 8. Explanation evaluation

Source: results/study/xai/aggregate.csv and expanded methods. 14 binary models at training seed 42 x two domains. Fix the original predicted class. Median masking, absolute feature ranking, k=1..5. Bootstrap intervals use 5,000 stratified resamples conditional on the fitted model.

### 9. Binary detection on UNSW

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.009066197183791503; RandomForest 0.006065935924989893; XGBoost 0.004995868585582929; SoftVoting 0.008925032539188563; ShallowMLP 0.17219511122690373; DeepMLP 0.009334764037067624; FeatureCNN 0.009976016759947309. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 10. Binary detection on IDS2018

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.014404769336826667; RandomForest 0.0028860869072894427; XGBoost 0.002112966418252044; SoftVoting 0.010316328885479382; ShallowMLP 0.003820579210452952; DeepMLP 0.001305051347687204; FeatureCNN 0.014551085107464026. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 11. Transfer from UNSW to IDS2018

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.11528164403090586; RandomForest 0.004796805770502372; XGBoost 0.004970545330764434; SoftVoting 0.00576485434017666; ShallowMLP 0.02827360985901998; DeepMLP 0.025593145845505986; FeatureCNN 0.035863280179991366. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 12. Transfer from IDS2018 to UNSW

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.03158189394582218; RandomForest 0.0005955645248190199; XGBoost 0.0232872598593301; SoftVoting 0.011181062250329759; ShallowMLP 0.09166378536828515; DeepMLP 0.02562501840034948; FeatureCNN 0.003121014155962509. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 13. Explanation stability after transfer

Source: results/study/xai/aggregate.csv. Twenty balanced cases, three explainer seeds, training seed 42. Stability describes repeatability only.

### 14. Masking advantage after transfer

Source: results/study/xai/aggregate.csv. Positive advantage means greater fixed-class probability removal than matched random masks. Intervals conditional on one fit and 20 cases. Values do not establish causal feature importance.

### 15. Stability does not establish faithfulness

RF UNSW to IDS2018: median absolute -0.1338, mean absolute -0.1247, median signed 0.0795, mean signed 0.2215. Source: expanded masking sensitivity section. 112 summary cells, 2,240 cases. Out-of-distribution perturbations remain a limitation.

### 16. Historical result audit

Source: results/study/audit and preserved report historical audit. Spearman correlations: DT .203684, RF .208214, XGB .258441. Maximum aggregate error 5.17e-7. Unmasked replay error 4.44e-16. Exact historical masks cannot be replayed because rankings were not saved. Overlap limits generalization claims. An inverse aggregate ordering alone is not evidence of fabricated results.

### 17. RQ4: agreement between explainers

Source: original thesis RQ4 results, preserved report. Historical protocol only. Do not generalize these values to the expanded neural fits or target-domain experiments. No new neural SHAP or TOPSIS evaluation is claimed.

### 18. Language-model extension

Source: results/study/llm and expanded LLM methods. Local instruction models, four-example prompt, constrained classification scoring. CPU float32, two threads, maximum 192 generated tokens for explanations.

### 19. LLM classification under the frozen prompt

Source: expanded LLM results. Qwen and Smol predict Benign throughout, TinyLlama predicts Attack. Macro-F1 1/3. This is a result for this prompt, scoring procedure and these small models, not every LLM.

### 20. Valid own-decision explanations

Source: results/study/llm/masking_coverage.csv. Validity requires usable feature selections under the saved protocol. Conditional masking performance cannot substitute for coverage.

### 21. Valid detector-grounded explanations

Source: results/study/llm/masking_coverage.csv. Validity requires usable feature selections under the saved protocol. Conditional masking performance cannot substitute for coverage.

### 22. Conclusions

Answer RQ1â€“RQ3 using the expanded evidence and RQ4 using historical agreement. Explain that a masking proxy cannot prove causal faithfulness. Avoid treating seed-42 case intervals as uncertainty across training runs.

### 23. Limitations and future work

Remaining scope includes per-attack-class explanation rank drift, expanded explainer comparisons, and realistic deployment validation. No causal ground truth or analyst study in this thesis.

### 24. Questions

Discussion. Main defense ends here. The following slides support examiner questions.

### 25. Backup: UNSW multiclass detection

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.047693142930470986; RandomForest 0.035371234882619944; XGBoost 0.04669684533074675; SoftVoting 0.02472046117464253; ShallowMLP 0.043681959742955224; DeepMLP 0.04868298781779598; FeatureCNN 0.002033069549416719. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 26. Backup: IDS2018 multiclass detection

Source: results/study/across_seed_summary.csv. Mean across seeds 7, 42, 1337. Individual SD values: DecisionTree 0.03366153565428263; RandomForest 0.03576606494204943; XGBoost 0.035547511085713836; SoftVoting 0.024476531260417572; ShallowMLP 0.10406992982841348; DeepMLP 0.1121817133935734; FeatureCNN 0.04605505259775461. Chart shows means only. Full report contains separate SD figures. Same feature-group protocol across models.

### 27. Backup: neural training protocol

Source: expanded methods. Learning rate .001, weight decay .0001, class-weighted cross entropy, early stopping on unweighted source validation loss. The CNN is not a temporal model.

### 28. Backup: sources and evidence

Primary project sources: thesis/reference/original_thesis.docx; output/pdf/thesis_xai_ids_preserved.pdf; thesis/manuscript.md (expanded numerical narrative only, original RQ4 numbering retained in deck). Complete bibliography in preserved report. Historical reference [28] remains unverified and supports no presentation claim. Repository: https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update

## Rebuilding

Authoring source: `study/build_defense.mjs`. Requires the bundled Artifact Tool runtime and presentation finalizer referenced in that source. Prepare `tmp/defense-deck/data.json` with `detection`, `xai`, and `llm` lists from the three source CSV files below. Copy the authoring script into `tmp/defense-deck/build.mjs`. Link the build directory node_modules to the bundled runtime, set RUNTIME_NODE_MODULES, and run with bundled Node. Use fresh final output and validation receipt paths for each rebuild. Native PDF export uses Microsoft PowerPoint.

## Input provenance

- `results/study/across_seed_summary.csv`: SHA-256 `7c1202bfd559fb59a53542c790c4768b9633b6a4de05a1af1cfd97e36fc98723`
- `results/study/xai/aggregate.csv`: SHA-256 `10d35a303cbb5b16f004964b919ece5f4a7b95672260f40a21b974d5c3c4ef13`
- `results/study/llm/masking_coverage.csv`: SHA-256 `b69ecbc91f88ad311082f79c218b330370efff9349a9c5f235a1d1d3de3de007`
- `thesis/reference/original_thesis.docx`: SHA-256 `7c52c19f5d02137223e261a54d9fe7d6291634f3a89b8efbd3a01301eb07b841`
