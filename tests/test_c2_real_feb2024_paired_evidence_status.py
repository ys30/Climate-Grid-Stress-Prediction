"""Guard published February 2024 source-clock diagnostic against scope creep."""
import json
import unittest
from pathlib import Path

STATUS = Path(__file__).resolve().parents[1] / "docs/E2_CISO_ARCO_FEB2024_PAIRED_VERIFIED_STATUS_2026_11_22.json"

class C2FebruaryEvidence(unittest.TestCase):
    def test_source_pinned_and_claims_blocked(self):
        record = json.loads(STATUS.read_text(encoding="utf-8"))
        self.assertEqual(record["expected_hours"], 696)
        self.assertEqual(record["paired_hours"], 696)
        self.assertEqual(record["paired"]["job_conclusion"], "success")
        self.assertEqual(record["paired"]["run_id"], 44764274383)
        self.assertEqual(record["weather"]["source_csv_sha256"],
                         "b572cfd5c2c5df6025f6e4f54b4e4ec97ab261c8c0d53dae1ec18e37b98c9a75")
        for scope in ("model_training_permitted","causal_attribution_permitted","future_projection_permitted"):
            self.assertIs(record[scope], False)
        self.assertIs(record["weather"]["weather_proxy_qualified"], False)
        for path in ("eia","weather"):
            self.assertEqual(len(record[path]["source_csv_sha256"]), 64)
        self.assertEqual(len(record["paired"]["independently_checked_join_csv_sha256"]), 64)

if __name__ == "__main__":
    unittest.main()
