"""Offline contract tests of the EIA raw API collector. No network or data claims."""
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.c2_eia930_raw_api_intake import collect, save


def result(data, total=None):
    return {"response": {"data": data, "total": str(len(data) if total is None else total)}}


def item(period, value="12000", ba="CISO", kind="D"):
    return {"period": period, "value": value, "respondent": ba, "type": kind}


class RawEIAIntakeTests(unittest.TestCase):
    @patch("scripts.c2_eia930_raw_api_intake.fetch_page")
    def test_source_period_preserved_without_interval_shift(self, get_page):
        get_page.return_value = result([item("2024-01-01T00"), item("2024-01-01T01")])
        rows = collect("dummy", "CISO", "2024-01-01T00", "2024-12-31T23")
        self.assertEqual(rows[0]["source_period_utc"], "2024-01-01T00")
        self.assertNotIn("timestamp_utc", rows[0])
        self.assertEqual(len(rows), 2)

    @patch("scripts.c2_eia930_raw_api_intake.fetch_page")
    def test_duplicate_period_fails_closed(self, get_page):
        get_page.return_value = result([item("2024-01-01T00"), item("2024-01-01T00")])
        with self.assertRaisesRegex(RuntimeError, "Duplicate"):
            collect("dummy", "CISO", "2024-01-01T00", "2024-12-31T23")

    @patch("scripts.c2_eia930_raw_api_intake.fetch_page")
    def test_invalid_value_fails_closed(self, get_page):
        get_page.return_value = result([item("2024-01-01T00", "NaN")])
        with self.assertRaisesRegex(RuntimeError, "Nonfinite"):
            collect("dummy", "CISO", "2024-01-01T00", "2024-12-31T23")

    @patch("scripts.c2_eia930_raw_api_intake.fetch_page")
    def test_missing_pagination_rows_fails_closed(self, get_page):
        get_page.side_effect = [result([item("2024-01-01T00")], 2), result([], 2)]
        with self.assertRaisesRegex(RuntimeError, "Empty EIA page"):
            collect("dummy", "CISO", "2024-01-01T00", "2024-12-31T23")

    @patch("scripts.c2_eia930_raw_api_intake.fetch_page")
    def test_wrong_respondent_fails_closed(self, get_page):
        get_page.return_value = result([item("2024-01-01T00", ba="BPAT")])
        with self.assertRaisesRegex(RuntimeError, "Unexpected BA"):
            collect("dummy", "CISO", "2024-01-01T00", "2024-12-31T23")

    def test_manifest_sha_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "raw.csv"
            rows = [{"ba": "CISO", "source_period_utc": "2024-01-01T00",
                     "measurement_type": "D", "reported_demand_mw": "12000",
                     "source": "EIA API electricity/rto/region-data"}]
            manifest = save(rows, path, ba="CISO", start="2024-01-01T00", end="2024-12-31T23")
            self.assertEqual(manifest["sha256_csv"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(manifest["clock_status"], "source_label_unconverted")
            with self.assertRaises(FileExistsError):
                save(rows, path, ba="CISO", start="2024-01-01T00", end="2024-12-31T23")


if __name__ == "__main__":
    unittest.main()
