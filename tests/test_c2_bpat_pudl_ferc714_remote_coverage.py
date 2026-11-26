"""No network: assert fixed-release DuckDB source candidate / hour admission."""
import csv
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.c2_bpat_pudl_ferc714_remote_coverage import run, VERSION


class FakeConn:
    def __init__(self, respondents, coverage=None):
        self.respondents=respondents
        self.coverage=coverage or []
        self.sqls=[]
    def execute(self, sql, params=None):
        self.sqls.append((sql,params))
        self.last=sql
        return self
    def fetchall(self):
        return self.coverage if "count(DISTINCT" in self.last else self.respondents


class TestRemoteCoverage(unittest.TestCase):
    def candidate(self, respondent_id=55):
        return (respondent_id,"Bonneville Power Administration",321,"xbrl-55","BPAT")

    def mocked(self, conn):
        return patch.dict(sys.modules,{"duckdb":types.SimpleNamespace(connect=lambda:conn)})

    def test_candidate_only_requires_review_and_never_claims_source_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            conn=FakeConn([self.candidate()])
            with self.mocked(conn):
                result=run(Path(temp)/"out")
            self.assertEqual(result["release"],VERSION)
            self.assertEqual(result["status"],"RESPONDENT_REVIEW_REQUIRED")
            self.assertFalse(result["full_original_parquet_bytes_downloaded"])
            self.assertFalse(result["original_parquet_sha256_verified"])
            self.assertFalse(result["respondent_identity_approved"])
            self.assertFalse(result["model_training_permitted"])
            self.assertFalse(result["EIA930_comparison_completed"])
            self.assertTrue(any("URL_STYLE 'path'" in q for q,_ in conn.sqls))
            self.assertTrue((Path(temp)/"out"/"BPA_FERC714_RESPONDENT_CANDIDATES.csv").is_file())

    def test_unknown_reviewed_id_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.mocked(FakeConn([self.candidate()])):
                with self.assertRaisesRegex(ValueError,"absent"):
                    run(Path(temp)/"out",reviewed_respondent_id=999)

    def test_coverage_output_not_identity_certification(self):
        with tempfile.TemporaryDirectory() as temp:
            conn=FakeConn([self.candidate()],[(2025,8760,8760,2,"2025-01-01","2025-12-31")])
            with self.mocked(conn):
                result=run(Path(temp)/"out",reviewed_respondent_id=55)
            self.assertEqual(result["status"],"SOURCE_COVERAGE_CANDIDATE_NOT_IDENTITY_CERTIFIED")
            self.assertEqual(len(result["hourly_coverage"]),1)
            self.assertFalse(result["respondent_identity_approved"])
            self.assertFalse(result["EIA930_comparison_completed"])
            self.assertEqual(conn.sqls[-1][1],[55])

    def test_duplicate_candidate_identity_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.mocked(FakeConn([self.candidate(),self.candidate()])):
                with self.assertRaisesRegex(ValueError,"Nonunique"):
                    run(Path(temp)/"out")

    def test_https_public_fixed_version_uses_range_url_not_s3_secret(self):
        with tempfile.TemporaryDirectory() as temp:
            conn=FakeConn([self.candidate()])
            with self.mocked(conn):
                result=run(Path(temp)/"https-output",transport="https")
            self.assertEqual(result["transport"],"https")
            self.assertIn("/v2026.10.0/",result["respondent_uri"])
            self.assertTrue(result["respondent_uri"].startswith("https://s3.us-west-2.amazonaws.com/"))
            self.assertFalse(any("CREATE SECRET" in sql for sql,_ in conn.sqls))
            self.assertTrue(any("read_parquet('https://" in sql for sql,_ in conn.sqls))

    def test_transport_outside_fixed_release_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError,"Only fixed-release"):
                run(Path(temp)/"invalid",transport="nightly")

    def test_output_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"out"
            path.mkdir()
            with self.assertRaises(FileExistsError):
                run(path)


if __name__=="__main__":
    unittest.main()
