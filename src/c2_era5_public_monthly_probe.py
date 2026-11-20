"""Read one complete real month of public ARCO ERA5 2m temperature at one grid cell.

This is a source-access and clock QA experiment, not CISO BA-wide exposure.
ARCO is publicly served reformatted ERA5 and the source object is not
cryptographically frozen by the resulting local CSV hash.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.c2_era5_public_probe import STORE, SOURCE, VARIABLE, normalize_lon

REGISTERED_YEAR = 2024
REGISTERED_MONTH = 2
LATITUDE = 38.5
LONGITUDE = -121.5


def extract_month(ds, *, year=REGISTERED_YEAR, month=REGISTERED_MONTH,
                  latitude=LATITUDE, longitude=LONGITUDE):
    import numpy as np

    if (year, month) != (REGISTERED_YEAR, REGISTERED_MONTH):
        raise ValueError("Only preregistered 2024-02 monthly pilot is supported")
    if (latitude, longitude) != (LATITUDE, LONGITUDE):
        raise ValueError("Spatial location changed; register a new source pilot")
    if VARIABLE not in ds:
        raise ValueError("ARCO 2m temperature variable missing")
    field = ds[VARIABLE]
    if set(field.dims) != {"time", "latitude", "longitude"}:
        raise ValueError("ARCO variable has unexpected dimensions")
    if str(field.attrs.get("units", "")).lower() not in ("k", "kelvin"):
        raise ValueError("ARCO 2m temperature must report units K")
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    n = calendar.monthrange(year, month)[1] * 24
    hours = [start + timedelta(hours=i) for i in range(n)]
    target = np.asarray([np.datetime64(h.replace(tzinfo=None), "ns") for h in hours])

    # Choose grid cell before slicing the month; avoid whole-region computation.
    point = field.sel(latitude=latitude, longitude=normalize_lon(longitude), method="nearest")
    chosen_lat = float(point.latitude.item())
    chosen_lon = float(point.longitude.item())
    if abs(chosen_lat - latitude) > .26:
        raise ValueError("Selected latitude differs from declared source grid")
    if abs((chosen_lon-normalize_lon(longitude)+180) % 360 - 180) > .26:
        raise ValueError("Selected longitude differs from declared source grid")

    point = point.sel(time=slice(target[0], target[-1]))
    actual = np.asarray(point.time.values, dtype="datetime64[ns]")
    if len(actual) != n or not np.array_equal(actual, target):
        raise ValueError("Missing, duplicate, or out-of-order ARCO hourly UTC valid times")
    values = np.asarray(point.values, dtype=float)
    if values.shape != (n,) or not np.all(np.isfinite(values)):
        raise ValueError("Missing/nonfinite ARCO 2m temperature samples")
    if np.any((values <= 180) | (values >= 340)):
        raise ValueError("ARCO 2m Kelvin samples outside validity guard")
    rows = [{"timestamp_utc": h.strftime("%Y-%m-%dT%H:%M:%SZ"),
             "temperature_c": f"{float(k)-273.15:.6f}"}
            for h, k in zip(hours, values)]
    return rows, {
        "source_kind": "public_ARCO_ERA5_Zarr_single_gridcell_month",
        "source_store": STORE,
        "source_project": SOURCE,
        "source_variable": VARIABLE,
        "source_units": "K",
        "output_units": "degrees_C",
        "requested_year": year,
        "requested_month": month,
        "requested_latitude": latitude,
        "requested_longitude": longitude,
        "selected_latitude": chosen_lat,
        "selected_longitude_0_360": chosen_lon,
        "clock": "UTC_instantaneous_valid_time_not_EIA_hour_ending",
        "n_unique_hours": n,
        "is_CISO_BA_weather_exposure": False,
        "eia_join_executed": False,
        "source_limitation": "Public ARCO Zarr is not immutable upstream source snapshot",
        "claim_status": "SINGLE_GRIDCELL_SOURCE_DIAGNOSTIC_NOT_BA",
    }


def save(rows, manifest, output):
    output = Path(output)
    if output.exists() or output.with_suffix(".manifest.json").exists():
        raise FileExistsError("Monthly evidence output exists; no overwrite")
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".partial")
    if tmp.exists():
        raise FileExistsError("Stale partial monthly evidence output")
    try:
        with tmp.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=("timestamp_utc", "temperature_c"))
            writer.writeheader()
            writer.writerows(rows)
        digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
        tmp.replace(output)
        full = dict(manifest, sha256_csv=digest)
        output.with_suffix(".manifest.json").write_text(json.dumps(full, indent=2)+"\n")
    finally:
        if tmp.exists():
            tmp.unlink()
    return full


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    import xarray as xr
    ds = xr.open_zarr(STORE, chunks=None, storage_options={"token": "anon"})
    try:
        rows, manifest = extract_month(ds)
    finally:
        ds.close()
    print(json.dumps(save(rows, manifest, a.output), indent=2))


if __name__ == "__main__":
    main()
