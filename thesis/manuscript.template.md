# Evaluating the Reliability of Explainable AI in Ensemble-Based Intrusion Detection Systems

Mehedi Hasan (C213061) and Sazzadul Islam (C213066R)

Department of Computer Science and Engineering

International Islamic University Chittagong

Supervisor: Mr. Md. Mahiuddin, Associate Professor

September 2026

# Abstract

Feature explanations can appear persuasive without being repeatable or accurately identifying the inputs on which a classifier depends. This thesis evaluates explanation reliability on NF-UNSW-NB15-v2 using LIME repeatability, frozen-model masking tests, and agreement between importance methods. The local dataset contains 1,986,745 flows, ten classes and 39 retained predictive features. Six individual classifiers provide the repeatability comparison; DecisionTree, RandomForest, XGBoost and their explicit equal-weight probability ensemble provide the revised evaluation of faithfulness and agreement. Repeated LIME seeds and a random-feature control separate explanation performance from variation introduced by the explanation procedure itself.

Across the six original classifiers, mean top-five Jaccard similarity ranges from 0.3373 for DecisionTree to 0.8684 for RandomForest. For the combined three-tree predictor it is {{ensemble_jaccard}}. Under mean masking, LIME's paired comprehensiveness advantage over random ranges from {{mean_effect_range}} probability points across the four evaluated predictors. Median masking changes these estimates, demonstrating why the replacement distribution must be reported. These results concern sensitivity of a frozen model, rather than causal identification of attack-generating features.

An audit found that 353,529 of 397,349 original test flows, or 88.97 percent, share an identical retained-feature vector with training. A separate validation therefore holds out complete feature-vector groups. Across three seeds, XGBoost's mean macro-F1 is {{xgb_random}} under the random flow split and {{xgb_grouped}} under the group-disjoint split. The results support measuring detection generalization and explanation reliability separately. They do not establish a universal stability-faithfulness tradeoff, cross-network reliability, or improved analyst decision-making.

Keywords: intrusion detection, explainable artificial intelligence, LIME, SHAP, faithfulness, repeatability, data leakage

# 1 Introduction

## 1.1 Problem and motivation

A network intrusion detector maps a traffic description to a benign or attack label. An analyst examining an alert may also need to understand which observed attributes influenced that decision. A feature-importance display offers one form of assistance, but it introduces another object that requires evaluation: the explanation. If a repeated explanation selects a different set of important features, or removing its selected features has no greater effect than removing random features, a clear visualization alone is insufficient evidence of reliability.

The operational distinction is straightforward. Detection performance concerns whether the model assigns correct labels to held-out traffic. Explanation repeatability concerns whether the explanation procedure gives similar results when the model and input are unchanged. Faithfulness concerns the relationship between an explanation and the behavior of the frozen predictor. Agreement concerns whether methods produce similar rankings under a stated comparison design. A method can perform well on one of these dimensions and poorly on another. The experiment therefore evaluates them separately rather than combining them into a single trust score.

The emphasis is measurement within a reproducible benchmark setting. The project does not implement a production security monitoring service, automatically block traffic, or measure an analyst's response to explanations. Such deployment claims would require different evidence, including realistic traffic arrival rates, prospective validation and a human study. The present work supplies a reproducible evaluation of models and explanations that could precede those activities.

## 1.2 Research questions

RQ1 asks whether LIME returns similar feature rankings across repeated runs on an identical input and frozen predictor. RQ2 asks whether the features ranked highly by LIME and, where evaluated, TreeSHAP produce larger prediction changes than random features under mean and median replacement. RQ4 asks how global rankings agree when methods use the same explained instances and original predicted classes. The original project identifier RQ3 is reserved for cross-network evaluation and remains outside the completed experiment scope; retaining that identifier preserves traceability to the project code.

A supplementary validation question asks how detection performance changes when identical retained-feature vectors are kept within one split. This question arose from a data audit during the final evaluation. It is an exploratory sensitivity analysis, not a preregistered hypothesis. Its inclusion is necessary because a model that sees the same predictive representation during training and testing has not demonstrated performance on novel representations.

## 1.3 Contributions and scope

The first contribution is a repeatability comparison across distinct model families under a fixed dataset and explanation configuration. The second is a paired masking evaluation with repeated LIME seeds, explicit random controls, and a second replacement baseline. The third is a comparison of matched-target global rankings that distinguishes explanation attribution from permutation sensitivity and data-only feature ranking. The fourth is an audit and group-disjoint detection evaluation that exposes a material limitation of the original random split.

