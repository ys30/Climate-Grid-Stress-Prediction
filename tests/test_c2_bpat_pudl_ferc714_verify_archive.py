"""Synthetic Parquet archive tests; no claim of actual PUDL source acquisition."""
import hashlib
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from scripts.c2_bpat_pudl_ferc714_verify_archive import verify_archive
from scripts.c2_bpat_pudl_ferc714_fixed_release import RELEASE, TABLES


class TestArchiveReview(unittest.TestCase):
    def setUp(self):
        import pyarrow as pa
        import pyarrow.parquet as pq
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        pq.write_table(pa.table({
            "respondent_id_ferc714": [123],
            "respondent_name_ferc714": ["Bonneville Power Administration"],
            "respondent_id_ferc714_csv": [123],
            "respondent_id_ferc714_xbrl": [None],
            "eia_code": ["BPAT"]}), self.path / (TABLES[0]+".parquet"))
        pq.write_table(pa.table({
            "respondent_id_ferc714": [123],
            "datetime_utc": [datetime(2025, 12, 31, 12)],
            "demand_mwh": [8200.0],
            "report_date": [datetime(2025, 12, 31).date()]}),
            self.path / (TABLES[1]+".parquet"))
        self.entries = []
        for table in TABLES:
            f = self.path/(table+".parquet")
            self.entries.append({"name":f.name,"bytes":f.stat().st_size,
                                 "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
        self.write_manifest()

    def write_manifest(self, **kw):
        m = {"release":RELEASE, "source_originals":self.entries, **kw}
        (self.path/"PUDL_FERC714_BPAT_SOURCE_AUDIT_MANIFEST.json").write_text(json.dumps(m))

    def test_hash_verified_and_candidate_left_unapproved(self):
        result = verify_archive(self.path)
        self.assertEqual(len(result["source_hashes_verified"]),2)
        self.assertEqual(result["respondent_audit"]["status"],"respondent_review_required")
        self.assertFalse(result["model_training_permitted"])

    def test_reviewed_id_audits_hour_without_EIA_comparison_claim(self):
        result = verify_archive(self.path, reviewed_respondent_id=123)
        self.assertEqual(result["respondent_audit"]["hourly_rows"],{2025:1})
        self.assertFalse(result["EIA930_full_hourly_comparison_completed"])

    def test_tampered_source_rejected(self):
        with (self.path/(TABLES[1]+".parquet")).open("ab") as f:
            f.write(b"modified")
        with self.assertRaisesRegex(ValueError,"SHA mismatch"):
            verify_archive(self.path)

    def test_missing_original_rejected(self):
        (self.path/(TABLES[1]+".parquet")).unlink()
        with self.assertRaisesRegex(ValueError,"missing"):
            verify_archive(self.path)

    def test_wrong_release_rejected(self):
        self.write_manifest(release="nightly")
        with self.assertRaisesRegex(ValueError,"release"):
            verify_archive(self.path)

    def test_unreviewed_id_rejected(self):
        with self.assertRaisesRegex(ValueError,"Reviewed respondent"):
            verify_archive(self.path,reviewed_respondent_id=999)


if __name__=="__main__":
    unittest.main()
