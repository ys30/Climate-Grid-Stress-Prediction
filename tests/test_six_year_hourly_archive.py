import unittest
from src.c2_six_year_hourly_archive import transform_row
class Tests(unittest.TestCase):
    def row(self):
        return {"ba":"SRP","timestamp_utc_start":"2025-07-07T06:00:00+00:00",
         "demand_mw_raw":"","temperature_c_experimental_area":"31.25",
         "source_missing_demand":"True","demand_spike_candidate":"False",
         "train_or_validate_eligible":"False",
         "historical_BA_area_approved":"False"}
    def test_missing_original_demand_preserved(self):
        item=transform_row(self.row(),2025,7)
        self.assertEqual(item["EIA930_original_demand_mw"],"")
        self.assertEqual(item["EIA930_demand_missing"],"True")
        self.assertEqual(item["model_training_eligible"],"False")
    def test_no_fabricated_original_load(self):
        row=self.row();row["demand_mw_raw"]="1000"
        with self.assertRaises(ValueError):transform_row(row,2025,7)
    def test_unapproved_data_never_claims_model_permission(self):
        row=self.row();row["train_or_validate_eligible"]="True"
        with self.assertRaises(ValueError):transform_row(row,2025,7)
if __name__=="__main__":unittest.main()
