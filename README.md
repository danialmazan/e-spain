# E-Spain

An English/Spanish static dashboard for exploring Spain's electricity generation, demand, installed capacity, storage, carbon-emitting generation share, and cross-border flows.

The hourly daily-shape view has its own month, week, weekday and multi-date filters. Source provenance and methodological limitations are collected on the final **Sources / method** page rather than repeated below every section.

Production URL: <https://danielalmazan.com/e-spain/>

## Data policy

- Monthly generation, demand, capacity, and CO2-equivalent classification come from the public REData API.
- Monthly physical border exchanges come directly from REData and do not require a token.
- Measured hourly peninsular generation and demand come from e·sios. A personal token is required only during refresh; request one from `consultasios@ree.es` and expose it only as `ESIOS_TOKEN` locally or in GitHub Actions.
- Monthly storage capacity comes from REData, with batteries separated from pumped storage.
- Missing data stays missing. The project contains no synthetic-data generator or fallback.

Raw downloads are cached under gitignored `data/raw/`. The browser reads compact validated monthly data and UTC-normalized yearly hourly shards from `frontend/public/data/`; it requires no production server. The current hourly archive covers 2019 through the latest complete day, preserves 23/25-hour daylight-saving days, and discloses missing source observations rather than filling them.

## Run locally

```bash
npm install --prefix frontend
# Add ESIOS_TOKEN to ~/.Renviron once; R passes it to the Python child.
npm run data:fetch
npm run data:validate
npm start
```

Open <http://127.0.0.1:5173/e-spain/>. Spanish is available at `?lang=es`.

## Verify

```bash
python3 -m unittest discover -s tests
npm run data:validate
npm run build
```

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for source refresh, token, and deployment details.
