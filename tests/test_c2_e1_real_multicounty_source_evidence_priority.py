import unittest
from src.c2_e1_real_multicounty_source_evidence_priority import rank
class SourcePriorityTests(unittest.TestCase):
    def fixtures(self):
        sales=[];annual=[]
        for ba in ("AZPS","BPAT","CISO","SRP"):
            for y in range(2020,2024):
                annual.append({"BA":ba,"year":str(y),"multi_county_unallocated_MWh":"30"})
                for utility,mwh in ((10,20.0),(20,10.0)):
                    sales.append({"BA":ba,"year":str(y),"utility_id_eia":str(utility),
                      "state":"AZ","source_status":"ambiguous_multi",
                      "county_support_cardinality":"3",
                      "utility_nonexclusive_BA_source":"False",
                      "actual_sales_mwh":str(mwh)})
        return sales,annual
    def test_concentration_ranking(self):
        rows,summary=self.fixtures();r,c,n=rank(rows,summary)
        self.assertEqual(n,32)
        x=next(v for v in r if v["BA"]=="AZPS")
        self.assertEqual(x["utility_id_eia"],10)
        self.assertAlmostEqual(x["share_of_BA_multi_county_observed_MWh"],2/3)
        self.assertFalse(x["county_allocation_identified"])
        self.assertEqual(next(v for v in c if v["BA"]=="SRP" and v["top_k"]==3)["top_k_fraction_of_BA_multi_county_source_MWh"],1)
    def test_nonexclusive_multicounty_fails_closed(self):
        rows,summary=self.fixtures();rows[0]["utility_nonexclusive_BA_source"]="True"
        with self.assertRaises(ValueError):rank(rows,summary)
    def test_independent_BA_year_control_fails(self):
        rows,summary=self.fixtures();summary[0]["multi_county_unallocated_MWh"]="31"
        with self.assertRaisesRegex(ValueError,"total mismatch"):rank(rows,summary)
if __name__=="__main__":unittest.main()
