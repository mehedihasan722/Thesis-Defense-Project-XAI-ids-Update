# Abstract

This thesis evaluates detection, explanation repeatability and masking sensitivity separately across NF-UNSW-NB15-v2 and NF-CSE-CIC-IDS2018-v2. Their cleaned releases contain 1,986,745 and 17,129,715 flows. A common 39-feature representation and global feature-group splits reduce exact-input overlap; training is capped at 200,000 sampled flows per dataset and seed.

Seven classical, ensemble and neural detector families produce 84 fitted configurations and 126 evaluation cells across three seeds. The highest mean within-dataset binary macro-F1 is 0.9750 for XGBoost on UNSW and 0.9852 for random forest on IDS2018. All seven models deteriorate under frozen cross-dataset evaluation. LIME transfer uses 20 balanced unique feature groups per domain and three explainer seeds. UNSW-trained random forest retains high target-domain Jaccard@5 (0.9222), but its removal advantage over random masks becomes negative (-0.1338). Repeatability therefore does not establish predictive relevance.

Three local instruction language models complete 1,200 classification cases and 240 pairs of own-decision and detector-grounded explanations. Each predicts only one class under the frozen four-example prompt and constrained scoring protocol, yielding macro-F1 0.3333 on balanced cohorts. Explanation validity coverage is limited and reported alongside conditional masking scores. Historical reconstruction reveals interpretation risks but no material arithmetic reversal or evidence that inverse associations alone demonstrate falsification. The contribution is a reproducible evaluation of detection, transfer and explanation sensitivity, with explicit limits on causal and deployment claims.

Keywords: intrusion detection; explainable AI; LIME; cross-dataset transfer; neural networks; language models; reproducibility.

# CHAPTER I
INTRODUCTION

## 1.1 Background and motivation

Network intrusion detection assigns security-relevant labels to observed traffic. In a flow-based system, a classifier receives a fixed vector of traffic measurements rather than a complete packet trace. A high score on a held-out portion of one dataset is useful evidence about that evaluation setting, but it does not establish performance on a different network. Differences in traffic composition, attack coverage, collection procedures and feature distributions can all matter. A common NetFlow representation makes a controlled cross-dataset comparison possible without making the domains interchangeable [1].

Explanations add another evaluation problem. A ranked feature list may be repeatable across repeated explainer runs, yet removal of those features may have little effect on the model. Conversely, correlated or substitutable features can produce different rankings with similar predictive effects. LIME constructs a local interpretable approximation of a predictor [2]; the existence of that approximation does not by itself validate every explanation for every model and domain. This study therefore measures repeatability, masking sensitivity and detection performance separately.

The original project emphasized tree-based intrusion detectors and explanation reliability. The revised work retains that motivation while adding neural baselines, a second dataset, frozen transfer tests and small local language models. The original thesis title is retained for continuity; the experimental scope now extends beyond ensembles. The revised numerical findings come from the expanded study. Earlier results are used only in an explicitly separated historical audit.

## 1.2 Problem statement

The practical question is whether a detector and its explanations remain informative when the evaluation domain changes. Treating explanation stability as a proxy for faithfulness would make a highly consistent but uninformative explanation appear reliable. Treating a large raw removal effect as explanation quality would also ignore whether randomly selected features cause comparable effects. Finally, accepting a fluent language-model rationale without checking its output validity or relationship to the explained model could mistake a plausible narrative for measured evidence.

There is also a reproducibility problem. Ambiguous metric names, missing feature rankings and incomplete run provenance limit what can be reconstructed after an experiment. The historical study contained metrics with different directions under similar faithfulness terminology. The revised evaluation explicitly records the original predicted class, perturbation baseline, rankings, matched random controls, sample sizes and valid-output denominators.

## 1.3 Research questions

Table 1.1. Research questions and corresponding evidence.

| Question | Evaluation |
| --- | --- |
| RQ1: How repeatable are local explanations? | Pairwise Jaccard@5 across three LIME seeds for each fixed case and detector. |
| RQ2: Do selected features influence predictions more than random features, and how does this relate to stability? | Fixed-class probability drops, matched-size random controls, historical reconstruction and baseline/ranking sensitivity. |
| RQ3: How do detection and explanation reliability transfer across datasets? | Frozen binary models in both directions, separate source and target explanation cohorts, three-seed detection summaries. |
| RQ4: How do small local LLMs perform as classifiers and explanation generators? | Matched balanced classification cohorts, own and detector-grounded rationales, valid-output coverage and conditional masking. |

These questions organize the revised report. RQ4 concerns the completed LLM extension rather than any historical use of that label. Native multiclass prediction is a within-dataset task; no equivalence between the two attack taxonomies is assumed.

## 1.4 Objectives and contributions

