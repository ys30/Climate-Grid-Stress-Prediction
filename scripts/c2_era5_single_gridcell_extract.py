"""Convert an official ERA5 hourly netCDF *single gridpoint pilot* to a SHA-pinned CSV.

No synthetic weather, no interpolation, no EIA clock shift. This output is
NOT a CISO-wide weather proxy and is deliberately incompatible with the
BA-hour join until defensible spatial aggregation has been documented.
Requires xarray, numpy and a netCDF backend (netcdf4/h5netcdf).
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path

def extract(src:Path,dst:Path,*,year:int,month:int,latitude:float=38.5,longitude:float=-121.5):
    import xarray as xr
    import numpy as np
    src,dst=Path(src),Path(dst)
    if year not in range(2020,2026) or month not in range(1,13):
        raise ValueError("Outside registered pilot period")
    if dst.exists() or dst.with_suffix(".manifest.json").exists():
        raise FileExistsError("Refuse to overwrite ERA5 pilot")
    if src.resolve()==dst.resolve():
        raise ValueError("Inputs and outputs must differ")
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    with xr.open_dataset(src) as ds:
        if "t2m" not in ds:
            raise ValueError("Official ERA5 t2m variable absent")
        v=ds["t2m"]
        if "expver" in v.dims:
            raise ValueError("ERA5 expver dimension must be resolved explicitly")
        lat_name=next((k for k in ("latitude","lat") if k in v.coords),None)
        lon_name=next((k for k in ("longitude","lon") if k in v.coords),None)
        time_name=next((k for k in ("valid_time","time") if k in v.coords),None)
        if not lat_name or not lon_name or not time_name:
            raise ValueError("Missing ERA5 latitude, longitude or valid_time coordinate")
        if v[time_name].size < 28*24:
            raise ValueError("Monthly source too small for hourly ERA5")
        chosen=v.sel({lat_name:latitude,lon_name:longitude},method="nearest")
        selected_lat=float(chosen[lat_name].item())
        selected_lon=float(chosen[lon_name].item())
        if selected_lon>180: selected_lon-=360
        if abs(selected_lat-latitude)>0.251 or abs(selected_lon-longitude)>0.251:
            raise ValueError("ERA5 source grid too far from registered pilot site")
        remaining=set(chosen.dims)-{time_name}
        if remaining:
            raise ValueError("Unexpected additional ERA5 dimensions")
        times=chosen[time_name].values
        values=chosen.values
        output=[]
        seen=set()
        for ts,k in zip(times,values):
            stamp=np.datetime64(ts,"s").astype("datetime64[s]").astype(int)
            dt=datetime.fromtimestamp(int(stamp),tz=timezone.utc)
            if dt.year!=year or dt.month!=month or dt.minute or dt.second:
                raise ValueError("Unexpected ERA5 hourly UTC validity time")
            if dt in seen:
                raise ValueError("Duplicate ERA5 UTC valid hour")
            seen.add(dt)
            kelvin=float(k)
            if not math.isfinite(kelvin) or not 170<kelvin<350:
                raise ValueError("ERA5 t2m temperature is missing or implausible")
            output.append({"timestamp_utc":dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           "temperature_c":f"{kelvin-273.15:.6f}"})
    import calendar
    expected=calendar.monthrange(year,month)[1]*24
    if len(output)!=expected:
        raise ValueError(f"ERA5 pilot has {len(output)}/{expected} hours: no fill permitted")
    output.sort(key=lambda r:r["timestamp_utc"])
    dst.parent.mkdir(parents=True,exist_ok=True)
    tmp=dst.with_suffix(dst.suffix+".partial")
    if tmp.exists():raise FileExistsError("Partial output exists")
    try:
        with tmp.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=["timestamp_utc","temperature_c"])
            w.writeheader()
            w.writerows(output)
        sha=hashlib.sha256(tmp.read_bytes()).hexdigest()
        tmp.replace(dst)
    finally:
        if tmp.exists():tmp.unlink()
    m={"source_kind":"ERA5_SINGLE_GRIDCELL_DEMONSTRATOR_NOT_BA_PROXY",
       "dataset":"reanalysis-era5-single-levels","variable":"2m_temperature",
       "source_netcdf_sha256":digest,"sha256_csv":sha,"year":year,"month":month,
       "time_reference":"UTC_instantaneous_validity_time",
       "clock_conversion":"none",
       "sample_location":"near Sacramento CA, illustrative only",
       "requested_latitude":latitude,"requested_longitude":longitude,
       "selected_latitude":selected_lat,"selected_longitude":selected_lon,
       "n_valid_hours":len(output),
       "is_measured_county_load_weighted":False,
       "is_qualified_CISO_geographic_proxy":False,
       "claim_status":"no BA spatial aggregation, no joint EIA model eligibility"}
    dst.with_suffix(".manifest.json").write_text(json.dumps(m,indent=2)+"\n")
    return m

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_netcdf",type=Path)
    p.add_argument("output_csv",type=Path)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True)
    a=p.parse_args()
    print(json.dumps(extract(a.source_netcdf,a.output_csv,year=a.year,month=a.month),indent=2))

if __name__=="__main__":
    main()
