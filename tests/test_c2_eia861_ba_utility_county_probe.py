import unittest
from src.c2_eia861_ba_utility_county_probe import assess,BAS
class Tests(unittest.TestCase):
    def test_ba_utility_county_nonexclusive_not_load(self):
        association=[{"report_date":f"{y}-01-01","balancing_authority_id_eia":i,
                     "utility_id_eia":1000+i,"state":"CA"}
              for y in range(2020,2026) for i in BAS.values()]
        territory=[{"report_date":f"{y}-01-01","utility_id_eia":1000+i,
                     "county_id_fips":6001}
              for y in range(2020,2026) for i in BAS.values()]
        summary,detail,ambiguous=assess(association,territory)
        self.assertEqual(len(summary),24)
        self.assertEqual(len(detail),24)
        self.assertEqual(ambiguous,[])
        self.assertTrue(all(x["training_permitted"] is False for x in summary))
        with self.assertRaises(ValueError):assess([],territory)
if __name__=="__main__":unittest.main()
