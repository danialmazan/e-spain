#!/usr/bin/env python3
"""Fetch and normalize public REE/OMIE data for the static E-Spain dashboard.

Raw responses are cached under gitignored data/raw. Only compact derived JSON
is written to frontend/public/data. No synthetic values or interpolation are
used. When ESIOS_TOKEN is absent, hourly modules are marked unavailable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import unicodedata
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from source_config import (
    ESIOS_BASE,
    ESIOS_EXPECTED_MAGNITUDE,
    ESIOS_EXPECTED_SOURCE_FREQUENCIES,
    ESIOS_HOURLY_KEYS,
    ESIOS_INDICATORS,
    MARGINAL_TECHNOLOGY_CUTOFF,
    OMIE_DOWNLOAD,
    PENINSULAR_GEO_ID,
    REDATA_BASE,
    REDATA_EXCHANGE_WIDGETS,
    REDATA_STORAGE_WIDGETS,
    REDATA_WIDGETS,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PUBLIC = ROOT / "frontend" / "public" / "data"


def fetch_bytes(url: str, headers: dict[str, str] | None = None, retries: int = 3) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "ree-dashboard/1.0", **(headers or {})})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError):
            if attempt == retries - 1:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError("unreachable")


def fetch_json(url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
    return json.loads(fetch_bytes(url, headers).decode("utf-8"))


def red_data(widget: str, year: int, refresh: bool = False) -> dict[str, Any]:
    cache = RAW / "redata" / widget.replace("/", "_")
    path = cache / f"{year}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text(encoding="utf-8"))
    query = urllib.parse.urlencode(
        {
            "start_date": f"{year}-01-01T00:00",
            "end_date": f"{year}-12-31T23:59",
            "time_trunc": "month",
        }
    )
    url = f"{REDATA_BASE}/{widget}?{query}"
    payload = fetch_json(url)
    if "included" not in payload or "data" not in payload:
        raise ValueError(f"Unexpected REData response for {widget}/{year}")
    cache.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return payload


def flatten_redata(payload: dict[str, Any], value_scale: float = 1.0) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for series in payload["included"]:
        attributes = series.get("attributes", {})
        for value in attributes.get("values", []):
            rows.append(
                {
                    "period": value["datetime"][:7],
                    "series": attributes.get("title") or series.get("type"),
                    "value": round(float(value["value"]) * value_scale, 4),
                    "share": round(float(value.get("percentage", 0)) * 100, 4),
                }
            )
    return rows


def normalize_monthly_rows(
    rows: list[dict[str, Any]], key: str, last_complete_month: str
) -> list[dict[str, Any]]:
    """Remove aggregate/partial rows and calculate honest monthly shares."""
    complete = [row for row in rows if row["period"] <= last_complete_month]
    if key == "generation":
        # REData includes the total beside its components. Its supplied
        # percentages therefore sum to 50%; derive shares from component GWh.
        complete = [row for row in complete if row["series"] != "Generación total"]
        totals: dict[str, float] = defaultdict(float)
        for row in complete:
            totals[row["period"]] += row["value"]
        for row in complete:
            denominator = totals[row["period"]]
            row["share"] = round(row["value"] / denominator * 100, 4) if denominator else 0
    elif key == "capacity":
        complete = [row for row in complete if row["series"] != "Potencia instalada total"]
    return complete


def flatten_exchanges(
    payload: dict[str, Any], country: str, last_complete_month: str
) -> list[dict[str, Any]]:
    """Normalize REData physical flows; imports positive and exports negative."""
    rows: list[dict[str, Any]] = []
    for series in payload["included"]:
        direction = series.get("attributes", {}).get("type")
        if direction not in {"import", "export"}:
            continue
        for value in series["attributes"].get("values", []):
            period = value["datetime"][:7]
            if period <= last_complete_month:
                amount = float(value["value"]) * 0.001
                rows.append(
                    {
                        "period": period,
                        "country": country,
                        "direction": direction,
                        "value_gwh": round(amount, 4),
                    }
                )
    return rows


def fetch_omie_day(day: date) -> list[dict[str, Any]]:
    filename = f"marginalpdbc_{day:%Y%m%d}.1"
    url = f"{OMIE_DOWNLOAD}?{urllib.parse.urlencode({'filename': filename, 'parents': 'marginalpdbc'})}"
    try:
        text = fetch_bytes(url).decode("latin-1")
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return []
        raise
    rows = []
    for line in text.splitlines():
        fields = line.strip().split(";")
        if len(fields) < 7 or not fields[0].isdigit():
            continue
        year, month, day_number, period = map(int, fields[:4])
        rows.append(
            {
                "date": f"{year:04d}-{month:02d}-{day_number:02d}",
                "period": period,
                "price_es_eur_mwh": float(fields[5]),
            }
        )
    return rows


def omie_monthly(days: int, today: date) -> list[dict[str, Any]]:
    by_month: dict[str, list[float]] = defaultdict(list)
    start = today - timedelta(days=days - 1)
    current = start
    while current <= today:
        for row in fetch_omie_day(current):
            by_month[row["date"][:7]].append(row["price_es_eur_mwh"])
        current += timedelta(days=1)
    current_month = today.strftime("%Y-%m")
    return [
        {"period": month, "price_es_eur_mwh": round(sum(values) / len(values), 2), "periods": len(values)}
        for month, values in sorted(by_month.items())
        if values and month < current_month
    ]


def esios_probe(token: str) -> dict[str, Any]:
    """Validate the pinned IDs and names against the live e·sios catalogue."""
    headers = esios_headers(token)
    catalog = fetch_json(f"{ESIOS_BASE}/indicators", headers)
    available = {int(item["id"]): item.get("name", "") for item in catalog.get("indicators", [])}
    checks = []
    for key, config in ESIOS_INDICATORS.items():
        name = available.get(config["id"], "")
        expected = normalize_text(config["expected"])
        valid = bool(name) and expected in normalize_text(name)
        checks.append({"key": key, "id": config["id"], "name": name, "valid": valid})
    if not all(check["valid"] for check in checks):
        invalid = [f'{check["id"]}: {check["name"] or "missing"}' for check in checks if not check["valid"]]
        raise ValueError(f"Configured e·sios indicators failed catalogue validation: {invalid}")
    return {"geo_id": PENINSULAR_GEO_ID, "indicators": checks}


def normalize_text(value: str) -> str:
    return "".join(
        character for character in unicodedata.normalize("NFKD", value.casefold())
        if not unicodedata.combining(character)
    )


def esios_headers(token: str) -> dict[str, str]:
    return {
        "Accept": "application/json; application/vnd.esios-api-v1+json",
        "Content-Type": "application/json",
        "x-api-key": token,
    }


def esios_indicator_url(indicator_id: int, start: str, end: str) -> str:
    query = urllib.parse.urlencode(
        {
            "start_date": start,
            "end_date": end,
            "geo_ids[]": PENINSULAR_GEO_ID,
            "time_trunc": "hour",
        }
    )
    return f"{ESIOS_BASE}/indicators/{indicator_id}?{query}"


def validate_esios_metadata(key: str, indicator: dict[str, Any]) -> dict[str, Any]:
    config = ESIOS_INDICATORS[key]
    name = str(indicator.get("name", ""))
    magnitudes = [str(item.get("name", "")) for item in indicator.get("magnitud") or []]
    frequencies = [str(item.get("name", "")) for item in indicator.get("tiempo") or []]
    geos = indicator.get("geos") or []
    if int(indicator.get("id", -1)) != config["id"]:
        raise ValueError(f"e·sios {key}: unexpected indicator id")
    if normalize_text(config["expected"]) not in normalize_text(name):
        raise ValueError(f"e·sios {key}: unexpected name {name!r}")
    if ESIOS_EXPECTED_MAGNITUDE not in magnitudes:
        raise ValueError(f"e·sios {key}: expected power magnitude, got {magnitudes}")
    source_frequency = next((frequency for frequency in ESIOS_EXPECTED_SOURCE_FREQUENCIES if frequency in frequencies), None)
    if source_frequency is None:
        raise ValueError(f"e·sios {key}: unexpected source frequency {frequencies}")
    if geos and not any(int(item.get("geo_id", -1)) == PENINSULAR_GEO_ID for item in geos):
        raise ValueError(f"e·sios {key}: peninsular geography unavailable")
    return {
        "id": config["id"],
        "name": name,
        "unit": "MW",
        "source_frequency": source_frequency,
        "published_frequency": "hour",
        "geo_id": PENINSULAR_GEO_ID,
        "geo_name": next((item.get("geo_name") for item in geos if int(item.get("geo_id", -1)) == PENINSULAR_GEO_ID), "Península"),
        "values_updated_at": indicator.get("values_updated_at"),
        "available_in_query": bool(indicator.get("values")),
    }


def fetch_esios_indicator(token: str, key: str, year: int, end: str, refresh: bool) -> tuple[dict[str, float], dict[str, Any]]:
    cache = RAW / "esios" / key
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f"{year}.json"
    if path.exists() and not refresh:
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = fetch_json(
            esios_indicator_url(ESIOS_INDICATORS[key]["id"], f"{year}-01-01T00:00", end),
            esios_headers(token),
        )
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    indicator = payload.get("indicator") or {}
    metadata = validate_esios_metadata(key, indicator)
    values: dict[str, float] = {}
    for item in indicator.get("values") or []:
        if int(item.get("geo_id", -1)) != PENINSULAR_GEO_ID:
            continue
        local_timestamp = str(item.get("datetime", ""))
        if not local_timestamp:
            continue
        # REE's datetime_utc field duplicates the autumn repeated hour in some
        # historical responses. The offset-aware local value distinguishes the
        # +02:00 and +01:00 observations, so derive canonical UTC from it.
        timestamp = datetime.fromisoformat(local_timestamp).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        if timestamp in values:
            raise ValueError(f"e·sios {key}/{year}: duplicate timestamp {timestamp}")
        values[timestamp] = round(float(item["value"]), 3)
    return values, metadata


def build_esios_hourly(token: str, start_year: int, end_year: int, today: date, force: bool = False) -> dict[str, Any]:
    """Download measured hourly power and write compact, UTC-normalized yearly shards."""
    catalog = esios_probe(token)
    hourly_dir = PUBLIC / "hourly"
    hourly_dir.mkdir(parents=True, exist_ok=True)
    complete_day = today - timedelta(days=1)
    years: list[int] = []
    files: list[dict[str, Any]] = []
    indicator_metadata: dict[str, Any] = {}
    overall_start: str | None = None
    overall_end: str | None = None
    columns = ["timestamp_utc", *ESIOS_HOURLY_KEYS]

    for year in range(start_year, end_year + 1):
        if year > complete_day.year:
            continue
        end = f"{year}-12-31T23:59" if year < complete_day.year else f"{complete_day:%Y-%m-%d}T23:59"
        series: dict[str, dict[str, float]] = {}
        for key in ESIOS_HOURLY_KEYS:
            values, metadata = fetch_esios_indicator(
                token, key, year, end, refresh=force or year == complete_day.year
            )
            series[key] = values
            indicator_metadata[key] = metadata
        timestamps = sorted(set().union(*(values.keys() for values in series.values())))
        rows = [[timestamp, *[series[key].get(timestamp) for key in ESIOS_HOURLY_KEYS]] for timestamp in timestamps]
        missing = {key: sum(row[index + 1] is None for row in rows) for index, key in enumerate(ESIOS_HOURLY_KEYS)}
        shard = {
            "schema_version": 1,
            "year": year,
            "timezone": "Europe/Madrid",
            "utc_normalization": "derived_from_offset_aware_source_datetime",
            "geography": {"geo_id": PENINSULAR_GEO_ID, "name": "Península"},
            "unit": "MW",
            "columns": columns,
            "rows": rows,
            "missing_by_column": missing,
        }
        path = hourly_dir / f"{year}.json"
        path.write_text(json.dumps(shard, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        years.append(year)
        overall_start = timestamps[0] if overall_start is None else min(overall_start, timestamps[0])
        overall_end = timestamps[-1] if overall_end is None else max(overall_end, timestamps[-1])
        files.append({"year": year, "path": f"hourly/{year}.json", "sha256": sha256(path), "bytes": path.stat().st_size, "rows": len(rows), "missing_by_column": missing})

    return {
        "status": "available",
        "years": years,
        "start_utc": overall_start,
        "end_utc": overall_end,
        "columns": columns,
        "files": files,
        "catalogue": catalog,
        "indicators": indicator_metadata,
        "provisional": True,
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-year", type=int, default=2019)
    parser.add_argument("--end-year", type=int, default=datetime.now().year)
    parser.add_argument("--omie-days", type=int, default=120)
    parser.add_argument("--skip-omie", action="store_true")
    parser.add_argument("--force-esios", action="store_true")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    PUBLIC.mkdir(parents=True, exist_ok=True)
    generation: list[dict[str, Any]] = []
    demand: list[dict[str, Any]] = []
    capacity: list[dict[str, Any]] = []
    emissions: list[dict[str, Any]] = []
    exchanges: list[dict[str, Any]] = []
    storage_energy: list[dict[str, Any]] = []
    storage_capacity: list[dict[str, Any]] = []
    source_updates: dict[str, str] = {}
    today = datetime.now().date()
    last_complete_month = (today.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

    for year in range(args.start_year, args.end_year + 1):
        for key, widget in REDATA_WIDGETS.items():
            payload = red_data(widget, year, refresh=year == args.end_year)
            source_updates[key] = max(
                source_updates.get(key, ""), payload["data"]["attributes"].get("last-update", "")
            )
            rows = flatten_redata(payload, 0.001 if key in {"generation", "demand", "emissions_context"} else 1.0)
            rows = normalize_monthly_rows(rows, key, last_complete_month)
            if key == "generation":
                generation.extend(rows)
            elif key == "demand":
                demand.extend(rows)
            elif key == "capacity":
                capacity.extend(rows)
            else:
                emissions.extend(rows)

        for country, widget in REDATA_EXCHANGE_WIDGETS.items():
            payload = red_data(widget, year, refresh=year == args.end_year)
            key = f"exchange_{country.lower()}"
            source_updates[key] = max(
                source_updates.get(key, ""), payload["data"]["attributes"].get("last-update", "")
            )
            exchanges.extend(flatten_exchanges(payload, country, last_complete_month))

        for key, widget in REDATA_STORAGE_WIDGETS.items():
            payload = red_data(widget, year, refresh=year == args.end_year)
            source_updates[key] = max(
                source_updates.get(key, ""), payload["data"]["attributes"].get("last-update", "")
            )
            rows = flatten_redata(payload, 0.001 if key == "storage_energy" else 1.0)
            rows = normalize_monthly_rows(rows, key, last_complete_month)
            if key == "storage_energy":
                storage_energy.extend(rows)
            else:
                storage_capacity.extend(
                    row for row in rows if row["series"] != "Potencia instalada total"
                )

    token = os.environ.get("ESIOS_TOKEN", "").strip()
    hourly = {"status": "unavailable", "reason": "token_required", "years": []}
    if token:
        hourly = build_esios_hourly(token, args.start_year, args.end_year, today, args.force_esios)

    prices = [] if args.skip_omie else omie_monthly(args.omie_days, today)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    dashboard = {
        "schema_version": 1,
        "generated_at": generated_at,
        "geography": {"generation": "Spain national", "hourly": "Spanish peninsular system"},
        "completeness": {"monthly_through": last_complete_month, "partial_months_excluded": True},
        "generation": generation,
        "demand": demand,
        "capacity": capacity,
        "emissions_context": emissions,
        "exchanges": exchanges,
        "storage_energy": storage_energy,
        "storage_capacity": storage_capacity,
        "hourly": hourly,
        "omie_prices": prices,
        "marginal_technology": {
            "cutoff": MARGINAL_TECHNOLOGY_CUTOFF,
            "rows": [],
            "status": "historical_source_requires_import",
        },
        "sources": [
            {"key": key, "url": f"{REDATA_BASE}/{widget}", "last_update": source_updates.get(key)}
            for key, widget in REDATA_WIDGETS.items()
        ]
        + [
            {
                "key": f"exchange_{country.lower()}",
                "url": f"{REDATA_BASE}/{widget}",
                "last_update": source_updates.get(f"exchange_{country.lower()}"),
            }
            for country, widget in REDATA_EXCHANGE_WIDGETS.items()
        ]
        + [
            {"key": key, "url": f"{REDATA_BASE}/{widget}", "last_update": source_updates.get(key)}
            for key, widget in REDATA_STORAGE_WIDGETS.items()
        ]
        + [
            {
                "key": "esios",
                "url": ESIOS_BASE,
                "last_update": max(
                    (item.get("values_updated_at") or "" for item in hourly.get("indicators", {}).values()),
                    default="",
                ) or None,
            },
            {"key": "omie", "url": OMIE_DOWNLOAD, "last_update": generated_at if prices else None},
        ],
    }
    output = PUBLIC / "dashboard.json"
    output.write_text(json.dumps(dashboard, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "generated_at": generated_at,
        "dashboard": {"path": "dashboard.json", "sha256": sha256(output), "bytes": output.stat().st_size},
        "coverage": {
            "monthly_start": min((row["period"] for row in generation), default=None),
            "monthly_end": max((row["period"] for row in generation), default=None),
            "hourly_status": hourly["status"],
            "hourly_start": hourly.get("start_utc"),
            "hourly_end": hourly.get("end_utc"),
        },
        "hourly": {"files": hourly.get("files", [])},
    }
    (PUBLIC / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {output} ({output.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
