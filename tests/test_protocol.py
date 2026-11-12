import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class Phase1ContractTests(unittest.TestCase):
    def test_frozen_c1_pin(self):
        text = (ROOT / "docs" / "SOURCE_AUDIT.md").read_text()
        self.assertIn("6b549a6612f280646389f87bfc35453dd0e5d7dc", text)
    def test_no_outage_prediction_claim(self):
        text = (ROOT / "docs" / "RESEARCH_DESIGN.md").read_text()
        self.assertIn("Not a probability forecast of real blackouts", text)
    def test_explicit_temporal_holdout(self):
        text = (ROOT / "docs" / "RESEARCH_DESIGN.md").read_text()
        self.assertIn("No random hourly split", text)
    def test_source_audit_distinguishes_download(self):
        text = (ROOT / "docs" / "SOURCE_AUDIT.md").read_text()
        self.assertIn("not in Git tree", text)

if __name__ == "__main__":
    unittest.main()
