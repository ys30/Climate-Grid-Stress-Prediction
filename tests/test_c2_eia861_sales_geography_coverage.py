"""Synthetic tests for annual EIA861 sales association coverage; no real load admitted."""
import unittest
from src.c2_eia861_sales_geography_coverage import analyze

def make(ba="AZPS",uid=1,mwh=100,customers=5,customer_class="residential",
         service_type="bundled",data_observed=True,business_model="retail"):
    return {"utility_id_eia":uid,"state":"AZ","report_date":"2023-01-01",
       "balancing_authority_code_eia":ba,"customer_class":customer_class,
       "business_model":business_model,"service_type":service_type,
       "data_observed":data_observed,"sales_mwh":mwh,"customers":customers}

class TestSourceCoverage(unittest.TestCase):
    def setUp(self):
        self.bridge={(2023,"AZPS",1,"AZ"):{"utility_counties_reported":"2"},
                     (2023,"AZPS",2,"AZ"):{"utility_counties_reported":"0"}}
    def test_match_and_unmatched_mwh_and_customers(self):
        data=[make(uid=1,mwh=100),make(uid=2,mwh=50,customer_class="industrial"),
              make(uid=3,mwh=25,customer_class="commercial")]
        detail,summary,_=analyze(self.bridge,data)
        self.assertEqual(len(detail),3)
        self.assertEqual(summary[0]["selected_observed_bundled_sales_mwh"],175)
        self.assertEqual(summary[0]["county_matched_sales_mwh"],100)
        self.assertAlmostEqual(summary[0]["county_matched_share_of_selected_sales"],100/175)
        self.assertEqual(summary[0]["selected_observed_customers"],15)
        self.assertFalse(summary[0]["model_training_permitted"])
    def test_missing_customers_not_invented_as_zero(self):
        _,summary,_=analyze(self.bridge,[make(customers=None)])
        self.assertFalse(summary[0]["customer_coverage_computable"])
        self.assertIsNone(summary[0]["selected_observed_customers"])
    def test_aggregate_total_and_unobserved_excluded(self):
        _,summary,exc=analyze(self.bridge,[make(mwh=100),make(mwh=999,customer_class="total"),
                       make(mwh=800,customer_class="commercial",data_observed=False)])
        self.assertEqual(summary[0]["selected_observed_bundled_sales_mwh"],100)
        self.assertEqual(exc["aggregate_or_unknown_customer_class"],1)
        self.assertEqual(exc["not_observed"],1)
    def test_nonbundled_excluded(self):
        _,summary,exc=analyze(self.bridge,[make(),make(service_type="delivery",customer_class="industrial")])
        self.assertEqual(summary[0]["selected_observed_bundled_sales_mwh"],100)
        self.assertEqual(exc["not_bundled"],1)
    def test_duplicate_primary_key_rejected(self):
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            analyze(self.bridge,[make(),make()])
    def test_negative_or_nan_rejected(self):
        for value in (-1,float("nan"),float("inf")):
            with self.subTest(value=value),self.assertRaisesRegex(ValueError,"Invalid"):
                analyze(self.bridge,[make(mwh=value)])
    def test_nonexclusive_county_source_is_not_credited_as_strict_matched(self):
        overlapping_bridge={(2023,"AZPS",1,"AZ"):
             {"utility_counties_reported":"2","nonexclusive_utility_state_ba":True},
            (2023,"AZPS",2,"AZ"):
             {"utility_counties_reported":"2","nonexclusive_utility_state_ba":False}}
        _,summary,_=analyze(overlapping_bridge,[
            make(uid=1,mwh=100),
            make(uid=2,mwh=50,customer_class="industrial")])
        r=summary[0]
        self.assertEqual(r["selected_observed_bundled_sales_mwh"],150)
        self.assertEqual(r["county_matched_sales_mwh"],50)
        self.assertEqual(r["nonexclusive_source_association_sales_mwh"],100)
        self.assertEqual(r["county_matched_but_nonexclusive_sales_mwh"],100)
        self.assertEqual(r["county_matched_including_nonexclusive_sales_mwh"],150)
        self.assertFalse(r["nonexclusive_source_allocation_is_verified"])

    def test_business_models_separated(self):
        _,summaries,_=analyze(self.bridge,[make(business_model="retail"),
                        make(business_model="other",customer_class="industrial")])
        self.assertEqual(len(summaries),2)
        self.assertEqual(sum(x["selected_observed_bundled_sales_mwh"] for x in summaries),200)

if __name__=="__main__":unittest.main()
