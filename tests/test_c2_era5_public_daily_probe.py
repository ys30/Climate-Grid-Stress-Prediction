"""Offline ARCO real-access adapter tests; mocked weather is NOT empirical evidence."""
import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from src.c2_era5_public_daily_probe import summarize,save

class ARCODailyTests(unittest.TestCase):
    def fixture(self):
        import xarray as xr
        import numpy as np
        dates=np.datetime64("2024-02-01T00:00") + np.arange(24).astype("timedelta64[h]")
        ds=xr.Dataset({"2m_temperature":(("time","latitude","longitude"),
                          np.full((24,1,1),285.0),{"units":"K"})},
                      coords={"time":dates,"latitude":[38.5],"longitude":[238.5]})
        return ds

    def test_24_UTC_hours_and_original_units(self):
        rows,meta=summarize(self.fixture(),date="2024-02-01",latitude=38.5,longitude=-121.5)
        self.assertEqual(len(rows),24)
        self.assertEqual(rows[0]["timestamp_utc"],"2024-02-01T00:00:00Z")
        self.assertEqual(rows[-1]["timestamp_utc"],"2024-02-01T23:00:00Z")
        self.assertEqual(float(rows[0]["temperature_c"]),11.85)
        self.assertFalse(meta["ba_exposure_qualified"])
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"sample.csv"
            manifest=save(rows,meta,f)
            self.assertEqual(manifest["sha256_csv"],hashlib.sha256(f.read_bytes()).hexdigest())
            self.assertFalse(manifest["joined_to_eia"])
            with self.assertRaises(FileExistsError):
                save(rows,meta,f)

    def test_reject_gap_even_when_nearest_sample_exists(self):
        ds=self.fixture().isel(time=slice(0,23))
        with self.assertRaises(ValueError):
            summarize(ds,date="2024-02-01",latitude=38.5,longitude=-121.5)

    def test_reject_nonkelvin_or_nan(self):
        ds=self.fixture()
        ds["2m_temperature"].attrs["units"]="C"
        with self.assertRaisesRegex(ValueError,"Kelvin"):
            summarize(ds,date="2024-02-01",latitude=38.5,longitude=-121.5)
        ds=self.fixture()
        ds["2m_temperature"].values[0,0,0]=float("nan")
        with self.assertRaisesRegex(ValueError,"implausible"):
            summarize(ds,date="2024-02-01",latitude=38.5,longitude=-121.5)

if __name__=="__main__":
    unittest.main()
