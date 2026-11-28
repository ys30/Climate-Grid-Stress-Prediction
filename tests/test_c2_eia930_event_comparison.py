import csv
import tempfile
import unittest
from pathlib import Path
from scripts.c2_eia930_event_comparison import compare

EVENT=("ba","date","target","estimator","event_category","episode_id","actual_mw","calendar_pred_mw","weather_pred_mw")
DAILY=("ba","date_utc","paired_hours","actual_daily_peak_mw","signed_peak_error_mw","forecast_daily_peak_mw")
def make(root,actual2="1000",one_day_missing=False,episode2="E1"):
    events=Path(root)/"events.csv"
    daily=Path(root)/"daily.csv"
    days=["2025-07-01","2025-07-02"]
    with events.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=EVENT);w.writeheader()
        for i,d in enumerate(days):
            w.writerow(dict(ba="SRP",date=d,target="peak",estimator="Huber",
                            event_category="observed_high_load",episode_id="E1" if i==0 else episode2,
                            actual_mw=actual2 if i==1 else "1000",
                            calendar_pred_mw="900",weather_pred_mw="950"))
    with daily.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=DAILY);w.writeheader()
        for d in days[:1 if one_day_missing else 2]:
            w.writerow(dict(ba="SRP",date_utc=d,paired_hours=24,
                            actual_daily_peak_mw=1000,signed_peak_error_mw=-200,forecast_daily_peak_mw=800))
    return events,daily

class TestEventDfComparison(unittest.TestCase):
    def test_two_persistent_days_signed_comparison(self):
        with tempfile.TemporaryDirectory() as td:
            out=compare(*make(td))
            self.assertEqual(out["matched_days"],2)
            self.assertEqual(out["frozen_episodes"],1)
            self.assertEqual(out["by_duration"]["2-3d"]["operator_underforecast_fraction"],1)
            self.assertEqual(out["all_matched"]["weather_peak_mae_mw"],50)
    def test_no_missing_operator_days_fabricated(self):
        with tempfile.TemporaryDirectory() as td:
            out=compare(*make(td,one_day_missing=True))
            self.assertEqual(out["matched_days"],1)
            self.assertEqual(out["unmatched_dates"],["2025-07-02"])
            self.assertEqual(out["by_duration"]["2-3d"]["matched_days"],1)
    def test_mismatched_observed_target_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"observed demand mismatch"):
                compare(*make(td,actual2="1050"))
    def test_split_nonpersistent_episode_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"episode not persistent"):
                compare(*make(td,episode2="E2"))
    def test_frozen_target_filter_no_fabricated_events(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(ValueError,"no matching pre-frozen"):
                compare(*make(td),target="mean")
    def test_episode_identifier_reusable_across_years(self):
        with tempfile.TemporaryDirectory() as td:
            event,daily=make(td)
            with event.open("a") as f:
                f.write("SRP,2024-07-01,peak,Huber,observed_high_load,E1,1000,900,950\n")
                f.write("SRP,2024-07-02,peak,Huber,observed_high_load,E1,1000,900,950\\n")
            with daily.open("a") as f:
                f.write("SRP,2024-07-01,24,1000,-200,800\n")
                f.write("SRP,2024-07-02,24,1000,-200,800\\n")
            result=compare(event,daily)
            self.assertEqual(result["frozen_episodes"],2)
            self.assertEqual(result["matched_days"],4)
            self.assertEqual(result["by_duration"]["2-3d"]["matched_days"],4)
    def test_operator_signed_error_identity_guard(self):
        with tempfile.TemporaryDirectory() as td:
            event,daily=make(td)
            daily.write_text(daily.read_text().replace(",-200,800",",-150,800"))
            with self.assertRaisesRegex(ValueError,"identity mismatch"):
                compare(event,daily)
if __name__=="__main__":unittest.main()
