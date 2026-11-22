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


    def test_standalone_ciso_and_azps_negative_demand_gate(self):
        docs = [{"cohorts": [{"ba": "AZPS", "year": 2023,
                 "status": "artifact_absent_or_expired", "gate_pass": False}]}]
        standalone = [{"ba": "CISO", "year": 2024,
                       "source_gate_pass": True,
                       "status": "standalone_artifact_hash_and_annual_gate_pass",
                       "raw_sha256": "a"*64, "csv_sha256": "b"*64,
                       "evidence_document": "docs/source.md"}]
        diagnostic = {"ba": "AZPS", "year": 2023,
                      "source_gate_pass": False, "invalid_numeric_rows": 2}
        rows = reconcile(docs, standalone, diagnostic)
        ciso = next(r for r in rows if r["ba"]=="CISO" and r["year"]==2024)
        azps = next(r for r in rows if r["ba"]=="AZPS" and r["year"]==2023)
        self.assertTrue(ciso["source_verified"])
        self.assertFalse(azps["source_verified"])
        self.assertEqual(azps["source_status"], "authenticated_negative_demand_strict_gate_failed")
        self.assertTrue(all(not r["model_training_permitted"] for r in rows))

    def test_standalone_cannot_override_wave(self):
        docs = [{"cohorts": [record("CISO", 2024)]}]
        standalone = [{"ba": "CISO", "year": 2024}]
        with self.assertRaises(ValueError):
            reconcile(docs, standalone)

if __name__ == "__main__":
    unittest.main()