The first objective is to compare classical, ensemble and neural detectors under the same feature representation and split rules. The second is to distinguish detection transfer from explanation transfer. The third is to evaluate LLM classification and explanation with the same held-out cases and explicit output-failure accounting. The fourth is to audit earlier results without modifying them to obtain a preferred relationship.

The resulting contribution is an auditable experimental comparison: 84 detector configurations, 126 evaluation cells, 14 binary explanation pilots, three complete local LLM runs and controlled extensions for calibration, class imbalance and masking choices. The work does not claim to introduce LLM intrusion detection, a new explanation algorithm, or the first cross-dataset evaluation. Its value is the combination of shared split controls, retained evidence and transparent negative findings in a bounded reproducible study.

## 1.5 Scope and organization

All conclusions apply to the two cleaned releases, sampled training sets, chosen feature representation and frozen configurations. No online deployment, chronological evaluation, causal ground-truth explanation benchmark or analyst usefulness experiment is performed. The local LLMs range from approximately 0.5 to 1.7 billion parameters and do not represent all language models.

Chapter II positions the work within prior research. Chapter III specifies the protocol and metrics. Chapter IV reports the completed results and historical audit. Chapter V answers the research questions and describes remaining limitations and future work. Appendices identify reproducibility artifacts and retain detailed numerical tables.

# CHAPTER II
LITERATURE REVIEW

## 2.1 Shared features and generalization

Sarhan, Layeghy and Portmann propose standard NetFlow feature sets to address incompatibility between intrusion datasets [1]. Their work motivates evaluating the same input schema across different data sources. A shared schema enables comparison, but does not remove differences in class proportions or feature distributions. In this thesis, the shared schema is an experimental prerequisite rather than evidence that transfer should succeed.

Within-dataset hold-out evaluation and cross-dataset evaluation answer different questions. The former tests performance on data drawn from the same released source under a stated partition; the latter tests a frozen model on another source. A fair transfer experiment must preserve the source-trained preprocessing and avoid choosing thresholds or model settings using target-test outcomes. The present work adopts that restriction and keeps native multiclass taxonomies separate.

## 2.2 Local explanation methods

Ribeiro, Singh and Guestrin introduce LIME as a model-agnostic local explanation method using an interpretable approximation near a prediction [2]. Its local sampling makes repeated runs a relevant object of investigation. This thesis measures top-feature overlap across random seeds and saves the full weights so that later interpretation does not depend only on an aggregate stability score.

Lundberg and Lee introduce SHAP as a framework for feature attribution [3]. SHAP is relevant to the original project's explanation context, but the completed expanded transfer pilot uses LIME. The revised report does not relabel historical SHAP output as a new cross-dataset result. Comparing explainers in a future extension would require matched cases, backgrounds and clearly specified attribution semantics.

## 2.3 Stability, sensitivity and faithfulness

Yeh et al. study explanation infidelity and sensitivity, and show why optimizing sensitivity alone can admit a constant explanation [4]. Their definition of sensitivity differs from seed-to-seed Jaccard overlap. The relevant implication is conceptual: stability and fidelity are distinct properties, so a positive relationship cannot be assumed in advance.

The ERASER benchmark evaluates rationalized NLP models and helps formalize removal and retention approaches to rationale evaluation [5]. This thesis adapts the general perturbation idea to numeric flows, but a source-background replacement is not the same as deleting words. Masked flow vectors may violate relationships among traffic measurements. A large removal effect therefore establishes sensitivity to the specified intervention, not a causal account of the actual attack.

Random controls are necessary because some models may react strongly to almost any masking. Comparing an explanation-selected set to an equally sized random set provides a relative measure under the same intervention. It still does not guarantee that the intervention is realistic. Reporting both raw and random-adjusted effects helps separate these concerns.

## 2.4 Language models for intrusion detection and explanation

Houssel et al. evaluate LLM network intrusion detection and discuss a complementary role in explanation and threat response [6]. Their study already establishes that using LLMs for these tasks is not a new idea. The present comparison differs in its small local models, fixed numerical serialization and retained matched-case evidence; it is not a replication of their full setup.

The eX-NIDS framework enriches prompts with flow context and threat-intelligence information to generate explanations of detector decisions [7]. This supports separating a detector's classification from the LLM's interpretive role. Here, detector-grounded prompts instead supply local feature-removal evidence from a frozen XGBoost model. The validity checks are deliberately narrow: JSON structure, exact feature references and named-versus-random masking do not verify every sentence of generated prose.

## 2.5 Research gap and positioning

Table 2.1. Positioning of the present study relative to selected work.

| Research strand | Existing contribution | Focus of this thesis |
| --- | --- | --- |
| Standard NetFlow features [1] | Common dataset representations. | Globally consistent encoded-feature grouping and frozen bidirectional evaluation. |
| LIME and SHAP [2,3] | Local explanation and attribution frameworks. | Empirical repeatability and masking evaluation, with LIME used in the new transfer pilot. |
| Explanation evaluation [4,5] | Distinguishes explanation properties and perturbation criteria. | Separate stability, random-adjusted removal and baseline/ranking sensitivity. |
| LLM NIDS [6,7] | Classification feasibility and context-supported explanations. | Small local models, matched cases, output-failure coverage and stored responses. |

