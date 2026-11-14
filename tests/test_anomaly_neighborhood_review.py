import unittest
from datetime import datetime,timedelta,timezone
from src.c2_anomaly_neighborhood_review import review_hourly
class Tests(unittest.TestCase):
    def make(self):
        start=datetime(2023,1,1,tzinfo=timezone.utc)
        rows=[]
        for h in range(15):
            value="60000" if h==7 else "1500"
            rows.append({"ba":"SRP","timestamp_utc_start":(start+timedelta(hours=h)).isoformat(),
                "EIA930_original_demand_mw":value,
                "EIA930_anomaly_candidate_not_confirmed":"True" if h==7 else "False",
                "geometry_historically_approved":"False","model_training_eligible":"False"})
        return rows
    def test_large_relative_jump_triaged_not_confirmed(self):
        review=review_hourly(self.make())
        self.assertEqual(len(review),1)
        self.assertEqual(review[0]["triage_class"],"large_positive_relative_to_neighbors")
        self.assertFalse(review[0]["flag_is_confirmed_data_error"])
        self.assertFalse(review[0]["model_training_eligible"])
    def test_unapproved_source_never_auto_fills(self):
        rows=self.make()
        rows[7]["EIA930_original_demand_mw"]=""
        result=review_hourly(rows)
        self.assertEqual(result[0]["triage_class"],"flagged_but_original_demand_missing")
        self.assertFalse(result[0]["automatic_imputation"])
    def test_false_training_claim_rejected(self):
        rows=self.make();rows[2]["model_training_eligible"]="True"
        with self.assertRaises(ValueError):review_hourly(rows)
if __name__=="__main__":unittest.main()
