"""Local calendar-boundary tests: synthetic input, never EIA source evidence."""
import csv,hashlib,tempfile,unittest
from datetime import datetime,timedelta,timezone,date
from zoneinfo import ZoneInfo
from pathlib import Path
from scripts.c2_eia_local_calendar_revision_probe import audit,civil_day_utc_bounds,classify_civil_day

class CalendarBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/"changes.csv"

    def make(self,rows):
        fields=["ba","year","timestamp_utc","classification"]
        with self.path.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def test_two_true_full_days_only_under_hypothetical_zones(self):
        rows=[]
        for ba,year,start in [
            ("AZPS","2025",datetime(2025,7,26,7,tzinfo=timezone.utc)),
            ("BPAT","2021",datetime(2021,9,15,7,tzinfo=timezone.utc))]:
            for i in range(24):
                rows.append({"ba":ba,"year":year,
                    "timestamp_utc":(start+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "classification":"numeric_changed"})
        d=audit(self.path,expected_sha=self.make(rows))
        self.assertEqual(d["total_nonidentical_hours"],48)
        self.assertEqual(d["complete_hypothetical_local_days"],2)
        self.assertEqual(d["number_of_episodes"],2)
        self.assertFalse(d["official_submission_vintage_or_change_log_obtained"])
        self.assertFalse(d["model_training_permitted"])
        self.assertTrue(all(not x["actual_BA_reporting_timezone_verified"] for x in d["episodes"]))

    def test_missing_hour_or_wrong_day_not_classed_complete(self):
        start=datetime(2025,7,26,7,tzinfo=timezone.utc)
        rows=[{"ba":"AZPS","year":"2025",
               "timestamp_utc":(start+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "classification":"numeric_changed"} for i in range(23)]
        d=audit(self.path,expected_sha=self.make(rows))
        self.assertEqual(d["complete_hypothetical_local_days"],0)

    def test_spring_and_fall_DST_local_day_have_23_or_25_hours(self):
        zone=ZoneInfo("America/Los_Angeles")
        for day,expected in ((date(2025,3,9),23),(date(2025,11,2),25)):
            start,end,hours=civil_day_utc_bounds(day,zone)
            self.assertEqual(hours,expected)
            self.assertEqual(int((end-start)/timedelta(hours=1)),hours)
            ok,eligible=classify_civil_day(start,end-timedelta(hours=1),hours,zone)
            self.assertTrue(ok)
            self.assertEqual(eligible,hours)
            not_full,_=classify_civil_day(start,end-timedelta(hours=2),hours-1,zone)
            self.assertFalse(not_full)

    def test_AZPS_Phoenix_has_24h_even_on_US_DST_transition(self):
        zone=ZoneInfo("America/Phoenix")
        for day in (date(2025,3,9),date(2025,11,2)):
            start,end,hours=civil_day_utc_bounds(day,zone)
            self.assertEqual(hours,24)
            self.assertTrue(classify_civil_day(start,end-timedelta(hours=1),24,zone)[0])

    def test_source_sha_or_duplicate_utc_rejected(self):
        t="2025-07-26T07:00:00Z"
        row={"ba":"AZPS","year":"2025","timestamp_utc":t,"classification":"numeric_changed"}
        sha=self.make([row])
        with self.assertRaisesRegex(ValueError,"SHA"):
            audit(self.path,expected_sha="0"*64)
        sha=self.make([row,row])
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            audit(self.path,expected_sha=sha)

if __name__=="__main__":unittest.main()
