import unittest
from datetime import datetime,timezone,timedelta
from src.c2_episode_quarantine import episodes,training_status
class Tests(unittest.TestCase):
    def test_48_contiguous_hours_same_episode(self):
        year=2024
        first=datetime(year,11,1,tzinfo=timezone.utc)
        data={ba:{} for ba in ("AZPS","BPAT","CISO","SRP")}
        jan=datetime(2024,1,1,tzinfo=timezone.utc)
        for i in range(8784):data["CISO"][jan+timedelta(hours=i)]=1000.
        for i in range(48):data["CISO"][first+timedelta(hours=i)]=None
        e=episodes(data,year)
        self.assertTrue(any(r["ba"]=="CISO" and r["start_utc"]==first.isoformat()
          and r["duration_hours"]>=48 and r["blank_hours"]==48 for r in e))
    def test_peak_candidate_preserves_original_value(self):
        year=2023
        t=datetime(2023,6,3,20,tzinfo=timezone.utc)
        data={ba:{} for ba in ("AZPS","BPAT","CISO","SRP")}
        data["SRP"]={t-timedelta(hours=1):4597.,t:70313.,t+timedelta(hours=1):5021.}
        rows,flags=training_status(data,year)
        val=next(r for r in rows if r["raw_demand_mw"]==70313.)
        self.assertTrue(val["quarantine"])
        self.assertFalse(val["model_eligible"])
if __name__=="__main__":unittest.main()
