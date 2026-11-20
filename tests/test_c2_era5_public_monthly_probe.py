"""Offline synthetic-only monthly ARCO extractor checks."""
import calendar
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from src.c2_era5_public_monthly_probe import extract_month, save


class MonthlyARCOTests(unittest.TestCase):
    def fixture(self):
        import numpy as np
        import xarray as xr
        n = calendar.monthrange(2024, 2)[1]*24
        ts = np.datetime64("2024-02-01T00") + np.arange(n).astype("timedelta64[h]")
        return xr.Dataset(
            {"2m_temperature": (("time", "latitude", "longitude"),
                                np.full((n, 1, 1), 285.0), {"units": "K"})},
            coords={"time": ts, "latitude": [38.5], "longitude": [238.5]})

    def test_real_month_definition_but_synthetic_fixture(self):
        rows, m = extract_month(self.fixture())
        self.assertEqual(len(rows), 696)
        self.assertEqual(rows[0]["timestamp_utc"], "2024-02-01T00:00:00Z")
        self.assertEqual(rows[-1]["timestamp_utc"], "2024-02-29T23:00:00Z")
        self.assertEqual(float(rows[0]["temperature_c"]), 11.85)
        self.assertFalse(m["is_CISO_BA_weather_exposure"])
        self.assertFalse(m["eia_join_executed"])
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root)/"month.csv"
            report=save(rows,m,dest)
            self.assertEqual(report["sha256_csv"], hashlib.sha256(dest.read_bytes()).hexdigest())
            self.assertEqual(len(list(csv.DictReader(dest.open()))),696)
            with self.assertRaises(FileExistsError):
                save(rows,m,dest)

    def test_missing_hour_fails_closed(self):
        ds=self.fixture().isel(time=slice(0,695))
        with self.assertRaisesRegex(ValueError,"Missing, duplicate"):
            extract_month(ds)

    def test_unregistered_geography_or_month_fails(self):
        ds=self.fixture()
        with self.assertRaisesRegex(ValueError,"preregistered"):
            extract_month(ds,year=2023,month=2)
        with self.assertRaisesRegex(ValueError,"Spatial location"):
            extract_month(ds,latitude=35)

    def test_nan_and_missing_units_fail(self):
        ds=self.fixture()
        ds["2m_temperature"].values[10,0,0]=float("nan")
        with self.assertRaisesRegex(ValueError,"nonfinite"):
            extract_month(ds)
        ds=self.fixture()
        ds["2m_temperature"].attrs["units"]="C"
        with self.assertRaisesRegex(ValueError,"units K"):
            extract_month(ds)


if __name__=="__main__":
    unittest.main()
