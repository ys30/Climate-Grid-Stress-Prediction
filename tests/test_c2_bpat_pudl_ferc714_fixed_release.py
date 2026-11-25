"""Synthetic contract tests only; official PUDL Parquet not acquired by tests."""
import json
import tempfile
from datetime import datetime, timedelta, timezone
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.c2_bpat_pudl_ferc714_fixed_release import BASE, RELEASE, NAME, TABLES, download, audit, normalize_utc

class TestFixedFERC714(unittest.TestCase):
    def test_offset_aware_utc_conversion_not_timezone_stripping(self):
        local = datetime(2025, 12, 31, 4, 0,
                         tzinfo=timezone(timedelta(hours=-8)))
        self.assertEqual(normalize_utc(local), datetime(2025, 12, 31, 12, 0))

    def test_utc_naive_hour_kept_as_utc(self):
        hour = datetime(2025, 12, 31, 12, 0)
        self.assertEqual(normalize_utc(hour), hour)

    def test_non_hourly_timestamp_rejected(self):
        with self.assertRaisesRegex(ValueError, "Non-hourly"):
            normalize_utc(datetime(2025, 12, 31, 12, 30))

    def test_invalid_time_type_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid FERC datetime"):
            normalize_utc("2025-12-31T12:00")

    def test_immutable_version_path_not_nightly(self):
        self.assertIn("/v2026.10.0/", BASE)
        self.assertNotIn("/nightly/", BASE)
        self.assertEqual(RELEASE, "v2026.10.0")

    def test_operator_name_aliases(self):
        self.assertIsNotNone(NAME.search("Bonneville Power Administration"))
        self.assertIsNotNone(NAME.search("BPA Balancing Authority"))
        self.assertIsNone(NAME.search("Other Regional Utility"))

    def test_unapproved_table_rejected_without_network(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"Unapproved"):
                download("out_ferc714__hourly_planning_area_demand",Path(temp))

    def test_unpinned_existing_filename_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"core_ferc714__respondent_id.parquet"
            path.write_bytes(b"previous-data")
            with self.assertRaises(FileExistsError):
                download("core_ferc714__respondent_id",Path(temp))
            self.assertEqual(path.read_bytes(),b"previous-data")

    def test_review_gate_without_external_parquet(self):
        """The no-review mode must never assert BPAT series availability.
        Actual schema and value tests run only when source Parquet is acquired.
        """
        self.assertEqual(len(TABLES),2)
        self.assertIn("core_ferc714__hourly_planning_area_demand",TABLES)

if __name__=="__main__":
    unittest.main()
