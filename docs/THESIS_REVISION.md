# Thesis revision preserving the original report

Updated 24 September 2026. This revision supersedes the shortened 50-page report as the current author-review draft. It starts from the supplied editable IIUC thesis, keeps its original content and formatting, and inserts completed study extensions in the relevant chapters.

- [Current 109-page PDF](../output/pdf/thesis_xai_ids_preserved.pdf)
- [Editable Word document](../output/docx/thesis_xai_ids_preserved.docx)
- [Original editable source](../thesis/reference/original_thesis.docx)
- [Separate figures and captions](../results/study/preserved_report/README.md)
- [Preservation and input-hash checks](../results/study/preserved_report/preservation_check.json)
- [Layout review and remaining editorial work](../results/study/preserved_report/REVIEW.md)

## Preservation and additions

| Content | Original retained | Added | Revised total |
| --- | ---: | ---: | ---: |
| Word tables, including front matter | 25 | 16 | 41 |
| Numbered figure captions | 18 | 23 | 41 |
| Bibliography entries | 36 | 6 | 42 |
| Appendices | A and B | C | 3 |

All original body paragraphs and table cell text are retained, apart from rebuilt navigation entries. Original media, styles, headers, footers and other unchanged package parts are verified byte for byte. Seven floating pictures were moved inline beside their captions so inserted text cannot push them outside a page. Original empty spacing and existing multi-panel figures remain; each added figure has a separate caption and its own PNG, SVG and vector PDF. Separate figures do not necessarily occupy separate pages.

The original institutional front matter, five chapters, references, appendices, margins, Times New Roman styles and Roman/Arabic page numbering are retained. Contents, figure and table lists have 199 refreshed page references. The source DOCX SHA-256 is `7c52c19f5d02137223e261a54d9fe7d6291634f3a89b8efbd3a01301eb07b841`.

## Where the expanded evidence appears

- Abstract and Section 1.5.1 explain the original and expanded scopes.
- Section 2.7.1 extends the research gap and positions the LLM comparison.
- Sections 3.8.1.1-3.8.1.9 specify the two datasets, disjoint feature-group splits, seven detector families, uncertainty, masking and LLM protocols.
- Sections 4.2.10-4.2.19 report detection, frozen transfer, historical audit, explanation transfer, masking sensitivity, LLM outcomes, calibration, imbalance and validity limits.
- Figures 4.12-4.34 extend the original visual comparisons using separate plots. Original Figures 4.1-4.11 are unchanged.
- Section 5.1.1 qualifies the historical conclusions. Section 5.3 explains completed RQ3 work; Section 5.3.4 records remaining future work.
- Appendix C adds all 28 model/direction explanation summaries. Appendices A and B remain intact.

The completed experiment inventory remains 84 detector configurations and 126 evaluation cells. The three LLMs completed 1,200 classifications and 480 generated explanations. This report revision performs no new training or inference and changes no experimental result.

## Interpretation boundaries

The original random-split results and corrected group-disjoint results are separately labelled and must not be pooled. The historical audit found consistent saved arithmetic, positive descriptive within-model stability/advantage correlations, and substantial original split overlap. It does not establish that every old result was falsified, nor validate unavailable original masked predictions.

RQ1 remains stability, RQ2 faithfulness, RQ3 transferability and RQ4 cross-explainer agreement. The LLM comparison is an additional extension. Completed RQ3 is the specified binary frozen-detection and LIME transfer protocol; it does not imply completion of every per-attack-class rank-drift idea in the original future-work plan. New SHAP/TOPSIS comparisons for all neural models are not claimed.

All three small LLMs produced constant-class predictions under the frozen protocol. Invalid explanations remain in coverage denominators; conditional masking scores do not describe all generated outputs. Bootstrap intervals over 20 explanation cases are not training-seed or deployment uncertainty.

Original wording is retained for provenance, including old future-work statements; inserted scope and completion notes qualify them. This is a preservation-first author-review draft, not a claim that every historical sentence is newly validated. Original reference [28] explicitly lacks confirmed bibliographic details. Exact-title searches on 24 September did not identify a matching source; related papers are not substitutes. Claims relying on [28] need source confirmation before submission. Signatures, dates, supervisor approval, a full bibliography audit and final editorial reconciliation remain human review items.

## Rebuild

Use the existing study Python for figures, and a document Python containing python-docx, lxml, pypdf and pdfplumber for document assembly and verification. The export step requires Microsoft Word on Windows. Document dependencies remain separate from `.venv-study`.

```powershell
.venv-study/Scripts/python.exe -m study.preservation_figures
& $DocumentPython -m study.preserve_thesis
./study/export_preserved_thesis.ps1
& $DocumentPython -m study.verify_preserved_thesis
```

Set `$DocumentPython` to the document-runtime executable. In this workspace the bundled runtime is `C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.

The builder uses the original DOCX, saved CSVs and the verified expanded narrative in `thesis/manuscript.md`. That Markdown and `output/pdf/thesis_xai_ids.pdf` remain historical inputs from the shortened revision; they are not the current full report. The original `study.build_report` / `render_thesis_pdf.py` pipeline produces that older format. Use the preservation pipeline above for this revision.

Word exports the PDF without saving over the preserved package. The verifier caches page fields, checks original content/package preservation, 42 references, all new captions, separate figure formats and image bounds, and writes hashes. Render and visually inspect a rebuilt PDF before publication; page counts can depend on the Word/font environment.