The gap investigated is whether these evaluation dimensions agree when tested together under a shared, leakage-controlled protocol. This is a scoped empirical question, not a claim that previous research has never combined any of these elements. The literature review is targeted to the study design rather than a systematic review of every explainable IDS publication.

# CHAPTER III
METHODOLOGY

## 3.1 Study design and evidence separation

The expanded study starts from the two raw cleaned NetFlow v2 parquet releases and preserves historical results separately. Configuration files fix the three seeds (42, 7 and 1337), sample caps and model families. Completed-run markers control inclusion in summaries. Partial runs do not count as completed experiments. Source hashes, model revisions and saved predictions support later validation.

![Figure 3.1. Experimental workflow: source fitting, held-out evaluation and retained evidence.](../results/study/report/figures/07_workflow.png)

The primary detector matrix contains seven families, two datasets, two tasks and three seeds: 7 x 2 x 2 x 3 = 84 configurations. Binary models are evaluated both within source and on the other dataset, producing 84 binary cells. Multiclass models produce 42 within-dataset cells. The total is 126 evaluation cells, each using 80,000 sampled test rows. Auxiliary explanation and LLM cohorts are smaller and explicitly separated.

## 3.2 Datasets, representation and splitting

Table 3.1. Data and sampling scope.

| Item | Specification |
| --- | --- |
| NF-UNSW-NB15-v2 | 1,986,745 rows in the downloaded cleaned release. |
| NF-CSE-CIC-IDS2018-v2 | 17,129,715 rows in the downloaded cleaned release. |
| Shared input | 39 retained numeric features after port and target removal; exact inventory in Appendix A. |
| Partition | Approximately 70/15/15 percent of encoded feature groups for train/validation/test. |
| Per dataset and seed | Up to 200,000 training, 40,000 validation and 80,000 test rows. |
| Sampling | Uniform row-priority reservoir after group assignment; original class imbalance is retained. |

For each raw numeric value x, the common transformation is sign(x) log(1 + abs(x)), stored at float32 precision. Non-finite inputs use a fixed zero replacement rule, with counts retained. Group assignment hashes the common encoded feature vector, using the same seed-dependent rule across both datasets. Consequently, identical model-input representations cannot be assigned to training in one dataset and test in the other for the same seed. Grouping uses features rather than labels. Repeated rows within a partition may still remain; group separation does not imply independent observations throughout a test set.

Uniform row sampling occurs after partition assignment. It does not balance classes or guarantee that rare categories appear in every training and test sample. All sampled class counts are retained in the data manifest. The signed-log transformation is fixed, while additional neural standardization is fitted only on source training rows. Target-test data are not used for scaling, early stopping, calibration or threshold selection.

The initial tree fit failed because extreme finite raw values exceeded float32 range. Before any successful new model fit, the representation was corrected to apply the common signed-log encoding to every detector and rebuild groups at the model-input precision. IDS2018 contains 213 such extreme values in 211 rows. Encoding avoids overflow, but does not prove that those traffic rates are physically valid. The correction and remaining data-quality limitation are retained rather than hidden.

## 3.3 Classical, ensemble and neural models

Table 3.2. Fixed detector configurations.

| Model | Configuration |
| --- | --- |
| DecisionTree | Maximum depth 30; minimum leaf size 5; balanced class weights. |
| RandomForest | 100 trees; maximum depth 30; minimum leaf size 5; balanced class weights. |
| XGBoost | 200 trees; depth 8; learning rate 0.1; row and column sampling 0.8; histogram tree method. |
| SoftVoting | Equal mean of aligned probabilities from DecisionTree, RandomForest and XGBoost. |
| ShallowMLP | 39 inputs, hidden layer 64 with ReLU, output layer. |
| DeepMLP | Hidden widths 256, 128, 64 with ReLU; dropout 0.1 after the first two hidden layers. |
| FeatureCNN | Feature-axis convolutions 1-to-16 and 16-to-32 channels, kernel 3, padding 1; flattened representation; dense 64; dropout 0.1. |

The neural models use source-training standardization, class-weighted cross-entropy, AdamW with learning rate 0.001 and weight decay 0.0001, batch size 1024 and at most 20 epochs. Early stopping uses unweighted source-validation loss with patience four. Best checkpoints and learning histories are retained. The output dimension follows the applicable binary or dataset-specific class inventory. The CNN acts along a fixed feature ordering; it is not a sequence model of chronological traffic.

These are fixed baselines under a bounded compute budget, not exhaustive architecture searches. Binary transfer reuses the same trained model and preprocessing on both datasets. A different training seed also changes the group partition and sample, so the reported standard deviation combines training and split variation. Three seeds do not establish a precise population uncertainty estimate.

