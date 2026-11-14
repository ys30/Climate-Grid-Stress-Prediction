import unittest
from src.c2_census_vs_hifld_era5 import make_proxy_weights,difference
class Tests(unittest.TestCase):
    def test_model_not_admitted_and_difference_sign(self):
        a=[{"ba":ba,"weighted_temperature_celsius":25,"grid_cells":10} for ba in ("AZPS","BPAT","CISO","SRP")]
        b=[{"ba":ba,"weighted_temperature_celsius":26,"grid_cells":20} for ba in ("AZPS","BPAT","CISO","SRP")]
        d=difference(a,b)
        self.assertEqual(len(d),4)
        self.assertTrue(all(x["county_minus_hifld_c"]==1 for x in d))
        self.assertTrue(all(x["training_eligible"] is False for x in d))
    def test_incomplete_BA_set_rejected(self):
        with self.assertRaises(ValueError):
            difference([{"ba":"SRP"}],[{"ba":"SRP"}])
if __name__=="__main__":unittest.main()
