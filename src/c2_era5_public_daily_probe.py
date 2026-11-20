"""Read 24 authentic hourly ARCO ERA5 t2m values for ONE demonstrator grid cell.

A public Google-hosted ARCO ERA5 Zarr sample, not a Copernicus CDS NetCDF
source, BA polygon-weighted exposure, or fitted EIA-weather panel.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_era5_public_probe import STORE,SOURCE,VARIABLE,normalize_lon

def summarize(ds,*,date,latitude,longitude):
    import numpy as np
    first=datetime.fromisoformat(date).replace(tzinfo=timezone.utc)
    if not 2020<=first.year<=2025 or first.month!=2 or first.year!=2024:
        raise ValueError("Registered source pilot is 2024-02 only")
    if not -90<=latitude<=90 or not -180<=longitude<=180:
        raise ValueError("Invalid latitude/longitude")
    expected=[first+timedelta(hours=i) for i in range(24)]
    if VARIABLE not in ds:
        raise ValueError("Missing ARCO ERA5 2m_temperature")
    field=ds[VARIABLE]
    if not {"time","latitude","longitude"}<=set(field.dims):
        raise ValueError("Unexpected ARCO ERA5 weather coordinates")
    if str(field.attrs.get("units","")) not in ("K","kelvin"):
        raise ValueError("ARCO t2m requires explicit Kelvin units")
    # Select time range and nearest 0.25-degree cell, no weather interpolation.
    times=np.array([np.datetime64(t.replace(tzinfo=None),"ns") for t in expected])
    selected=field.sel(time=times,latitude=latitude,
                       longitude=normalize_lon(longitude),method="nearest")
    sel_lat=float(selected.latitude.item())
    sel_lon=float(selected.longitude.item())
    if abs(sel_lat-latitude)>0.26:
        raise ValueError("Unexpected latitude grid displacement")
    if abs((sel_lon-normalize_lon(longitude)+180)%360-180)>0.26:
        raise ValueError("Unexpected longitude grid displacement")
    if set(selected.dims)!={"time"}:
        raise ValueError("ARCO sampled data must have time dimension only")
    observed_time=[np.datetime64(t,"s") for t in selected.time.values]
    if observed_time!=[np.datetime64(t.replace(tzinfo=None),"s") for t in expected]:
        raise ValueError("ARCO UTC validity timeline mismatch")
    vals=selected.values
    if len(vals)!=24:
        raise ValueError("Need exactly 24 actual hourly ARCO values")
    rows=[]
    for t,k in zip(expected,vals):
        v=float(k)
        if not math.isfinite(v) or not 180<v<340:
            raise ValueError("Missing or implausible real ARCO Kelvin: fail")
        rows.append({"timestamp_utc":t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "temperature_c":f"{v-273.15:.6f}"})
    return rows,{"source_kind":"public_ARCO_ERA5_Zarr_one_gridcell",
                 "source_store":STORE,"source_project":SOURCE,
                 "variable":VARIABLE,"units_source":"K",
                 "clock":"UTC_instantaneous_valid_time_not_EIA_hour_ending",
                 "requested_date":date,"requested_latitude":latitude,
                 "requested_longitude":longitude,
                 "selected_latitude":sel_lat,"selected_longitude_0_360":sel_lon,
                 "n_unique_hours":len(rows),
                 "ba_exposure_qualified":False,"joined_to_eia":False,
                 "source_pin_limitation":"Public mutable Zarr path; this is not immutable netCDF source SHA",
                 "claim_status":"public_real_weather_source_pilot_only_not_CISO_BA"}

def save(rows,meta,path:Path):
    path=Path(path)
    if path.exists() or path.with_suffix(".manifest.json").exists():
        raise FileExistsError("Existing observational source sample cannot be overwritten")
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["timestamp_utc","temperature_c"])
        writer.writeheader()
        writer.writerows(rows)
    meta=dict(meta,sha256_csv=hashlib.sha256(path.read_bytes()).hexdigest())
    path.with_suffix(".manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--date",default="2024-02-01")
    p.add_argument("--lat",type=float,default=38.5)
    p.add_argument("--lon",type=float,default=-121.5)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    try:
        rows,m=summarize(ds,date=a.date,latitude=a.lat,longitude=a.lon)
    finally:
        ds.close()
    manifest=save(rows,m,a.output)
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    main()
