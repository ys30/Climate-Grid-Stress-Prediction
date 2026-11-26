"""Tests for the fail-closed C2 validated audit entrypoint."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from scripts.c2_run_validated_audit import run

HEADERS = ("ba", "date", "target", "estimator", "event_category",
           "episode_id", "actual_mw", "calendar_pred_mw", "weather_pred_mw")


def make_rows():
    return [
        dict(ba="SRP", date="2025-07-0"+str(d), target="peak",
             estimator=model, event_category="observed_high_load",
             episode_id="SRP-2025-E01", actual_mw="1000",
             calendar_pred_mw="800", weather_pred_mw="900")
        for d in (1, 2) for model in ("Huber", "Ridge")
    ]


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)


class TestValidatedAudit(unittest.TestCase):
    def test_valid_pair_creates_hashed_manifest_and_metrics(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)/"input.csv"
            out = Path(root)/"out"
            write_csv(source, make_rows())
            result = run(source, out, bootstrap=5)
            self.assertTrue(result["integrity_passed"])
            self.assertEqual(len(result["input_sha256"]), 64)
            self.assertEqual(result["episodes"], 2)
            self.assertTrue((out/"episode_duration_metrics.csv").exists())
            manifest = json.loads((out/"audit_manifest.json").read_text())
            self.assertEqual(result["input_sha256"], manifest["input_sha256"])
            self.assertEqual(result["evidence_level"], "retrospective_nonblind_observed_weather")

    def test_refuses_overwriting_previous_metrics(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)/'input.csv'
            out = Path(root)/'out'
            write_csv(source, make_rows())
            run(source, out, bootstrap=0)
            with self.assertRaisesRegex(ValueError, 'OUTPUT EXISTS'):
                run(source, out, bootstrap=0)
    def test_missing_one_model_fails_before_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)/"input.csv"
            out = Path(root)/"out"
            write_csv(source, [r for r in make_rows() if r["estimator"] == "Ridge"])
            with self.assertRaisesRegex(ValueError, "INTEGRITY FAILED"):
                run(source, out)
            self.assertFalse(out.exists())

    def test_mismatched_actual_fails_before_outputs(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)/"input.csv"
            out = Path(root)/"out"
            rows = make_rows()
            rows[1]["actual_mw"] = "2000"
            write_csv(source, rows)
            with self.assertRaisesRegex(ValueError, "actual_mw differs"):
                run(source, out)
            self.assertFalse(out.exists())

if __name__ == "__main__":
    unittest.main()
