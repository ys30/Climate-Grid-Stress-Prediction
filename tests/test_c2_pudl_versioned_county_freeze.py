import unittest
from src.c2_pudl_versioned_county_freeze import build_new_crosswalk,compare_source,BAS,YEARS
class TestVersionedSource(unittest.TestCase):
    def test_new_source_same_county_membership(self):
        ids={"AZPS":"803","BPAT":"1738","CISO":"2775","SRP":"16572"}
        code=[{"report_date":f"{year}-01-01","balancing_authority_code_eia":ba,
              "balancing_authority_id_eia":ids[ba]} for year in YEARS for ba in BAS]
        counties=[{"report_date":f"{year}-01-01","balancing_authority_id_eia":ids[ba],
                   "county_id_fips":4013} for year in YEARS for ba in BAS]
        m,new_ids=build_new_crosswalk(code,counties)
        self.assertEqual(len(m),24)
        self.assertEqual(m[(2020,"AZPS")],{"04013"})
        diff=compare_source(m,new_ids,m,new_ids)
        self.assertTrue(all(x["identical_county_membership"] for x in diff))
    def test_fail_if_BA_ID_missing(self):
        with self.assertRaises(ValueError):build_new_crosswalk([],[])
if __name__=="__main__":unittest.main()
