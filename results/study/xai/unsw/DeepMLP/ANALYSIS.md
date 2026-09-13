# Frozen-model explanation transfer pilot

| Target | Cases | Jaccard@5 | LIME minus random removal drop |
| --- | --- | --- | --- |
| unsw | 20 | 0.758730 | 0.304272 |
| ids2018 | 20 | 0.780952 | 0.605750 |

Across-domain mean absolute LIME importance Spearman: 0.979555.

Twenty balanced unique feature groups per domain; one training seed. Different domains contain different instances: rank drift is distributional, not a paired-instance correctness test. Removal drop is higher-is-larger effect; sufficiency gap is lower-is-better retention. Absolute-weight rankings include opposing evidence. Median masking can create unrealistic flows. This pilot does not establish causal explanation validity.
