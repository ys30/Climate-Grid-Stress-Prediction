"""Offline tests of provenance-gated EIA–weather hourly joins, not empirical data."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_eia_era5_provenance_join import join


class ProvenanceJoinTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write_source(self, name, columns, rows, manifest):
        p = self.root / (name + ".csv")
        with p.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=columns)
            w.writeheader()
            w.writerows(rows)
        manifest["sha256_csv"] = hashlib.sha256(p.read_bytes()).hexdigest()
        p.with_suffix(".manifest.json").write_text(json.dumps(manifest))
        return p

    def inputs(self, *, weather_hour="2024-01-01T00:00:00Z", weather_method="single_gridcell"):
        eia = self.write_source("eia",
            ["ba", "timestamp_utc", "demand_mw", "original_source_he_utc"],
            [{"ba": "CISO", "timestamp_utc": "2024-01-01T00:00:00Z",
              "demand_mw": "1000", "original_source_he_utc": "2024-01-01T01"}],
            {"source_kind": "derived_from_official_EIA_930_API", "target_year": 2024,
             "clock_conversion": "UTC_hour_ending_minus_one_hour"})
        weather = self.write_source("weather",
            ["ba", "timestamp_utc", "temperature_c"],
            [{"ba": "CISO", "timestamp_utc": weather_hour, "temperature_c": "12.5"}],
            {"source_kind": "ERA5_BA_geographic_proxy",
             "retrieval_timestamp_utc": "2026-11-18T00:00:00Z",
             "era5_dataset": "ERA5 single levels", "era5_variables": ["2m_temperature"],
             "spatial_method": weather_method, "geometry_source": "documented_grid_cell_id",
             "time_reference": "UTC_interval_start",
             "is_measured_county_load_weighted": False})
        return eia, weather

    def test_exact_match_preserves_source_hashes(self):
        eia, weather = self.inputs()
        out = self.root / "joined.csv"
        r = join(eia, weather, out, ba="CISO", year=2024)
        self.assertEqual(r["shared_hours"], 1)
        self.assertEqual(r["unmatched_eia_hours"], 0)
        self.assertTrue(out.exists())
        self.assertEqual(json.loads(out.with_suffix(".manifest.json").read_text())["source_kind"],
                         "EIA930_ERA5_BA_proxy_joint")

    def test_source_null_demand_is_dropped_not_interpolated(self):
        eia, weather = self.inputs()
        with eia.open("a", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "ba", "timestamp_utc", "demand_mw", "original_source_he_utc"])
            writer.writerow({"ba": "CISO", "timestamp_utc": "2024-01-01T01:00:00Z",
                             "demand_mw": "", "original_source_he_utc": "2024-01-01T02"})
        manifest_path = eia.with_suffix(".manifest.json")
        manifest = json.loads(manifest_path.read_text())
        manifest["sha256_csv"] = hashlib.sha256(eia.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        outcome = join(eia, weather, self.root / "joined.csv", ba="CISO", year=2024)
        self.assertEqual(outcome["source_null_demand_hours_excluded"], 1)
        self.assertEqual(outcome["shared_hours"], 1)

    def test_reject_duplicate_hour_even_when_first_eia_row_is_null(self):
        eia, weather = self.inputs()
        with eia.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["ba", "timestamp_utc", "demand_mw", "original_source_he_utc"])
            w.writerow({"ba": "CISO", "timestamp_utc": "2024-01-01T00:00:00Z",
                        "demand_mw": "", "original_source_he_utc": "2024-01-01T01"})
        manifest_path = eia.with_suffix(".manifest.json")
        m = json.loads(manifest_path.read_text())
        m["sha256_csv"] = hashlib.sha256(eia.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, "duplicate EIA hour"):
            join(eia, weather, self.root / "joined.csv", ba="CISO", year=2024)

    def test_nonoverlap_fails(self):
        eia, weather = self.inputs(weather_hour="2024-01-01T02:00:00Z")
        with self.assertRaisesRegex(ValueError, "No overlapping"):
            join(eia, weather, self.root / "joined.csv", ba="CISO", year=2024)

    def test_reject_unvalidated_load_weighting(self):
        eia, weather = self.inputs(weather_method="population_weighted")
        with self.assertRaisesRegex(ValueError, "geography-only"):
            join(eia, weather, self.root / "joined.csv", ba="CISO", year=2024)

    def test_reject_weather_hash_tampering(self):
        eia, weather = self.inputs()
        with weather.open("a") as f:
            f.write("\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            join(eia, weather, self.root / "joined.csv", ba="CISO", year=2024)

    def test_refuse_existing_output(self):
        eia, weather = self.inputs()
        out = self.root / "joined.csv"
        out.write_text("existing")
        with self.assertRaises(FileExistsError):
            join(eia, weather, out, ba="CISO", year=2024)


if __name__ == "__main__":
    unittest.main()
