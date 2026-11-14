import unittest
from src.c2_full_source_event_audit import check_rows
class Tests(unittest.TestCase):
    def fixture(self):
        m={"source_BA_hour_slots":2,"source_missing_demand_hours":1,
           "eia_candidate_anomaly_flags_in_window":1,"paired_source_rows":1}
        rows=[
         {"ba":"AZPS","timestamp_utc_start":"2025-03-01T00:00:00+00:00",
          "demand_mw_raw":"4000","temperature_c_experimental_area":"22.5",
          "train_or_validate_eligible":"False","historical_BA_area_approved":"False",
          "source_missing_demand":"False","demand_spike_candidate":"True"},
         {"ba":"SRP","timestamp_utc_start":"2025-03-01T00:00:00+00:00",
          "demand_mw_raw":"","temperature_c_experimental_area":"24.5",
          "train_or_validate_eligible":"False","historical_BA_area_approved":"False",
          "source_missing_demand":"True","demand_spike_candidate":"False"}]
        return rows,m
    def test_flag_is_only_review_candidate_and_gap_never_filled(self):
        rows,m=self.fixture()
        events,gaps=check_rows(rows,m)
        self.assertEqual(len(events),1)
        self.assertEqual(len(gaps),1)
        self.assertEqual(events[0]["flag_status"],"candidate_needs_review_not_confirmed_error")
        self.assertFalse(events[0]["model_eligible"])
    def test_fabricated_demand_rejected(self):
        rows,m=self.fixture()
        rows[1]["demand_mw_raw"]="12"
        with self.assertRaises(ValueError):check_rows(rows,m)
    def test_false_geography_approval_rejected(self):
        rows,m=self.fixture()
        rows[0]["historical_BA_area_approved"]="True"
        with self.assertRaises(ValueError):check_rows(rows,m)
if __name__=="__main__":unittest.main()
