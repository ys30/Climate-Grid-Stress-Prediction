"""Eight real ARCO ERA5 fixed-hour proxy-geography sensitivity comparisons.

Computes HIFLD-2018 A vs Census-TIGER2024/EIA861 county union B on identical
genuine public ERA5 2m grids. Neither proxy is approved for electricity BA
operating territories, weather-demand models, or climate attribution.
"""
import argparse,csv,hashlib,json,math
from datetime import datetime,timezone
from pathlib import Path
from src.c2_era5_public_probe import STORE,VARIABLE
from src.c2_era5_full_grid_one_hour import load_exploratory_weights,compute_from_loaded_grid
from src.c2_census_vs_hifld_era5 import difference

SAMPLE_TIMES=(
 "2020-01-15T12:00:00Z","2020-07-01T12:00:00Z",
 "2023-01-15T12:00:00Z","2023-04-01T12:00:00Z",
 "2023-07-01T12:00:00Z","2023-10-01T12:00:00Z",
 "2025-01-15T12:00:00Z","2025-07-01T12:00:00Z")

def source_hour(shared,groups_a,groups_b,when):
    import numpy as np
    instant=datetime.fromisoformat(when.replace("Z","+00:00"))
    if instant.utcoffset() is None or instant.utcoffset().total_seconds()!=0 or instant.minute or instant.second:
        raise ValueError("Source observation instant must be on UTC hour")
    ds_var=shared[VARIABLE]
    tkey="time" if "time" in ds_var.dims else "valid_time"
    time=np.datetime64(instant.replace(tzinfo=None),"ns")
    region=ds_var.sel({tkey:time})
    all_cells=[c for groups in (groups_a,groups_b) for cells in groups.values() for c in cells]
    latmin=min(c[0] for c in all_cells);latmax=max(c[0] for c in all_cells)
    lonmin=min(c[1] for c in all_cells);lonmax=max(c[1] for c in all_cells)
    descending=float(region.latitude.values[0])>float(region.latitude.values[-1])
    sub=region.sel(latitude=slice(latmax,latmin) if descending else slice(latmin,latmax),
                   longitude=slice(lonmin,lonmax))
    if sub.size<=0 or sub.size>20000:
        raise ValueError("Expected bounded Western-US ERA5 0.25 degree spatial grid")
    grid=sub.load()
    old=compute_from_loaded_grid(grid,groups_a)
    new=compute_from_loaded_grid(grid,groups_b)
    return [{**x,"utc_time":when,"sample_year":instant.year,
         "source_same_actual_ERA5_grid":True}
        for x in difference(old,new)],int(grid.size)

def sample_summary(rows):
    from statistics import median
    summary=[]
    for ba in ("AZPS","BPAT","CISO","SRP"):
        subset=[x for x in rows if x["ba"]==ba]
        if len(subset)!=len(SAMPLE_TIMES):
            raise ValueError("Sample count incomplete by BA")
        vals=[x["county_minus_hifld_c"] for x in subset]
        summary.append({"ba":ba,"N_sample_UTC_hours":len(vals),
         "minimum_proxy_B_minus_A_c":min(vals),"maximum_proxy_B_minus_A_c":max(vals),
         "median_proxy_B_minus_A_c":round(median(vals),6),
         "positive_hour_count":sum(v>0 for v in vals),
         "negative_hour_count":sum(v<0 for v in vals),
         "historical_BA_geography_approved":False,
         "climate_change_attribution_done":False,
         "training_permitted":False})
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hifld-weights",required=True)
    p.add_argument("--county-weights",required=True)
    p.add_argument("--out",default="outputs/e1_AB_eight_hours")
    a=p.parse_args()
    old=load_exploratory_weights(a.hifld_weights)
    new=load_exploratory_weights(a.county_weights)
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    rows=[];sizes=[]
    for time in SAMPLE_TIMES:
        one,n=source_hour(ds,old,new,time)
        rows.extend(one);sizes.append(n)
        print("REAL_AB_SEASONAL_SAMPLE",json.dumps({"utc":time,"values":one,
               "read_ARCO_grid_cells":n,"training_eligible":False}),flush=True)
    summary=sample_summary(rows)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    def save_csv(path,items):
        with (out/path).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(items[0]))
            writer.writeheader();writer.writerows(items)
    save_csv("actual_ERA5_eight_hour_HIFLD_vs_Census_TIGER_proxy_C.csv",rows)
    save_csv("actual_ERA5_eight_hour_BA_proxy_difference_summary.csv",summary)
    manifest={"actually_observed_UTC_instants":list(SAMPLE_TIMES),
      "rows":len(rows),"sample_ERA5_grid_cells_per_UTC_instant":sizes,
      "source_zarr":STORE,"source_variable":VARIABLE,
      "source_hifld_weight_sha256":hashlib.sha256(Path(a.hifld_weights).read_bytes()).hexdigest(),
      "source_county_weight_sha256":hashlib.sha256(Path(a.county_weights).read_bytes()).hexdigest(),
      "BA_proxy_A":"2018 HIFLD national control area repaired candidates",
      "BA_proxy_B":"2024 Census TIGER annual EIA-861 county union proxy",
      "date_sample_not_full_hourly_B_source":True,
      "model_geography_approved":False,
      "no_weather_demand_training":True,
      "no_anthropogenic_climate_attribution":True}
    (out/"eight_real_hour_spatial_sensitivity_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("REAL_AB_8_HOUR_SUMMARY",json.dumps({"BA":summary,**manifest}),flush=True)
if __name__=="__main__":main()
