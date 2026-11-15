import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_ABC_four_day import normalize_day,summarize,DAYS,BAS
class Tests(unittest.TestCase):
    def test_all_three_proxies_daily_observations(self):
        start=datetime(2023,1,15,tzinfo=timezone.utc)
        source=[]
        for tag in "ABC":
            for h in range(24):
                for ba in BAS:
                    source.append({"ba":tag+"_"+ba,
                      "timestamp_utc_start":(start+timedelta(hours=h)).isoformat(),
                      "historical_weather_exposure_approved":False,
                      "weighted_temperature_celsius":{"A":20,"B":18,"C":23}[tag]})
        result=normalize_day(source,DAYS[0])
        self.assertEqual(len(result),96)
        self.assertTrue(all(x["C_minus_B_celsius"]==5 for x in result))
        with self.assertRaises(ValueError):normalize_day(source[:-1],DAYS[0])
    def test_summary_refuses_incomplete_days(self):
        with self.assertRaises(ValueError):summarize([])
if __name__=="__main__":unittest.main()
