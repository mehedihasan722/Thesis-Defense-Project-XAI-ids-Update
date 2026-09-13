# Frozen-model explanation transfer pilot

| Target | Cases | Jaccard@5 | LIME minus random removal drop |
| --- | --- | --- | --- |
| unsw | 20 | 0.977778 | 0.316474 |
| ids2018 | 20 | 0.922222 | -0.133832 |

Across-domain mean absolute LIME importance Spearman: 0.953441.

Twenty balanced unique feature groups per domain; one training seed. Different domains contain different instances: rank drift is distributional, not a paired-instance correctness test. Removal drop is higher-is-larger effect; sufficiency gap is lower-is-better retention. Absolute-weight rankings include opposing evidence. Median masking can create unrealistic flows. This pilot does not establish causal explanation validity.
