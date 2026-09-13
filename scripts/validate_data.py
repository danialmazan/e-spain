#!/usr/bin/env python3
"""Fail fast when a generated public dataset is incomplete or misleading."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "frontend" / "public" / "data" / "dashboard.json"


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema_version") != 1:
        errors.append("unsupported schema_version")
    generation = payload.get("generation", [])
    if not generation:
        errors.append("generation is empty")
    if any(row.get("period", "") < "2019-01" for row in generation):
        errors.append("generation predates configured coverage")
    last_complete_month = (datetime.now().date().replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    if any(row.get("period", "") > last_complete_month for row in generation):
        errors.append("generation contains an incomplete month")
    seen = set()
    for row in generation:
        key = (row.get("period"), row.get("series"))
        if key in seen:
            errors.append(f"duplicate generation row: {key}")
            break
        seen.add(key)
        if row.get("value", 0) < 0:
            errors.append(f"negative generation: {key}")
    shares_by_month: dict[str, float] = {}
    for row in generation:
        shares_by_month[row["period"]] = shares_by_month.get(row["period"], 0) + row["share"]
    if any(abs(total - 100) > 0.05 for total in shares_by_month.values()):
        errors.append("generation percentages do not sum to 100%")
    cutoff = payload.get("marginal_technology", {}).get("cutoff", "")
    for row in payload.get("marginal_technology", {}).get("rows", []):
        if row.get("timestamp", "") > cutoff:
            errors.append("marginal technology extends beyond source cutoff")
            break
    if payload.get("hourly", {}).get("status") == "unavailable" and payload.get("hourly", {}).get("years"):
        errors.append("unavailable hourly module contains data")
    exchange_seen = set()
    for row in payload.get("exchanges", []):
        key = (row.get("period"), row.get("country"), row.get("direction"))
        if key in exchange_seen:
            errors.append(f"duplicate exchange row: {key}")
            break
        exchange_seen.add(key)
        if row.get("direction") == "import" and row.get("value_gwh", 0) < 0:
            errors.append(f"negative import: {key}")
        if row.get("direction") == "export" and row.get("value_gwh", 0) > 0:
            errors.append(f"positive export: {key}")
    return errors


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Validated {len(payload['generation']):,} generation rows from real sources")


if __name__ == "__main__":
    main()
