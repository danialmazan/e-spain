#!/usr/bin/env python3
"""Fail fast when a generated public dataset is incomplete or misleading."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "frontend" / "public" / "data" / "dashboard.json"
PUBLIC = DATA.parent


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_hourly_shard(shard: dict) -> list[str]:
    errors: list[str] = []
    columns = shard.get("columns", [])
    rows = shard.get("rows", [])
    if not columns or columns[0] != "timestamp_utc" or "demand" not in columns:
        return ["hourly shard has invalid columns"]
    timestamps = [row[0] for row in rows]
    if len(timestamps) != len(set(timestamps)):
        errors.append("hourly shard contains duplicate UTC timestamps")
    parsed = [datetime.fromisoformat(value.replace("Z", "+00:00")) for value in timestamps]
    if any(right - left != timedelta(hours=1) for left, right in zip(parsed, parsed[1:])):
        errors.append("hourly shard has missing or non-hourly UTC intervals")
    expected_missing = {}
    for index, key in enumerate(columns[1:], start=1):
        expected_missing[key] = sum(row[index] is None for row in rows)
        if any(row[index] is not None and not isinstance(row[index], (int, float)) for row in rows):
            errors.append(f"hourly shard contains non-numeric {key}")
    if expected_missing != shard.get("missing_by_column"):
        errors.append("hourly shard missing counts do not reconcile")
    demand_index = columns.index("demand")
    if any(row[demand_index] is not None and row[demand_index] < 0 for row in rows):
        errors.append("hourly shard contains negative demand")
    local_counts: dict[str, int] = {}
    madrid = ZoneInfo("Europe/Madrid")
    for timestamp in parsed:
        day = timestamp.astimezone(madrid).date().isoformat()
        local_counts[day] = local_counts.get(day, 0) + 1
    year = shard.get("year")
    if len(rows) >= 8700 and (23 not in local_counts.values() or 25 not in local_counts.values()):
        errors.append(f"hourly shard {year} does not preserve both DST transition days")
    return errors


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
    if payload.get("hourly", {}).get("status") == "available":
        files = payload.get("hourly", {}).get("files", [])
        if [item.get("year") for item in files] != payload.get("hourly", {}).get("years"):
            errors.append("hourly years do not match shard manifest")
        for item in files:
            path = PUBLIC / item.get("path", "")
            if not path.is_file():
                errors.append(f"hourly shard missing: {path.name}")
                continue
            if path.stat().st_size != item.get("bytes") or file_sha256(path) != item.get("sha256"):
                errors.append(f"hourly shard checksum mismatch: {path.name}")
                continue
            shard = json.loads(path.read_text(encoding="utf-8"))
            errors.extend(f"{path.name}: {error}" for error in validate_hourly_shard(shard))
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
    hourly_rows = sum(item.get("rows", 0) for item in payload.get("hourly", {}).get("files", []))
    print(f"Validated {len(payload['generation']):,} monthly generation rows and {hourly_rows:,} measured hourly intervals from real sources")


if __name__ == "__main__":
    main()
