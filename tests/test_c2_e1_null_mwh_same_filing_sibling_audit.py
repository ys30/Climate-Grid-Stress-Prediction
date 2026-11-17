import unittest
from src.c2_e1_null_mwh_same_filing_sibling_audit import audit

def row(cls,mwh,ba="CISO",observed=True,utility=1,year="2023-01-01"):
    return {"utility_id_eia":utility,"state":"CA","report_date":year,
      "balancing_authority_code_eia":ba,"business_model":"retail",
      "service_type":"bundled","data_observed":observed,
      "customer_class":cls,"sales_mwh":mwh,"customers":None,
      "sales_revenue":None}

class TestSiblingEvidence(unittest.TestCase):
    def test_same_grain_positive_sibling_distinction(self):
        # Audit enforces original complete source counts; use the exact full
        # expected class distribution with synthetic sibling examples.
        rows=[]
        counts={"other":709,"transportation":386,"industrial":127,"commercial":52,"residential":47}
        for cls,n in counts.items():
            for i in range(n):
                rows.append(row(cls,None,utility=10000+len(rows)))
        rows.append(row("commercial",12,utility=10000))
        rows.append(row("residential",0,utility=10001))
        summary,detail=audit(rows)
        self.assertEqual(len(detail),1321)
        self.assertTrue(detail[0]["other_class_positive_sales_same_filing"])
        self.assertFalse(detail[1]["other_class_positive_sales_same_filing"])
        self.assertTrue(detail[1]["other_class_nonnull_sales_same_filing"])
        self.assertEqual(sum(s["positive_sibling_sales_same_filing"] for s in summary),1)
        self.assertFalse(summary[0]["original_raw_filing_slot_verified"])
    def test_imputed_or_other_BA_sibling_not_accepted(self):
        # Does not match original positive sibling because imputed or other BA
        rows=[]
        counts={"other":709,"transportation":386,"industrial":127,"commercial":52,"residential":47}
        for cls,n in counts.items():
            for i in range(n):
                rows.append(row(cls,None,utility=10000+len(rows)))
        rows.append(row("commercial",100,utility=10000,observed=False))
        rows.append(row("industrial",90,utility=10001,ba="ERCO"))
        summary,_=audit(rows)
        self.assertEqual(sum(s["positive_sibling_sales_same_filing"] for s in summary),0)

if __name__=="__main__":unittest.main()
