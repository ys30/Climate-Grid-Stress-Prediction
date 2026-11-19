"""EIA-only annual completeness gate contract checks; fixtures are synthetic."""
import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.c2_eia930_year_coverage_gate import audit_file


class YearCoverageTests(unittest.TestCase):
    def fixture(self, *, year=2024, missing=0, corrupt_he=False):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        p = Path(temp.name) / "eia.csv"
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
        with p.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "ba", "timestamp_utc", "demand_mw", "original_source_he_utc"])
            writer.writeheader()
            time = start
            while time < end - timedelta(hours=missing):
                source_he = time + timedelta(hours=1)
                if corrupt_he and time == start:
                    source_he += timedelta(hours=1)
                writer.writerow({
                    "ba": "CISO",
                    "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "demand_mw": "1000",
                    "original_source_he_utc": source_he.strftime("%Y-%m-%dT%H")
                })
                time += timedelta(hours=1)
        m = {"source_kind": "derived_from_official_EIA_930_API",
             "target_year": year, "clock_conversion": "UTC_hour_ending_minus_one_hour",
             "sha256_csv": hashlib.sha256(p.read_bytes()).hexdigest()}
        p.with_suffix(".manifest.json").write_text(json.dumps(m))
        return p

    def test_full_leap_year_passes(self):
        report = audit_file(self.fixture(), year=2024, ba="CISO")
        self.assertTrue(report["pass"])
        self.assertEqual(report["expected_hours"], 8784)
        self.assertEqual(report["missing_hours"], 0)

    def test_missing_hours_reported_without_imputation(self):
        report = audit_file(self.fixture(missing=200), year=2024, ba="CISO")
        self.assertFalse(report["pass"])
        self.assertEqual(report["missing_hours"], 200)

    def test_hour_ending_mismatch_blocks_even_full_coverage(self):
        report = audit_file(self.fixture(corrupt_he=True), year=2024, ba="CISO")
        self.assertFalse(report["pass"])
        self.assertEqual(report["source_he_mismatch_rows"], 1)

    def test_wrong_year_fails_manifest_gate(self):
        with self.assertRaisesRegex(ValueError, "target year"):
            audit_file(self.fixture(), year=2023, ba="CISO")

    def test_tampering_fails_hash_gate(self):
        p = self.fixture()
        with p.open("a") as f:
            f.write("\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            audit_file(p, year=2024, ba="CISO")

    def test_null_demand_is_not_counted_as_valid_coverage(self):
        path = self.fixture(year=2024)
        rows = list(csv.DictReader(path.open(newline="")))
        rows[0]["demand_mw"] = ""
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        manifest_path = path.with_suffix(".manifest.json")
        manifest = json.loads(manifest_path.read_text())
        manifest["sha256_csv"] = hashlib.sha256(path.read_bytes()).hexdigest()
        manifest_path.write_text(json.dumps(manifest))
        report = audit_file(path, year=2024, ba="CISO")
        self.assertFalse(report["pass"])
        self.assertEqual(report["missing_demand_rows"], 1)
        self.assertEqual(report["valid_demand_hours"], 8783)
        self.assertEqual(report["source_hour_coverage"], 1.0)
        self.assertLess(report["coverage"], 1.0)

    def test_ordinary_year_8760(self):
        report = audit_file(self.fixture(year=2023), year=2023, ba="CISO")
        self.assertEqual(report["expected_hours"], 8760)
        self.assertTrue(report["pass"])


if __name__ == "__main__":
    unittest.main()
