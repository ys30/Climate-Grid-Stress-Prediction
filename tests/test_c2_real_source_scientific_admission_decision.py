"""C2 real-source scientific admission must fail closed; synthetic-only fixtures."""
import json,tempfile,unittest,zipfile
from pathlib import Path
from unittest.mock import patch

from scripts.c2_real_source_scientific_admission_decision import summarize,REAL_SEMANTIC_MEMBER

class RealSourceAdmissionTests(unittest.TestCase):
    def setup_artifact(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root=Path(tmp.name)
        rows=[{"ba":"AZPS","year":y,"expected_hours":1} for y in range(2020,2026)]
        rows+=[{"ba":b,"year":y,"expected_hours":1} for b in ("BPAT","CISO","SRP") for y in range(2020,2026)]
        rows=[r for r in rows if not (r["ba"]=="AZPS" and r["year"]==2023)]
        rows[0]["expected_hours"]+=201672-len(rows)
        d={"BA_years":23,"expected_hours":201672,"observed_hours":201671,
           "absent_time_keys":1,"null_demand_rows":210,
           "zero_demand_hours":1,"exploratory_low_positive_hours":2,
           "historical_BA_geography_approved":False,"model_training_permitted":False,
           "per_BA_year":rows,
           "review_rows":[
             {"timestamp_utc":"2025-07-31T19:00:00Z","reported_demand_mw":0.0},
             {"timestamp_utc":"2025-07-31T21:00:00Z","reported_demand_mw":273.0},
             {"timestamp_utc":"2025-07-31T22:00:00Z","reported_demand_mw":485.0}]}
        raw=json.dumps(d).encode()
        import hashlib
        p=root/"art.zip"
        with zipfile.ZipFile(p,"w") as z:
            z.writestr(REAL_SEMANTIC_MEMBER,raw)
        return p,hashlib.sha256(raw).hexdigest(),d

    def test_source_semantics_does_not_override_geography_and_holdout(self):
        p,checksum,_=self.setup_artifact()
        with patch("scripts.c2_real_source_scientific_admission_decision.REAL_SEMANTIC_JSON_SHA",checksum):
            d=summarize(p,Path("."))
        self.assertFalse(d["model_training_permitted"])
        self.assertFalse(d["future_SSP_PyPSA_stress_claims_permitted"])
        self.assertEqual(len(d["mandatory_scientific_gates"]),3)
        self.assertTrue(all(not v["cleared"] for v in d["mandatory_scientific_gates"]))
        self.assertEqual(d["verified_observed_source"]["source_canonical_years_pass"],23)
        geo=d["independent_geography_and_load_relevance"]
        self.assertTrue(geo["actual_2020_2023_sales_MWh_source_available"])
        self.assertEqual(geo["actual_2020_2023_selected_retail_sales_mwh"],924201242)
        self.assertEqual(geo["actual_2020_2023_multicounty_not_uniquely_allocated_mwh"],757691947)
        self.assertEqual(geo["actual_2020_2023_no_source_county_mwh"],20217011)
        self.assertEqual(geo["actual_2020_2023_one_county_support_conditional_mwh"],146292284)
        self.assertEqual(sum((geo["actual_2020_2023_multicounty_not_uniquely_allocated_mwh"],
                              geo["actual_2020_2023_no_source_county_mwh"],
                              geo["actual_2020_2023_one_county_support_conditional_mwh"])),924201242)
        self.assertFalse(geo["actual_MWh_per_county_observed"])
        self.assertFalse(geo["actual_hourly_BA_load_grid_weights_observed"])

    def test_tampered_pinned_source_rejected(self):
        p,checksum,_=self.setup_artifact()
        with self.assertRaisesRegex(ValueError,"changed"):
            summarize(p,Path("."))

    def test_modified_candidate_values_cannot_silently_be_accepted(self):
        p,_,d=self.setup_artifact()
        d["review_rows"][0]["reported_demand_mw"]=6600
        raw=json.dumps(d).encode()
        import hashlib
        with zipfile.ZipFile(p,"w") as z:
            z.writestr(REAL_SEMANTIC_MEMBER,raw)
        with patch("scripts.c2_real_source_scientific_admission_decision.REAL_SEMANTIC_JSON_SHA",hashlib.sha256(raw).hexdigest()):
            with self.assertRaisesRegex(ValueError,"review values changed"):
                summarize(p,Path("."))

if __name__=="__main__":unittest.main()
