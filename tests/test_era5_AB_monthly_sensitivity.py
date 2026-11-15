import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_AB_monthly_sensitivity import check_month,build_joint_source_groups,split_one_read,month_stats,BAS
class Tests(unittest.TestCase):
    def test_preregistered_months_and_reject_2024_historical_inference(self):
        self.assertEqual(check_month("2023-01-01T00:00:00Z")[1],31)
        self.assertEqual(check_month("2025-07-01T00:00:00Z")[1],31)
        with self.assertRaises(ValueError):check_month("2024-07-01T00:00:00Z")
        with self.assertRaises(ValueError):check_month("2023-02-01T00:00:00Z")
    def test_joint_one_read_produces_same_exact_24h_AB_pairing(self):
        names=build_joint_source_groups({ba:[(1,2,1)] for ba in BAS},
            {ba:[(1,2,1)] for ba in BAS})
        self.assertEqual(len(names),8)
        dt=datetime(2023,1,1,tzinfo=timezone.utc)
        rows=[]
        for h in range(24):
            for key in names:
                rows.append({"ba":key,
                  "timestamp_utc_start":(dt+timedelta(hours=h)).isoformat(),
                  "weighted_temperature_celsius":20. if key.startswith("A_") else 18.,
                  "grid_cells":12,
                  "historical_weather_exposure_approved":False})
        paired=split_one_read(rows)
        self.assertEqual(len(paired),96)
        self.assertTrue(all(r["Census_minus_HIFLD_celsius"]==-2 for r in paired))
    def test_diagnostics_are_day_based_not_pseudoreplicated(self):
        dt=datetime(2023,1,1,tzinfo=timezone.utc)
        rows=[{"ba":ba,"timestamp_utc_start":(dt+timedelta(hours=h)).isoformat(),
               "Census_minus_HIFLD_celsius":-1.5}
              for ba in BAS for h in range(24*31)]
        overall,daily=month_stats(rows,31)
        self.assertEqual(len(daily),4*31)
        self.assertTrue(all(x["days_with_negative_daily_mean"]==31 for x in overall))
        self.assertTrue(all(x["weather_load_model_permitted"] is False for x in overall))
        with self.assertRaises(ValueError):month_stats(rows[:-1],31)
if __name__=="__main__":unittest.main()
