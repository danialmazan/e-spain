# E-Spain

An English/Spanish static dashboard for exploring Spain's electricity generation, demand, installed capacity, storage, carbon-emitting generation share, cross-border flows, and day-ahead market context.

Production URL: <https://danielalmazan.com/ree-dashboard/>

## Data policy

- Monthly generation, demand, capacity, and CO2-equivalent classification come from the public REData API.
- Day-ahead Spanish prices come from OMIE's public `MARGINALPDBC` files.
- Monthly physical border exchanges come directly from REData and do not require a token.
- Hourly generation and demand still require a personal e·sios token. Request one from `consultasios@ree.es` and expose it only as `ESIOS_TOKEN` locally or in GitHub Actions.
- Monthly storage capacity comes from REData, with batteries separated from pumped storage.
- Marginal price-setting technology is never classified after 18 March 2025 because OMIE states that the new bid typology prevents identification after that date.
- Missing data stays missing. The project contains no synthetic-data generator or fallback.

Raw downloads are cached under gitignored `data/raw/`. The browser reads compact validated assets from `frontend/public/data/` and requires no production server.

## Run locally

```bash
npm install --prefix frontend
npm run data:fetch
npm run data:validate
npm start
```

Open <http://127.0.0.1:5173/ree-dashboard/>. Spanish is available at `?lang=es`.

## Verify

```bash
python3 -m unittest discover -s tests
npm run data:validate
npm run build
```

See [docs/RUNBOOK.md](docs/RUNBOOK.md) for source refresh, token, and deployment details.