The combined ensemble is explicitly the mean of DecisionTree, RandomForest and XGBoost probability vectors. GaussianNB, logistic regression and MLP are retained as architectural controls for RQ1. They are not silently included in the revised voting model. The historical six-model voting score is not used as the performance of the three-model predictor. No universal mechanism is inferred from the small set of model architectures.

## 1.4 Thesis organization

Chapter 2 relates the design to explanation methods and prior explainable intrusion-detection studies. Chapter 3 defines the data, models and protocols. Chapter 4 presents detection and split-audit results. Chapters 5 through 7 present repeatability, faithfulness and agreement. Chapter 8 discusses their joint interpretation, Chapter 9 states validity limits, and Chapter 10 gives conclusions and future work. The appendices record reproducibility instructions, metric definitions and the evidence inventory.

# 2 Background and Related Work

## 2.1 Local explanations and additive attribution

Ribeiro, Singh and Guestrin introduced LIME as a method that fits an interpretable surrogate near a prediction [1]. Its model-agnostic interface makes it suitable for comparing heterogeneous classifiers through predicted probabilities. In this project, the sampling and local fitting procedure is precisely the source of randomness examined by RQ1. LIME's availability for a model does not eliminate the need to test its behavior on that model.

Lundberg and Lee introduced SHAP as an additive feature-attribution framework grounded in desirable explanation properties [2]. Here, the tree models use TreeSHAP through the installed SHAP package. An attribution is defined with respect to a model output and assumptions about unavailable features. The comparison therefore records that native SHAP output units can differ across model types. Attribution magnitudes should not be pooled across those output scales as if they measured the same numerical quantity.

## 2.2 Evaluation of explanation quality

Yeh and colleagues study infidelity and sensitivity as separate explanation properties [3]. Their analysis shows why minimizing sensitivity alone can be inadequate: an explanation can be stable without being informative. The present experiment follows that conceptual separation but does not implement their exact infidelity estimator. It instead evaluates rank repeatability and prediction changes under a specified masking rule.

DeYoung and colleagues' ERASER benchmark distinguishes rationale plausibility and faithfulness and evaluates the effects of rationale removal and retention [4]. The present work adapts the removal/retention idea to tabular traffic features. Its retained-probability ratio is a locally defined statistic, not an assertion that it reproduces ERASER's sufficiency implementation. Neither feature masking nor comparison with random features proves a causal account of a network attack.

## 2.3 Explainable intrusion detection

Patil and colleagues combine DecisionTree, RandomForest and SVM with a voting classifier and LIME on CICIDS-2017 [5]. Their reported 96.25 percent accuracy belongs to their dataset and processing pipeline, so it is not directly comparable with macro-F1 in this thesis. Their study motivates examining explanations around ensemble-based intrusion detection. This work emphasizes repeated explanations and paired perturbation effects instead of treating an explanation display as sufficient validation.

Kalutharage and colleagues use autoencoder anomalies, KernelSHAP feature influence and feature thresholds to identify DDoS attack flows on USB-IDS [6]. Their aim includes mapping anomalous behavior to attack-related features. This thesis addresses a different question: how consistently and effectively explanation methods characterize an already fitted multiclass predictor. It does not reproduce their attack-certainty mechanism or claim to outperform it.

Hermosilla and colleagues evaluate SHAP and LIME for XGBoost and TabNet on UNSW-NB15, including differences in feature importance and local consistency [7]. This is relevant evidence that model-specific explanation consistency has already been investigated. The present study therefore does not claim that explanation reliability has never been evaluated in intrusion detection. Its contribution is the particular combination of repeated-seed rank metrics, two masking baselines, a random control, an explicit voting predictor, and a split-overlap audit.

## 2.4 Benchmark representation and comparability

Sarhan, Layeghy and Portmann propose standard NetFlow-based feature sets to improve comparability across intrusion-detection datasets [8]. A common feature schema helps align datasets but does not guarantee independence between examples, comparable attack labels, or transfer across infrastructures. Removing identifying columns can also collapse previously distinct records into identical predictive representations. The experimental audit therefore checks the retained feature space rather than relying on a dataset's upstream deduplication description.

## 2.5 Position of the present study

The reviewed studies supply methods and motivation, not interchangeable benchmarks. Differences in datasets, split procedures, label definitions, feature engineering and class balance prevent a simple ranking by reported accuracy. The experimental comparisons in this thesis are internal: the same data representation and split within each protocol, explicitly named predictors, and fixed explanation settings. The literature review is focused rather than systematic, and no exhaustive novelty claim is made.

# 3 Data and Methodology

## 3.1 Dataset and preprocessing

