"""Offline contract tests for evidence-only AZPS 2023 diagnostics."""
import unittest
from unittest.mock import patch

from scripts.c2_azps2023_diagnostic_evidence import diagnose, REPO


class AZPSDiagnosticTests(unittest.TestCase):
    @patch("scripts.c2_azps2023_diagnostic_evidence.request")
    def test_pending_diagnostic_is_not_marked_successful(self, get):
        def fake(path, token, **kwargs):
            if "/actions/workflows/" in path:
                return {"workflow_runs": [{"id": 1234, "status": "in_progress"}]}
            if path == f"/repos/{REPO}/actions/runs/1234":
                return {"id": 1234, "status": "in_progress", "html_url": "https://github.com/example"}
            self.fail("Pending workflow must not access artifacts")
        get.side_effect = fake
        answer = diagnose("FAKE_TOKEN")
        self.assertEqual(answer["status"], "diagnostic_run_not_completed")
        self.assertFalse(answer["source_gate_pass"])

    @patch("scripts.c2_azps2023_diagnostic_evidence.request")
    def test_missing_artifact_is_not_a_pass(self, get):
        def fake(path, token, **kwargs):
            if path.endswith("/actions/runs/1234"):
                return {"id": 1234, "status": "completed", "conclusion": "success"}
            if path.endswith("/actions/runs/1234/artifacts?per_page=100"):
                return {"artifacts": []}
            self.fail("Unexpected API path")
        get.side_effect = fake
        a = diagnose("FAKE_TOKEN", run_id=1234)
        self.assertEqual(a["status"], "diagnostic_evidence_absent")
        self.assertFalse(a["source_gate_pass"])

    @patch("scripts.c2_azps2023_diagnostic_evidence.request")
    def test_no_runs_does_not_create_source_gate(self, get):
        get.return_value = {"workflow_runs": []}
        a = diagnose("FAKE_TOKEN")
        self.assertEqual(a["status"], "diagnostic_run_absent")
        self.assertFalse(a["source_gate_pass"])


if __name__ == "__main__":
    unittest.main()
