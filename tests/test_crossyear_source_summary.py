import unittest
from src.c2_crossyear_source_summary import combine
class Tests(unittest.TestCase):
    def fixture(self,year):
        return {"utc_start":f"{year}-07-01T00:00:00+00:00",
          "BAs":["AZPS","BPAT","CISO","SRP"],"historical_geometry_approved":False,
          "training_or_validation_permitted":False,"no_imputation":True,
          "days":2,"hours_per_BA":48,"paired_source_rows":192,
          "weather_source_rows":192,"all_source_hours_present":True,
          "weights_sha256":"abc","eia_candidate_anomaly_flags_in_window":0}
    def test_six_years_not_full_annual_data(self):
        rows,summary=combine([self.fixture(y) for y in range(2020,2026)])
        self.assertEqual(summary["real_source_pairs_total"],1152)
        self.assertFalse(summary["annual_full_weather_data_verified"])
        self.assertFalse(summary["training_authorized"])
    def test_missing_year_fails_closed(self):
        with self.assertRaises(ValueError):
            combine([self.fixture(y) for y in range(2021,2026)])
    def test_model_admission_rejected(self):
        audits=[self.fixture(y) for y in range(2020,2026)]
        audits[2]["training_or_validation_permitted"]=True
        with self.assertRaises(ValueError):combine(audits)
if __name__=="__main__":unittest.main()
