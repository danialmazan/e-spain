# Changelog

## 2026-09-17 — restore hourly Pages data and require the e·sios secret

- Diagnosed the live Coverage and daily-shape unavailable state as a GitHub Actions refresh performed without the repository `ESIOS_TOKEN` secret.
- Added the saved token as an encrypted repository secret and made the Pages workflow fail before ingestion when the secret is absent, preserving the last validated deployment.
- Files changed: `.github/workflows/deploy-pages.yml`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run the Pages workflow, confirm its credential guard and source refresh succeed, then verify the live manifest reports hourly data as `available` with yearly shards.

## 2026-09-17 — live release and portfolio publication

- Published the measured-hourly-data dashboard and the completed navigation, filter, mobile, and Marginal-price removal changes to `https://danielalmazan.com/e-spain/`.
- Added E-Spain as the first project in the bilingual Other / Otros section on both the main `danielalmazan.com` landing page and `danielalmazan.com/other/`, using the shared portfolio catalogue.
- Verified successful GitHub Pages workflows, cache-busted live output, EN/ES project links and copy, 390px layout, clean browser consoles, canonical/asset paths, and synchronized branches.
- Files changed in this repository: `docs/CHANGELOG.md` and `docs/PROMPT_LOG.md`; the portfolio catalogue and generated homepage/Other indexes were updated in their established separate publication repositories.
- Reproduce: run `npm run data:validate`, `npm run build`, then check `/e-spain/`, `/?lang=es`, and `/other/?lang=es` with cache-busting query parameters.

## 2026-09-16 — two-row header, filter polish and marginal-page removal

- Moved the page navigation to a dedicated row below the E-Spain identity at every viewport and aligned the title and strap on a shared text baseline.
- Aligned the daily-shape filter fields and actions, made the weekday menu close on outside tap/click or Escape, and increased mobile touch targets for Android and iOS-sized screens.
- Removed the Marginal price page, navigation entry, OMIE source listing and related product-method copy because the available price context does not identify the price-setting technology and the historical classification is not current.
- Files changed: `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/src/types.ts`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, inspect the two-row header and daily-shape filters in EN/ES at desktop, 390px iOS and 360px Android widths, then verify outside-click dismissal and the absence of Marginal price from navigation and Sources / method.

## 2026-09-16 — daily-shape filters and Sources / method page

- Reworked the identity into a self-link reading “E-Spain: an analysis of Spain's electricity system”, while retaining the established IBM Plex typography.
- Added chart-specific month range, week, multi-weekday and multi-date controls to “The shape of a day”, plus reset behavior and an included-hour count. These controls do not change the generation mix, trend or balance dates.
- Rewrote the interconnector and coverage introductions, moved source provenance into a new bilingual Sources / method page, and replaced the repeated source footer with a portfolio link and dataset update date.
- Added explicit marginal-page copy explaining that the historical technology classifier has not yet been imported and that the visible OMIE series is only a rolling 120-day monthly price context.
- Files changed: `frontend/src/App.tsx`, `frontend/src/styles.css`, `frontend/src/types.ts`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open Generation and combine the chart-specific filters, verify reset and unchanged global dates, then check Marginal price and Sources / method in EN/ES at desktop and 390px.

## 2026-09-14 — measured e·sios hourly archive