## 3.4 Detection metrics

For a class treated as positive, precision is TP/(TP+FP), recall is TP/(TP+FN), and F1 is twice precision times recall divided by their sum. Macro-F1 averages class F1 values; balanced accuracy averages class recalls. Binary false-alarm rate is FP/(FP+TN) on benign cases. Accuracy and average precision are retained with confusion matrices and class support in the result artifacts. Per-class undefined precision/F1 values are set to zero. Macro-F1 averages the complete dataset class inventory, including zero scores for absent test classes; balanced accuracy averages recalls for classes present in the test labels. Average precision is averaged only over classes having both positive and negative test examples. Absent classes are recorded.

Results are summarized by mean and sample standard deviation across the three seeds. Macro-F1 is emphasized because accuracy alone can conceal minority-class failures, but it remains dependent on the evaluation cohort. In particular, an 80,000-row prevalence-preserving sample and a balanced 100-case LLM cohort are different evaluation settings. Their scores must not be pooled into a single ranking without that distinction.

## 3.5 LIME repeatability and feature masking

For each of the 14 seed-42 binary models, the explanation pilot uses 20 unique feature groups per domain: ten benign and ten attack cases. Each case is explained with three LIME seed offsets (101, 202 and 303) and 5,000 perturbations per explanation. Each offset is added to the row identity modulo 2^32. The discretized tabular explainer uses a fixed 10,000-row source-training background sampled with seed 42. Full feature rankings, weights, local fit information, original probabilities and row/group identities are saved. Absolute coefficient magnitude defines the primary ranking.

Let S(a) and S(b) be the top-five feature sets from two explainer seeds for the same case. Jaccard@5 is the size of their intersection divided by the size of their union. The pilot averages pairwise overlap across the three seed pairs, then across cases. A value near one means repeatable selected sets; it does not directly measure predictive correctness.

Let c be the original predicted class, p(c|x) its original probability, and x(-S) the vector obtained by replacing selected features with their source-training-background medians. The removal drop is p(c|x) - p(c|x(-S)). The class c is held fixed after masking. Matched-size random sets provide control drops. The reported advantage is the selected-feature drop minus the random-control drop, averaged over k = 1, 2, 3, 4 and 5 removed features, then over the three explainer runs and cases. Each run uses one saved random permutation, so selected and random masks have the same size at every k. Positive advantage means the selected features produce a greater reduction than random features under that intervention.

Retention and removal measure different quantities. A sufficiency gap compares original probability with probability after retaining only selected features; smaller gaps indicate better retention under the baseline. The old study's retained-probability ratio is a different measure and can exceed one. This report avoids interpreting either a raw remaining probability or a discrete mean of drops as an unlabeled universal faithfulness score.

For uncertainty, LIME-seed values are averaged within a case before 5,000 stratified bootstrap repetitions resample ten benign and ten attack groups separately. Percentile intervals are conditional on one trained model and the small selected cohort. They are not across-training-seed intervals, are not corrected for multiple comparisons, and do not establish causal validity. Domain arrows connect different cohorts, not paired flows.

## 3.6 Masking sensitivity extension

After the primary pilot, a disclosed post-hoc extension compares source-background mean versus median replacement and absolute versus signed-descending rankings. The same cases, saved weights and controls produce four variants per model/domain cell: 112 summary cells and 2,240 case variants. Original median/absolute curves are replayed before interpreting alternatives. Signed-descending ranking may still include nonpositive coefficients when fewer than k positive coefficients exist. All variants are retained; none is selected merely because it produces a preferred correlation.

## 3.7 Local language-model protocol

Qwen2.5-0.5B-Instruct, TinyLlama-1.1B-Chat-v1.0 and SmolLM2-1.7B-Instruct are frozen at immutable revisions [8-10]. Each runs locally on CPU in float32 with two PyTorch threads. No fine-tuning or quantization is used. Each source prompt contains four training examples, two per binary class. The 39 signed-log flow values are serialized to three significant digits, which differs from the full detector input precision.

Each model classifies the same 100 balanced unique feature groups per target, using each of the two source contexts: four source/target combinations and 400 cases per model. Label-completion likelihoods for 0 and 1 are normalized to choose a class. These are not calibrated attack probabilities. TinyLlama's shared whitespace-prefix token is handled before comparing suffix logits; regression checks cover that compatibility correction. Tokenizer correctness alone cannot rule out prompt or label-token bias.

Twenty cases per combination also receive an own-decision explanation and a detector-grounded explanation using supplied evidence from frozen XGBoost. Generation is greedy with a maximum of 192 new tokens. Thus each LLM produces 80 own and 80 detector explanations, with prompts and raw outputs retained. A valid response requires the specified JSON structure, a nonempty explanation and one to three exact feature names. Invalid or truncated responses remain in the coverage denominator.

