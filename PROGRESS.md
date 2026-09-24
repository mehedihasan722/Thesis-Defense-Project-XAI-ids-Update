# Completed executable study

All 84 detector configurations and 126 evaluation cells are complete and independently checked. All 14 RQ3 model pilots, source-only calibration, training-only imbalance comparison and three full local LLM runs with classification and explanations are complete. Valid LLM explanations have named-versus-random masking checks; invalid outputs remain in coverage denominators.

Results, tables and embedded figures are in results/study/RESULTS.md, ACROSS_SEEDS.md and the xai/, llm/, calibration/, imbalance/ and shift/ analysis files. The thesis report has been revised from the completed evidence. See [revision notes](docs/THESIS_REVISION.md), [current PDF](output/pdf/thesis_xai_ids_preserved.pdf) and [editable Word](output/docx/thesis_xai_ids_preserved.docx). Author signatures and supervisor review remain human tasks.

Limitations remain scientific, not hidden: small explanation cohorts, three small CPU LLMs, rounded flow serialization, masking distribution shifts and no temporal/analyst validation. Historical original probabilities replay, but exact old masks cannot be replayed because original rankings were not saved. Do not interpret inverse stability/faithfulness relationships as proof of falsification.


## Original-report restoration on 24 September 2026

The full preservation revision replaces the shortened report as the current draft: 109 pages, 41 Word tables, 41 figure captions and 42 bibliography entries. All 25 original tables, 18 original figure captions, 36 references, both original appendices and original body text are retained. Twenty-three added figures are individually available in PNG, SVG and PDF and embedded with captions in the [figure index](results/study/preserved_report/README.md).

The original DOCX is archived for reproducibility. Seven floating figures were anchored inline beside captions, navigation fields were refreshed, and structural/content/image-boundary checks passed. See [revision notes](docs/THESIS_REVISION.md) and [review record](results/study/preserved_report/REVIEW.md). No model was rerun and no saved experimental result changed.

Before submission: confirm original reference [28], reconcile historical wording with the qualified expanded conclusions, and obtain author/supervisor approval. RQ3 completion applies to the specified binary/LIME protocol, not every future per-class or SHAP experiment.


## Interactive website implementation

Added `website/` with an exact-source ThreeUI Living Green scene and verified chart data exported from the frozen CSVs. All 41 figures are preserved in the searchable library; the 23 added figures have interactive controls, data inspection and CSV export. The site supports mobile tap, keyboard focus, a scatter-case slider, pause/play and reduced-motion charts. No model or report was changed.

Public GitHub Pages deployment awaits explicit approval. Automatic approval review rejected creating a persistent public deployment workflow because that destination and side effect had not been explicitly authorized. No deployment workflow was written or enabled. Source and local production preview remain available; see `website/README.md` and the browser verification record.


## Thesis defense presentation

Completed a 28-slide editable defense deck and native PowerPoint PDF export. Includes 11 separate charts, speaker notes, the neural/LLM extension, RQ3 transfer, historical audit, limitations and future work. Sources and slide outline: [docs/THESIS_PRESENTATION.md](docs/THESIS_PRESENTATION.md).
