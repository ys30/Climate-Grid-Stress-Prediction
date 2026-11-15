import unittest
from src.c2_eia861_ba_utility_county_probe import assess,BAS
class Tests(unittest.TestCase):
    def test_ba_utility_county_nonexclusive_not_load(self):
        association=[{"report_date":f"{y}-01-01","balancing_authority_id_eia":i,
                     "utility_id_eia":1000+i,"state":"CA"}
              for y in range(2020,2026) for i in BAS.values()]
        territory=[{"report_date":f"{y}-01-01","utility_id_eia":1000+i,
                     "county_id_fips":6001,"state":"CA"}
              for y in range(2020,2026) for i in BAS.values()]
        summary,detail,ambiguous=assess(association,territory)
        self.assertEqual(len(summary),24)
        self.assertEqual(len(detail),24)
        self.assertEqual(ambiguous,[])
        self.assertTrue(all(x["training_permitted"] is False for x in summary))
        self.assertTrue(all(x["unrestricted_utility_union_counties"]==1 for x in summary))
        extra={"report_date":"2020-01-01","utility_id_eia":1000+BAS["AZPS"],
               "county_id_fips":32001,"state":"NV"}
        summary2,_,_=assess(association,territory+[extra])
        azps2020=next(x for x in summary2 if x["year"]==2020 and x["BA"]=="AZPS")
        self.assertEqual(azps2020["candidate_union_counties"],1)
        self.assertEqual(azps2020["unrestricted_utility_union_counties"],2)
        self.assertEqual(azps2020["excluded_cross_state_county_association_slots"],1)
        with self.assertRaises(ValueError):assess([],territory)
if __name__=="__main__":unittest.main()
