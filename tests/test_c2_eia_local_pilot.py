"""Offline tests of key-file runner; do not include real credentials."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.c2_eia_local_pilot import run


class LocalPilotTests(unittest.TestCase):
    def test_key_is_not_in_command_arguments_or_returned_report(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            key = root / "API.txt"
            key.write_text("FAKE_TEST_TOKEN_ONLY\n")
            output = root / "evidence"
            calls = []
            def fake_call(command, *, env, check):
                self.assertTrue(check)
                self.assertEqual(env.get("EIA_API_KEY"), "FAKE_TEST_TOKEN_ONLY")
                self.assertNotIn("FAKE_TEST_TOKEN_ONLY", " ".join(command))
                calls.append(command)
                if any("c2_eia930_year_coverage_gate" in arg for arg in command):
                    report = output / "audit" / "eia930_CISO_2024_coverage.json"
                    report.write_text(json.dumps({"pass": True, "coverage": 1.0}))
            with patch("scripts.c2_eia_local_pilot.subprocess.run", side_effect=fake_call):
                response = run(key, "CISO", 2024, output)
            self.assertEqual(len(calls), 3)
            self.assertTrue(response["coverage_gate_pass"])
            self.assertNotIn("FAKE_TEST_TOKEN_ONLY", str(response))

    def test_missing_or_multiline_key_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            key = root / "API.txt"
            for content in ("", "abc def"):
                key.write_text(content)
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    run(key, "CISO", 2024, root / "out")

    def test_existing_output_rejected_before_network(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            key = root / "API.txt"
            key.write_text("FAKE_TEST_TOKEN_ONLY")
            out = root / "evidence"
            existing = out / "raw" / "eia930_CISO_2024_he.csv"
            existing.parent.mkdir(parents=True)
            existing.write_text("preserved")
            with patch("scripts.c2_eia_local_pilot.subprocess.run") as shell:
                with self.assertRaises(FileExistsError):
                    run(key, "CISO", 2024, out)
                shell.assert_not_called()


if __name__ == "__main__":
    unittest.main()