The local NF-UNSW-NB15-v2 checkpoint contains 1,986,745 records. There are 1,911,666 benign records and 75,079 attack records, making the attack fraction approximately 3.78 percent. The ten-class target comprises Benign, Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Shellcode and Worms. The local counts are used throughout because they differ from counts often associated with other releases of the dataset.

Column names are normalized and identifying fields are removed using the configured exclusion list. The available release already omits IP addresses and timestamps; source and destination ports are additionally excluded. Both binary and multiclass target columns are removed from the predictive matrix, leaving 39 features. Infinite and missing numeric values are replaced with zero by the existing cleaning stage. This replacement is a fixed rule, not a statistic fitted using test data. Nevertheless, zero can conflate an absent measurement with a genuine zero and is a validity limitation.

The analysis uses the cleaned checkpoint and saved split metadata. A checksum identifies each revised run's dataset, model and split inputs. No statement that upstream deduplication makes the retained matrix unique is assumed. The overlap audit hashes all 39 retained values for each row and compares those hashes across the split. Group hashes do not incorporate target labels.

{{class_table}}

## 3.2 Detection splits and label encoding

The original detection protocol uses an 80/20 random stratified flow split. With seed 42, this produces 1,589,396 training and 397,349 test records. LabelEncoder provides a common integer class order for all classifiers. Models fitted through a scaling pipeline learn their scaling parameters from training data only. The same saved test indices are used when sampling cases for explanation experiments.

Two additional random-split evaluations use seeds 7 and 1337. Each seed controls both the split and stochastic estimator behavior. These runs therefore measure their combined variation; they do not isolate training randomness while holding the test set fixed. Mean and sample standard deviation across the three seeds are descriptive. Three seeds do not support a precise estimate of performance over all possible training sets.

The supplementary group-disjoint protocol uses GroupShuffleSplit with 20 percent of feature groups held out, for the same three seeds. Every instance with a given retained-feature hash stays on one side of a split. Because groups differ in size, the test fraction of flows need not be exactly 20 percent, and this splitter does not promise exact class stratification. Each run verifies that every class is represented in both partitions and that no feature group overlaps. This evaluation addresses representation overlap; it is not a temporal, host-disjoint or cross-network evaluation.

## 3.3 Classifiers and explicit voting

DecisionTree uses maximum depth 30, minimum leaf size 5 and balanced class weights. RandomForest uses 100 trees with those depth, leaf and class-weight settings. XGBoost uses 200 boosting rounds, depth 8, learning rate 0.1, row and column subsampling of 0.8, and the histogram tree method. It does not receive balanced class weights in this implementation. Those differences are reported because they can affect both class performance and explanation behavior.

The RQ1 controls are scaled logistic regression, GaussianNB and a scaled MLP with hidden layers of 64 and 32 units. Logistic regression reached its historical iteration limit; that checkpoint remains a control rather than a tuned competitive detector. No claim that a linear score model must have a perfectly stable LIME explanation is made. Its predicted probabilities and LIME's discretized local representation are different objects.

The combined predictor uses p_vote(c|x) = [p_DT(c|x) + p_RF(c|x) + p_XGB(c|x)] / 3. Member class order is checked before averaging. The stored ensemble uses the existing fitted seed-42 members without refitting. Prediction and serialization checks verify equality with direct probability averaging. This construction ensures that the explanation targets the combined predictor itself, not a selected member being described as the ensemble.

## 3.4 Detection metrics

Macro-F1 gives each class equal weight in the final average and is the leading detection metric. Macro-average precision, implemented through one-versus-rest average-precision scores, is also reported. The output column historically called PR-AUC contains average precision rather than a trapezoidal numerical integral of the precision-recall curve. False alarm rate is the proportion of benign examples assigned a non-benign label. Per-class precision, recall, F1 and support are retained in the output files.

Accuracy is secondary because approximately 96.22 percent of the dataset is benign. A majority-class rule would appear accurate while failing to detect every attack family. At the other extreme, improving rare-class recall by issuing many false alerts can also be unsuitable in practice. Reporting macro-F1 and false alarm rate together makes these different consequences visible.

## 3.5 Sampling for explanation evaluation

RQ1 requests 1,000 instances and samples up to 100 from each true class. Worms has only 33 cases in the seed-42 test set, producing 933 instances. RQ2 requests 500 and samples up to 50 per class, producing 483 instances. RQ4 uses 30 cases per class, producing 300 instances. This roughly class-balanced sampling is intended to expose minority-class behavior; the resulting averages are not estimates weighted by deployment traffic prevalence.

