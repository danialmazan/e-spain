import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    path = ROOT / "scripts" / name
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class IngestionTests(unittest.TestCase):
    def test_flatten_redata_preserves_source_values(self):
        module = load_script("ingest_sources.py")
        payload = {"included": [{"type": "Eólica", "attributes": {"title": "Eólica", "values": [
            {"datetime": "2025-01-01T00:00:00+01:00", "value": 1000, "percentage": 0.25}
        ]}}]}
        self.assertEqual(module.flatten_redata(payload, 0.001), [
            {"period": "2025-01", "series": "Eólica", "value": 1.0, "share": 25.0}
        ])

    def test_generation_total_is_excluded_and_shares_are_recomputed(self):
        module = load_script("ingest_sources.py")
        rows = [
            {"period": "2025-01", "series": "Eólica", "value": 30.0, "share": 15.0},
            {"period": "2025-01", "series": "Solar fotovoltaica", "value": 20.0, "share": 10.0},
            {"period": "2025-01", "series": "Generación total", "value": 50.0, "share": 100.0},
            {"period": "2025-02", "series": "Eólica", "value": 1.0, "share": 100.0},
        ]
        normalized = module.normalize_monthly_rows(rows, "generation", "2025-01")
        self.assertEqual(len(normalized), 2)
        self.assertAlmostEqual(sum(row["share"] for row in normalized), 100.0)

    def test_physical_exchange_signs_are_preserved(self):
        module = load_script("ingest_sources.py")
        payload = {"included": [
            {"attributes": {"type": "import", "values": [{"datetime": "2025-01-01", "value": 1250}]}},
            {"attributes": {"type": "export", "values": [{"datetime": "2025-01-01", "value": -750}]}},
            {"attributes": {"type": "saldo", "values": [{"datetime": "2025-01-01", "value": 500}]}},
        ]}
        rows = module.flatten_exchanges(payload, "France", "2025-01")
        self.assertEqual([row["value_gwh"] for row in rows], [1.25, -0.75])

    def test_dst_repeated_hour_offsets_map_to_distinct_utc_instants(self):
        from datetime import datetime, timezone
        first = datetime.fromisoformat("2019-10-27T02:00:00.000+02:00").astimezone(timezone.utc)
        second = datetime.fromisoformat("2019-10-27T02:00:00.000+01:00").astimezone(timezone.utc)
        self.assertEqual(first.isoformat(), "2019-10-27T00:00:00+00:00")
        self.assertEqual(second.isoformat(), "2019-10-27T01:00:00+00:00")

    def test_validator_rejects_post_cutoff_marginal_classification(self):
        module = load_script("validate_data.py")
        payload = {"schema_version": 1, "generation": [{"period": "2019-01", "series": "Eólica", "value": 1, "share": 100}], "hourly": {"status": "unavailable", "years": []}, "marginal_technology": {"cutoff": "2025-03-18T23:00:00+01:00", "rows": [{"timestamp": "2025-03-19T00:00:00+01:00"}]}}
        self.assertIn("marginal technology extends beyond source cutoff", module.validate(payload))

    def test_hourly_validator_rejects_duplicate_utc_intervals(self):
        module = load_script("validate_data.py")
        shard = {"year": 2025, "columns": ["timestamp_utc", "demand"], "rows": [["2025-01-01T00:00:00Z", 10], ["2025-01-01T00:00:00Z", 11]], "missing_by_column": {"demand": 0}}
        self.assertIn("hourly shard contains duplicate UTC timestamps", module.validate_hourly_shard(shard))


if __name__ == "__main__":
    unittest.main()
