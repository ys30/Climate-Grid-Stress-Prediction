"""Unit tests for coverage gate; synthetic fixtures test guards, not empirical skill."""
import csv
import tempfile
import unittest
from pathlib import Path

from scripts.c2_e2_joint_coverage_gate import audit, expected_hours, utc_hour


class CoverageGateTests(unittest.TestCase):
    def make_csv(self, rows):
        temp = tempfile.TemporaryDirectory()
        path = Path(temp.name) / "joined.csv"
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["ba", "timestamp_utc", "demand_mw", "temperature_c"])
            writer.writeheader()
            writer.writerows(rows)
        self.addCleanup(temp.cleanup)
        return path

    def test_leap_year_denominator(self):
        self.assertEqual(expected_hours(2020), 8784)
        self.assertEqual(expected_hours(2021), 8760)

    def test_utc_explicit_and_hourly(self):
        self.assertEqual(utc_hour("2020-01-01T00:00:00Z").year, 2020)
        for bad in ("2020-01-01T00:00:00", "2020-01-01T00:30:00Z",
                    "2020-01-01T00:00:00-07:00"):
            with self.assertRaises(ValueError):
                utc_hour(bad)

    def test_sparse_panel_cannot_pass(self):
        path = self.make_csv([dict(ba="CISO", timestamp_utc="2020-01-01T00:00:00Z",
                                   demand_mw="100", temperature_c="20")])
        report = audit(path, bas=("CISO",))
        self.assertFalse(report["split_eligibility"]["CISO"]["three_complete_annual_cycles"])
        self.assertFalse(report["split_eligibility"]["CISO"]["predeclared_2020_2025_split"])

    def test_duplicate_blocks_annual_pass(self):
        row = dict(ba="CISO", timestamp_utc="2020-01-01T00:00:00Z",
                   demand_mw="100", temperature_c="20")
        report = audit(self.make_csv([row, row]), bas=("CISO",))
        year = next(x for x in report["yearly"] if x["year"] == 2020)
        self.assertEqual(year["duplicate_hours"], 1)
        self.assertFalse(year["pass"])

    def test_nan_and_missing_weather_fail_closed(self):
        rows = [dict(ba="CISO", timestamp_utc="2020-01-01T00:00:00Z",
                     demand_mw="100", temperature_c="NaN")]
        report = audit(self.make_csv(rows), bas=("CISO",))
        year = next(x for x in report["yearly"] if x["year"] == 2020)
        self.assertEqual(year["invalid_joint_rows"], 1)
        self.assertEqual(year["valid_joint_hours"], 0)

    def test_missing_columns_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.csv"
            path.write_text("ba,timestamp_utc\nCISO,2020-01-01T00:00:00Z\n")
            with self.assertRaisesRegex(ValueError, "missing required columns"):
                audit(path)


if __name__ == "__main__":
    unittest.main()
