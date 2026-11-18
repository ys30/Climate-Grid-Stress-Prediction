"""Offline orchestration tests. Synthetic mocks are never called empirical data."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.c2_eia930_batch_intake import run


class BatchIntakeTests(unittest.TestCase):
    def test_24_jobs_dry_run_has_no_network(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("scripts.c2_eia930_batch_intake.collect") as fetch:
                report = run(Path(d), ("CISO", "AZPS", "BPAT", "SRP"),
                             tuple(range(2020, 2026)), "", dry_run=True)
                self.assertEqual(len(report["jobs"]), 24)
                self.assertEqual(report["status"], "dry_run_no_network_no_data")
                fetch.assert_not_called()

    def test_absent_key_fails_before_network(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "EIA_API_KEY"):
                run(Path(d), ("CISO",), (2024,), "")

    def test_invalid_cohort_fails(self):
        with tempfile.TemporaryDirectory() as d:
            for bas, years in [(("CISO", "CISO"), (2024,)),
                                (("WRONG",), (2024,)),
                                (("CISO",), (2024, 2024)),
                                (("CISO",), (2026,))]:
                with self.assertRaises(ValueError):
                    run(Path(d), bas, years, "dummy", dry_run=True)

    def test_existing_output_preflight_prevents_fetch(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            raw = root / "raw" / "eia930_CISO_2024_he.csv"
            raw.parent.mkdir(parents=True)
            raw.write_text("pinned")
            with patch("scripts.c2_eia930_batch_intake.collect") as fetch:
                with self.assertRaises(FileExistsError):
                    run(root, ("CISO",), (2024,), "dummy")
                fetch.assert_not_called()

    @patch("scripts.c2_eia930_batch_intake.convert")
    @patch("scripts.c2_eia930_batch_intake.save")
    @patch("scripts.c2_eia930_batch_intake.collect")
    def test_request_includes_next_year_boundary(self, fetch, save, convert):
        fetch.return_value = [{"ba": "CISO"}]
        save.return_value = {"sha256_csv": "raw", "row_count": 1}
        convert.return_value = {"sha256_csv": "clocked", "row_count": 1}
        with tempfile.TemporaryDirectory() as d:
            report = run(Path(d), ("CISO",), (2024,), "dummy")
            self.assertEqual(report["completed"][0]["clocked_sha256"], "clocked")
        self.assertEqual(fetch.call_args.args[3], "2025-01-01T00")
        self.assertEqual(convert.call_args.kwargs["target_year"], 2024)


if __name__ == "__main__":
    unittest.main()
