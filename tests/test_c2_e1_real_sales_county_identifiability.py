import unittest,math
from src.c2_e1_real_sales_county_identifiability import analyze

def row(year=2023,ba="AZPS",mwh=10,utility=1,state="AZ"):
    return {"report_date":f"{year}-01-01","balancing_authority_code_eia":ba,
        "data_observed":True,"service_type":"bundled",
        "customer_class":"residential","sales_mwh":mwh,
        "utility_id_eia":utility,"state":state,"business_model":"retail",
        "customers":2}

class IdentifiabilityTests(unittest.TestCase):
    def _complete(self):
        from src.c2_e1_real_sales_county_identifiability import BAS
        records=[];links={}
        for year in range(2020,2024):
            for i,ba in enumerate(BAS):
                for j,n in enumerate((0,1,3)):
                    utility=100+i*3+j
                    records.append(row(year=year,ba=ba,mwh=10*(j+1),utility=utility))
                    links[(year,ba,utility,"AZ")]={"source_county_count":str(n),
                        "utility_multi_BA_source":"False"}
        return records,links
    def test_exact_full_reconciliation(self):
        records,links=self._complete()
        detail,summaries,_=analyze(records,links)
        self.assertEqual(len(summaries),16)
        for s in summaries:
            self.assertEqual(s["selected_observed_bundled_MWh"],60)
            self.assertEqual(s["exactly_one_county_source_MWh"],20)
            self.assertEqual(s["multiple_county_unallocated_MWh"],30)
            self.assertEqual(s["zero_county_source_MWh"],10)
            self.assertFalse(s["model_training_permitted"])
    def test_missing_association_kept_unallocated(self):
        records,links=self._complete()
        records[0]["utility_id_eia"]=99999
        _,summaries,_=analyze(records,links)
        self.assertEqual(summaries[0]["no_utility_source_link_MWh"],10)
    def test_negative_source_fails_closed(self):
        records,links=self._complete()
        records[0]["sales_mwh"]=-1
        with self.assertRaises(ValueError):analyze(records,links)
    def test_missing_mwh_is_excluded_not_imputed(self):
        records,links=self._complete()
        records[0]["sales_mwh"]=None
        _,summaries,_=analyze(records,links)
        self.assertEqual(summaries[0]["selected_observed_bundled_MWh"],50)
if __name__=="__main__":unittest.main()
