import unittest
from src.c2_pudl_ba_county_source_probe import assess
class TestPUDLCounty(unittest.TestCase):
    def test_annual_coverage_does_not_admit_geometry(self):
        rows=[{"report_date":f"{y}-12-31","balancing_authority_id_eia":100,
               "county_id_fips":"4013"} for y in (2020,2021,2022,2023,2024)]
        r=assess(rows)
        self.assertEqual(r["source_years"],[2020,2021,2022,2023,2024])
        self.assertFalse(r["calendar_years_2020_2025_all_present"])
        self.assertFalse(r["model_geography_approved"])
        self.assertFalse(r["official_eia930_BA_code_to_id_mapping_established"])
    def test_missing_county_rejected(self):
        with self.assertRaises(ValueError):
            assess([{"report_date":"2024-12-31","balancing_authority_id_eia":9,
                     "county_id_fips":None}])
if __name__=="__main__":unittest.main()
