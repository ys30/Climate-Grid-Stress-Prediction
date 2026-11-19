"""Synthetic fixture tests only; empirical scores are in a separate SHA-pinned report."""
import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.c2_e2_real_demand_lag_baselines import calculate


class DemandLagBaselineTests(unittest.TestCase):
    def make_year(self, year=2024, *, omit_last=False, alter_hash=False):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        csv_path = Path(folder.name) / "hourly.csv"
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "ba", "timestamp_utc", "demand_mw", "original_source_he_utc"])
            writer.writeheader()
            hour = start
            while hour < end - timedelta(hours=int(omit_last)):
                writer.writerow({
                    "ba": "CISO",
                    "timestamp_utc": hour.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "demand_mw": "1000",
                    "original_source_he_utc":
                        (hour + timedelta(hours=1)).strftime("%Y-%m-%dT%H"),
                })
                hour += timedelta(hours=1)
        manifest = {
            "sha256_csv": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
            "source_kind": "derived_from_official_EIA_930_API",
            "clock_conversion": "UTC_hour_ending_minus_one_hour",
            "target_year": year,
        }
        csv_path.with_suffix(".manifest.json").write_text(json.dumps(manifest))
        if alter_hash:
            csv_path.write_bytes(csv_path.read_bytes() + b"\n")
        return csv_path

    def test_full_2024_identical_targets(self):
        r = calculate(self.make_year(), ba="CISO", year=2024)
        self.assertEqual(r["expected_source_hours"], 8784)
        self.assertEqual(r["matched_target_hours"], 8616)
        self.assertEqual(r["baselines"]["lag24"]["mae_mw"], 0)
        self.assertEqual(r["baselines"]["lag168"]["rmse_mw"], 0)

    def test_2023_year_has_8592_common_targets(self):
        r = calculate(self.make_year(2023), ba="CISO", year=2023)
        self.assertEqual(r["matched_target_hours"], 8760 - 168)

    def test_missing_hour_is_not_imputed(self):
        with self.assertRaisesRegex(ValueError, "Complete real UTC-year"):
            calculate(self.make_year(omit_last=True), ba="CISO", year=2024)

    def test_bad_provenance_hash_fails(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            calculate(self.make_year(alter_hash=True), ba="CISO", year=2024)


if __name__ == "__main__":
    unittest.main()
