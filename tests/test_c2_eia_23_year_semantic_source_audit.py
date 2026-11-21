"""Fail-closed source-scope tests; original yearly contents checked by live CI."""
import unittest
from pathlib import Path
from scripts.c2_eia_23_year_semantic_source_audit import approved_cohorts,scan

class Canonical23Semantics(unittest.TestCase):
    def test_yearly_authentic_evidence_keys(self):
        d=approved_cohorts(Path("docs"))
        self.assertEqual(len(d),23)
        self.assertNotIn(("AZPS",2023),d)
        self.assertIn(("AZPS",2025),d)
        self.assertEqual(d[("CISO",2021)]["missing_hours"],1)
        self.assertEqual(d[("CISO",2021)]["missing_demand_rows"],5)
        self.assertEqual(d[("CISO",2024)]["expected_hours"],8784)

    def test_missing_a_passing_source_zip_is_hard_fail(self):
        with self.assertRaisesRegex(ValueError,"exact 23"):
            scan({},Path("docs"))

if __name__=="__main__":
    unittest.main()
