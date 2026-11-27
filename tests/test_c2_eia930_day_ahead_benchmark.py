"""Synthetic unit tests for EIA-930 historical operator DF benchmark."""
import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_day_ahead_benchmark import read_pairs

class TestEia930DayAhead(unittest.TestCase):
    def make(self,rows,root):
        path=Path(root)/"input.csv"
        with path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=["period","respondent","type","value"])
            writer.writeheader();writer.writerows(rows)
        return path

    def rows(self):
        result=[]
        for h in range(24):
            period=f"2025-11-01T{h+1:02d}" if h<23 else "2025-11-02T00"
            result.append(dict(period=period,respondent="SRP",type="D",value=100+h))
            result.append(dict(period=period,respondent="SRP",type="DF",value=90+h))
        return result

    def test_full_utc_day_peak(self):
        with tempfile.TemporaryDirectory() as d:
            rows,excluded,meta=read_pairs(self.make(self.rows(),d))
            self.assertEqual(len(rows),1)
            self.assertFalse(excluded)
            self.assertEqual(meta["complete_days"],1)
            self.assertEqual(rows[0]["actual_daily_peak_mw"],123)
            self.assertEqual(rows[0]["forecast_daily_peak_mw"],113)
            self.assertEqual(rows[0]["signed_peak_error_mw"],-10)

    def test_incomplete_dropped_not_zero_filled(self):
        with tempfile.TemporaryDirectory() as d:
            rows,excluded,_=read_pairs(self.make(self.rows()[:-1],d))
            self.assertFalse(rows)
            self.assertEqual(excluded[0]["paired_hours"],23)

    def test_duplicate_fails(self):
        with tempfile.TemporaryDirectory() as d:
            rows=self.rows()+[dict(self.rows()[0])]
            with self.assertRaisesRegex(ValueError,"duplicate"):
                read_pairs(self.make(rows,d))

    def test_invalid_time_fails(self):
        with tempfile.TemporaryDirectory() as d:
            rows=self.rows();rows[0]["period"]="invalid"
            with self.assertRaisesRegex(ValueError,"invalid UTC hour"):
                read_pairs(self.make(rows,d))

    def test_null_source_value_marks_day_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            rows=self.rows()
            rows[0]["value"]=None
            scored,excluded,_=read_pairs(self.make(rows,d))
            self.assertEqual(scored,[])
            self.assertEqual(excluded[0]["paired_hours"],23)

    def test_negative_demand_fails(self):
        with tempfile.TemporaryDirectory() as d:
            rows=self.rows();rows[0]["value"]="-1"
            with self.assertRaisesRegex(ValueError,"negative"):
                read_pairs(self.make(rows,d))

if __name__=="__main__":
    unittest.main()
