import unittest
from src.c2_eia930_probe import summarize, build_url

class TestEIAProbe(unittest.TestCase):
    def test_complete_day(self):
        rows = [{"period": f"2024-07-01T{h:02d}", "value": "120", "respondent": "CISO", "type": "D"} for h in range(1,24)]
        rows.append({"period": "2024-07-02T00", "value": "130", "respondent": "CISO", "type": "D"})
        got = summarize(rows, "2024-07-01T01", "2024-07-02T00")
        self.assertTrue(got["coverage_complete"])
    def test_null_and_missing_not_imputed(self):
        got = summarize([{"period": "2024-07-01T01", "value": None}], "2024-07-01T01", "2024-07-01T02")
        self.assertFalse(got["coverage_complete"])
        self.assertEqual(got["missing_expected_hours"], 1)
    def test_url_no_key(self):
        url = build_url("2024-07-01T01", "2024-07-02T00", "CISO")
        self.assertIn("region-data/data", url)
        self.assertIn("respondent", url)
if __name__ == "__main__":
    unittest.main()
