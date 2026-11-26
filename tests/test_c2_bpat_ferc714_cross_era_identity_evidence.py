import unittest
from scripts.c2_bpat_ferc714_cross_era_identity_evidence import (
    git_blob,parse_rows,reconcile,LEGACY_FIELDS,PUDL_FIELDS,audit,
)

class TestCrossEraIdentity(unittest.TestCase):
    def setUp(self):
        self.legacy=[dict(zip(LEGACY_FIELDS,["122","Bonneville Power Administration, USDOE","1738","WECC"]))]
        self.pudl=[dict(zip(PUDL_FIELDS,["21","C002357","122","Migration files and manually confirmed",""]))]

    def test_real_source_mapping_fields_yield_historical_identity(self):
        r=reconcile(self.legacy,self.pudl)
        self.assertEqual(r["pudl_respondent_id_ferc714"],21)
        self.assertEqual(r["ferc714_xbrl_respondent_id"],"C002357")
        self.assertEqual(r["eia_numeric_id"],1738)
        self.assertFalse(r["2020_2025_hourly_FERC714_available_verified"])
        self.assertFalse(r["pudl_2026_10_core_respondent_metadata_verified"])

    def test_legacy_identity_missing_fails_closed(self):
        self.legacy[0]["respondent_id"]="999"
        with self.assertRaisesRegex(ValueError,"historical"):reconcile(self.legacy,self.pudl)

    def test_legacy_EIA_numeric_id_mismatch_fails_closed(self):
        self.legacy[0]["eia_code"]="BPAT"
        with self.assertRaisesRegex(ValueError,"historical"):reconcile(self.legacy,self.pudl)

    def test_crosswalk_xbrl_mismatch_fails_closed(self):
        self.pudl[0]["respondent_id_ferc714_xbrl"]="C999999"
        with self.assertRaisesRegex(ValueError,"cross-era"):reconcile(self.legacy,self.pudl)

    def test_crosswalk_not_unique_fails_closed(self):
        self.pudl.append(self.pudl[0].copy())
        with self.assertRaisesRegex(ValueError,"zero or multiple"):reconcile(self.legacy,self.pudl)

    def test_raw_file_git_hash_known_vector(self):
        self.assertEqual(git_blob(b"hello"),"b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0")

    def test_unpinned_input_refused_before_parse(self):
        with self.assertRaisesRegex(ValueError,"source Git blob"):
            audit(b"respondent_id,respondent_name,eia_code,nerc\n",b"fake")

    def test_header_schema_exact(self):
        data=b"respondent_id,respondent_name,eia_code,nerc\n122,Bonneville,1738,WECC\n"
        r=parse_rows(data,LEGACY_FIELDS)
        self.assertEqual(len(r),1)
        with self.assertRaisesRegex(ValueError,"headers"):
            parse_rows(data,PUDL_FIELDS)

if __name__=="__main__":unittest.main()
