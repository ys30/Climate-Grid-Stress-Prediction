import unittest
from src.c2_era5_three_proxy_comparison import SAMPLES
class TestThreeProxy(unittest.TestCase):
    def test_four_UTC_real_source_instants_not_full_year(self):
        self.assertEqual(len(SAMPLES),4)
        self.assertTrue(all(x.endswith("12:00:00Z") for x in SAMPLES))
if __name__=="__main__":unittest.main()
