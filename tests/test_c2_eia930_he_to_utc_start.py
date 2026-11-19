"""Offline tests: official EIA-930 UTC hour-ending boundary and provenance."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_eia930_he_to_utc_start import convert, he_to_start


class ClockConversionTests(unittest.TestCase):
    def make_raw(self, records):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        path = root / "raw.csv"
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "ba", "source_period_utc", "measurement_type",
                "reported_demand_mw", "source"])
            writer.writeheader()
            for period, value in records:
                writer.writerow(dict(ba="CISO", source_period_utc=period,
                                     measurement_type="D", reported_demand_mw=value,
                                     source="EIA API electricity/rto/region-data"))
        manifest = dict(ba="CISO", source_kind="official_EIA_930_API",
                        clock_status="source_label_unconverted",
                        sha256_csv=hashlib.sha256(path.read_bytes()).hexdigest())
        path.with_suffix(".manifest.json").write_text(json.dumps(manifest))
        return path, root / "out.csv"

    def test_hour_ending_minus_one_hour(self):
        self.assertEqual(he_to_start("2024-01-01T01").isoformat(),
                         "2024-01-01T00:00:00+00:00")
        self.assertEqual(he_to_start("2025-01-01T00").isoformat(),
                         "2024-12-31T23:00:00+00:00")

    def test_reject_non_utc_or_nonhourly(self):
        for value in ["2024-01-01T01-07:00", "2024-01-01T01:30", "bad"]:
            with self.assertRaises(ValueError):
                he_to_start(value)

    def test_annual_boundary_and_original_clock_retained(self):
        raw, output = self.make_raw([
            ("2024-01-01T00", "3"),
            ("2024-01-01T01", "4"),
            ("2025-01-01T00", "5"),
        ])
        report = convert(raw, output, target_year=2024)
        self.assertEqual(report["row_count"], 2)
        with output.open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["timestamp_utc"], "2024-01-01T00:00:00Z")
        self.assertEqual(rows[1]["timestamp_utc"], "2024-12-31T23:00:00Z")
        self.assertEqual(rows[1]["original_source_he_utc"], "2025-01-01T00")

    def test_duplicate_is_rejected(self):
        raw, out = self.make_raw([("2024-01-01T01", "4"), ("2024-01-01T01", "4")])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            convert(raw, out)

    def test_raw_hash_tampering_rejected(self):
        raw, out = self.make_raw([("2024-01-01T01", "4")])
        raw.write_text(raw.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "hash"):
            convert(raw, out)

    def test_null_demand_preserved_across_hour_ending_conversion(self):
        raw, output = self.make_raw([("2024-01-01T01", "")])
        manifest = convert(raw, output, target_year=2024)
        self.assertEqual(manifest["source_null_demand_rows"], 1)
        with output.open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]["demand_mw"], "")

    def test_no_overwrite(self):
        raw, out = self.make_raw([("2024-01-01T01", "4")])
        convert(raw, out)
        with self.assertRaises(FileExistsError):
            convert(raw, out)


if __name__ == "__main__":
    unittest.main()
