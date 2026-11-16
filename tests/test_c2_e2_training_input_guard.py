"""Synthetic checks for source-only admission. No historical holdout is read."""
import csv,json,tempfile,unittest
from pathlib import Path
from src.c2_e2_training_input_guard import verify,EXPECTED_FIELDS,REQUIRED_DENIALS

class TestSourceGate(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.csv=Path(self.t.name)/'obs.csv';self.meta=Path(self.t.name)/'meta.json'
        self.rows=[
         {'year':'2023','ba':'SRP','timestamp_utc_start':'2023-02-26T23:00:00+00:00','raw_demand_mw':'68520','quarantine':'True','reason':'isolated_high','source_candidate_eligible':'False','model_eligible':'False'},
         {'year':'2023','ba':'SRP','timestamp_utc_start':'2023-02-26T22:00:00+00:00','raw_demand_mw':'2958','quarantine':'False','reason':'','source_candidate_eligible':'True','model_eligible':'False'}]
        self.m={k:False for k in REQUIRED_DENIALS}
        self.m.update(raw_observed_points=2,source_candidate_eligible_observed_points=1,
                      quarantined_candidate_points=1,model_eligible_observed_points=0)
        self.write()
    def write(self):
        with self.csv.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=EXPECTED_FIELDS);w.writeheader();w.writerows(self.rows)
        self.meta.write_text(json.dumps(self.m))
    def test_clean_source_still_blocks_training(self):
        result=verify(self.csv,self.meta)
        self.assertFalse(result['training_permitted'])
        self.assertEqual(result['source_candidate_passed'],1)
    def test_forged_true_model_flag_rejected(self):
        self.rows[1]['model_eligible']='True';self.write()
        with self.assertRaisesRegex(ValueError,'Unsafe E2'):verify(self.csv,self.meta)
    def test_missing_gate_field_rejected(self):
        del self.m['load_relevance_approved'];self.write()
        with self.assertRaisesRegex(ValueError,'load_relevance_approved'):verify(self.csv,self.meta)
    def test_duplicate_hour_rejected(self):
        self.rows.append(dict(self.rows[0]));self.write()
        with self.assertRaisesRegex(ValueError,'Duplicate'):verify(self.csv,self.meta)
    def test_candidate_quarantine_conflict_rejected(self):
        self.rows[1]['quarantine']='True';self.write()
        with self.assertRaisesRegex(ValueError,'Conflicting'):verify(self.csv,self.meta)
    def test_manifest_count_mismatch_rejected(self):
        self.m['quarantined_candidate_points']=2;self.write()
        with self.assertRaisesRegex(ValueError,'Quarantine row count'):verify(self.csv,self.meta)

if __name__=='__main__':unittest.main()
