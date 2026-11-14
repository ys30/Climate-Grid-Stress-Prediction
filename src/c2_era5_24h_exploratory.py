"""Continuous 24-hour real ERA5 four-BA exploratory area-weighted temperature.

Fetches one bounded 24xWestern-US grid from public ARCO ERA5. All geographic
weights remain explicitly UNAPPROVED for model training or climate attribution.
"""
import argparse,csv,hashlib,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_era5_public_probe import STORE,VARIABLE
from src.c2_era5_full_grid_one_hour import load_exploratory_weights,compute_from_loaded_grid

def calculate_24(ds,groups,start):
    import numpy as np
    begin=datetime.fromisoformat(start.replace("Z","+00:00"))
    if begin.tzinfo is None or begin.utcoffset().total_seconds()!=0 or any(
            [begin.minute,begin.second,begin.microsecond]):
        raise ValueError("UTC-aware whole-hour start required")
    var=ds[VARIABLE]
    time_key="time" if "time" in var.dims else "valid_time"
    t0=np.datetime64(begin.replace(tzinfo=None),"ns")
    t1=np.datetime64((begin+timedelta(hours=23)).replace(tzinfo=None),"ns")
    lats=[v[0] for cells in groups.values() for v in cells]
    lons=[v[1] for cells in groups.values() for v in cells]
    source=var.sel({time_key:slice(t0,t1)})
    lat_desc=float(source.latitude.values[0])>float(source.latitude.values[-1])
    bbox=source.sel(latitude=slice(max(lats),min(lats)) if lat_desc else slice(min(lats),max(lats)),
                    longitude=slice(min(lons),max(lons)))
    if bbox.sizes.get(time_key,0)!=24:raise ValueError("ERA5 grid missing 24 requested time steps")
    if bbox.size>500000:raise ValueError("Unexpected large real ERA5 data request")
    times=[np.datetime64(x,"ns") for x in bbox[time_key].values]
    for n,t in enumerate(times):
        expected=np.datetime64((begin+timedelta(hours=n)).replace(tzinfo=None),"ns")
        if t!=expected:raise ValueError("ERA5 timestamps not contiguous or not aligned")
    # Bounded single load: original source cells and hourly temperature are real.
    actual=bbox.load()
    rows=[]
    for idx in range(24):
        spatial=actual.isel({time_key:idx},drop=True)
        ba_rows=compute_from_loaded_grid(spatial,groups)
        stamp=(begin+timedelta(hours=idx)).isoformat()
        for entry in ba_rows:
            rows.append({"timestamp_utc_start":stamp,**entry})
    return rows,{"hours":24,"BA_count":len(groups),"row_count":len(rows),
                 "source_grid_cells_per_hour":int(bbox.size//24),
                 "observed_kelvin_units":var.attrs.get("units"),
                 "utc_start":begin.isoformat(),"utc_end_inclusive":
                     (begin+timedelta(hours=23)).isoformat(),
                 "contiguous_UTC_hours_verified":True,
                 "all_requested_BA_cells_covered":True,
                 "historical_geography_admitted":False,
                 "weather_demand_join_performed":False,
                 "forecast_training_performed":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weights",required=True)
    p.add_argument("--start",default="2023-07-01T00:00:00Z")
    p.add_argument("--out",default="outputs/e1_24h")
    a=p.parse_args()
    import xarray as xr
    groups=load_exploratory_weights(a.weights)
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    rows,info=calculate_24(ds,groups,a.start)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    fields=["timestamp_utc_start","ba","grid_cells","weighted_temperature_kelvin",
        "weighted_temperature_celsius","observed_grid_cell_min_celsius",
        "observed_grid_cell_max_celsius","all_source_cells_present",
        "experimental_geography_only","historical_weather_exposure_approved"]
    with (out/"REAL_ERA5_24h_UNAPPROVED.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    info.update({"ARCO_store":STORE,"source_variable":VARIABLE,
        "weights_sha256":hashlib.sha256(Path(a.weights).read_bytes()).hexdigest(),
        "interpretation":"Real ERA5 2m K with provisional 2018 BA candidate area weights; NOT modeling data"})
    (out/"real_era5_24h_manifest.json").write_text(json.dumps(info,indent=2)+"\n")
    print("REAL_ERA5_24H_SUMMARY",json.dumps(info))
    for ba in sorted(groups):
        vals=[x["weighted_temperature_celsius"] for x in rows if x["ba"]==ba]
        print("BA_24H_RANGE",json.dumps({"ba":ba,"min_celsius":min(vals),
         "max_celsius":max(vals),"number_of_hours":len(vals)}))
if __name__=="__main__":main()
