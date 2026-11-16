"""C2 admission regression: source QA screening must never admit E2 model fitting.

Uses only synthetic observations and mocked source ingestion; no true holdout read.
"""
import csv
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from src.c2_episode_quarantine import BAS, training_status, main


class TestFailClosedE2Admission(unittest.TestCase):
    def make_source(self):
        hour = datetime(2023, 6, 1, 0, tzinfo=timezone.utc)
        data = {ba: {} for ba in BAS}
        data["SRP"][hour] = 3000.0
        data["SRP"][hour + timedelta(hours=1)] = 45000.0
        flag = {
            "ba": "SRP",
            "timestamp_utc_start": (hour + timedelta(hours=1)).isoformat(),
            "candidate_reason": "synthetic_spike_only",
        }
        return data, [flag]

    def test_unflagged_source_hour_is_not_model_admitted(self):
        data, flags = self.make_source()
        with patch("src.c2_episode_quarantine.flag_series", return_value=(None, None, flags)):
            rows, source_flags = training_status(data, 2023)
        self.assertEqual(source_flags, flags)
        self.assertEqual(len(rows), 2)
        clean = next(x for x in rows if x["raw_demand_mw"] == 3000.0)
        flagged = next(x for x in rows if x["raw_demand_mw"] == 45000.0)
        self.assertTrue(clean["source_candidate_eligible"])
        self.assertFalse(clean["model_eligible"])
        self.assertFalse(flagged["source_candidate_eligible"])
        self.assertFalse(flagged["model_eligible"])
        self.assertTrue(flagged["quarantine"])
        self.assertFalse(clean["quarantine"])

    def test_written_csv_and_json_never_admit_training(self):
        data, flags = self.make_source()
        with tempfile.TemporaryDirectory() as temp:
            with (patch.object(sys, "argv", [
                "c2_episode_quarantine", "--year", "2023",
                "--source", "synthetic-only.csv", "--out", temp
            ]), patch("src.c2_episode_quarantine.load_records",
                     return_value=(data, [], {"synthetic": True})),
                  patch("src.c2_episode_quarantine.episodes", return_value=[]),
                  patch("src.c2_episode_quarantine.flag_series",
                        return_value=(None, None, flags))):
                main()
            out = Path(temp)
            with (out / "observed_values_with_quarantine.csv").open(newline="") as f:
                csv_rows = list(csv.DictReader(f))
            self.assertEqual(len(csv_rows), 2)
            self.assertEqual(sum(x["source_candidate_eligible"] == "True" for x in csv_rows), 1)
            self.assertTrue(all(x["model_eligible"] == "False" for x in csv_rows))
            summary = json.loads((out / "episode_quarantine_manifest.json").read_text())
            self.assertEqual(summary["source_candidate_eligible_observed_points"], 1)
            self.assertEqual(summary["model_eligible_observed_points"], 0)
            self.assertIs(summary["model_training_permitted"], False)
            self.assertIs(summary["historical_BA_geography_approved"], False)
            self.assertIs(summary["load_relevance_approved"], False)
            self.assertIs(summary["training_executed"], False)
            self.assertIs(summary["imputation_performed"], False)


if __name__ == "__main__":
    unittest.main()
