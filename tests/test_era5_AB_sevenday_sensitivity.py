import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_AB_sevenday_sensitivity import check_window,summarize_all,BAS
class TestSevenDay(unittest.TestCase):
    def test_registered_windows(self):
        self.assertEqual(check_window("2023-01-15T00:00:00Z",7).year,2023)
        self.assertEqual(check_window("2025-07-01T00:00:00Z",7).year,2025)
        with self.assertRaises(ValueError):check_window("2023-07-03T00:00:00Z",7)
        with self.assertRaises(ValueError):check_window("2023-01-15T00:00:00Z",14)
    def test_source_sums_not_model_admitted(self):
        begin=datetime(2023,7,1,tzinfo=timezone.utc)
        rows=[{"ba":ba,"timestamp_utc_start":(begin+timedelta(hours=h)).isoformat(),
               "Census_minus_HIFLD_celsius":-1.7}
              for h in range(168) for ba in BAS]
        stats,days=summarize_all(rows)
        self.assertEqual(len(stats),4);self.assertEqual(len(days),28)
        self.assertTrue(all(r["negative_hours"]==168 for r in stats))
        self.assertTrue(all(r["model_training_permitted"] is False for r in stats))
        with self.assertRaises(ValueError):summarize_all(rows[:-1])
if __name__=="__main__":unittest.main()