- Activated the saved `ESIOS_TOKEN` without exposing it and replaced the hourly unavailable states with 67,511 measured peninsular intervals covering 2019 through 13 September 2026.
- Added pinned live-catalogue, name, MW magnitude, source-frequency, geography, duplicate, checksum, cadence, missing-value, and DST validation. UTC is derived from REE's offset-aware local timestamp to preserve both autumn repeated hours.
- Added lazy yearly hourly shards, a selected-technology daily demand-share profile, and Solar-PV-default Coverage results with overall, monthly, and hour-of-day statistics. Unsupported hourly technologies are visibly disabled and missing observations are excluded and counted.
- Added an R refresh wrapper so `npm run data:fetch` automatically inherits `ESIOS_TOKEN` from `~/.Renviron` without printing it.
- Files changed: `.gitignore`, `scripts/`, `tests/`, `frontend/public/data/`, `frontend/src/`, `package.json`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run data:fetch`, `npm run data:validate`, `python3 -m unittest discover -s tests`, and `npm run build`; inspect Generation and Coverage in EN/ES at desktop and 390px.

## 2026-09-13 — signed net-country stacking

- Corrected the net interconnector chart to use sign-separated stacking: each country's imports and exports are netted first, positive country totals stack upward, and negative country totals stack downward without crossing zero.
- Files changed: `frontend/src/App.tsx`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, choose `Net by country`, filter to April 2026, and confirm France's `+423 GWh` segment is blue above zero while Portugal, Morocco, and Andorra stack below zero.

## 2026-09-13 — interconnector tooltip colours

- Restored each country's series colour in the cross-border hover/tap data card while preserving the dark tooltip surface and transparent chart cursor; forced localized grouping for four-digit tooltip values, including Spanish `1.055`.
- Files changed: `frontend/src/App.tsx`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open Interconnectors, and hover or tap a month in both chart modes; each country label should match its chart colour.

## 2026-09-13 — interconnector controls

- Changed cross-border flows to stacked country columns, with separate `Imports + exports` and signed `Net by country` modes and independent France, Portugal, Morocco, and Andorra visibility toggles.
- Removed the light Recharts hover/tap cursor and explicitly retained the dashboard's navy tooltip surface.
- Changed hourly coverage's default technology set to Solar PV only and removed the storage-capacity explanatory note.
- Files changed: `frontend/src/App.tsx`, `frontend/src/styles.css`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open Interconnectors, switch modes and toggle countries; then open Coverage and confirm only Solar PV is active by default.

## 2026-09-13

- Renamed the product to E-Spain and refined the Grid Monitor interface, removing the generated-at header and methodological "verified data" language.
- Added shared generation presets, individual technology toggles, synchronized date/source state across the monthly mix and rolling trend, and consistently rounded/localized chart tooltips with units and technology names.
- Replaced synthetic interconnector flows with official monthly REData physical exchanges for France, Portugal, Morocco, and Andorra; imports are positive and exports negative.
- Added coverage source/threshold/date controls with an explicit hourly-data unavailable state, moved System before Marginal price, replaced the capacity bars with monthly installed-capacity lines, added battery versus pumped-storage capacity, and explained the CO2-associated generation series.
- Extended ingestion, validation, contracts, fixtures, provenance, and published data for physical exchanges and storage. Refreshed official data through the latest complete month available from each widget.
- Completed EN/ES desktop and 390px interaction QA, including preset reset behavior, horizontal control scrolling, body overflow, tap targets, and browser-console checks.
- Files changed: `scripts/`, `tests/`, `frontend/`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, and `docs/PROMPT_LOG.md`.
- Reproduce: run `python3 scripts/ingest_sources.py --start-year 2019 --end-year 2026 --omie-days 120`, `python3 scripts/validate_data.py`, `python3 -m unittest discover -s tests`, and `npm run build`; inspect EN/ES at desktop and 390px.

## 2026-09-09

- Rebuilt the project as REE Dashboard with a static Grid Monitor interface, complete EN/ES UI, real REData monthly generation/demand/capacity/carbon-context data, an OMIE price adapter, strict provenance/validation, token-safe e·sios configuration, and GitHub Pages deployment at `/ree-dashboard/`.
- Removed the obsolete FastAPI runtime and all synthetic generators; hourly sections now report the missing e·sios token instead of showing invented values.
- Recomputed generation shares from component GWh (excluding REData's aggregate total), excluded incomplete current-month observations, and added validation that each monthly mix sums to 100%.
- Completed live mobile refinements by removing the remaining backdrop blur and preventing the Spanish headline from overflowing at 390px.
- Files changed: source/validation scripts, generated public data, frontend, tests, Pages workflow, README, and runbook.
- Reproduce: run `npm run data:fetch`, `npm run data:validate`, `python3 -m unittest discover -s tests`, and `npm run build`; inspect EN/ES at desktop and 390px.

## 2026-03-27

- Fixed the interconnector split chart so export bars use their own negative stack instead of sharing the import stack, which makes exports render from zero down to their full absolute magnitude rather than collapsing toward the net line.
- Files changed: `frontend/src/App.tsx`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open the interconnectors page in `Imports / exports` mode, and verify that a month like `2022-10` shows France near `+79` for imports, `-286` for exports, and the white net line near `-207`.

- Fixed the interconnector split-mode tooltip so export series are displayed as absolute values while still rendering below zero on the chart, which avoids reading export magnitudes as negative net values.
- Files changed: `frontend/src/App.tsx`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open the interconnectors page in `Imports / exports` mode, and hover a month with exports to confirm the tooltip shows export magnitudes without a minus sign.

- Extended the synthetic hourly sample store so coverage and marginal-technology data now span 2019-01 through 2026-03 instead of only a short 2024-2025 window, and updated the dashboard copy/docs to match.
- Files changed: `backend/app/sample_store.py`, `backend/app/repository.py`, `backend/tests/test_api.py`, `frontend/src/App.tsx`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `python3 scripts/build_sample_store.py`, `./backend/.venv/bin/pytest`, `npm run build`, then query coverage or marginal technology for 2019 and 2026 months in the dashboard.

- Widened the generation-page balance chart plus the system-page capacity and emissions cards, stopped rendering out-of-window coverage months as fake zero bars, added explicit sample-data availability notes, and made sample interconnector imports/exports more realistic than a direct transform of net balance.
- Files changed: `backend/app/sample_store.py`, `backend/tests/test_api.py`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `python3 scripts/build_sample_store.py`, `./backend/.venv/bin/pytest`, `npm run build`, then restart the dashboard and inspect the generation, interconnectors, coverage, marginal, and system pages.

## 2026-03-25

- Implemented the first Spain electricity dashboard MVP scaffold with a FastAPI backend, generated local analytics store, React/Vite frontend shell, and repo run documentation.
- Files changed: `backend/`, `frontend/`, `scripts/build_sample_store.py`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`, `.gitignore`.
- Reproduce: install backend/frontend dependencies, run `python3 scripts/build_sample_store.py`, start `uvicorn app.main:app --reload`, then `npm run dev`.

