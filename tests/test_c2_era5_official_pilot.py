"""Offline ERA5 pilot request/NetCDF conversion contracts. Test data are synthetic."""
import calendar
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.c2_era5_official_pilot_request import request, DATASET, PILOT_AREA


class ERA5RequestTests(unittest.TestCase):
    def test_hourly_2024_february_request(self):
        r=request(2024,2)
        self.assertEqual(r["variable"],["2m_temperature"])
        self.assertEqual(r["product_type"],["reanalysis"])
        self.assertEqual(len(r["time"]),24)
        self.assertEqual(r["area"],PILOT_AREA)
        self.assertEqual(r["data_format"],"netcdf")
        self.assertEqual(DATASET,"reanalysis-era5-single-levels")

    def test_reject_year_outside_cohort(self):
        for year in (2019,2026):
            with self.assertRaises(ValueError):
                request(year,1)

    def test_era5_hourly_netCDF_extract_fixture(self):
        try:
            import numpy as np
            import xarray as xr
        except ImportError:
            self.skipTest("xarray/numpy not installed; CI installs")
        from scripts.c2_era5_single_gridcell_extract import extract
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            n=calendar.monthrange(2024,2)[1]*24
            times=np.datetime64("2024-02-01T00") + np.arange(n).astype("timedelta64[h]")
            ds=xr.Dataset({"t2m":(("time","latitude","longitude"),
                                   np.full((n,1,1),280.0))},
                          coords={"time":times,"latitude":[38.5],"longitude":[-121.5]})
            nc=root/"test.nc"
            ds.to_netcdf(nc)
            nc.with_suffix(".manifest.json").write_text(json.dumps({
                "source_kind":"SYNTHETIC_TEST_NETCDF_ONLY",
                "dataset":"reanalysis-era5-single-levels",
                "year":2024,"month":2,
                "sha256_netcdf":hashlib.sha256(nc.read_bytes()).hexdigest()
            }))
            out=root/"output.csv"
            m=extract(nc,out,year=2024,month=2)
            self.assertEqual(m["n_valid_hours"],696)
            self.assertEqual(m["source_kind"],"ERA5_SINGLE_GRIDCELL_DEMONSTRATOR_NOT_BA_PROXY")
            self.assertFalse(m["is_qualified_CISO_geographic_proxy"])
            self.assertFalse(m["source_credential_authenticated"])
            self.assertEqual(m["claim_status"],"SYNTHETIC_OFFLINE_FIXTURE_NOT_REAL_ERA5")
            self.assertTrue(out.exists())
            with self.assertRaises(FileExistsError):
                extract(nc,out,year=2024,month=2)
            tampered=root/"tampered.csv"
            nc.write_bytes(nc.read_bytes()+b"tampering")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                extract(nc,tampered,year=2024,month=2)
            nc.with_suffix(".manifest.json").unlink()
            with self.assertRaisesRegex(ValueError,"manifest"):
                extract(nc,root/"missing_source_provenance.csv",year=2024,month=2)


if __name__=="__main__":
    unittest.main()
