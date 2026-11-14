import unittest
from datetime import datetime,timedelta,timezone
from src.c2_full_source_event_audit import check_rows

class Tests(unittest.TestCase):
    def fixture(self):
        start=datetime(2025,3,1,tzinfo=timezone.utc)
        rows=[]
        for ba in ("AZPS","BPAT","CISO","SRP"):
            for h in range(24):
                missing=ba=="SRP" and h==6
                anomalous=ba=="AZPS" and h==0
                rows.append({"ba":ba,
                    "timestamp_utc_start":(start+timedelta(hours=h)).isoformat(),
                    "demand_mw_raw":"" if missing else "4000",
                    "temperature_c_experimental_area":"22.5",
                    "train_or_validate_eligible":"False",
                    "historical_BA_area_approved":"False",
                    "source_missing_demand":"True" if missing else "False",
                    "demand_spike_candidate":"True" if anomalous else "False"})
        manifest={"utc_start":start.isoformat(),"days":1,
                  "source_BA_hour_slots":96,"source_missing_demand_hours":1,
                  "eia_candidate_anomaly_flags_in_window":1,"paired_source_rows":95}
        return rows,manifest
    def test_flag_remains_candidate_gap_unfilled(self):
        rows,m=self.fixture()
        events,gaps=check_rows(rows,m)
        self.assertEqual(len(events),1)
        self.assertEqual(len(gaps),1)
        self.assertEqual(events[0]["flag_status"],"candidate_needs_review_not_confirmed_error")
        self.assertFalse(events[0]["model_eligible"])
    def test_fabricated_demand_rejected(self):
        rows,m=self.fixture()
        gap=next(r for r in rows if r["source_missing_demand"]=="True")
        gap["demand_mw_raw"]="12"
        with self.assertRaises(ValueError):check_rows(rows,m)
    def test_false_geography_approval_rejected(self):
        rows,m=self.fixture()
        rows[0]["historical_BA_area_approved"]="True"
        with self.assertRaises(ValueError):check_rows(rows,m)
    def test_missing_BA_hour_cannot_be_hidden_by_extra_row(self):
        rows,m=self.fixture()
        rows.pop()
        rows.append({**rows[0],"ba":"SRP"})
        with self.assertRaises(ValueError):check_rows(rows,m)
if __name__=="__main__":unittest.main()
