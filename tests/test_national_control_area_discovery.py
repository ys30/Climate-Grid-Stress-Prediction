import unittest
from src.c2_national_control_area_discovery import match_names,TARGETS
class Tests(unittest.TestCase):
    def test_four_names_not_inferred_from_unrelated_remarks(self):
        attrs={"NAME":"Arizona Public Service Company","OBJECTID":7}
        self.assertEqual(match_names(attrs)[0]["ba_candidate"],"AZPS")
        self.assertEqual(match_names({"REMARKS":"SALT RIVER PROJECT", "NAME":"Unknown"}),[])
    def test_four_candidates_patterns(self):
        for code,name in [("BPAT","BONNEVILLE POWER ADMINISTRATION"),("CISO","CALIFORNIA INDEPENDENT SYSTEM OPERATOR"),("SRP","SALT RIVER PROJECT")]:
            self.assertEqual(match_names({"NAME":name})[0]["ba_candidate"],code)
if __name__=="__main__":unittest.main()