LIME estimates its feature distributions from 20,000 training rows sampled with seed 42. Continuous features are discretized using the installed LIME configuration. All 39 feature weights are requested, and rankings are formed by descending absolute weight. Each explanation uses 5,000 perturbation samples. The target is the model's original predicted class, even when the prediction is wrong. Correctness of the alert and repeatability of its explanation remain separate questions.

## 3.6 RQ1 repeatability protocol

For each input, the predictor is frozen and LIME is evaluated with seeds 101, 202, 303, 404, 505, 606, 707, 808, 909 and 1010. Mean pairwise Jaccard similarity is computed for the top five and top ten feature sets. Kendall correlation is computed after converting each full ranking to feature positions. The 45 pairs within one input are summarized before averaging across inputs; they are not treated as 45 independent observations.

The six original models' instance-level RQ1 results are retained because their repeatability protocol did not change. Their source CSVs are explicitly identified and hashed in the final evidence inventory. The combined ensemble receives a new full-size run. This distinction preserves the provenance of historical observations rather than presenting them as freshly rerun experiments. Confidence intervals in the final analysis resample groups of identical feature vectors to reduce false precision from repeated representations.

## 3.7 RQ2 masking protocol

Let c be the original predicted class and p0 = p(c|x). For each k from 1 through 10, the removal experiment replaces the top-k ranked features with a training-derived baseline. Comprehensiveness is the arithmetic mean of p0 minus the masked probability across these ten values of k. A larger value indicates a larger average probability drop under that intervention. The historical name comprehensiveness_auc is retained in CSV files, but the estimator is an equally weighted mean across k, not an integral over a continuous axis.

The retention experiment replaces every feature except the top-k set. Its reported statistic is the mean retained probability divided by p0. This ratio averages k=1 through 10 and can exceed one if masking increases the original-class probability. It is not a bounded accuracy measure and it is not simply the result at k=10. Both removal and retention act on a frozen predictor; no model is trained on a selected subset.

Mean and median replacement values are computed from training rows. LIME runs use seeds 101, 202 and 303, and each instance-seed pair receives a random permutation of all feature indices as a control. TreeSHAP is evaluated for the three tree models. For the combined predictor, RQ2 evaluates LIME against random only; no member SHAP explanation is presented as an explanation of the voting model. The exclusion is recorded in the run metadata and in every final comparison.

Repeated observations are averaged within each instance and method before summary statistics. The final comparison uses the paired explainer-minus-random difference, a 95 percent bootstrap interval over identical-feature groups, and a one-sided Wilcoxon test on group-average differences. The confidence interval retains the instance-weighted effect, whereas the group-level test gives each unique representation one paired observation. P-values are adjusted across the complete family of model, masking and explainer comparisons. These procedures quantify conditional benchmark uncertainty, not uncertainty from changing the trained model or deploying on another network.

## 3.8 RQ4 agreement protocol

LIME and TreeSHAP importance are aggregated over the same 300 selected instances and their original predicted classes. Importance is the mean absolute attribution per feature. Probability permutation sensitivity measures the mean absolute change in the original-class probability when one feature column is shuffled across those same rows. The original class is kept fixed after perturbation. Ten shuffles per feature quantify the variation of this sensitivity estimate.

This probability permutation statistic differs from conventional permutation importance based on a drop in a performance score. It was chosen to make the target and evaluation population closer to those used by LIME. It does not make local attribution and global sensitivity mathematically identical, because their perturbation distributions and objectives still differ. For the ensemble, the comparison includes LIME, probability permutation sensitivity and TOPSIS, without a SHAP column.

TOPSIS is a data-only comparator formed from variance, histogram entropy and inverted mean absolute correlation on a training sample. Its criteria are design choices and variance depends on feature units. It is not an oracle for model behavior. Pairwise Spearman correlation is computed over the full ranking and Jaccard overlap over the top-five and top-ten sets. Low agreement is interpreted descriptively, not as proof that one method is false. Near-zero or tied importance values can make full-ranking statistics sensitive to arbitrary ordering.

## 3.9 Computation and reproducibility

The environment uses CPython 3.11.16 and the project's preserved scientific package versions, including NumPy 1.26.4, scikit-learn 1.4.2, SHAP 0.45.1 and XGBoost 2.0.3. A dependency consistency check and protocol unit tests pass. Masked inputs are evaluated as a batch, which preserves their values while reducing prediction-call overhead. The equivalence is tested against individual predictions.

Each revised run has a separate output directory with parameters, package versions, sampled indices, input checksums, source checksums and completion status. A resumable suite records commands, logs and the exact result directories selected for the final tables. Figures use that explicit selection rather than whichever file was most recently written. Historical seed-42 baseline tables and model checkpoints are preserved.

