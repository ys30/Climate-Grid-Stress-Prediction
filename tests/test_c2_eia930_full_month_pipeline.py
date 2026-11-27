"""Full July UTC month end-to-end pipeline regression using *synthetic* EIA BALANCE rows.

This is software validation only and cannot substantiate historical demand skill.
"""
import csv
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_fetch_eia930_bulk import csv_to_month
from scripts.c2_verify_eia930_source import verify
from scripts.c2_eia930_day_ahead_benchmark import read_pairs
from scripts.c2_eia930_coverage_scorecard import build_summary


HEADERS = ("Balancing Authority", "UTC Time at End of Hour",
           "Demand (MW)", "Demand Forecast (MW)")


class TestFullMonthBulkPipeline(unittest.TestCase):
    def make_complete_month(self, path, *, omit=None):
        start=dt.datetime(2025,7,1,1)
        end=dt.datetime(2025,8,1,0)
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=HEADERS)
            writer.writeheader()
            now=start
            while now<=end:
                if now!=omit:
                    writer.writerow({
                        HEADERS[0]:"SRP",
                        HEADERS[1]:now.strftime("%m/%d/%Y %I:%M:%S %p"),
                        HEADERS[2]:"1000",
                        HEADERS[3]:"950"})
                now+=dt.timedelta(hours=1)

    def test_31_complete_days_and_signed_bias(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"bulk.csv"
            self.make_complete_month(source)
            dest=root/"normalized"
            manifest=csv_to_month(source,dest,year=2025,month=7,ba="SRP")
            self.assertEqual(manifest["row_count"],1488) # 31*24*2
            check=verify(dest/"eia930_D_DF_hourly.csv",
                         dest/"source_manifest.json")
            self.assertTrue(check["passed"],check["issues"])
            days,excluded,meta=read_pairs(dest/"eia930_D_DF_hourly.csv",{"SRP"})
            july=[r for r in days if r["date_utc"].startswith("2025-07-")]
            self.assertEqual(len(july),31)
            self.assertEqual(excluded,[])
            self.assertTrue(all(r["signed_peak_error_mw"]==-50 for r in july))
            daily=root/"daily.csv"
            rejected=root/"rejected.csv"
            with daily.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=list(days[0]))
                w.writeheader();w.writerows(days)
            with rejected.open("w",newline="") as f:
                w=csv.DictWriter(f,fieldnames=("ba","date_utc"))
                w.writeheader()
            score=build_summary(daily,rejected,["SRP"],2025,2025)[0]
            self.assertEqual(score["complete_days"],31)
            self.assertEqual(score["wholly_missing_days"],334)
            self.assertEqual(score["status"],"PARTIAL")
            self.assertAlmostEqual(score["peak_mae_mw"],50)
            self.assertAlmostEqual(score["peak_mean_bias_mw"],-50)
            self.assertEqual(score["underforecast_fraction"],1)

    def test_missing_month_end_hour_does_not_fabricate_last_day(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            source=root/"bulk.csv"
            self.make_complete_month(source,omit=dt.datetime(2025,8,1,0))
            dest=root/"normalized"
            csv_to_month(source,dest,year=2025,month=7,ba="SRP")
            days,excluded,_=read_pairs(dest/"eia930_D_DF_hourly.csv",{"SRP"})
            self.assertEqual(len(days),30)
            self.assertEqual(len(excluded),1)
            self.assertEqual(excluded[0]["date_utc"],"2025-07-31")
            self.assertEqual(excluded[0]["paired_hours"],23)


if __name__=="__main__":
    unittest.main()
