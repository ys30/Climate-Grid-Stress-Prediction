import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_24h_source_pair_audit import pair_audit
class Tests(unittest.TestCase):
    def test_real_hour_label_exact_matching_no_model(self):
        start=datetime(2023,7,1,tzinfo=timezone.utc)
        bas=("AZPS","BPAT","CISO","SRP")
        d={ba:{start+timedelta(hours=i):1000+i for i in range(24)} for ba in bas}
        w=[{"ba":ba,"timestamp_utc_start":(start+timedelta(hours=i)).isoformat(),
           "weighted_temperature_celsius":"28",
           "experimental_geography_only":"True",
           "historical_weather_exposure_approved":"False"}
           for ba in bas for i in range(24)]
        paired=pair_audit(d,[],w)
        self.assertEqual(len(paired),96)
        self.assertTrue(all(not row["model_training_eligible"] for row in paired))
        w[0]["timestamp_utc_start"]=(start+timedelta(hours=25)).isoformat()
        with self.assertRaises(ValueError):pair_audit(d,[],w)
if __name__=="__main__":unittest.main()
