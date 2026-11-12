import unittest,tempfile
from pathlib import Path
from src.c2_yearly_coverage import analyze_files,expected_hours

class TestYearlyCoverage(unittest.TestCase):
    def test_leap_year_expected(self):
        self.assertEqual(expected_hours(2024),8784)
        self.assertEqual(expected_hours(2023),8760)
    def test_hour_ending_and_missingness(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"sample.csv"
            f.write_text("Balancing Authority,UTC Time at End of Hour,Demand (MW)\nAZPS,01/01/2024 01:00:00 AM,500\nAZPS,01/01/2024 01:00:00 AM,500\nBPAT,01/01/2024 01:00:00 AM,\n")
            a=analyze_files([f],2024)
            az=next(x for x in a if x["ba"]=="AZPS")
            bp=next(x for x in a if x["ba"]=="BPAT")
            self.assertEqual(az["valid_values"],1)
            self.assertEqual(az["duplicate_keys"],1)
            self.assertEqual(bp["blank_or_invalid"],1)
            self.assertFalse(az["complete"])
    def test_crossyear_boundary_to_interval_start(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"cross.csv"
            f.write_text("Balancing Authority,UTC Time at End of Hour,Demand (MW)\nAZPS,01/01/2025 12:00:00 AM,600\n")
            a=analyze_files([f],2024)
            az=next(x for x in a if x["ba"]=="AZPS")
            self.assertEqual(az["valid_values"],1)
if __name__=="__main__":unittest.main()
