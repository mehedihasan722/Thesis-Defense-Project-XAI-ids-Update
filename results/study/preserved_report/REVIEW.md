# Preservation revision review

Date: 24 September 2026. Current artifacts: `output/docx/thesis_xai_ids_preserved.docx` and `output/pdf/thesis_xai_ids_preserved.pdf`. Machine-readable checks and artifact/input hashes are in [preservation_check.json](preservation_check.json).

## Checks performed

- Original body paragraph text retained, excluding rebuilt contents/list entries; all 25 original tables retain identical cell text.
- Thirty-two untouched OOXML package parts, including original media and styles, match the original bytes.
- 109 PDF pages, 41 numbered figure captions, 41 Word tables, 42 reference entries and 199 cached page references.
- All 23 new figures have individual PNG, SVG and PDF files. Added figures have separate numbered captions even where two figures share a page.
- Every PDF image checked against its page bounds. No image extends outside the page. No missing-bookmark/reference errors.
- Microsoft Word rendered the document; Poppler produced review page images. The packaged LibreOffice renderer could not run because soffice.exe was unavailable, so Word was used for the render gate.
- Visual review covered the original-content pages during iteration and rechecked changed front matter, moved original figures, new results and the final discussion/references/appendices. In the final 109-page render, pages 7-14, 31, 35, 38, 56, 62-63 and 69-109 were inspected individually; earlier pages had been inspected in the preceding render. Final image-bound checks cover all 109 pages. This record distinguishes iterative visual coverage from a claim that every final page was individually re-opened.

The floating original Figure 4.9 previously crossed a page boundary after insertion; moving the unchanged image inline fixed it. Original blank spacing is retained, so some pages have substantial whitespace. A suspected chart-label crop was checked against the embedded image and full-size page crop: complete labels are present.

## Remaining author review

Original reference [28] explicitly says its bibliographic details are unconfirmed. Exact-title searches on 24 September did not resolve it. No replacement citation was invented. All original references are preserved, but preservation is not a full bibliography authenticity audit.

Original prose and historical future-work statements remain, with new scope notes and qualified conclusions. Authors should reconcile those statements before submission. Completed RQ3 means the frozen binary-detection and LIME protocols actually run; the original per-attack-class rank-drift proposal is not claimed complete. Historical and new results use different protocols and must not be pooled.

Signature/date fields and supervisor certification require the appropriate people. This draft does not establish causal explanation correctness, analyst usefulness or deployment readiness.
