"""Matched 24-hour REAL ARCO ERA5 alternative BA geographic-mask sensitivity.

All weather is actual public ERA5 reanalysis, both BA spatial masks remain
explicitly UNAPPROVED, and this script neither fits demand nor attribution.
"""
import argparse,csv,hashlib,json,statistics
from pathlib import Path
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_public_probe import STORE
from src.c2_census_vs_hifld_era5 import difference

BAS=("AZPS","BPAT","CISO","SRP")
def match_days(a_rows,b_rows):
    a={(x["timestamp_utc_start"],x["ba"]):x for x in a_rows}
    b={(x["timestamp_utc_start"],x["ba"]):x for x in b_rows}
    if len(a)!=96 or len(b)!=96 or set(a)!=set(b):
        raise ValueError("All four BAs must have exactly 24 identical UTC hours")
    joined=[]
    for time,ba in sorted(a):
        old=a[time,ba];new=b[time,ba]
        if old["historical_weather_exposure_approved"] is not False or new["historical_weather_exposure_approved"] is not False:
            raise ValueError("Both geographic proxy exposures are unapproved")
        delta=round(new["weighted_temperature_celsius"]-old["weighted_temperature_celsius"],6)
        joined.append({"timestamp_utc_start":time,"ba":ba,
            "HIFLD_2018_candidate_celsius":old["weighted_temperature_celsius"],
            "Census_2024_county_proxy_celsius":new["weighted_temperature_celsius"],
            "Census_minus_HIFLD_celsius":delta,
            "HIFLD_grid_cells":old["grid_cells"],
            "Census_grid_cells":new["grid_cells"],
            "historical_geography_approved":False,
            "training_permitted":False})
    return joined

def summarize(rows):
    records=[]
    for ba in BAS:
        vals=[x["Census_minus_HIFLD_celsius"] for x in rows if x["ba"]==ba]
        if len(vals)!=24:raise ValueError("Not 24 source hours for "+ba)
        records.append({"ba":ba,"hours":24,
            "mean_Census_minus_HIFLD_celsius":round(statistics.mean(vals),6),
            "median_Census_minus_HIFLD_celsius":round(statistics.median(vals),6),
            "min_Census_minus_HIFLD_celsius":min(vals),
            "max_Census_minus_HIFLD_celsius":max(vals),
            "negative_hours":sum(x<0 for x in vals),
            "positive_hours":sum(x>0 for x in vals),
            "model_geography_approved":False})
    return records

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hifld-weights",required=True)
    p.add_argument("--county-weights",required=True)
    p.add_argument("--utc-day",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    if not a.utc_day.endswith("T00:00:00Z"):
        raise ValueError("UTC midnight required for an exact 24h comparison")
    aa=load_exploratory_weights(a.hifld_weights)
    bb=load_exploratory_weights(a.county_weights)
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    old,oldqa=calculate_24(ds,aa,a.utc_day)
    new,newqa=calculate_24(ds,bb,a.utc_day)
    if oldqa["row_count"]!=96 or newqa["row_count"]!=96:
        raise ValueError("Missing real hourly ERA5 record")
    paired=match_days(old,new)
    summary=summarize(paired)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    def write(name,rows):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    write("REAL_ERA5_24h_Census_minus_HIFLD_spatial_sensitivity.csv",paired)
    write("REAL_ERA5_24h_BA_spatial_sensitivity_statistics.csv",summary)
    provenance={"UTC_start":a.utc_day,"BA_hour_comparisons":len(paired),
      "source":"public ARCO ERA5 genuine 2m temperature 0.25 degree reanalysis",
      "source_HIFLD_weight_SHA256":hashlib.sha256(Path(a.hifld_weights).read_bytes()).hexdigest(),
      "source_Census_weight_SHA256":hashlib.sha256(Path(a.county_weights).read_bytes()).hexdigest(),
      "HIFLD_source_vintage":2018,"Census_TIGER_geometry_vintage":2024,
      "hifld_real_source_BA_hours":oldqa["row_count"],
      "census_real_source_BA_hours":newqa["row_count"],
      "all_24_UTC_hours_present":True,
      "summary":summary,
      "BA_geography_approved":False,"weather_load_model_fitted":False,
      "anthropogenic_attribution_performed":False}
    (out/"REAL_ERA5_24h_A_B_geography_provenance.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("REAL_24H_AB_GEOGRAPHY_SENSITIVITY",json.dumps(provenance),flush=True)
if __name__=="__main__":main()
