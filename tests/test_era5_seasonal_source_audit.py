import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_seasonal_source_audit import seasonal_source_pair
class TestSeasonalPair(unittest.TestCase):
    def test_48h_exact_join_and_training_block(self):
        start=datetime(2023,1,15,tzinfo=timezone.utc)
        bas=("AZPS","BPAT","CISO","SRP")
        demands={ba:{start+timedelta(hours=i):4000+i for i in range(48)} for ba in bas}
        rows=[{"ba":ba,"timestamp_utc_start":(start+timedelta(hours=i)).isoformat(),
               "weighted_temperature_celsius":20.,"historical_weather_exposure_approved":False}
               for ba in bas for i in range(48)]
        paired=seasonal_source_pair(rows,demands,[],start.isoformat(),2)
        self.assertEqual(len(paired),192)
        self.assertTrue(all(not r["train_or_validate_eligible"] for r in paired))
        with self.assertRaises(ValueError):
            seasonal_source_pair(rows[:-1],demands,[],start.isoformat(),2)
    def test_unapproved_exposure_cannot_claim_approval(self):
        start=datetime(2023,1,15,tzinfo=timezone.utc)
        bas=("AZPS","BPAT","CISO","SRP")
        d={ba:{start+timedelta(hours=i):2000 for i in range(48)} for ba in bas}
        w=[{"ba":ba,"timestamp_utc_start":(start+timedelta(hours=i)).isoformat(),
            "weighted_temperature_celsius":10.,"historical_weather_exposure_approved":False}
            for ba in bas for i in range(48)]
        w[0]["historical_weather_exposure_approved"]=True
        with self.assertRaises(ValueError):seasonal_source_pair(w,d,[],start.isoformat(),2)
if __name__=="__main__":unittest.main()
