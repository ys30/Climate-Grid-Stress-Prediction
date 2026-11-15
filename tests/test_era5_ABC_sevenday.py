import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_ABC_sevenday import check_start,summarize,BAS
class Tests(unittest.TestCase):
    def test_preregistered_dates(self):
        self.assertEqual(check_start("2023-01-15T00:00:00Z").year,2023)
        with self.assertRaises(ValueError):check_start("2023-02-01T00:00:00Z")
    def test_requires_exact_day_and_no_authorized_training(self):
        begin=datetime(2023,1,15,tzinfo=timezone.utc)
        rows=[{"BA":ba,"UTC_timestamp":(begin+timedelta(hours=h)).isoformat(),
             "C_minus_B_celsius":1.25} for ba in BAS for h in range(168)]
        stats,daily=summarize(rows)
        self.assertEqual(len(stats),4)
        self.assertEqual(len(daily),28)
        self.assertTrue(all(x["hours_C_warmer_than_B"]==168 for x in stats))
        self.assertTrue(all(x["model_training_permitted"] is False for x in stats))
        with self.assertRaises(ValueError):summarize(rows[:-1])
if __name__=="__main__":unittest.main()
