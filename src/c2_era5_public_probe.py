"""Verify publicly accessible gridded ARCO ERA5 metadata and one sample cell.

This is a DATA ACCESS smoke test, not a BA exposure, weather–demand join, or
validated area-weighted climate measurement.
"""
import argparse,hashlib,json
from datetime import datetime,timezone
from pathlib import Path

STORE="gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
SOURCE="https://github.com/google-research/arco-era5"
VARIABLE="2m_temperature"

def normalize_lon(value):
    if not -180 <= value <= 360:raise ValueError("Invalid longitude")
    return value % 360

def sample_record(ds,when,lat,lon):
    if VARIABLE not in ds:raise ValueError("Missing 2m_temperature")
    if "time" not in ds.coords or "latitude" not in ds.coords or "longitude" not in ds.coords:
        raise ValueError("Missing required ARCO coordinate dimensions")
    dt=datetime.fromisoformat(when.replace("Z","+00:00"))
    if dt.utcoffset() is None or dt.utcoffset().total_seconds()!=0:
        raise ValueError("UTC-aware time required")
    if dt.minute or dt.second or dt.microsecond:raise ValueError("Hourly time required")
    import numpy as np
    stamp=np.datetime64(dt.replace(tzinfo=None),"ns")
    cell=ds[VARIABLE].sel(time=stamp,latitude=lat,longitude=normalize_lon(lon),method="nearest")
    kelvin=float(cell.values)
    if not 180<kelvin<340:raise ValueError("Implausible Kelvin sample: do not silently correct")
    actual_time=str(cell.time.values)
    selected_lat=float(cell.latitude.values)
    selected_lon=float(cell.longitude.values)
    if abs(selected_lat-lat)>0.26:raise ValueError("ERA5 source lat unexpectedly distant")
    delta=abs((selected_lon-normalize_lon(lon)+180)%360-180)
    if delta>0.26:raise ValueError("ERA5 source longitude unexpectedly distant")
    return {"requested_utc":when,"observed_source_time":actual_time,
            "requested_latitude":lat,"requested_longitude":lon,
            "era5_cell_latitude":selected_lat,"era5_cell_longitude_0_360":selected_lon,
            "temperature_kelvin":kelvin,"temperature_celsius":round(kelvin-273.15,5),
            "units_input":"K","units_output":"degC","source_variable":VARIABLE,
            "note":"single_cell_source_probe_NOT_BA_weather_exposure"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--time",default="2023-07-01T12:00:00Z")
    p.add_argument("--lat",type=float,default=35.)
    p.add_argument("--lon",type=float,default=-112.)
    p.add_argument("--out",default="outputs/e1_era5_source")
    a=p.parse_args()
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    record=sample_record(ds,a.time,a.lat,a.lon)
    record.update({"source_store":STORE,"source_readme":SOURCE,
                   "zarr_metadata_valid_time_start":str(ds.attrs.get("valid_time_start")),
                   "zarr_metadata_valid_time_stop":str(ds.attrs.get("valid_time_stop")),
                   "no_polygon_weights":True,"weather_join_executed":False,
                   "forecast_skill_not_estimated":True})
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    (output/"era5_public_source_probe.json").write_text(json.dumps(record,indent=2)+"\n")
    print(json.dumps(record,indent=2))
if __name__=="__main__":main()
