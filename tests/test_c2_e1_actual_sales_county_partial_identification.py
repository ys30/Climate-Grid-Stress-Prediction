import unittest
from src.c2_e1_actual_sales_county_partial_identification import aggregate,BAS

def sale(y,ba,u,v):
    return {"report_date":f"{y}-01-01","balancing_authority_code_eia":ba,
        "data_observed":True,"service_type":"bundled","customer_class":"residential",
        "sales_mwh":v,"utility_id_eia":u,"state":"AZ"}
class BoundsTests(unittest.TestCase):
    def fixture(self):
        rec=[];links={}
        for y in range(2020,2024):
            for i,ba in enumerate(BAS):
                for j,(fs,v) in enumerate(((("04013",),10.0),(("04013","04021"),30.0),((),7.0))):
                    u=i*10+j+100;rec.append(sale(y,ba,u,v))
                    links[y,ba,u,"AZ"]=(fs,False)
        return rec,links
    def test_conditional_marginal_limits_are_not_weights(self):
        rec,links=self.fixture()
        d,c,s=aggregate(rec,links)
        self.assertEqual(len(s),16)
        for summary in s:
            self.assertEqual(summary["actual_selected_annual_sales_MWh"],47)
            self.assertEqual(summary["county_lower_bounds_sum_MWh"],10)
        row=next(r for r in c if r["year"]==2020 and r["BA"]=="AZPS" and r["county_FIPS"]=="04013")
        self.assertEqual(row["conditional_marginal_lower_MWh"],10)
        self.assertEqual(row["conditional_marginal_upper_MWh"],40)
        self.assertFalse(row["bounds_are_jointly_independent"])
    def test_no_county_source_never_allocated(self):
        rec,links=self.fixture()
        _,c,_=aggregate(rec,links)
        r=next(x for x in c if x["year"]==2020 and x["BA"]=="AZPS" and x["county_FIPS"]=="04021")
        self.assertEqual(r["conditional_marginal_lower_MWh"],0)
        self.assertEqual(r["conditional_marginal_upper_MWh"],30)
    def test_negative_MWh_fails(self):
        rec,links=self.fixture();rec[0]["sales_mwh"]=-1
        with self.assertRaises(ValueError):aggregate(rec,links)
if __name__=="__main__":unittest.main()
