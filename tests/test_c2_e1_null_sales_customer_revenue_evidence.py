"""Local synthetic source-only reporting evidence tests."""
import unittest
from src.c2_e1_null_sales_customer_revenue_evidence import state,eligible_missing

def row(cls="transportation",customers=12,revenue=20,mwh=None):
    return dict(balancing_authority_code_eia="CISO",report_date="2023-01-01",
      data_observed=True,service_type="bundled",customer_class=cls,
      customers=customers,sales_revenue=revenue,sales_mwh=mwh)

class EvidenceTests(unittest.TestCase):
    def test_positive_zero_missing(self):
        self.assertEqual(state(1),"positive")
        self.assertEqual(state(0),"zero")
        self.assertEqual(state(None),"missing")
    def test_invalid_negative_nonfinite(self):
        self.assertEqual(state(-1),"negative")
        self.assertEqual(state(float("nan")),"invalid")
        self.assertEqual(state(float("inf")),"invalid")
    def test_eligible_non_other_null(self):
        self.assertTrue(eligible_missing(row()))
    def test_other_remains_in_scope(self):
        self.assertTrue(eligible_missing(row(cls="other")))
    def test_not_missing_sales(self):
        self.assertFalse(eligible_missing(row(mwh=0)))
    def test_unobserved_and_nonbundled_excluded(self):
        r=row();r["data_observed"]=False
        self.assertFalse(eligible_missing(r))
        r=row();r["service_type"]="delivery"
        self.assertFalse(eligible_missing(r))
    def test_holdout_other_BA_excluded(self):
        r=row();r["balancing_authority_code_eia"]="ERCO"
        self.assertFalse(eligible_missing(r))

if __name__=="__main__":unittest.main()
