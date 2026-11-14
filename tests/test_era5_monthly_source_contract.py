import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_seasonal_source_audit import seasonal_source_pair
class MonthHourAuditTest(unittest.TestCase):
    def test_month_gap_kept_null_and_no_training(self):
        begin=datetime(2025,7,1,tzinfo=timezone.utc)
        bas=("AZPS","BPAT","CISO","SRP")
        demand={ba:{begin+timedelta(hours=h):1000+h for h in range(744)} for ba in bas}
        gap=begin+timedelta(days=6,hours=6)
        del demand["SRP"][gap]
        weather=[{"ba":ba,"timestamp_utc_start":(begin+timedelta(hours=h)).isoformat(),
                  "weighted_temperature_celsius":30.,"historical_weather_exposure_approved":False}
                 for ba in bas for h in range(744)]
        rows=seasonal_source_pair(weather,demand,[],begin.isoformat(),31,allow_missing_demand=True)
        self.assertEqual(len(rows),2976)
        bad=[r for r in rows if r["source_missing_demand"]]
        self.assertEqual(len(bad),1)
        self.assertEqual((bad[0]["ba"],bad[0]["timestamp_utc_start"]),("SRP",gap.isoformat()))
        self.assertIsNone(bad[0]["demand_mw_raw"])
        self.assertTrue(all(not r["train_or_validate_eligible"] for r in rows))
if __name__=="__main__":unittest.main()