## 2026-03-26

- Added a repo-root `package.json` so `npm run dev` and `npm run build` work from the project root by forwarding to the frontend app.
- Files changed: `package.json`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: from the repo root run `npm run dev` or `npm run build`.

- Added frontend API error handling so the dashboard shows a visible backend-start message instead of hanging on "Loading local analytics store…", and added a repo-root `npm run api:dev` script.
- Files changed: `frontend/src/App.tsx`, `frontend/src/styles.css`, `package.json`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: stop the backend, load the frontend, and confirm the error state appears; then run `npm run api:dev`.

- Fixed the `/api/exchanges` monthly net path so interconnector requests return `value_gwh` instead of crashing with `KeyError: 'net_imports_gwh'`, and added a regression test for that endpoint.
- Files changed: `backend/app/repository.py`, `backend/tests/test_api.py`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `./backend/.venv/bin/pytest`, then start the API and load the dashboard with the interconnectors panel requesting `direction=net`.

- Restructured the dashboard into page-based sections, added top-level month-range filtering, converted the national mix to monthly stacked bars / 12-month averages, changed marginal technology to monthly percentage shares, removed the right-side panel, and updated chart formatting and capacity bars.
- Files changed: `frontend/src/App.tsx`, `frontend/src/components/Sidebar.tsx`, `frontend/src/api.ts`, `frontend/src/styles.css`, `backend/app/main.py`, `backend/app/repository.py`, `backend/tests/test_api.py`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `./backend/.venv/bin/pytest`, run `npm run build`, then open the app with `npm run dev` and `npm run api:dev`.

- Split page-specific source selectors so generation and coverage no longer share the same selection state, moved the generation selector into the generation chart block, and corrected the 12-month mode to use monthly data with a rolling 12-month average instead of annual backend totals.
- Files changed: `frontend/src/App.tsx`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `npm run build`, open the app, compare source selections across pages, and switch the main chart between `Monthly` and `12M average`.

- Refined page-specific controls and semantics: signed import-gap bars in the balance chart, interconnector `Net` vs `Imports / exports` modes with country multi-select and net total line, indexed capacity vs generation chart on the generation page, percentage-based coverage breakdowns, fixed marginal-tech stack/axis behavior, and higher-precision CO2 intensity labels.
- Files changed: `frontend/src/App.tsx`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `./backend/.venv/bin/pytest`, run `npm run build`, then inspect the generation, interconnectors, coverage, marginal, and system pages in the browser.

- Added a single-command local launcher so the dashboard can be started from one terminal with `npm start`, which runs both the backend and frontend and shuts both down on `Ctrl+C`.
- Files changed: `scripts/dev.mjs`, `package.json`, `README.md`, `docs/RUNBOOK.md`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: from the repo root run `npm start`.

- Split date filters by page, fixed the generation trend and balance chart semantics, added generation-family presets plus an independent capacity selector, changed coverage threshold updates to explicit apply, separated system context into two sections, and varied interconnector country shares by month in the sample store.
- Files changed: `backend/app/sample_store.py`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `python3 scripts/build_sample_store.py`, `./backend/.venv/bin/pytest`, `npm run build`, then refresh the app.

- Extended the monthly sample store through March 2026, made monthly net imports vary materially so balance/interconnector charts are not flat, updated default page ranges to `2019-01` through `2026-03`, removed the capacity-generation index chart, widened the selected-source trend chart, padded the coverage timeline to the selected range, and increased chart margins / emissions-axis width to prevent clipped labels.
- Files changed: `backend/app/sample_store.py`, `frontend/src/App.tsx`, `frontend/src/styles.css`, `docs/CHANGELOG.md`, `docs/PROMPT_LOG.md`.
- Reproduce: run `python3 scripts/build_sample_store.py`, `./backend/.venv/bin/pytest`, `npm run build`, then restart the app.
## 2026-09-15 — public path moved to /e-spain/

- Changed the GitHub Pages public base path from `/ree-dashboard/` to `/e-spain/`, including Vite asset URLs, canonical/Open Graph metadata, README, and runbook instructions.
- Files changed: `frontend/vite.config.ts`, `frontend/vite.config.js`, `frontend/index.html`, `README.md`, `docs/RUNBOOK.md`.
- Reproduce: run `npm run build`, then inspect `frontend/dist/index.html` and built asset paths for `/e-spain/`.
