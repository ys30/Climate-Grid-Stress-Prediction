"""Offline regression tests for Wave 1 evidence freshness and fail-closed status."""
import unittest
from unittest.mock import patch

from scripts.c2_eia_wave1_artifact_audit import get_latest_run, report, REPO, WORKFLOW, WAVE_CONFIG


class Wave1FreshnessTests(unittest.TestCase):
    @patch("scripts.c2_eia_wave1_artifact_audit.request")
    def test_latest_queued_run_not_replaced_by_old_success(self, request):
        request.return_value = {"workflow_runs": [
            {"id": 222, "status": "queued", "head_sha": "new"},
            {"id": 111, "status": "completed", "conclusion": "success", "head_sha": "old"},
        ]}
        found = get_latest_run("FAKE_TEST_TOKEN")
        self.assertEqual(found["id"], 222)

    @patch("scripts.c2_eia_wave1_artifact_audit.request")
    def test_pending_run_does_not_get_artifacts_from_old_run(self, request):
        def fake(path, token, **kwargs):
            if "/actions/workflows/" in path:
                return {"workflow_runs": [{"id": 222, "status": "in_progress"}]}
            if path == f"/repos/{REPO}/actions/runs/222":
                return {"id": 222, "status": "in_progress", "head_sha": "sha_new",
                        "run_attempt": 1, "html_url": "https://github.com/example/actions/runs/222"}
            self.fail("No job/artifact requests allowed for pending run")
        request.side_effect = fake
        result = report("FAKE_TEST_TOKEN")
        self.assertEqual(result["status"], "wave1_not_yet_completed")
        self.assertEqual(result["run_id"], 222)
        self.assertEqual(result["head_sha"], "sha_new")
        self.assertEqual(result["verified_ba_years"], 0)

    def test_wave2_matrix_is_six_nonduplicated_cohorts(self):
        workflow, expected = WAVE_CONFIG["wave2"]
        self.assertEqual(workflow, "c2-eia-expansion-wave2.yml")
        self.assertEqual(len(expected), 6)
        self.assertNotIn(("CISO", 2024), expected)
        self.assertIn(("SRP", 2021), expected)

    @patch("scripts.c2_eia_wave1_artifact_audit.request")
    def test_wave2_pending_labels_are_not_wave1(self, request):
        def fake(path, token, **kwargs):
            if "/actions/workflows/" in path:
                return {"workflow_runs": [{"id": 333, "status": "queued"}]}
            if path.endswith("/actions/runs/333"):
                return {"id": 333, "status": "queued", "head_sha": "new"}
            self.fail("Unexpected artifact access on queued Wave 2")
        request.side_effect = fake
        result = report("FAKE_TEST_TOKEN", wave="wave2")
        self.assertEqual(result["status"], "wave2_not_yet_completed")
        self.assertEqual(result["expected_ba_years"], 6)

    @patch("scripts.c2_eia_wave1_artifact_audit.request")
    def test_no_runs_no_invented_progress(self, request):
        request.return_value = {"workflow_runs": []}
        r = report("FAKE_TEST_TOKEN")
        self.assertEqual(r["status"], "no_completed_wave1_run")
        self.assertNotIn("run_id", r)


if __name__ == "__main__":
    unittest.main()
