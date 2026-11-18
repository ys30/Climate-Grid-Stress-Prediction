import unittest
from src.c2_e1_2020_2023_strict_raw_sales_disambiguation import strict

def r(member="Sales_Ult_Cust_2023.xlsx",sheet="States",part="A",
      service="Bundled",dtype="O",state="CA",ba="CISO"):
    import json
    cells=["2023","17609","Southern California Edison",part,service,dtype,
           state,"Investor Owned",ba]
    return {"year":"2023","utility_id_eia":"17609","state":"CA",
            "BA":"CISO","archive_member":member,"sheet":sheet,
            "raw_values_json":json.dumps(cells)}

class OriginalSalesDisambiguationTests(unittest.TestCase):
    def test_true_bundled_states_is_accepted(self):
        self.assertTrue(strict(r()))
    def test_delivery_is_rejected(self):
        self.assertFalse(strict(r(part="C",service="Delivery")))
    def test_decoupled_sheet_rejected(self):
        self.assertFalse(strict(r(sheet="Decoupled")))
    def test_customer_sited_workbook_rejected(self):
        self.assertFalse(strict(r(member="Sales_Ult_Cust_CS_2023.xlsx")))
    def test_other_BA_rejected(self):
        self.assertFalse(strict(r(ba="AZPS")))
    def test_imputed_status_rejected(self):
        self.assertFalse(strict(r(dtype="I")))
    def test_wrong_state_rejected(self):
        self.assertFalse(strict(r(state="AZ")))
if __name__=="__main__":unittest.main()
