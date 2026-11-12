"""Aggregate actual gridded ERA5 hourly temperature to BA exposure using frozen grid weights.

Input is an ERA5 NetCDF subset + independently provenance-approved grid weights.
Never accept a point-station proxy, interpolate missing grid cells, or average
without explicit cell-intersection weights. Does not download or fit a model.
"""
import argparse,csv,hashlib,json,math
from collections import defaultdict
from datetime import datetime,timezone
from pathlib import Path

def load_weights(path):
    with open(path,newline="") as f:
        rd=csv.DictReader(f)
        required={"ba","latitude","longitude_0_360","weight","exposure_method"}
        if not required.issubset(rd.fieldnames or []):raise ValueError("Bad BA area weight schema")
        weights=defaultdict(list)
        for row in rd:
            if row["exposure_method"]!="ba_area_weighted_era5":
                raise ValueError("Not an approved BA area-weight exposure")
            v=float(row["weight"])
            if not math.isfinite(v) or v<=0:raise ValueError("Invalid positive area weight")
            weights[row["ba"]].append((float(row["latitude"]),float(row["longitude_0_360"]),v))
    if set(weights)!={"AZPS","BPAT","CISO","SRP"}:
        raise ValueError("Require approved four-BA polygon weights")
    if any(abs(sum(z[2] for z in w)-1)>1e-6 for w in weights.values()):
        raise ValueError("BA grid weights must sum to one")
    return dict(weights)

def aggregate(ds,weights,var="2m_temperature"):
    import numpy as np
    import xarray as xr
    if var not in ds:raise ValueError("Expected ERA5 2m temperature variable")
    da=ds[var]
    tdim="time" if "time" in da.dims else "valid_time"
    if tdim not in da.dims or not {"latitude","longitude"}.issubset(da.dims):
        raise ValueError("Unexpected ERA5 coordinate dimensions")
    if str(da.attrs.get("units","")) not in ("K","kelvin"):
        raise ValueError("ERA5 temperature must be documented as Kelvin")
    if any(dim not in (tdim,"latitude","longitude") for dim in da.dims):
        raise ValueError("Unexpected extra ERA5 dimensions")
    arr=ds[tdim].values
    if len(arr)<1:raise ValueError("No ERA5 hourly samples")
    timeline=[np.datetime_as_string(np.datetime64(t,"ns"),unit="s") for t in arr]
    if any(not label.endswith(":00:00") for label in timeline):
        raise ValueError("ERA5 timestamps are not hourly")
    if len(set(timeline))!=len(timeline):raise ValueError("Duplicate ERA5 time keys")
    rows=[];qa=[]
    for ba,cells in sorted(weights.items()):
        lat=np.array([x[0] for x in cells]);lon=np.array([x[1] for x in cells])
        source_lat=ds.latitude.values
        source_lon=ds.longitude.values
        # nearest-grid audit: all declared weight cells must match ERA5 coordinates.
        if any(np.min(np.abs(source_lat-v))>1e-5 for v in lat):
            raise ValueError("ERA5 latitude grid mismatch: no implicit spatial interpolation")
        if any(np.min(np.abs(source_lon-v))>1e-5 for v in lon):
            raise ValueError("ERA5 longitude grid mismatch: no implicit spatial interpolation")
        region=da.sel(latitude=xr.DataArray(lat,dims="cell"),
                      longitude=xr.DataArray(lon,dims="cell"))
        matrix=np.asarray(region.transpose(tdim,"cell").values,dtype=float)
        if matrix.shape!=(len(timeline),len(cells)):
            raise ValueError("ERA5 time/cell array dimensional mismatch")
        w=np.array([x[2] for x in cells])
        good=np.isfinite(matrix)
        num=np.where(good,matrix,0.)@w
        coverage=good.astype(float)@w
        for idx,label in enumerate(timeline):
            if coverage[idx]<1-1e-8:
                qa.append({"ba":ba,"timestamp_utc_start":label+"+00:00",
                           "reason":"missing_grid_temperature","coverage_fraction":float(coverage[idx])})
                continue
            kelvin=float(num[idx])
            if not 180<kelvin<340:
                raise ValueError("Implausible BA ERA5 Kelvin average")
            rows.append({"ba":ba,"timestamp_utc_start":label+"+00:00",
                         "temperature_2m_c":round(kelvin-273.15,6),
                         "exposure_method":"ba_area_weighted_era5",
                         "source_dataset":"ERA5"})
    return rows,qa

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--era5",required=True)
    p.add_argument("--weights",required=True)
    p.add_argument("--weights-manifest",required=True)
    p.add_argument("--out",default="outputs/e1_era5_weighted")
    a=p.parse_args()
    meta=json.loads(Path(a.weights_manifest).read_text())
    if meta.get("no_weather_fetched") is not True or meta.get("weighting")!="polygon-overlap area only, NOT demand-weighted":
        raise ValueError("Area grid-weight provenance contract missing")
    import xarray as xr
    weights=load_weights(a.weights)
    with xr.open_dataset(a.era5) as ds:
        rows,qa=aggregate(ds,weights)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    def write(name,data,cols):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(data)
    write("hourly_ba_era5_exposure.csv",rows,
          ["ba","timestamp_utc_start","temperature_2m_c","exposure_method","source_dataset"])
    write("incomplete_hourly_grids.csv",qa,
          ["ba","timestamp_utc_start","reason","coverage_fraction"])
    summary={"source_era5_sha256":sha(a.era5),"weights_sha256":sha(a.weights),
             "weights_provenance":meta["source"],"valid_hourly_exposures":len(rows),
             "incomplete_hourly_exposures":len(qa),"outcome_model_fitted":False,
             "not_an_attribution_result":True}
    (out/"exposure_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
