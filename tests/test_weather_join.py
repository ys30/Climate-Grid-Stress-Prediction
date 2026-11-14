import unittest
from src.c2_weather_join import join
class Tests(unittest.TestCase):
    def setUp(self):
        self.d=[{"year":"2023","ba":"SRP","timestamp_utc_start":"2023-06-03T20:00:00+00:00",
                 "raw_demand_mw":"70313","quarantine":"True","model_eligible":"False"},
                {"year":"2023","ba":"SRP","timestamp_utc_start":"2023-06-03T21:00:00+00:00",
                 "raw_demand_mw":"5021","quarantine":"False","model_eligible":"True"}]
        self.w=[{"ba":"SRP","timestamp_utc_start":"2023-06-03T21:00:00+00:00",
                 "temperature_2m_c":"31.1","exposure_method":"ba_area_weighted_era5",
                 "source_dataset":"ERA5","geometry_approved":"True","geometry_admission_id":"test-only-fixture"}]
    def test_quarantine_is_not_joined(self):
        out,report=join(self.d,self.w)
        self.assertEqual(report["quarantined"],1)
        self.assertEqual(len(out),1)
        self.assertEqual(out[0]["demand_mw"],5021)
    def test_unapproved_experiment_cannot_join(self):
        self.w[0]["geometry_approved"]="False"
        with self.assertRaisesRegex(ValueError,"unapproved"):
            join(self.d,self.w)
    def test_missing_geography_review_cannot_join(self):
        self.w[0]["geometry_admission_id"]=""
        with self.assertRaises(ValueError):join(self.d,self.w)
    def test_reject_single_city_point(self):
        self.w[0]["exposure_method"]="single_city_era5"
        with self.assertRaises(ValueError):join(self.d,self.w)
    def test_reject_missing_timezone(self):
        self.w[0]["timestamp_utc_start"]="2023-06-03T21:00:00"
        with self.assertRaises(ValueError):join(self.d,self.w)
    def test_weather_duplicates_fail(self):
        with self.assertRaises(ValueError):join(self.d,self.w*2)
if __name__=="__main__":unittest.main()
