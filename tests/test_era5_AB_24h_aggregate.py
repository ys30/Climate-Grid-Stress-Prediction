import unittest,tempfile,csv,json
from pathlib import Path
from datetime import datetime,timedelta
from src.c2_era5_AB_24h_aggregate import consolidate,TIMES,A_SHA,B_SHA,DATA_NAME,META_NAME,BAS
class Tests(unittest.TestCase):
    def test_all_four_actual_days_and_source_model_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            paths=[]
            for i,when in enumerate(TIMES):
                folder=Path(temp)/str(i);folder.mkdir()
                paths.append(folder)
                (folder/META_NAME).write_text(json.dumps({
                    "UTC_start":when,"source_HIFLD_weight_SHA256":A_SHA,
                    "source_Census_weight_SHA256":B_SHA,
                    "BA_geography_approved":False,
                    "weather_load_model_fitted":False,
                    "anthropogenic_attribution_performed":False,
                    "BA_hour_comparisons":96,"all_24_UTC_hours_present":True}))
                base=datetime.fromisoformat(when.replace("Z","+00:00"))
                with (folder/DATA_NAME).open("w",newline="") as f:
                    cols=["timestamp_utc_start","ba","HIFLD_2018_candidate_celsius",
                        "Census_2024_county_proxy_celsius","Census_minus_HIFLD_celsius",
                        "historical_geography_approved","training_permitted"]
                    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
                    for h in range(24):
                        for ba in BAS:
                            w.writerow({"timestamp_utc_start":(base+timedelta(hours=h)).isoformat(),
                             "ba":ba,"HIFLD_2018_candidate_celsius":"21",
                             "Census_2024_county_proxy_celsius":"20",
                             "Census_minus_HIFLD_celsius":"-1",
                             "historical_geography_approved":"False",
                             "training_permitted":"False"})
            rows,summary=consolidate(paths)
            self.assertEqual(len(rows),384)
            self.assertTrue(all(x["negative_hours"]==96 for x in summary))
            self.assertTrue(all(x["training_permitted"] is False for x in summary))
            with self.assertRaises(ValueError):consolidate(paths[:-1])
if __name__=="__main__":unittest.main()
