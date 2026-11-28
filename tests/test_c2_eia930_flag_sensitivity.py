import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_flag_sensitivity import sensitivity

class TestEiaQualitySensitivity(unittest.TestCase):
    def fixture(self,root,flags=None,rows=None):
        root=Path(root)
        daily=root/"daily.csv";quality=root/"flags.json"
        if rows is None:rows=[
            {"ba":"SRP","date_utc":"2025-07-01","signed_peak_error_mw":"-100","paired_hours":24},
            {"ba":"SRP","date_utc":"2025-07-02","signed_peak_error_mw":"200","paired_hours":24},
            {"ba":"SRP","date_utc":"2025-07-03","signed_peak_error_mw":"-300","paired_hours":24},
        ]
        with daily.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=("ba","date_utc","signed_peak_error_mw","paired_hours"))
            w.writeheader();w.writerows(rows)
        quality.write_text(json.dumps({"ba":"SRP","year":2025,"month":7,
              "flagged_dates_utc":flags if flags is not None else ["2025-07-02"]}))
        return daily,quality
    def test_all_vs_clean_scores_are_both_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            result=sensitivity(*self.fixture(d))
            self.assertEqual(result["all_scored_days"]["days"],3)
            self.assertEqual(result["clean_flag_sensitivity"]["days"],2)
            self.assertAlmostEqual(result["all_scored_days"]["mean_absolute_peak_error_mw"],200)
            self.assertAlmostEqual(result["clean_flag_sensitivity"]["mean_signed_peak_error_mw"],-200)
            self.assertEqual(result["clean_flag_sensitivity"]["underforecast_fraction"],1)
    def test_flagged_day_without_complete_score_is_reported(self):
        with tempfile.TemporaryDirectory() as d:
            result=sensitivity(*self.fixture(d,flags=["2025-07-31"]))
            self.assertEqual(result["flagged_source_dates_without_complete_daily_score"],["2025-07-31"])
    def test_wrong_ba_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.fixture(d)
            meta=json.loads(b.read_text());meta["ba"]="AZPS";b.write_text(json.dumps(meta))
            with self.assertRaisesRegex(ValueError,"mismatch"):sensitivity(a,b)
    def test_duplicate_daily_date_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.fixture(d)
            with a.open("a") as f:f.write("SRP,2025-07-01,-100,24\n")
            with self.assertRaisesRegex(ValueError,"duplicate"):sensitivity(a,b)
    def test_bad_source_hour_count_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.fixture(d)
            a.write_text(a.read_text().replace("200,24","200,23"))
            with self.assertRaisesRegex(ValueError,"24 paired"):sensitivity(a,b)
    def test_no_clean_days_is_null_not_zero(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.fixture(d,flags=["2025-07-01","2025-07-02","2025-07-03"])
            result=sensitivity(a,b)
            self.assertIsNone(result["clean_flag_sensitivity"]["mean_absolute_peak_error_mw"])
            self.assertEqual(result["clean_flag_sensitivity"]["days"],0)
    def test_out_of_month_flags_fail(self):
        with tempfile.TemporaryDirectory() as d:
            a,b=self.fixture(d,flags=["2025-08-01"])
            with self.assertRaisesRegex(ValueError,"outside requested month"):sensitivity(a,b)
if __name__=="__main__":unittest.main()
