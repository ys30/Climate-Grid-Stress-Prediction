import unittest
from src.c2_e1_e2_source_admission_gate import make_gate,verify_abc,verify_census,verify_crosswalk
class Tests(unittest.TestCase):
    def test_absent_sources_fail_closed(self):
        for fn in (verify_abc,verify_census,verify_crosswalk):
            with self.assertRaises((ValueError,FileNotFoundError,NotADirectoryError)):
                fn("/nonexistent/c2-e1-snapshot")
    def test_unapproved_geography_not_automatically_marked_ready(self):
        with self.assertRaises((ValueError,FileNotFoundError)):
            make_gate("/nonexistent/abc","/nonexistent/population","/nonexistent/crosswalk")
if __name__=="__main__":unittest.main()
