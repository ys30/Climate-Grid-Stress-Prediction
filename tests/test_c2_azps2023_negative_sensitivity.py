"""Synthetic 8760-hour AZPS 2023 sensitivity contract; no observed data in tests."""
import csv
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.c2_azps2023_negative_sensitivity import build, FLAGS, OUTPUT_KIND


class AZPSSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.source = root / "source.csv"
        self.diagnostic = root / "diagnostic.json"
        self.out = root / "sensitivity.csv"
        start = datetime(2023, 1, 1, tzinfo=timezone.utc)
        fields = ["ba", "timestamp_utc", "demand_mw", "original_source_he_utc"]
        with self.source.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for hour in range(8760):
                ts = start + timedelta(hours=hour)
                label = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
                w.writerow({"ba": "AZPS", "timestamp_utc": label,
                            "demand_mw": FLAGS.get(label, "1200"),
                            "original_source_he_utc": (ts + timedelta(hours=1)).strftime("%Y-%m-%dT%H")})
        self.sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        self.source.with_suffix(".manifest.json").write_text(json.dumps({
            "source_kind": "derived_from_official_EIA_930_API",
            "target_year": 2023, "clock_conversion": "UTC_hour_ending_minus_one_hour",
            "sha256_csv": self.sha
        }))
        self.diag = {
            "utc_start_sha256": self.sha, "source_gate_pass": False,
            "annual_audit_pass": False, "invalid_numeric_rows": 2,
            "anomalies_max20": [{"timestamp_utc": k, "reported_demand_mw": v} for k, v in FLAGS.items()]
        }
        self.diagnostic.write_text(json.dumps(self.diag))

    def run_builder(self):
        with patch("scripts.c2_azps2023_negative_sensitivity.SOURCE_SHA", self.sha):
            return build(self.source, self.diagnostic, self.out)

    def test_excludes_only_two_registered_anomalies_and_preserves_original(self):
        initial = self.source.read_bytes()
        result = self.run_builder()
        self.assertEqual(result["source_kind"], OUTPUT_KIND)
        self.assertFalse(result["canonical_source_gate_pass"])
        self.assertEqual(result["retained_real_hourly_rows"], 8758)
        self.assertEqual(len(result["excluded_real_hourly_rows"]), 2)
        self.assertEqual(self.source.read_bytes(), initial)
        with self.out.open(newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 8758)
        self.assertFalse(any(r["timestamp_utc"] in FLAGS for r in rows))
        self.assertTrue(self.out.with_suffix(".manifest.json").exists())

    def test_rejects_undocumented_additional_negative_hour(self):
        rows = list(csv.DictReader(self.source.open(newline="")))
        rows[0]["demand_mw"] = "-5"
        with self.source.open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        new_sha = hashlib.sha256(self.source.read_bytes()).hexdigest()
        manifest_path = self.source.with_suffix(".manifest.json")
        m = json.loads(manifest_path.read_text())
        m["sha256_csv"] = new_sha
        manifest_path.write_text(json.dumps(m))
        diag = json.loads(self.diagnostic.read_text())
        diag["utc_start_sha256"] = new_sha
        self.diagnostic.write_text(json.dumps(diag))
        with patch("scripts.c2_azps2023_negative_sensitivity.SOURCE_SHA", new_sha):
            with self.assertRaisesRegex(ValueError, "Unexpected extra abnormal"):
                build(self.source, self.diagnostic, self.out)

    def test_refuses_diagnosis_that_claims_gate_passed(self):
        self.diag["source_gate_pass"] = True
        self.diagnostic.write_text(json.dumps(self.diag))
        with self.assertRaisesRegex(ValueError, "Independent diagnosis"):
            self.run_builder()

    def test_refuses_overwrite(self):
        self.out.write_text("existing")
        with self.assertRaises(FileExistsError):
            self.run_builder()


if __name__ == "__main__":
    unittest.main()