The repeatability runner saves a checkpoint every ten instances, including the LIME random-generator state. Recovery requires matching inputs, scientific source files, package versions and parameters. A serialization test confirms that the next explanation is identical after restoring a saved state. Checkpoint recovery therefore preserves the intended random sequence rather than restarting it at the beginning of each resumed segment.

# 4 Detection Results and Split Audit

## 4.1 Original split performance

The reconstructed three-member ensemble obtains macro-F1 0.6687 on the original seed-42 split. XGBoost alone obtains 0.6731, so the combined predictor does not improve this metric on that split. The historical six-member ensemble obtained 0.6743, but it is a different model composition. Reporting the member list is therefore necessary to interpret any ensemble claim.

{{split_table}}

Figure 1 reports mean macro-F1 and sample standard deviation over the three seeds. The comparison is descriptive because split membership differs between seeds and protocols. Results should not be read as a controlled estimate of the effect of deleting duplicates while holding every other factor fixed.

![Figure 1 Detection performance under random flow and feature group splits](../results/final/figures/01_detection_splits.png)

## 4.2 Identical representation overlap

The audit identifies 236,999 unique retained-feature hashes among almost two million flows. Some distinct original records therefore become identical after preprocessing and identifier removal. In the seed-42 random split, 353,529 test cases share a retained-feature vector with training, leaving 43,820 test cases without such overlap. This is representation overlap, not a claim that test target labels were deliberately used for training.

The distinction matters because a random split estimates performance on another sample from a highly repetitive representation distribution. It offers limited evidence about predictions on unseen representations. The problem is not corrected by merely asserting that the original source release was deduplicated: uniqueness must be assessed in the feature space actually supplied to the model. The supplementary audit also finds 1,555 feature groups associated with more than one class label, indicating that the retained representation does not uniquely determine the target throughout the dataset.

## 4.3 Group-disjoint validation

The grouped protocol verifies zero overlap of feature groups for every seed. Across seeds, the resulting macro-F1 values are summarized in Table 2 and Figure 1. For XGBoost, the mean changes from {{xgb_random}} on random flow splits to {{xgb_grouped}} on feature-group splits. For the voting predictor, the corresponding means are {{ensemble_random}} and {{ensemble_grouped}}. These differences materially constrain generalization claims.

Keeping exact feature vectors together still allows nearby vectors and traffic from the same source environment on both sides. It also changes which traffic patterns are represented in training and testing. The grouped result is therefore a stronger representation-disjoint check, not a definitive estimate of live-network performance. A temporal or independent-network evaluation would answer a further question that the available split metadata cannot resolve.

# 5 RQ1 Explanation Repeatability

## 5.1 Overall results

{{stability_table}}

DecisionTree's mean top-five Jaccard similarity is 0.3373 and RandomForest's is 0.8684 in the retained original results. The difference is large despite both being tree-based classifiers. The combined predictor's new result is {{ensemble_jaccard}}. Figure 2 displays these estimates with feature-group bootstrap intervals. Intervals describe variability over the selected benchmark representations, conditional on the fitted model and explanation configuration.

![Figure 2 LIME repeatability with feature group bootstrap intervals](../results/final/figures/02_stability.png)

## 5.2 Set overlap and rank agreement

Jaccard overlap answers whether the selected feature sets are similar; Kendall correlation answers whether their full ordering is similar. These metrics need not rank models identically. A method can preserve the top set but reorder its elements, or preserve much of a long ordering while changing a few features at the selection boundary. Reporting one scalar would obscure that distinction.

The result is also conditional on k. Selecting ten features includes lower-weight features that may vary more across perturbation samples. Conversely, expanding a set can sometimes stabilize its overlap by including competing features together. Neither pattern establishes a universal relationship between set size and stability. The two observed set sizes should be reported directly rather than extrapolated to all explanation lengths.

## 5.3 Model properties do not identify a mechanism

These observations do not establish that model accuracy, tree structure, probability granularity or an informal smoothness ordering causes explanation repeatability. The model comparison contains only a few architectures, with different fitting objectives, regularization and probability behavior. Models can also predict different classes for the same flow, so a cross-model comparison can change the class being explained. Logistic regression's outcome does not refute every smoothness hypothesis, and a nonsignificant correlation across six models is not proof that a mechanism is absent.

The practical conclusion is narrower: explanation repeatability cannot safely be inferred from the broad model family alone in this experiment. It should be measured for the fitted predictor and the selected explanation settings. The result also does not show that repeating an explanation until it looks plausible improves its validity; selectively choosing a favorable run would conceal the variation being measured.

# 6 RQ2 Faithfulness and Masking Sensitivity

