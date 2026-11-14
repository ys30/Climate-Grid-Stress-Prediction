import unittest
from src.c2_temporal_gate import evaluate

class TestTemporalGate(unittest.TestCase):
    def test_pilot_cannot_authorize_full_model(self):
        rows=[{"year":"2023","ba":ba,"valid_coverage_ratio":"1.0",
               "duplicate_keys":"0","missing_hour_keys":"0","expected_hours":"8760"} for ba in ("AZPS","BPAT","CISO","SRP")]
        r=evaluate(rows)
        self.assertFalse(r["empirical_model_training_permitted"])
        self.assertTrue(r["validation"]["admitted"])
        self.assertFalse(r["train"]["admitted"])
    def test_full_year_source_coverage_is_not_model_training_permission(self):
        rows=[{"year":str(year),"ba":ba,"valid_coverage_ratio":"1.0",
               "duplicate_keys":"0","missing_hour_keys":"0",
               "expected_hours":"8784" if year in (2020,2024) else "8760"}
              for year in range(2020,2026) for ba in ("AZPS","BPAT","CISO","SRP")]
        r=evaluate(rows)
        self.assertTrue(r["coverage_only_source_gate_passed"])
        self.assertFalse(r["historical_geography_approved"])
        self.assertFalse(r["ERA5_historical_full_panel_approved"])
        self.assertFalse(r["empirical_model_training_permitted"])
    def test_no_random_split(self):
        from src.c2_temporal_gate import SPLITS
        years=[y for vals in SPLITS.values() for y in vals]
        self.assertEqual(len(years),len(set(years)))
        self.assertLess(max(SPLITS["train"]),min(SPLITS["validation"]))
        self.assertLess(max(SPLITS["validation"]),min(SPLITS["test"]))
if __name__=="__main__":unittest.main()