Only valid explanations enter masking. Their named features are compared with three random sets of the same size using the source-background median. Own explanations are checked against the generating LLM; detector explanations against XGBoost. Original LLM scores must replay within 1e-4. These two types of masking score are not interchangeable because they refer to different models. Feature-name membership and masking do not certify every prose claim.

## 3.8 Calibration, imbalance and feature shift

The calibration extension fits a temperature using source-validation negative log likelihood and evaluates Brier score and 15-bin positive-class expected calibration error on test data. Both metrics are lower-is-better. Probabilities are clipped to 1e-7 before scaling. This is a seed-42 extension with no target adaptation.

The imbalance extension compares random forest with balanced class weights, no class weights, and random undersampling of source training rows. Test prevalence is unchanged. Synthetic oversampling is deferred because generating valid mixed protocol/count fields requires an explicit policy. Marginal domain shift is described with empirical KS and Wasserstein distances on 20,000 held-out rows per dataset in the encoded representation. Correlated features and different class mixtures prevent causal attribution from these distances alone.

## 3.9 Reproducibility and validation

The repository stores dataset manifests, immutable LLM revisions, configuration files, completion markers, raw outputs, tables and figures. Long runs save recoverable progress. Completed prediction metrics are independently reconstructed, while historical inference replay is reported separately. Concurrent execution and resumed neural fits make the saved timing unsuitable for a controlled efficiency comparison; some neural times cover only the resumed segment. This report therefore makes no runtime winner claim.

# CHAPTER IV
RESULTS AND DISCUSSION

## 4.1 Completed evidence and reading conventions

All 84 detector configurations and 126 evaluation cells are complete. The 42 model/task/direction groups each contain three seeds. All 14 explanation pilots and all three 400-case LLM runs are complete. Tables below are generated from the saved CSVs rather than manually transcribed. U denotes NF-UNSW-NB15-v2 and I denotes NF-CSE-CIC-IDS2018-v2. Direction is always training source to evaluation target. Scores are proportions, not percentages.

## 4.2 Within-dataset binary and multiclass detection

{{WITHIN_TABLE}}

XGBoost has the largest mean binary macro-F1 on U (0.9750), while random forest has the largest on I (0.9852). The latter is close to XGBoost and DeepMLP; these descriptive means do not establish a statistically significant ranking. DeepMLP reaches 0.9627 on U and 0.9842 on I, showing that neural baselines are competitive in familiar domains. ShallowMLP's U result has substantial seed variation (SD 0.1722), so a single favorable run would be misleading.

{{MULTICLASS_TABLE}}

Native multiclass macro-F1 is substantially lower than binary macro-F1. Random forest has the largest mean in both datasets: 0.5467 on U and 0.7179 on I. These outcomes concern different native label sets and are not directly comparable as equally difficult tasks. Rare classes may be absent from bounded samples, and macro averages must be read together with per-class support. The neural architectures do not provide a uniform improvement over trees under the fixed protocol.

![Figure 4.1. Detector macro-F1 across three training/split seeds; error bars show sample standard deviation.](../results/study/report/figures/10_across_seed_variation.png)

## 4.3 RQ3: detection transfer

{{TRANSFER_TABLE}}

Every detector's cross-dataset mean macro-F1 is below its corresponding within-source mean. U-trained XGBoost falls from 0.9750 to 0.4629 on I; U-trained random forest falls from 0.9701 to 0.4366. In the reverse direction, DeepMLP changes from 0.9842 within I to 0.5164 on U. The U-to-I decision tree has the highest mean transfer macro-F1 in that direction (0.5118), but its SD is 0.1153. The result does not justify selecting that detector for deployment without further validation.

{{TRANSFER_ERRORS}}

Balanced accuracy and false-alarm rate reveal why a single macro-F1 value is insufficient. A model can recover some attack recall while creating many false alarms, or produce few alarms while missing attacks. The domain shift is a combined empirical effect; the experiment does not isolate a single causal feature or collection artifact responsible for it.

The largest marginal KS distance in the 20,000-row descriptive comparison is 0.6690 for retransmitted_out_bytes. Several retransmission and ICMP fields also differ strongly. These observations show distribution differences in the shared representation, not evidence that changing those fields would repair transfer. IDS2018's extreme finite rates are separately documented; numerical overflow prevention does not resolve their physical interpretation.

![Figure 4.2. Marginal encoded-feature shifts between held-out domain samples; descriptive distances do not imply causation.](../results/study/report/figures/09_feature_shift.png)

## 4.4 RQ1 and RQ2: stability versus masking sensitivity

The historical audit addresses the concern that less stable explanations appeared more faithful. For 483 matched cases per original tree model, reconstructing stored aggregate formulas produces only numerically small discrepancies: at most 5.17e-7 for the XGBoost retained-probability ratio and below 7e-16 for the other two models. Replaying original unmasked maximum probabilities yields no errors above 1e-6. These checks support arithmetic consistency; they do not validate unavailable historical masks.