## 6.1 Paired effects relative to random

{{faithfulness_table}}

The table reports the mean paired comprehensiveness advantage over random, with feature-group bootstrap intervals. Averaging repeated seeds within each input avoids treating multiple explanations of the same input as independent evidence. The random control matters because perturbing arbitrary features can already produce substantial probability changes. An explainer's raw comprehensiveness should therefore be interpreted relative to this control.

![Figure 3 Paired comprehensiveness effects for both masking baselines](../results/final/figures/03_faithfulness.png)

{{faithfulness_interpretation}}

TreeSHAP results are restricted to the three individual tree models. LIME is evaluated on the actual three-model voting function. The absence of a SHAP estimate for the combined model is explicit; averaging native member attributions with different output scales would not provide a justified probability attribution for that ensemble.

## 6.2 Sensitivity to replacement values

{{masking_table}}

![Figure 4 Sensitivity of LIME comprehensiveness to masking baseline](../results/final/figures/05_masking.png)

The median-minus-mean differences compare the same sampled instances and explanation seed configurations. They show how much the reported probability-drop statistic depends on replacement values. A change need not imply an implementation error: mean and median describe different interventions. A feature can be important relative to one reference point while a different replacement produces a smaller or even reversed effect.

Neither reference preserves all physical relationships between packet counts, bytes, timing, flags and protocol fields. Features are masked independently, so some evaluated combinations may be impossible traffic records. Median replacement tests sensitivity to one design choice but does not solve the off-manifold problem. Conditional replacement or domain-valid counterfactuals would provide additional evidence.

## 6.3 Retention and explanation seed variation

The retention statistic is included in the full output tables. It is interpreted as a conditional probability ratio, not as a guarantee that selected features are sufficient in a causal or operational sense. Values above one mean the masked input raises the original-class probability relative to the unmasked input. A highly variable ratio is possible when the original predicted-class probability is low.

For each model and baseline, the output also records the mean, standard deviation and range of LIME comprehensiveness over its three explanation seeds for each instance. Three seeds expose some stochastic variation but do not characterize the entire distribution of explanations. A larger seed set would improve estimation of the seed component of uncertainty. The final bootstrap intervals primarily describe the sampling of feature groups after seed averaging.

## 6.4 Matched stability and faithfulness

{{association_table}}

The matched-instance association joins RQ1 repeatability and RQ2 comprehensiveness by original row index. This is preferable to inferring a relationship from three model-level averages. It remains descriptive: repeated feature representations, class mixture and different probability surfaces can influence the correlation. The study does not claim a universal inverse relation or an unavoidable tradeoff between stability and faithfulness.

# 7 RQ4 Agreement Between Importance Methods

## 7.1 Matched target comparison

{{agreement_table}}

![Figure 5 Agreement over full feature rankings](../results/final/figures/04_agreement.png)

The final comparison uses identical selected instances and the original predicted class for every model-based method. This removes two confounds from the historical implementation, which aggregated SHAP across classes and evaluated performance-based permutation importance on a separate population. The revised results therefore supersede the historical RQ4 interpretation; the two protocols should not be combined into a single table.

The methods still answer related rather than identical questions. LIME fits a local surrogate, TreeSHAP attributes a native model output under its feature-dependence assumptions, and probability permutation sensitivity measures response to a shuffled feature column. Differences in ranking remain possible even when each method is computed correctly. Agreement offers a descriptive consistency check, not an external correctness label.

## 7.2 Head features and low-importance tails

The run folders preserve top-five and top-ten Jaccard matrices alongside full-rank Spearman correlations and feature-importance values. A strong full-rank correlation can coexist with limited agreement at the head, and weak full-rank correlation can be driven by the ordering of near-zero features. The probability-permutation output additionally records variability over ten shuffles. That standard deviation is a heuristic variability measure, not a formal confidence interval proving which features are irrelevant.

TOPSIS is interpreted separately because it uses data distributions without the fitted predictor. Similarity to TOPSIS can motivate further inspection but cannot establish that an explanation is merely describing the dataset. Feature variance depends on the measurement scale and entropy depends on histogram binning, so this comparator is sensitive to its own choices. It is not used to select a winning explainer.

# 8 Discussion

## 8.1 Reliability requires separate evidence

The experiments distinguish an accurate prediction, a repeatable explanation and a large masking effect. A model can be competitive on a random split while that split contains extensive feature overlap. A repeatable explanation can consistently select features whose removal is not especially consequential relative to a baseline. A large removal effect can depend on a replacement value that produces unusual inputs. None of these measurements alone establishes that an analyst should trust a particular alert.

