"""Tests use synthetic records only and do not claim observed utility measurements."""
import unittest
from scripts.c2_sce_sdge_2020q1_combined_privacy_audit import asnum,summarize_records

class CombinedPrivacySourceTests(unittest.TestCase):
    def test_zero_and_blanks_remain_distinct(self):
        self.assertEqual(asnum("0"),"zero")
        self.assertEqual(asnum(""),"blank")
        self.assertEqual(asnum("."),"non_numeric")
        self.assertEqual(asnum("-1"),"negative")
        self.assertEqual(asnum("1200"),"positive")
    def test_combined_cannot_be_equated_with_zero(self):
        rows=[
            {"zip":"90001","month":"1","year":"2020","class":"Residential","combined":"Y","accounts":"0","kwh":"0"},
            {"zip":"90002","month":"1","year":"2020","class":"Residential","combined":"N","accounts":"10","kwh":"130"},
        ]
        result=summarize_records("SCE",rows)
        self.assertEqual(result["combined_Y_rows"],1)
        self.assertEqual(result["combined_N_rows"],1)
        self.assertFalse(result["strata"][0]["reported_zero_kwh_is_true_zero_verified"])
        self.assertFalse(result["strata"][0]["combined_record_zip_allocation_approved"])
    def test_duplicate_zip_month_class_rejected(self):
        r={"zip":"92101","month":"2","year":"2020","class":"C","combined":"N","accounts":"5","kwh":"10"}
        with self.assertRaisesRegex(ValueError,"duplicate"):
            summarize_records("SDGE",[r,r])
    def test_bad_combined_flag_rejected(self):
        r={"zip":"92101","month":"2","year":"2020","class":"C","combined":"UNKNOWN","accounts":"5","kwh":"10"}
        with self.assertRaisesRegex(ValueError,"Combined"):
            summarize_records("SDGE",[r])
    def test_outside_quarter_rejected(self):
        r={"zip":"92101","month":"12","year":"2020","class":"C","combined":"N","accounts":"5","kwh":"10"}
        with self.assertRaisesRegex(ValueError,"period"):
            summarize_records("SDGE",[r])

if __name__=="__main__":unittest.main()
