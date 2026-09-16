# E-Spain runbook

## 1. Install

```bash
cd /Users/danielalmazan/Projects/codex/test_ree
npm install --prefix frontend
```

The local directory and GitHub repository retain their historical names. The product's public base path is `e-spain`.

## 2. Configure e·sios

Request a personal API token from `consultasios@ree.es`. Never add it to Git.

Store it in the user-level `~/.Renviron` file (never in the repository):

```text
ESIOS_TOKEN=your-token-here
```

`npm run data:fetch` starts through R, so R loads `.Renviron` and passes the token to the Python ingestion child without printing it. A direct Python run requires `ESIOS_TOKEN` to already exist in that process environment.

Add the same value as the `ESIOS_TOKEN` GitHub Actions secret. Without it, the pipeline still publishes monthly REData generation, capacity, storage and physical border exchanges, while hourly generation/coverage modules visibly report `token_required`.

## 3. Refresh sources

```bash
npm run data:fetch
npm run data:validate
```

`scripts/ingest_sources.py` requests REData year by year, retrieves measured e·sios demand and generation, caches raw replies in `data/raw/`, and writes `frontend/public/data/dashboard.json`, `frontend/public/data/hourly/<year>.json`, and their checksummed manifest. Hourly UTC is derived from REE's offset-aware timestamp so both autumn DST hours remain distinct. It never interpolates or synthesizes missing observations. The legacy OMIE adapter remains available for data-maintenance compatibility, but E-Spain no longer presents a marginal-price section or lists OMIE as a product source because the available series cannot provide a current, continuous marginal-setting technology measure.

Useful options:

```bash
npm run data:fetch -- --start-year 2019 --end-year 2026 --omie-days 120
npm run data:fetch -- --skip-omie
```

If a source schema changes, do not publish. Update its parser and fixture, regenerate, then validate again.

## 4. Develop and test

```bash
npm start
python3 -m unittest discover -s tests
npm run build
```

Open `http://127.0.0.1:5173/e-spain/` and `http://127.0.0.1:5173/e-spain/?lang=es`.

Acceptance checks:

- Generation begins in 2019 and ends at the latest complete REData month.
- The browser console is clean at desktop and 390px widths.
- EN/ES labels, tooltips, error states, and source notes switch together.
- Hourly sections load measured yearly shards on demand, preserve 23/25-hour DST days, and disclose excluded observations.
- Coverage defaults to Solar PV and reports threshold hits overall, month by month, and by Madrid-local hour.
- The Generation daily-shape filters are independent of the page-level generation dates; test month, week, multi-weekday, multi-date and reset states.
- The final Sources / method page contains the sources used by the visible product and its limitations; ordinary pages end with the portfolio link and generated-data update date.
- There is no Marginal price navigation item, page, OMIE source listing, or marginal-price methodology copy.
- Built asset URLs and canonical metadata use `/e-spain/`.

## 5. Publish

The repository must be public and named `danialmazan/ree-dashboard`. GitHub Pages uses GitHub Actions as its source. The daily workflow refreshes, validates, builds, and deploys; failed refreshes do not replace the last successful artifact.

After pushing, verify the workflow and then check both language URLs with a cache-busting query:

```text
https://danielalmazan.com/e-spain/?v=<commit>
https://danielalmazan.com/e-spain/?lang=es&v=<commit>
```

Confirm repository sync with `git rev-list --left-right --count origin/main...HEAD`; the expected result is `0 0`.

## 6. Recovery

If the refresh fails, inspect the Actions log and the cached raw response locally. Do not bypass validation or substitute a sample. GitHub Pages continues serving its last successful deployment.