The combined predictor illustrates why implementation details matter to scientific interpretation. Its probability function is explicitly defined and evaluated. The historical six-member result cannot substitute for the three-member model. Likewise, native member SHAP values cannot be relabeled as explanations of the averaged probability function without checking that their output spaces and background assumptions match that function.

## 8.2 The effect of the data audit

The overlap audit changes the strength of the detection conclusion. The original random-split scores remain valid descriptions of performance on that particular held-out sample, but they provide limited evidence of generalization to unseen feature vectors. The group-disjoint evaluation supplies a more demanding comparison and shows why a high score should be accompanied by an independence audit. It does not retrospectively change the frozen predictions used by the explanation experiments.

There are therefore two evidence layers in the thesis. The explanation experiments characterize specified historical seed-42 fitted predictors, including their limitations. The grouped training experiments evaluate how detector performance changes when exact representations are held out. Explaining every newly trained grouped model would be a further extension, rather than a result implied by the current explanation tables.

## 8.3 Implications for evaluating an IDS

A practical evaluation should identify the data release, retained features, split unit, ensemble members, explanation target, baseline distribution and source of uncertainty. Each of these choices can affect the conclusion. The project records them in machine-readable manifests and supplies both aggregate and instance-level results. This makes it possible to revisit an interpretation without rerunning an undocumented pipeline.

The evaluation does not prescribe an automatic threshold for accepting explanations. Such a threshold would require application-specific costs and evidence about analyst decisions. Instead, the results support an evaluation procedure: check split independence, evaluate class performance, measure repeatability, compare perturbation effects against random, and inspect sensitivity to the metric and intervention. This procedure is a methodological contribution rather than a deployment certificate.

# 9 Threats to Validity

## 9.1 Internal validity

Exact feature overlap is high in the original split. Group-disjoint validation addresses that overlap for detector evaluation but cannot remove other forms of dependence, such as temporally related flows with slightly different values. The grouping procedure uses 64-bit hashes of all retained features; accidental collisions are possible in principle, although the design groups equal representations conservatively. It does not rely on target labels for partitioning.

Model hyperparameters are fixed rather than extensively tuned. Balanced class weights are used for DT and RF but not XGBoost. The historical logistic regression checkpoint did not converge to its stopping criterion. These facts limit interpretations that attribute differences solely to architecture. Probability averaging is also sensitive to member calibration, which is not separately optimized in this project.

## 9.2 Construct validity

Mean and median masking can create unrealistic records. Absolute feature weights combine evidence supporting and opposing the original class, so deleting a high-magnitude opposing feature may increase its probability. Comprehensiveness therefore need not be positive for every case. Retained probability is not causal sufficiency. Rank metrics can be affected by ties and near-zero tails, and TOPSIS is sensitive to scales and chosen criteria.

SHAP output units and feature-dependence assumptions differ from LIME's probability surrogate. Matched instances and class targets improve comparability without making the estimands identical. Omitting SHAP for the combined voting predictor bounds the inference: this thesis evaluates its LIME reliability and probability sensitivity, not every available ensemble attribution method.

## 9.3 Statistical validity

The explanation sample is roughly class-balanced and limited by rare-class support. It is not drawn in proportion to operational traffic volume. Bootstrap groups account for exact retained-feature duplication within the sample, but other dependence can remain. Group-average Wilcoxon testing and instance-weighted effect estimation emphasize different weighting schemes, which are reported explicitly. Corrections cover the defined final comparison family rather than every exploratory statement in the project.

Three training seeds and three RQ2 LIME seeds are limited. Training seeds vary the split and model initialization together. The study does not claim exact replication across hardware or package versions beyond the checks recorded in the manifests. Historical RQ1 files have more limited provenance than the newly logged runs; they are explicitly retained as historical results and are not presented as new executions.

## 9.4 External validity

The dataset represents one benchmark environment. No independent network, prospective deployment, adversarial manipulation or analyst user study is evaluated. Group-disjoint results should not be described as cross-network generalization. Rare attack classes contain few unique feature groups, and their apparent performance can change sharply when those groups are repartitioned. Human usefulness of an explanation remains an open question.

# 10 Conclusions and Future Work

The thesis evaluates explanation reliability through repeatability, paired masking effects and agreement under explicit protocols. It finds substantial model-specific variation in LIME repeatability and shows how faithfulness estimates depend on a random control and the chosen masking baseline. The combined voting model is evaluated as a concrete probability function with named members, and its performance is separated from historical ensembles with different compositions.

