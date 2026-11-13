import unittest
from src.c2_national_polygon_extract import IDS,NAMES
class Tests(unittest.TestCase):
    def test_expected_id_crosswalk_unique(self):
        self.assertEqual(len(set(IDS.values())),4)
        self.assertEqual(set(IDS),{"AZPS","BPAT","CISO","SRP"})
    def test_name_identity_not_guessed(self):
        self.assertEqual(NAMES["AZPS"],"ARIZONA PUBLIC SERVICE COMPANY")
        self.assertEqual(NAMES["SRP"],"SALT RIVER PROJECT")
if __name__=="__main__":unittest.main()
