import unittest
from shapely.geometry import box
from src.c2_era5_population_county_weights import parse_population_estimates_csv,county_population_overlap_weights
class Tests(unittest.TestCase):
    def test_official_estimates_base_county_only_and_FIPS(self):
        bulk=("SUMLEV,STATE,COUNTY,ESTIMATESBASE2020\n"
              "040,04,000,999999\n"
              "050,04,013,100\n"
              "050,04,015,200\n")
        output=parse_population_estimates_csv(bulk.encode(),{"04013","04015"})
        self.assertEqual(output,{"04013":100,"04015":200})
        with self.assertRaises(ValueError):
            parse_population_estimates_csv(bulk.encode(),{"04013","06001"})
    def test_within_county_allocation_and_not_utility_customers(self):
        geom={"04013":box(-112.125,32.875,-111.875,33.125),
              "06001":box(-119.125,34.875,-118.875,35.125)}
        members={"AZPS":{"04013"},"SRP":{"04013"},"BPAT":{"06001"},"CISO":{"06001"}}
        rows,stats=county_population_overlap_weights(members,geom,{"04013":1000,"06001":2000})
        self.assertEqual(len(stats),4)
        self.assertTrue(all(abs(x["weight_sum"]-1)<1e-8 for x in stats))
        self.assertTrue(all(x["approved_for_utility_customer_exposure"] is False for x in stats))
    def test_reject_missing_population(self):
        with self.assertRaises(ValueError):
            county_population_overlap_weights({"AZPS":{"04013"},"SRP":{"04013"},
             "BPAT":{"04013"},"CISO":{"04013"}},{"04013":box(-112,33,-111,34)}, {})
if __name__=="__main__":unittest.main()