The most consequential validity result is the extent of retained-feature overlap in the original random split. Group-disjoint evaluation provides a stronger test and constrains claims about detector generalization. This observation reinforces the need to evaluate the entire experimental design rather than relying on either prediction scores or attractive explanation plots.

Future work should prioritize independent-network or temporal validation, explanation evaluation on the group-disjoint fitted models, domain-valid feature replacement, more training and explanation seeds, calibration analysis and analyst-centered evaluation. RQ3 remains a specified cross-network extension rather than a completed result. The present evidence supports measured reliability for specified benchmark predictors; it does not establish universally trustworthy explanations.

# References

[1] Ribeiro, M. T., Singh, S., and Guestrin, C. (2016). Why Should I Trust You? Explaining the Predictions of Any Classifier. KDD. https://arxiv.org/abs/1602.04938

[2] Lundberg, S. M., and Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. NeurIPS. https://arxiv.org/abs/1705.07874

[3] Yeh, C. K., Hsieh, C. Y., Suggala, A., Inouye, D. I., and Ravikumar, P. K. (2019). On the Infidelity and Sensitivity of Explanations. NeurIPS. https://papers.nips.cc/paper_files/paper/2019/hash/a7471fdc77b3435276507cc8f2dc2569-Abstract.html

[4] DeYoung, J., Jain, S., Rajani, N. F., Lehman, E., Xiong, C., Socher, R., and Wallace, B. C. (2020). ERASER: A Benchmark to Evaluate Rationalized NLP Models. ACL, 4443-4458. https://aclanthology.org/2020.acl-main.408/

[5] Patil, S., Varadarajan, V., Mazhar, S. M., Sahibzada, A., Ahmed, N., Sinha, O., Kumar, S., Shaw, K., and Kotecha, K. (2022). Explainable Artificial Intelligence for Intrusion Detection System. Electronics, 11(19), 3079. https://doi.org/10.3390/electronics11193079

[6] Kalutharage, C. S., Liu, X., Chrysoulas, C., Pitropakis, N., and Papadopoulos, P. (2023). Explainable AI-Based DDOS Attack Identification Method for IoT Networks. Computers, 12(2), 32. https://doi.org/10.3390/computers12020032

[7] Hermosilla, P., Diaz, M., Berrios, S., and Allende-Cid, H. (2025). Use of Explainable Artificial Intelligence for Analyzing and Explaining Intrusion Detection Systems. Computers, 14(5), 160. https://doi.org/10.3390/computers14050160

[8] Sarhan, M., Layeghy, S., and Portmann, M. (2021). Towards a Standard Feature Set for Network Intrusion Detection System Datasets. https://arxiv.org/abs/2101.11315

# Appendix A Reproduction Procedure

Activate the project Python environment and run the dependency and protocol checks. Execute run_final_suite.py to reproduce the explicitly configured revised evaluations. The runner records completed jobs and resumes remaining work from its status file. Execute run_grouped_validation.py for the three group-disjoint training runs. Then execute build_final_results.py to validate the selected completed runs and create the aggregate tables and figures. The manuscript builder inserts those final values into this document's editable source.

The original six RQ1 datasets are intentionally retained rather than automatically regenerated. Their paths and checksums appear in selected_runs.json. Reproducing those measurements from scratch requires invoking run_rq1_stability.py for each corresponding frozen model with 1,000 requested cases and 5,000 perturbation samples. The existing results remain a historical comparison until such additional runs are explicitly selected.

Reproducing detection training requires the processed dataset and enough memory for the full flow matrix. The baseline runner writes checkpoints by model, task and seed, so rerunning the same seed replaces those checkpoints. The final experiment suite avoids refitting seed 42 and instead reconstructs the explicit ensemble from its existing members. Generated figures and tables should always retain the selected-run inventory that identifies their source observations.

# Appendix B Evidence Inventory

{{inventory_table}}

The final results folder additionally contains per-class detection tables, per-class faithfulness tables, per-instance seed variation, split audit data, full logs and source-run manifests. Reported numbers are computed from these outputs. Small environment-verification runs are not selected for the thesis tables.

# Appendix C Interpretation Guide

A high Jaccard score indicates similar selected sets under the stated repetition procedure. It does not establish that those features are useful. A positive comprehensiveness advantage indicates a larger average probability drop than random under the chosen mask. It does not establish causality. A high rank correlation indicates similar ordering under two methods' definitions. It does not identify a correct explanation without independent evidence.

Group-disjoint macro-F1 evaluates performance on feature representations held out from training within this dataset. It does not establish performance on a new organization or unseen attack mechanism. A narrow conditional interval does not include all deployment uncertainty. These distinctions are necessary when translating the numerical results into thesis conclusions or proposed operational use.