The main interpretation risks were opposite metric directions and different levels of comparison. Historical comp_k values are probabilities remaining after removal, where lower means a larger effect. Historical comprehensiveness_auc is a discrete mean of probability drops, where higher means a larger effect; it is not an integrated area. Historical sufficiency_auc is a retained/original probability ratio, where higher means more retention and values can exceed one. Mixing these under one faithfulness axis can reverse an interpretation without any falsified numbers.

Within each model, historical Spearman correlations between Jaccard@5 and the LIME-minus-random removal effect are positive: 0.2037 for decision tree, 0.2082 for random forest and 0.2584 for XGBoost. This differs from ordering three model averages. Neither comparison establishes a universal law. Duplicate feature groups further limit independent-observation assumptions. Exact original masked predictions cannot be replayed because the historical feature rankings were not retained.

The historical random split also had substantial exact retained-feature overlap: 88.97% of test flows shared a representation with training. That finding motivates the new group-disjoint protocol and prevents treating old headline detection scores as directly comparable to the revised results. The evidence does not support declaring all previous outcomes falsified. It supports narrower corrections to metric interpretation, leakage control and provenance.

![Figure 4.3. Historical matched-case stability and random-adjusted removal effects, shown separately by model.](../results/study/report/figures/02_historical_stability_faithfulness.png)

## 4.5 RQ3: explanation transfer

{{XAI_U}}

For U-trained random forest, within-domain Jaccard@5 is 0.9778 and the removal advantage is 0.3165. On I, Jaccard remains 0.9222 while advantage becomes -0.1338, with a conditional interval below zero. Thus a highly repeatable ranking can be less effective than matched random masks under the chosen baseline. U-trained XGBoost shows another dissociation: stability rises from 0.5165 to 0.5706 while advantage declines from 0.3922 to 0.0268. Its target interval includes zero.

{{XAI_I}}

The reverse direction is also model-dependent. I-trained DeepMLP and ShallowMLP have negative cross-domain primary advantages, while the feature CNN's interval crosses zero. U-trained DeepMLP and FeatureCNN show larger target-domain masking advantages despite weak full-test transfer macro-F1. Explaining the sensitivity of a frozen model is not the same as establishing that its predictions are correct. All intervals refer to 20-case balanced cohorts and one trained model, not the 80,000-row test population.

![Figure 4.4. Conditional bootstrap intervals for random-adjusted LIME masking effects.](../results/study/report/figures/08_rq3_uncertainty.png)

## 4.6 Sensitivity to the masking definition

The four-variant post-hoc check changes measured explanation relevance without changing the underlying classifier. For U-trained random forest evaluated on I, mean advantage is -0.1338 with median/absolute masking and -0.1247 with mean/absolute masking. Signed-descending ranking changes these values to 0.0795 and 0.2215 respectively. Removing a feature that opposes the original class can increase its probability, so absolute and signed ranking have different meanings.

This sensitivity is a reason to retain all variants and state the intervention precisely. It is not a reason to replace the primary result with whichever variant appears favorable. Mean and median baselines can both create implausible combinations of flow features. The measured quantity is conditional perturbation sensitivity; causal or semantic explanation correctness remains unmeasured.

![Figure 4.5. Cross-domain masking sensitivity for all four baseline/ranking combinations.](../results/study/report/figures/13_masking_sensitivity.png)

## 4.7 RQ4: matched LLM classification

{{LLM_TABLE}}

Qwen and SmolLM2 predict Benign for every evaluated case, while TinyLlama predicts Attack for every case. Each source/target cell is balanced, so all three obtain accuracy 0.5, balanced accuracy 0.5 and macro-F1 0.3333. A zero false-alarm rate for the benign-only models is accompanied by zero attack recall; it is not successful detection. TinyLlama attains attack recall one by flagging every benign case as well.

These outcomes are negative results for the frozen small-model, four-example, rounded-input and constrained-label protocol. They do not establish that all LLM intrusion detection fails. Label verbalization, example order, serialization and prompt format remain plausible sensitivities requiring a separately specified follow-up. The completed test cohort must not become a hidden development set for improving the original headline result.

{{MATCHED_TABLE}}

The matched detector results use exactly the balanced 100-case cohorts. They must not be substituted for full-test metrics. For example, a detector can look much stronger on a 50/50 sample than on a domain's original prevalence while making the same kinds of conditional errors. This is an evaluation-cohort distinction, not evidence that the transfer experiment changed its saved predictions.

## 4.8 LLM explanation validity and conditional masking

{{COVERAGE_TABLE}}

Across all four directions, Qwen produces 26 valid own-decision explanations out of 80 and 58 valid detector explanations out of 80. SmolLM2 produces no valid own explanations and five valid detector explanations. TinyLlama produces no valid explanations under the required schema. Failures include outputs that do not meet the required format or feature constraints; the raw responses remain available. No valid masking subset is silently expanded to represent all outputs.

