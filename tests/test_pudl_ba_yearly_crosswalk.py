import unittest
from src.c2_pudl_ba_yearly_crosswalk import analyze_codes,BAS
class Tests(unittest.TestCase):
    def test_overlap_not_exclusive_and_yearly_change(self):
        codes=[];counties=[]
        for year in range(2020,2026):
            for idx,ba in enumerate(BAS):
                ids=100+idx
                codes.append({"report_date":f"{year}-12-31",
                  "balancing_authority_code_eia":ba,"balancing_authority_id_eia":ids})
                counties.append({"report_date":f"{year}-12-31",
                  "balancing_authority_id_eia":ids,"county_id_fips":"04013" if idx in (0,3) else str(41001+idx)})
        rows,overlap,change,members,s=analyze_codes(codes,counties)
        self.assertEqual(len(rows),24)
        self.assertEqual(len(members),24)
        self.assertTrue(all(x['model_ready'] is False for x in members))
        self.assertEqual(len(overlap),36)
        self.assertEqual(len(change),20)
        self.assertEqual(s["observed_yearly_BA_county_membership_slots"],24)
        self.assertTrue(any(x["BA_a"]=="AZPS" and x["BA_b"]=="SRP" and x["county_FIPS_intersection_count"]==1 for x in overlap))
        self.assertFalse(s["geography_historically_approved"])
    def test_missing_BA_identity_is_explicit_not_inferred(self):
        rows,overlap,change,members,summary=analyze_codes([],[])
        self.assertEqual(summary["observed_annual_code_ID_mappings"],0)
        self.assertFalse(summary["model_training_permitted"])
if __name__=="__main__":unittest.main()
