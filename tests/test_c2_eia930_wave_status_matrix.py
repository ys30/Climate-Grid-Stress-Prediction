import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from c2_eia930_wave_status_matrix import reconcile

def record(ba, year, ok=True):
    if ok:
        return {"ba": ba, "year": year, "gate_pass": True,
                "status": "artifact_hash_and_annual_gate_pass",
                "csv_sha256": "a"*64, "raw_sha256": "b"*64}
    return {"ba": ba, "year": year, "gate_pass": False,
            "status": "artifact_absent_or_expired"}

class TestStatusMatrix(unittest.TestCase):
    def test_source_only_and_missing_artifact(self):
        docs = [{"cohorts": [record("CISO", 2020), record("AZPS", 2023, False)],
                 "run_id": 123, "run_conclusion": "failure"}]
        rows = reconcile(docs)
        self.assertEqual(len(rows), 24)
        ciso = next(x for x in rows if x["ba"] == "CISO" and x["year"] == 2020)
        azps = next(x for x in rows if x["ba"] == "AZPS" and x["year"] == 2023)
        self.assertTrue(ciso["source_verified"])
        self.assertFalse(ciso["era5_join_verified"])
        self.assertFalse(ciso["model_training_permitted"])
        self.assertEqual(azps["source_status"], "artifact_absent_or_expired")
        self.assertFalse(azps["source_verified"])

    def test_duplicate_wave_claim_rejected(self):
        row = record("SRP", 2025)
        with self.assertRaises(ValueError):
            reconcile([{"cohorts": [row]}, {"cohorts": [row]}])

    def test_non_verified_unlisted(self):
        rows = reconcile([{"cohorts": []}])
        self.assertTrue(all(not x["source_verified"] for x in rows))
        self.assertEqual(rows[0]["source_status"], "unlisted_in_status_files")

if __name__ == "__main__":
    unittest.main()
