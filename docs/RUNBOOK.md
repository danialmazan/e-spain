# E-Spain runbook

## 1. Install

```bash
cd /Users/danielalmazan/Projects/codex/test_ree
npm install --prefix frontend
```

The local directory may retain its historical name. The product, GitHub repository, and public base path are `ree-dashboard`.

## 2. Configure e·sios

Request a personal API token from `consultasios@ree.es`. Never add it to Git.

```bash
cp .env.example .env
# Add ESIOS_TOKEN to .env, then:
set -a
source .env
set +a
```

Add the same value as the `ESIOS_TOKEN` GitHub Actions secret. Without it, the pipeline still publishes monthly REData generation, capacity, storage and physical border exchanges plus OMIE prices, while hourly generation/coverage modules visibly report `token_required`.

## 3. Refresh sources

```bash
npm run data:fetch
npm run data:validate
```

`scripts/ingest_sources.py` requests REData year by year, caches raw replies in `data/raw/`, retrieves the rolling OMIE price window, and writes `frontend/public/data/dashboard.json` plus its checksummed manifest. It never interpolates or synthesizes missing observations.

Useful options:

```bash
python3 scripts/ingest_sources.py --start-year 2019 --end-year 2026 --omie-days 120
python3 scripts/ingest_sources.py --skip-omie
```

If a source schema changes, do not publish. Update its parser and fixture, regenerate, then validate again.

## 4. Develop and test

```bash
npm start
python3 -m unittest discover -s tests
npm run build
```

Open `http://127.0.0.1:5173/ree-dashboard/` and `http://127.0.0.1:5173/ree-dashboard/?lang=es`.

Acceptance checks:

- Generation begins in 2019 and ends at the latest complete REData month.
- The browser console is clean at desktop and 390px widths.
- EN/ES labels, tooltips, error states, and source notes switch together.
- Hourly sections never display generated values when the token/data is absent.
- Marginal-technology timestamps cannot exceed `2025-03-18T23:00:00+01:00`.
- Built asset URLs and canonical metadata use `/ree-dashboard/`.

## 5. Publish

The repository must be public and named `danialmazan/ree-dashboard`. GitHub Pages uses GitHub Actions as its source. The daily workflow refreshes, validates, builds, and deploys; failed refreshes do not replace the last successful artifact.

After pushing, verify the workflow and then check both language URLs with a cache-busting query:

```text
https://danielalmazan.com/ree-dashboard/?v=<commit>
https://danielalmazan.com/ree-dashboard/?lang=es&v=<commit>
```

Confirm repository sync with `git rev-list --left-right --count origin/main...HEAD`; the expected result is `0 0`.

## 6. Recovery

If the refresh fails, inspect the Actions log and the cached raw response locally. Do not bypass validation or substitute a sample. GitHub Pages continues serving its last successful deployment.
