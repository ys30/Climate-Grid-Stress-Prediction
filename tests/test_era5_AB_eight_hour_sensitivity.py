import unittest
from src.c2_era5_AB_eight_hour_sensitivity import sample_summary,SAMPLE_TIMES
class TestABSeasonal(unittest.TestCase):
    def test_all_BAs_no_model_and_sign_counts(self):
        rows=[{"ba":ba,"county_minus_hifld_c":(-1)**i*(i+.5)}
          for ba in ("AZPS","BPAT","CISO","SRP") for i in range(len(SAMPLE_TIMES))]
        out=sample_summary(rows)
        self.assertEqual(len(out),4)
        self.assertTrue(all(r["N_sample_UTC_hours"]==8 for r in out))
        self.assertTrue(all(r["positive_hour_count"]==4 and r["negative_hour_count"]==4 for r in out))
        self.assertTrue(all(r["training_permitted"] is False for r in out))
    def test_incomplete_BA_observations_rejected(self):
        with self.assertRaises(ValueError):sample_summary([])
if __name__=="__main__":unittest.main()
