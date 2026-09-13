# Research gap and future-work ledger

The expanded study investigates a reproducibility and evaluation gap: under a shared leakage-controlled protocol, do classification transfer, explanation repeatability and random-controlled explanation sensitivity tell the same story across network datasets and model families?

## Position relative to prior work

LLM intrusion detection and explanation are not new contributions by themselves. [Houssel et al. (2024)](https://arxiv.org/abs/2408.04342) already evaluate LLM network detection and discuss their complementary explanatory role. [eX-NIDS (2025)](https://arxiv.org/abs/2507.16241) already studies context-augmented LLM explanations. Our work must therefore make a narrower contribution: a reproducible, matched-case comparison of local LLM classification and detector explanations, alongside classical and neural detectors, with explicit cross-dataset and masking controls. This is a proposed contribution, not a claim that no previous paper contains these elements.

[Yeh et al. (2019)](https://papers.neurips.cc/paper_files/paper/2019/hash/a7471fdc77b3435276507cc8f2dc2569-Abstract.html) distinguish explanation sensitivity and fidelity; perfect sensitivity optimization can admit a constant explanation. This motivates separate measurement, not an assumed positive relationship. Their sensitivity definition is different from seed-to-seed Jaccard used here.

## Evidence required

| Question | Implemented evidence | Remaining limitation |
| --- | --- | --- |
| Detection generalization | Frozen binary models in both dataset directions; three completed training seeds | Complete matrix; capped training samples |
| Explanation transfer (RQ3) | Seed-42 LIME, 20 balanced unique feature groups/domain, three explainer seeds, random masking controls, full rankings saved | Pilot cohort; no causal or analyst validation; all 14 model pilots completed |
| Historical inverse association | Aggregate reconstruction and original-probability replay for 483 cases/model | Original masked rankings absent; cannot exactly reconstruct old masks |
| LLM classification and explanation | Local immutable model snapshots and auditable runner under validation | No completed LLM comparison yet; small models are not representative of all LLMs |

## Future work and feasible extensions

| Extension | Status | Reason / acceptance condition |
| --- | --- | --- |
| Source-validation calibration and target-domain calibration drift | Completed for seed 42 | Fit temperature only on source validation; evaluate Brier/ECE without target-test tuning |
| Training-only imbalance strategies | Weighting and undersampling completed for seed 42 | Compare weighting/resampling without changing test prevalence or leaking synthetic points across splits |
| Alternative explanation baselines and signed evidence | Completed post-hoc check; original masks replayed | Test mean/median and supporting/opposing features; do not force desired correlations |
| Longer temporal deployment | Future work | Current shared features lack a validated chronological split; random group partition is not temporal validation |
| Analyst usefulness study | Future work | Requires recruited analysts and an approved study design; generated rationales alone cannot validate usefulness |
| Larger LLMs / additional external datasets | Future work | CPU/RAM and data provenance constraints; current local models and two releases bound claims |

## Reporting workflow

Keep measured results in results/study/RESULTS.md and per-experiment ANALYSIS.md files. Only completed outputs enter comparison tables. Preserve historical results separately, retain seeds and source hashes, and publish gitmoji commits with validation details. Revise the thesis report only after the expanded study is complete, as requested by the user.


