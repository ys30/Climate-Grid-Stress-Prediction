import unittest
from src.c2_e1_pudl_missing_mwh_filter_audit import classify

def row(observed=True,service="bundled",cls="residential",mwh=None):
    return {"data_observed":observed,"service_type":service,
            "customer_class":cls,"sales_mwh":mwh}

class TestActualSalesMissingnessFilter(unittest.TestCase):
    def test_true_eligible_missing(self):
        self.assertEqual(classify(row()),"04_eligible_bundled_missing_mwh")
    def test_actual_selected(self):
        self.assertEqual(classify(row(mwh=0)),"05_selected_nonmissing_mwh")
    def test_missing_but_unobserved_not_eligible(self):
        self.assertEqual(classify(row(observed=False)),"01_unobserved")
    def test_missing_but_nonbundled_not_eligible(self):
        self.assertEqual(classify(row(service="delivery")),"02_not_bundled")
    def test_aggregate_total_not_eligible(self):
        self.assertEqual(classify(row(cls="total")),"03_total_or_unknown_class")
    def test_boolean_and_none_values(self):
        self.assertEqual(classify(row(observed=None)),"01_unobserved")
        self.assertEqual(classify(row(mwh="")),"04_eligible_bundled_missing_mwh")

if __name__=="__main__":unittest.main()
