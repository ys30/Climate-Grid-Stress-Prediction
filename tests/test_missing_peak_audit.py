import unittest,tempfile
from pathlib import Path
from src.c2_missing_peak_audit import inspect

class Tests(unittest.TestCase):
    def test_peak_preserved_and_missing_not_imputed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"data.csv"
            p.write_text("Balancing Authority,UTC Time at End of Hour,Demand (MW)\n"
                "SRP,01/01/2023 01:00:00 AM,1200\n"
                "SRP,01/01/2023 02:00:00 AM,70313\n"
                "SRP,01/01/2023 03:00:00 AM,1250\n")
            qa,a,missing=inspect([p],2023,top_n=3)
            self.assertEqual(next(x for x in qa if x["ba"]=="SRP")["max_raw_demand_mw"],70313)
            spike=next(x for x in a if x["ba"]=="SRP" and x["demand_mw_raw"]==70313)
            self.assertTrue(spike["candidate_spike"])
            self.assertTrue(any(x["reason"]=="missing_source_timestamp" for x in missing))
if __name__=="__main__":unittest.main()
