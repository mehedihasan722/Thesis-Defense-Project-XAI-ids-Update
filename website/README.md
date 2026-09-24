# XAI / IDS research observatory

A responsive thesis website built directly in this repository, with the original-preserving thesis, all 41 figures, and interactive versions of the 23 added scientific figures.

## Run locally

Requires Node 22.12+ or a compatible newer release.

```powershell
cd website
npm ci
npm run dev -- --port 4173
```

For production preview: `npm run build`, then `npm run preview -- --port 4174`. No Python environment or experimental result is changed. React, Vite and custom HTML/SVG charts are used. Fonts, runtime, figures and PDF are served locally; reading the site does not require an external API.

## Exact ThreeUI source

The four registered files are copied byte-for-byte from https://threeui.com/source-code/sylva-living-world.json at the requested revision `fd922291297d`. Their original paths and all supplied SHA-256 hashes are recorded in `threeui-source.json`. Every build verifies these hashes. `.gitattributes` prevents checkout newline conversions in the vendor directory.

`src/Scene.jsx` uses the requested import names and `<SylvaLivingWorldScene variant="living-green" />`. Vite aliases `@designcodeio/threeui` and its stylesheet to the exact local registered files. The authored component creates a sandboxed scene iframe from its canonical HTML and bundled Three.js r149 runtime. No documentation page is embedded and no scene was approximated.

The authored shaders, geometry, pollen, butterfly, scan, pointer handling and responsive behavior remain unchanged. A surrounding pause/play button unmounts/remounts the component. The component also unloads off-screen; full-page screenshots can miss it, so review the visible hero at viewport size.

Lexend is supplied at the canonical `public/inner-green-assets/lexend-latin.woff2` path. Fragment Mono is supplied at the shared CSS's referenced path. Font source URLs and hashes are in `font-sources.json`; Google Fonts OFL notices are in `licenses/`. ThreeUI source remains attributed to its provider; this integration does not relicense that source. Three.js retains its original notices.

## Evidence and interaction

Detection controls cover both datasets, binary/native multiclass tasks, macro-F1 and false-alarm rates. Means and sample SD reflect three seeds. Binary frozen transfer is available in both directions. Explanation controls cover all four dataset directions, Jaccard@5 and random-controlled masking advantage; confidence intervals are conditional on one fitted model.

LLM plots show valid own-decision or detector-grounded explanation coverage out of all 80 requested outputs per model. They do not imply classifier accuracy. The historical scatter includes all 483 matched cases per original tree model.

Hover or focus bars for exact data, click/tap to pin values, use the historical case slider by keyboard, open full data tables, and download unrounded CSV values. Each added figure's library card selects its corresponding interactive chart. The original diagrams/plots remain unchanged images with zoom and individual vector PDF links; static diagrams are not passed off as interactive measurements.

The library supports search, collection filtering, separate PNG downloads and Escape-to-close zoom. The full 109-page PDF and editable Word link are available. Original reference [28] and final editorial reconciliation remain tracked in repository issue #11.

## Refreshing evidence

From the repository root, run `python website/scripts/export_data.py` with standard-library Python. It reads saved CSVs, caption metadata and the original DOCX package without model training or inference. Input hashes are recorded in the exported snapshot. The build fails if current research inputs differ. Refresh only after a reviewed evidence update; do not hand-edit values.

## Browser verification

`npm run test:browser` uses installed Microsoft Edge and `http://127.0.0.1:4173` by default. Set `SITE_URL` for the production preview; `BROWSER_CHANNEL=chromium` works with a Playwright-installed Chromium on other systems. Screenshots and temporary logs go to the ignored `tmp/website-review/` directory. The release verification record is copied to `verification/browser-checks.json` after successful testing.

Tests cover runtime rendering, pointer response, pause/play, CSV-derived hover values, pinning, keyboard focus, data tables/downloads, negative intervals, LLM denominators, all 23 figure selectors, search/reset, modal Escape, PDF access, mobile overflow/tap and reduced-motion chart behavior.

The exact scene source and r149 runtime form a separate large lazy-loaded chunk. Vite's size advisory is expected; source should not be altered to silence it.

## Deployment status

The production build is ready for local review. Public GitHub Pages deployment is pending explicit user approval. No automatic public deployment workflow has been installed or enabled. Publishing would make this website, its charts and the already-public thesis PDF accessible at a public Pages URL. Repository source updates and public website deployment are tracked separately.
