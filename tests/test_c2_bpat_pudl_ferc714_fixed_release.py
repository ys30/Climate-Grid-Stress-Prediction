"""Synthetic contract tests only; official PUDL Parquet not acquired by tests."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.c2_bpat_pudl_ferc714_fixed_release import BASE, RELEASE, NAME, TABLES, download, audit

class TestFixedFERC714(unittest.TestCase):
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
