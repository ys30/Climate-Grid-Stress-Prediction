import unittest
from src.c2_e1_pudl_2026_10_utility_county_fips_original import normalize_fips,summarize

class OriginalUtilityCountyTests(unittest.TestCase):
    def test_fips_zero_padding(self):
        self.assertEqual(normalize_fips(4013),"04013")
        self.assertEqual(normalize_fips("04021"),"04021")
    def test_fips_bad_fails(self):
        for bad in (None,"nonsense","123456"):
            with self.assertRaises(ValueError):normalize_fips(bad)
    def test_wrong_original_source_link_count_fails(self):
        with self.assertRaisesRegex(ValueError,"Expected 933"):
            summarize([{"year":"2023","BA":"SRP","utility_id_eia":"99",
             "state":"AZ","utility_counties_reported":"1"}],
             [{"report_date":"2023-01-01","utility_id_eia":99,
               "state":"AZ","county_id_fips":"04013"}])
if __name__=="__main__":unittest.main()
