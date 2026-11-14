import unittest
from src.c2_january_july_source_summary import validate_months,EXPECTED_WEIGHT
class Tests(unittest.TestCase):
    def item(self,year,month,gaps=0):
        return {"utc_start":f"{year}-{month:02d}-01T00:00:00+00:00",
            "days":31,"hours_per_BA":744,"source_BA_hour_slots":2976,
            "weather_source_rows":2976,"all_weather_hours_present":True,
            "BAs":["AZPS","BPAT","CISO","SRP"],"weights_sha256":EXPECTED_WEIGHT,
            "paired_source_rows":2976-gaps,"source_missing_demand_hours":gaps,
            "missing_demand_BA_hours":[{"ba":"SRP","utc":"time"} for _ in range(gaps)],
            "historical_geometry_approved":False,"training_or_validation_permitted":False,
            "no_imputation":True,"eia_candidate_anomaly_flags_in_window":1}
    def full(self):
        return [self.item(y,m) for y in range(2020,2026) for m in (1,7)]
    def test_exact_twelve_month_windows_without_annual_claims(self):
        rows,s=validate_months(self.full())
        self.assertEqual(len(rows),12)
        self.assertEqual(s["total_real_ERA5_BA_hours"],35712)
        self.assertFalse(s["all_12_months_each_year_verified"])
        self.assertFalse(s["training_permitted"])
    def test_month_missing_or_unapproved_change_fails(self):
        with self.assertRaises(ValueError):validate_months(self.full()[:-1])
        rows=self.full()
        rows[3]["training_or_validation_permitted"]=True
        with self.assertRaises(ValueError):validate_months(rows)
if __name__=="__main__":unittest.main()