{{MASK_TABLE}}

Qwen's valid own explanations are limited to the two I-source cells, with mean advantages -0.0114 and -0.0038. Detector-grounded conditional advantages are positive in its four cells, but are conditional on validity and refer to XGBoost rather than Qwen's collapsed classifier. SmolLM2's 0.4036 detector advantage in I-to-U is based on only two valid explanations. Such a small selected subset cannot establish overall explanation quality. A missing conditional score is not a measured zero.

![Figure 4.6. Generated-explanation checks across the four source/target combinations per LLM.](../results/study/report/figures/12_llm_explanation_checks.png)

## 4.9 Calibration and imbalance extensions

Source-only calibration produces metric-dependent changes rather than a universal repair. For U-trained random forest on I, Brier score improves from 0.227757 to 0.209142 while ECE15 worsens from 0.324661 to 0.345976. These measures summarize different aspects of probability error. The outcome warns against selecting one calibration score after observing the target results.

![Figure 4.7. Change in Brier score after source-validation temperature scaling; negative means improvement.](../results/study/report/figures/04_calibration.png)

For the U-trained random forest, removing class weights raises within-domain macro-F1 from 0.9645 to 0.9710, but lowers I-domain macro-F1 from 0.4373 to 0.3064 and raises FAR from 0.1412 to 0.5044. Training-only undersampling yields transfer macro-F1 0.3355 and FAR 0.5348. Improvements within a source domain therefore need not improve transfer. These are seed-42 ablations, not three-seed conclusions.

![Figure 4.8. Random-forest class-imbalance ablation with unchanged validation and test prevalence.](../results/study/report/figures/05_imbalance.png)

## 4.10 Threats to validity

Internal validity is strengthened by source-only preprocessing, consistent feature-group splits, saved predictions and matched controls. It is limited by the chosen representation, bounded samples and finite model configurations. Grouping prevents exact encoded-input overlap across partitions but does not remove every possible dependence or collection artifact. The cleaned releases and extreme-value handling differ from an assumption of pristine original packet captures.

Construct validity is limited because Jaccard measures repeatability and masking measures response to an artificial intervention. Neither is a direct measure of causal explanation correctness, semantic truth or analyst usefulness. Bootstrap intervals are conditional and exploratory. LLM validity checks cannot certify full prose accuracy; excluding invalid responses creates a selected subset whose composition can differ from the original balanced cohort.

External validity is limited to two datasets, three small LLMs, fixed architectures and a CPU-feasible sample budget. The feature CNN provides no temporal evidence. The neural results do not imply an exhaustive comparison of deep learning. Repeated seeds improve transparency but do not establish deployment reliability. Operational timing was affected by concurrent work and interrupted runs and is not used as a controlled speed comparison.

# CHAPTER V
CONCLUSION AND FUTURE WORKS

## 5.1 Answers to the research questions

RQ1 finds that explanation repeatability varies by detector and domain. High Jaccard overlap can persist across a domain shift, but that persistence is not sufficient evidence that an explanation identifies influential features. RQ2 finds that random controls, metric direction and perturbation definitions materially affect interpretation. The historical audit identifies reporting and provenance limitations without evidence that inverse relationships alone prove falsification.

RQ3 finds a consistent decline in frozen cross-dataset detection macro-F1 across all seven detector families. Explanation transfer is more varied: some primary masking advantages decline, some become negative, and some increase even when detection remains weak. Detection correctness and explanation sensitivity therefore require separate evaluation. The RF transfer example demonstrates why a stable explanation cannot be accepted as faithful solely on the basis of repeatability.

RQ4 finds constant-class predictions from all three small local LLMs under the tested protocol, alongside low valid explanation coverage. Detector-grounded explanation subsets sometimes show positive masking advantages, but these conditional results do not repair failed classification or establish general explanation reliability. Invalid outputs and negative results are central findings rather than excluded cases.

## 5.2 Practical implications

A responsible assessment of an explainable detector should state the training source, target domain, sampling scheme and explanation intervention. It should report more than one detection metric, include random explanation controls, and retain the outputs needed to reproduce numerical claims. A workflow that preserves unfavorable results is more useful for future improvement than one that forces stability and faithfulness to agree.

For this study, the appropriate deliverable is a reproducible experimental comparison and a bounded set of conclusions. None of the evaluated configurations is certified for autonomous operational deployment. The evidence supports further development and validation, including task-specific thresholds and human review, rather than an unqualified claim of reliable attack detection.

## 5.3 Future work

The first priority is a separately preregistered LLM sensitivity study. It should vary label verbalization and order, prompt structure, feature serialization and example selection using independent development data, then evaluate a locked protocol on new held-out cases. Constant-class baselines and invalid-output coverage should remain explicit. Larger models, retrieval and fine-tuning can be studied as separate configurations with their own compute and provenance records.

