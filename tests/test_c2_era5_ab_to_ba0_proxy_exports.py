import csv
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from c2_era5_ab_to_ba0_proxy_exports import validate, BAS, MONTHS
from datetime import datetime,timedelta,timezone
import calendar

class TestFourMonthBridge(unittest.TestCase):
    def data(self):
        rows=[]
        for ba in BAS:
            for year,month in MONTHS:
                start=datetime(year,month,1,tzinfo=timezone.utc)
                for h in range(calendar.monthrange(year,month)[1]*24):
                    ts=(start+timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
                    rows.append({"ba":ba,"timestamp_utc_start":ts,
                                 "HIFLD_2018_candidate_celsius":"10.0",
                                 "Census_2024_county_proxy_celsius":"11.0",
                                 "Census_minus_HIFLD_celsius":"1.0",
                                 "historical_geography_approved":"False",
                                 "training_permitted":"False"})
        return rows
    def evidence(self):
        return {"geography_approved":False,"training_permitted":False,
                "independently_verified_BA_hours":11904,"verified_months":4,
                "source_months":[f"{year:04}-{month:02}-01T00:00:00Z" for year,month in MONTHS],
                "BA_results":[{"ba":ba,"real_ERA5_hours":2976,
                               "historical_geometry_approved":False,
                               "training_allowed":False} for ba in BAS],
                "A_weights_SHA256":"a"*64,"B_weights_SHA256":"b"*64}
    def test_full_four_month_hourly_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            f=Path(directory)/"source.csv"
            rows=self.data()
            with f.open("w",newline="") as handle:
                w=csv.DictWriter(handle,fieldnames=list(rows[0]))
                w.writeheader();w.writerows(rows)
            rows[0]["timestamp_utc_start"]=rows[0]["timestamp_utc_start"].replace("Z","+00:00")
            with f.open("w",newline="") as handle:
                w=csv.DictWriter(handle,fieldnames=list(rows[0]))
                w.writeheader();w.writerows(rows)
            out=validate(f,self.evidence())
            self.assertEqual(len(out["A_HIFLD_2018"]),11904)
            self.assertEqual(len(out["B_TIGER_2024"]),11904)
            self.assertEqual(out["A_HIFLD_2018"][0]["weather_value"],"10.000000")
            with self.assertRaises(ValueError):
                validate(f,{**self.evidence(),"training_permitted":True})
            with self.assertRaises(ValueError):
                validate(f,{**self.evidence(),"source_months":["2023-01-01T00:00:00Z"]})
            wrong=self.evidence()
            wrong["BA_results"][0]["ba"]="CISO"
            wrong["BA_results"][1]["ba"]="CISO"
            with self.assertRaises(ValueError):
                validate(f,wrong)
            rows[-1]["Census_minus_HIFLD_celsius"]="7"
            with f.open("w",newline="") as handle:
                w=csv.DictWriter(handle,fieldnames=list(rows[0]))
                w.writeheader();w.writerows(rows)
            with self.assertRaises(ValueError):validate(f,self.evidence())
    def test_missing_source_file_is_not_fabricated(self):
        with self.assertRaises(FileNotFoundError):
            validate("/does/not/exist.csv",self.evidence())

if __name__=="__main__":unittest.main()
