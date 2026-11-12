import unittest
from src.c2_hifld_geometry_discovery import candidate_names
class Tests(unittest.TestCase):
    def test_candidate_match_requires_name_review(self):
        f={"type":"FeatureCollection","features":[
            {"type":"Feature","properties":{"NAME":"Salt River Project","ID":"x"},
             "geometry":{"type":"Polygon","coordinates":[]}}]}
        rows=candidate_names(f)
        self.assertEqual(rows[0]["candidate_bas"],["SRP"])
        self.assertTrue(rows[0]["no_auto_mapping"])
    def test_zero_match_not_implicitly_approved(self):
        self.assertEqual(candidate_names({"type":"FeatureCollection","features":[]}),[])
if __name__=="__main__":unittest.main()
