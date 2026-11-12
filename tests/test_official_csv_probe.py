import unittest
from src.c2_official_csv_probe import extract_text
class TestOfficialCSV(unittest.TestCase):
    def test_hour_ending_to_hour_start(self):
        csv="Balancing Authority,UTC Time at End of Hour,Demand (MW)\n"
        for ba in ("AZPS","BPAT","CISO","SRP"):
            csv+=f"{ba},07/01/2024 01:00:00 AM,100\n"
        r,rows=extract_text(csv,"2024-07-01T00:00:00+00:00","2024-07-01T00:00:00+00:00")
        self.assertTrue(r["coverage_complete"])
        self.assertEqual(len(rows),4)
    def test_missing_hour_rejected(self):
        s="Balancing Authority,UTC Time at End of Hour,Demand (MW)\nAZPS,07/01/2024 01:00:00 AM,123\n"
        r,_=extract_text(s,"2024-07-01T00:00:00+00:00","2024-07-01T00:00:00+00:00")
        self.assertFalse(r["coverage_complete"])
        self.assertEqual(r["missing_keys"],3)
if __name__=="__main__":unittest.main()
