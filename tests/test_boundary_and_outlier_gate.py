import unittest,tempfile
from pathlib import Path
from src.c2_boundary_and_outlier_gate import load_records,flag_series

class GateTests(unittest.TestCase):
    def test_uses_previous_halfyear_for_january_boundary(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"prior.csv"
            p.write_text("Balancing Authority,UTC Time at End of Hour,Demand (MW)\nSRP,01/01/2024 01:00:00 AM,4300\n")
            data,conflicts,_=load_records(2024,[p])
            self.assertEqual(len(conflicts),0)
            self.assertEqual(data["SRP"][__import__("datetime").datetime.fromisoformat("2024-01-01T00:00:00+00:00")],4300)
    def test_isolated_spike_quarantined(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"qa.csv"
            p.write_text("Balancing Authority,UTC Time at End of Hour,Demand (MW)\n"
                "SRP,06/03/2023 08:00:00 PM,4597\n"
                "SRP,06/03/2023 09:00:00 PM,70313\n"
                "SRP,06/03/2023 10:00:00 PM,5021\n")
            data,_,_=load_records(2023,[p])
            _,_,flags=flag_series(data,2023)
            self.assertTrue(any(x["raw_mw"]==70313 and x["training_status"]=="hold_until_source_review" for x in flags))
if __name__=="__main__":unittest.main()
