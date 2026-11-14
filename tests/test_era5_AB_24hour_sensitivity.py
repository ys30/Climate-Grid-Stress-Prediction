import unittest
from datetime import datetime,timedelta,timezone
from src.c2_era5_AB_24hour_sensitivity import match_days,summarize
class Tests(unittest.TestCase):
    def test_exact_matching_hourly_exposure_is_never_admitted(self):
        begin=datetime(2023,7,1,tzinfo=timezone.utc)
        a=[{"timestamp_utc_start":(begin+timedelta(hours=h)).isoformat(),
            "ba":ba,"grid_cells":20,"weighted_temperature_celsius":23.5,
            "historical_weather_exposure_approved":False}
            for h in range(24) for ba in ("AZPS","BPAT","CISO","SRP")]
        b=[{**x,"weighted_temperature_celsius":22.} for x in a]
        rows=match_days(a,b)
        self.assertEqual(len(rows),96)
        stats=summarize(rows)
        self.assertTrue(all(x["negative_hours"]==24 for x in stats))
        self.assertTrue(all(not x["training_permitted"] for x in rows))
        b.pop()
        with self.assertRaises(ValueError):match_days(a,b)
if __name__=="__main__":unittest.main()
