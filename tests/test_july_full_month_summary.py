import unittest
from src.c2_july_full_month_summary import consolidate,EXPECTED_WEIGHTS
class Tests(unittest.TestCase):
    def sample(self,year,gaps=0):
        return {"utc_start":str(year)+"-07-01T00:00:00+00:00","days":31,"hours_per_BA":744,
        "source_BA_hour_slots":2976,"weather_source_rows":2976,
        "all_weather_hours_present":True,"source_dataset":"ARCO ERA5 real 2m temperature",
        "source_missing_demand_hours":gaps,"paired_source_rows":2976-gaps,
        "weights_sha256":EXPECTED_WEIGHTS,"training_or_validation_permitted":False,
        "historical_geometry_approved":False,"no_imputation":True,
        "missing_demand_BA_hours":[{"ba":"SRP","utc":"sample"} for _ in range(gaps)],
        "eia_candidate_anomaly_flags_in_window":0}
    def test_six_full_months_but_not_six_full_years(self):
        rows,report=consolidate([self.sample(y,2 if y==2025 else 0) for y in range(2020,2026)])
        self.assertEqual(report["observed_EIA_weather_pairs"],17854)
        self.assertEqual(report["missing_source_demand_hours"],2)
        self.assertFalse(report["training_permitted"])
        self.assertFalse(report["all_years_complete"])
    def test_missing_year_rejected(self):
        with self.assertRaises(ValueError):
            consolidate([self.sample(y) for y in range(2020,2025)])
    def test_missing_hour_accounting_fail_closed(self):
        items=[self.sample(y) for y in range(2020,2026)]
        items[0]["paired_source_rows"]=3000
        with self.assertRaises(ValueError):consolidate(items)
if __name__=="__main__":unittest.main()
