"""Source revision prioritization tests with synthetic data only."""
import csv,hashlib,tempfile,unittest
from pathlib import Path
from scripts.c2_eia_revision_priority_review import screen

FIELDS=["ba","year","timestamp_utc","classification",
        "frozen_eia930_demand_mw","new_api_eia930_demand_mw","delta_mw"]

class SourceRevisionScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name)
        self.src=root/"changes.csv"
        self.out=root/"priority.json"

    def write(self,rows):
        with self.src.open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=FIELDS)
            w.writeheader();w.writerows(rows)
        return hashlib.sha256(self.src.read_bytes()).hexdigest()

    def test_large_revision_and_zero_not_a_model_admission(self):
        sha=self.write([{"ba":"AZPS","year":"2025","timestamp_utc":"2025-07-31T19:00:00Z",
          "classification":"numeric_changed","frozen_eia930_demand_mw":"6569",
          "new_api_eia930_demand_mw":"0","delta_mw":"-6569"}])
        d=screen(self.src,self.out,expected_sha=sha)
        self.assertEqual(d["counts"]["high_impact_1000mw"],1)
        self.assertEqual(d["counts"]["new_zero_demand_after_positive"],1)
        self.assertFalse(d["model_training_permitted"])
        self.assertFalse(d["source_error_proven"])
        self.assertFalse(d["source_values_replaced"])
        with self.assertRaises(FileExistsError):
            screen(self.src,self.out,expected_sha=sha)

    def test_invalid_delta_or_changed_source_rejected(self):
        sha=self.write([{"ba":"BPAT","year":"2021","timestamp_utc":"2021-11-07T03:00:00Z",
          "classification":"numeric_changed","frozen_eia930_demand_mw":"6635",
          "new_api_eia930_demand_mw":"8003","delta_mw":"1370"}])
        with self.assertRaisesRegex(ValueError,"arithmetic"):
            screen(self.src,self.out,expected_sha=sha)
        with self.assertRaisesRegex(ValueError,"SHA"):
            screen(self.src,self.out,expected_sha="0"*64)

if __name__=="__main__":unittest.main()
