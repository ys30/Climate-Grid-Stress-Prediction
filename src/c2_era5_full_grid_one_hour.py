"""One-hour FULL-grid experimental BA exposure from actual public ARCO ERA5.

This intentionally uses unapproved 2018-derived candidate BA geometry.
Never publish output as a validated BA exposure or train a forecast on it.
"""
import argparse,csv,hashlib,json,math
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path
from src.c2_era5_public_probe import STORE,VARIABLE

def load_exploratory_weights(path):
    groups=defaultdict(list)
    with open(path,newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        required={"ba","latitude","longitude_0_360","weight","research_status"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Missing experimental grid columns")
        for row in reader:
            if row["research_status"]!="exploratory_unapproved_geometry":
                raise ValueError("Only UNAPPROVED candidate weights may enter this pilot")
            ba=row["ba"];lat=float(row["latitude"]);lon=float(row["longitude_0_360"])
            w=float(row["weight"])
            if ba not in ("AZPS","BPAT","CISO","SRP") or not math.isfinite(w) or w<=0:
                raise ValueError("Invalid BA cell weight")
            groups[ba].append((lat,lon,w))
    if set(groups)!={"AZPS","BPAT","CISO","SRP"}:raise ValueError("Missing BA cells")
    for ba,cells in groups.items():
        if abs(sum(x[2] for x in cells)-1)>1e-7:
            raise ValueError("Whole-area BA weights must sum to one")
        if len(set((x[0],x[1]) for x in cells))!=len(cells):
            raise ValueError("Duplicate BA ERA5 cells")
    return dict(groups)

def compute_from_loaded_grid(grid,groups):
    """Index exact ERA5 cells, failing closed on nonfinite/out-of-domain samples."""
    import numpy as np,xarray as xr
    if not {"latitude","longitude"}.issubset(grid.dims):
        raise ValueError("Expected latitude/longitude grid")
    if str(grid.attrs.get("units","")) not in ("K","kelvin"):
        raise ValueError("ARCO ERA5 2m temperature must use Kelvin")
    results=[]
    for ba,cells in sorted(groups.items()):
        lats=xr.DataArray([c[0] for c in cells],dims="cell")
        lons=xr.DataArray([c[1] for c in cells],dims="cell")
        values=grid.sel(latitude=lats,longitude=lons).values
        import numpy as np
        values=np.asarray(values,dtype=float).reshape(-1)
        if values.shape!=(len(cells),) or not np.all(np.isfinite(values)):
            raise ValueError("Incomplete weighted ERA5 grid coverage for "+ba)
        if np.any((values<=180)|(values>=340)):
            raise ValueError("Unexpected Kelvin grid value "+ba)
        weighted_kelvin=sum(float(v)*w for v,(_,_,w) in zip(values,cells))
        results.append({"ba":ba,"grid_cells":len(cells),
            "weighted_temperature_kelvin":weighted_kelvin,
            "weighted_temperature_celsius":round(weighted_kelvin-273.15,6),
            "observed_grid_cell_min_celsius":round(float(values.min())-273.15,5),
            "observed_grid_cell_max_celsius":round(float(values.max())-273.15,5),
            "all_source_cells_present":True,
            "experimental_geography_only":True,
            "historical_weather_exposure_approved":False})
    return results

def fetch_real_hour(groups,when):
    import numpy as np,xarray as xr
    dt=datetime.fromisoformat(when.replace("Z","+00:00"))
    if dt.utcoffset() is None or dt.utcoffset().total_seconds()!=0 or dt.minute or dt.second or dt.microsecond:
        raise ValueError("Full UTC hour required")
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    if VARIABLE not in ds:raise ValueError("Missing public ERA5 2m temperature")
    var=ds[VARIABLE]
    time_key="time" if "time" in var.dims else "valid_time"
    stamp=np.datetime64(dt.replace(tzinfo=None),"ns")
    source=var.sel({time_key:stamp})
    all_lat=[c[0] for values in groups.values() for c in values]
    all_lon=[c[1] for values in groups.values() for c in values]
    low_lat=min(all_lat);high_lat=max(all_lat);low_lon=min(all_lon);high_lon=max(all_lon)
    # Fetch a bounded western-US 0.25-degree subgrid for a single UTC hour.
    descending=float(source.latitude.values[0])>float(source.latitude.values[-1])
    bound_lat=slice(high_lat,low_lat) if descending else slice(low_lat,high_lat)
    bbox=source.sel(latitude=bound_lat,longitude=slice(low_lon,high_lon))
    if bbox.size>20000:
        raise ValueError("Excessive bounding ERA5 grid request: refuses large download")
    loaded=bbox.load()
    if not loaded.size:raise ValueError("Empty ERA5 source bbox")
    results=compute_from_loaded_grid(loaded,groups)
    return results,{"zarr_store":STORE,"utc_timestamp":when,
       "actual_grid_bbox_cells":int(loaded.size),
       "source_latitude_range":[low_lat,high_lat],
       "source_longitude_0_360_range":[low_lon,high_lon],
       "source_temp_units":var.attrs.get("units"),
       "BA_region_model_approval":False,
       "not_prediction_or_attribution":True}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--weights",required=True)
    p.add_argument("--time",default="2023-07-01T12:00:00Z")
    p.add_argument("--out",default="outputs/e1_one_hour_full_weight")
    args=p.parse_args()
    groups=load_exploratory_weights(args.weights)
    rows,meta=fetch_real_hour(groups,args.time)
    meta["weights_sha256"]=hashlib.sha256(Path(args.weights).read_bytes()).hexdigest()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    meta["source_geometry_status"]="make_valid source-year-2018 experimental candidate; NOT model eligible"
    (out/"full_cell_one_hour_experimental_era5.json").write_text(
        json.dumps({"metadata":meta,"per_BA":rows},indent=2)+"\n")
    print("REAL_ERA5_FULL_GRID_EXPERIMENT",json.dumps(meta))
    for row in rows:print("FULL_WEIGHT_BA_EXPERIMENT",json.dumps(row))
if __name__=="__main__":main()
