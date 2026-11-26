"""Synthetic source rows; no actual FERC-714 data fetched in this test module."""
import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from scripts.c2_bpat_ferc714_21_real_core_hour_export import export,uri,normalize_row

class FakeConnection:
    def __init__(self,rows):
        self.rows=rows
        self.done=False
        self.queries=[]
    def execute(self,sql):
        self.queries.append(sql)
        return self
    def fetchmany(self,n):
        if self.done:
            return []
        self.done=True
        return self.rows

class TestCoreHourlyExport(unittest.TestCase):
    def test_fixed_source_is_unimputed_core(self):
        self.assertIn("/v2026.10.0/",uri("https"))
        self.assertIn("core_ferc714__",uri("s3"))
        self.assertNotIn("out_ferc714",uri("https"))

    def test_unapproved_transport_rejected(self):
        with self.assertRaisesRegex(ValueError,"approved"):
            uri("nightly")

    def test_export_source_only_with_missing_and_spillover(self):
        rows=[(21,"2025-12-31",datetime(2026,1,1,tzinfo=timezone.utc),1300.0),
              (21,"2025-01-01",datetime(2025,1,1,1,tzinfo=timezone.utc),None)]
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"out"
            evidence=export(target,connector=FakeConnection(rows))
            self.assertEqual(evidence["rows"],2)
            self.assertEqual(evidence["utc_year_spillover_by_report_year"][2025],1)
            self.assertEqual(evidence["missing_demand_by_report_year"][2025],1)
            self.assertFalse(evidence["full_original_parquet_sha_verified"])
            self.assertFalse(evidence["model_training_permitted"])
            self.assertTrue((target/"PUDL_FERC714_BPA_RESPONDENT21_2020_2025_CORE_HOURLY.csv").exists())

    def test_duplicate_utc_even_across_report_years_fails(self):
        rows=[(21,"2024-12-31",datetime(2025,1,1),200.),
              (21,"2025-01-01",datetime(2025,1,1),300.)]
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"Duplicate"):
                export(Path(temp)/"out",connector=FakeConnection(rows))

    def test_wrong_respondent_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unexpected respondent"):
            normalize_row((122,"2025-01-01",datetime(2025,1,1),10.))

    def test_utc_offset_converted_before_storing(self):
        row=normalize_row((21,"2025-01-01",datetime(2024,12,31,16,
                          tzinfo=timezone(timedelta(hours=-8))),10.))
        self.assertEqual(row[2],"2025-01-01T00:00:00+00:00")

    def test_empty_source_fails_and_writes_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"out"
            with self.assertRaisesRegex(ValueError,"No real respondent"):
                export(target,connector=FakeConnection([]))
            data=json.loads((target/"PUDL_FERC714_BPA21_CORE_HOURLY_SOURCE_PROVENANCE.json").read_text())
            self.assertEqual(data["status"],"FAILED")

    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/"out"
            target.mkdir()
            with self.assertRaises(FileExistsError):
                export(target,connector=FakeConnection([]))

if __name__=="__main__":
    unittest.main()
