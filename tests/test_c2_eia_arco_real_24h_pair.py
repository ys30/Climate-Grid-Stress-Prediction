"""Synthetic ZIP-only contract for real EIA–ARCO one-day pairing.

This test does not replace or claim actual observed source data.
"""
import csv
import hashlib
import io
import json
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.c2_eia_arco_real_24h_pair import pair


class RealPairContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.eia = root / "eia.zip"
        self.weather = root / "weather.zip"
        self.output = root / "joined.csv"
        first = datetime(2024, 2, 1, tzinfo=timezone.utc)
        hours = [first + timedelta(hours=i) for i in range(24)]
        eia_rows = [
            {"ba": "CISO", "timestamp_utc": h.strftime("%Y-%m-%dT%H:%M:%SZ"),
             "demand_mw": str(23000 + i),
             "original_source_he_utc": (h + timedelta(hours=1)).strftime("%Y-%m-%dT%H")}
            for i, h in enumerate(hours)]
        weather_rows = [
            {"timestamp_utc": h.strftime("%Y-%m-%dT%H:%M:%SZ"),
             "temperature_c": str(12 + i * .1)}
            for i, h in enumerate(hours)]
        self.eia_sha = self.makezip(
            self.eia, "utc_start/eia930_CISO_2024_start.csv",
            "utc_start/eia930_CISO_2024_start.manifest.json",
            eia_rows, {"target_year": 2024,
                       "clock_conversion": "UTC_hour_ending_minus_one_hour"})
        self.weather_sha = self.makezip(
            self.weather, "arco_2024_02_01_sacramento_single_gridcell.csv",
            "arco_2024_02_01_sacramento_single_gridcell.manifest.json",
            weather_rows, {"source_kind": "public_ARCO_ERA5_Zarr_one_gridcell",
                           "ba_exposure_qualified": False,
                           "clock": "UTC_instantaneous_valid_time_not_EIA_hour_ending"})

    @staticmethod
    def makezip(path, source, manifest_path, rows, m):
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        data = buf.getvalue().encode()
        sha = hashlib.sha256(data).hexdigest()
        with zipfile.ZipFile(path, "w") as zipf:
            zipf.writestr(source, data)
            zipf.writestr(manifest_path, json.dumps(dict(m, sha256_csv=sha)))
        return sha

    def run_pair(self):
        with patch("scripts.c2_eia_arco_real_24h_pair.EIA_SHA", self.eia_sha),              patch("scripts.c2_eia_arco_real_24h_pair.ARCO_SHA", self.weather_sha):
            return pair(self.eia, self.weather, self.output)

    def test_precise_hours_and_no_geographic_overclaim(self):
        m = self.run_pair()
        self.assertEqual(m["hours"], 24)
        self.assertFalse(m["model_skill_computed"])
        self.assertFalse(m["causal_claim"])
        with self.output.open(newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 24)
        self.assertEqual(rows[0]["ciso_demand_mw"], "23000")
        self.assertEqual(rows[-1]["original_eia_hour_ending_utc"], "2024-02-02T00")
        with self.assertRaises(FileExistsError):
            self.run_pair()

    def test_reject_one_missing_weather_hour(self):
        with zipfile.ZipFile(self.weather) as f:
            data = list(csv.DictReader(io.StringIO(
                f.read("arco_2024_02_01_sacramento_single_gridcell.csv").decode())))
        sha = self.makezip(
            self.weather, "arco_2024_02_01_sacramento_single_gridcell.csv",
            "arco_2024_02_01_sacramento_single_gridcell.manifest.json",
            data[:-1], {"source_kind": "public_ARCO_ERA5_Zarr_one_gridcell",
                         "ba_exposure_qualified": False,
                         "clock": "UTC_instantaneous_valid_time_not_EIA_hour_ending"})
        with patch("scripts.c2_eia_arco_real_24h_pair.EIA_SHA", self.eia_sha),              patch("scripts.c2_eia_arco_real_24h_pair.ARCO_SHA", sha):
            with self.assertRaisesRegex(ValueError, "24 UTC hours"):
                pair(self.eia, self.weather, self.output)


if __name__ == "__main__":
    unittest.main()