The second priority is temporal and external validation. Additional releases and a verified chronological split would test robustness to time and collection changes. Domain adaptation should be separated from frozen transfer and should state exactly which target data are used. Native attack-taxonomy harmonization needs an explicit mapping and uncertainty treatment rather than assuming labels with similar names are identical.

The third priority is explanation realism and usefulness. Conditional or domain-constrained perturbations could reduce implausible flow combinations. Comparisons of signed evidence, alternative explainers and larger multi-seed cohorts should preserve all prespecified variants. An analyst study would need recruited participants, an appropriate protocol and task outcomes such as triage accuracy and time; generated prose alone cannot substitute for that evidence.

Finally, data-quality work should investigate extreme rate values and rare-category coverage. Controlled efficiency tests would need isolated hardware use, complete end-to-end timing and consistent recovery accounting. These are future experiments. The present report distinguishes them from completed calibration, imbalance and masking extensions.

# References

[1] M. Sarhan, S. Layeghy and M. Portmann. Towards a Standard Feature Set for Network Intrusion Detection System Datasets. 2021. https://arxiv.org/abs/2101.11315

[2] M. T. Ribeiro, S. Singh and C. Guestrin. Why Should I Trust You? Explaining the Predictions of Any Classifier. KDD, 2016. https://arxiv.org/abs/1602.04938

[3] S. M. Lundberg and S.-I. Lee. A Unified Approach to Interpreting Model Predictions. NeurIPS, 2017. https://arxiv.org/abs/1705.07874

[4] C.-K. Yeh, C.-Y. Hsieh, A. Suggala, D. I. Inouye and P. Ravikumar. On the (In)fidelity and Sensitivity of Explanations. NeurIPS, 2019. https://arxiv.org/abs/1901.09392

[5] J. DeYoung et al. ERASER: A Benchmark to Evaluate Rationalized NLP Models. ACL, pp. 4443-4458, 2020. https://doi.org/10.18653/v1/2020.acl-main.408

[6] P. R. B. Houssel, P. Singh, S. Layeghy and M. Portmann. Towards Explainable Network Intrusion Detection using Large Language Models. 2024. https://arxiv.org/abs/2408.04342

[7] P. R. B. Houssel, S. Layeghy, P. Singh and M. Portmann. eX-NIDS: A Framework for Explainable Network Intrusion Detection Leveraging Large Language Models. 2025. https://arxiv.org/abs/2507.16241

[8] Qwen. Qwen2.5-0.5B-Instruct model card. https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct

[9] TinyLlama. TinyLlama-1.1B-Chat-v1.0 model card. https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0

[10] Hugging Face. SmolLM2-1.7B-Instruct model card. https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B-Instruct

Bibliographic records checked on 21 September 2026. Experimental file hashes and immutable model revisions are retained in the repository.

# Appendix A: Reproducibility and feature inventory

The report is built with study/build_report.py from this narrative template and the completed CSV evidence. render_thesis_pdf.py applies the supplied IIUC reference dimensions, Times New Roman typography, front matter, five chapters and Roman/Arabic pagination. The reference is a layout and identity source; its old numerical conclusions do not override the new measured results. Declaration signatures and supervisor certification require the appropriate people's review.

{{PROVENANCE_TABLE}}

{{FEATURE_TABLE}}

To reproduce the report from completed outputs, run python -m study.build_report after python -m study.report_figures, followed by python render_thesis_pdf.py and python verify_thesis_pdf.py in an environment containing ReportLab, Pillow and pdfplumber with the Windows Times New Roman fonts available. The report-input manifest records SHA-256 hashes of all data inputs and figures. Regenerating experiments requires the study environment, raw releases and pinned model downloads described in the repository.

# Appendix B: Detailed explanation-transfer results

The tables below include within-domain and cross-domain results omitted from the compact comparison in Chapter IV. Every row has 20 balanced unique groups and three LIME seeds under a fixed training-seed-42 detector. Intervals are class-stratified percentile bootstrap intervals over case means, not deployment guarantees.

{{XAI_FULL}}

# Appendix C: Revision record and evidence boundaries

This revision replaces the old numerical narrative with the completed expanded study, adds neural and local LLM comparisons, completes RQ3, separates historical reconstruction from new measurements, and revises the research-gap and future-work discussion. Existing historical source templates and result files are preserved. Exact old masks remain unrecoverable from the available historical CSVs because their rankings were not stored. No conclusion of fabricated data is drawn from an inverse stability relationship.

The report intentionally reports the LLM constant-class outcomes and low valid-output coverage. It identifies source-only calibration and training-only imbalance studies as completed, while temporal deployment, analyst validation, larger-model evaluation and causal explanation claims remain future work. Author declarations and supervisor approval are left for human completion. Scientific completion of the recorded experiments does not imply institutional approval of the thesis.
