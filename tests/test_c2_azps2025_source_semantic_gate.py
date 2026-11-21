"""Offline synthetic unit tests; no real EIA data are fabricated as observations."""
import unittest
from scripts.c2_azps2025_source_semantic_gate import source_value_flags,LOW_REVIEW_MW

class AZPSSemanticTests(unittest.TestCase):
    def test_zero_is_official_anomaly_category(self):
        self.assertEqual(source_value_flags(0),["eia_zero_demand_anomaly"])

    def test_low_positive_is_only_provisional_review(self):
        self.assertEqual(source_value_flags(273),["exploratory_low_positive_review_only"])
        self.assertEqual(source_value_flags(485),["exploratory_low_positive_review_only"])
        self.assertEqual(source_value_flags(LOW_REVIEW_MW),[])
        self.assertEqual(source_value_flags(6600),[])

    def test_negative_and_nonfinite_must_fail(self):
        for bad in (-1,float("nan"),float("inf")):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    source_value_flags(bad)

if __name__=="__main__":unittest.main()
