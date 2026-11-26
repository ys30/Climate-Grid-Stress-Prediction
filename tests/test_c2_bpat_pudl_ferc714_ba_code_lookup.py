import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_bpat_pudl_ferc714_ba_code_lookup import FIELDS, inspect_rows, run, source_url

class FakeConnection:
    def __init__(self,rows):
        self.rows=rows
        self.sql=[]
    def execute(self,query):
        self.sql.append(query)
        return self
    def fetchall(self):
        return self.rows

class TestBACodeLinkage(unittest.TestCase):
    def row(self,typ="balancing_authority",code="BPAT"):
        return (123,"2025-01-01","Bonneville Power Administration",456,
                typ,456,code,"Bonneville Power Administration",None)
    def test_fixed_version_endpoints(self):
        self.assertIn("/v2026.10.0/",source_url("s3"))
        self.assertIn("/v2026.10.0/",source_url("https"))
        with self.assertRaises(ValueError):source_url("nightly")
    def test_bpat_derived_linkage_marked_not_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn=FakeConnection([self.row()])
            result=run(Path(tmp)/"result",connector=conn)
            self.assertEqual(result["status"],"PUDL_DERIVED_BPAT_LINKAGE_CANDIDATE")
            self.assertEqual(result["candidate_respondent_ids"],["123"])
            self.assertFalse(result["respondent_identity_independently_approved"])
            self.assertFalse(result["hourly_load_verified"])
            self.assertIn("out_ferc714__summarized_demand",conn.sql[-1])
            self.assertIn("balancing_authority_code_eia='BPAT'",conn.sql[-1])
            self.assertTrue((Path(tmp)/"result"/"PUDL_BPAT_FERC714_YEARLY_RESPONDENT_LINKS.csv").is_file())
    def test_wrong_category_not_promoted(self):
        with self.assertRaisesRegex(ValueError,"non-BA"):
            inspect_rows([self.row(typ="utility")])
    def test_no_matching_identity_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"No BPAT"):
            inspect_rows([self.row(code="CISO")])
    def test_failure_keeps_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"result"
            with self.assertRaisesRegex(ValueError,"No BPAT"):
                run(path,connector=FakeConnection([]))
            data=json.loads((path/"PUDL_FERC714_BPAT_CURATED_IDENTITY_PROVENANCE.json").read_text())
            self.assertEqual(data["status"],"QUERY_FAILED")
            self.assertEqual(data["error_stage"],"remote_identity_query")
            self.assertFalse(data["model_training_permitted"])
    def test_duplicate_respondent_year_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate respondent-year"):
            inspect_rows([self.row(),self.row()])
    def test_2026_outside_target_rejected(self):
        row=list(self.row());row[1]="2026-01-01"
        with self.assertRaisesRegex(ValueError,"outside 2020-2025"):
            inspect_rows([tuple(row)])
    def test_malformed_result_shape_rejected(self):
        with self.assertRaisesRegex(ValueError,"schema width"):
            inspect_rows([self.row()[:-1]])
    def test_missing_2020_2024_not_silently_backfilled(self):
        x=inspect_rows([self.row()])
        self.assertEqual(len(x),1)
        self.assertEqual(x[0]["report_date"],"2025-01-01")
    def test_output_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"result"
            path.mkdir()
            with self.assertRaises(FileExistsError):
                run(path,connector=FakeConnection([self.row()]))

if __name__=="__main__":
    unittest.main()
