# Revised thesis: completed study

The user authorized manuscript revision after the expanded experiments completed. The revised report uses the supplied IIUC reference format: A4 dimensions, Times New Roman, institutional cover and front matter, five chapters, references, appendices and Roman/Arabic page numbering. Its length follows the completed evidence rather than copying the old page count.

- [Revised PDF](../output/pdf/thesis_xai_ids.pdf)
- [Editable manuscript](../thesis/manuscript.md)
- [Narrative template](../thesis/study/report.template.md)
- [Input hashes](../results/study/report/input_manifest.json)
- [Structural PDF checks](../results/study/report/pdf_structure_check.json)

## What changed

The report incorporates all seven classical/ensemble/neural detector families, both datasets, three training/split seeds, 84 configurations and 126 evaluation cells. RQ3 covers frozen detection transfer and a separately scoped explanation-transfer pilot. Three local LLMs contribute 1,200 classification cases and 480 generated explanations (240 pairs).

The interpretation preserves the constant-class LLM outcomes and invalid explanation responses. It separates stability from random-adjusted masking sensitivity, explains historical metric directions, and reports the limits of historical replay. It does not claim falsification from an inverse association. Calibration, class imbalance, masking sensitivity, domain shift, research positioning and future work are included.

Nine print-sized scientific figures were generated from existing evidence, with PNG and SVG sources under `results/study/report/figures/`. The report has 20 numbered tables, including methodology, results and appendices. Historical study artifacts and the original manuscript template remain preserved.

## Build

From the repository root:

```powershell
.venv-study/Scripts/python.exe -m study.report_figures
python -m study.build_report
python render_thesis_pdf.py
python verify_thesis_pdf.py
```

The first command uses the existing study environment for pandas, matplotlib and scipy. The remaining commands require ReportLab, Pillow and pdfplumber; rendering uses Windows Times New Roman fonts. In this task the bundled document Python runtime supplied those packages without changing `.venv-study`.

`build_report.py` requires all 42 three-seed groups, all 126 detector cells with 80,000 test rows, all 12 LLM direction cells and the full explanation coverage denominator. It generates tables from saved CSVs, validates figure paths and records hashes. No training or inference is performed by the report build.

## Review boundaries

The PDF is a revised research manuscript for author and supervisor review. Signature, date and approval fields remain blank. The cover title and author identities follow the reference PDF. The expanded experimental scope is explained in the introduction. This revision does not provide institutional certification, causal explanation validation, a deployment guarantee or an analyst usefulness study.

The repository's raw experiment analyses remain primary provenance. Earlier status snapshots may describe work as deferred or pending at their historical date; the report and this revision record state the completed evidence and remaining scientific limitations explicitly.
