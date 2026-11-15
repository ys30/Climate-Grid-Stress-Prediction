"""Seven-day, independent real ERA5 geographical exposure proxy sensitivity.

A = HIFLD 2018 repaired candidate; B = EIA861 county / TIGER 2024 union.
Both unapproved, no historical BA load/weather modeling or attribution.
"""
import argparse,csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_AB_24hour_sensitivity import match_days
from src.c2_era5_public_probe import STORE

BAS=("AZPS","BPAT","CISO","SRP")
A_SHA="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"
B_SHA="6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8"

def check_window(start,days):
    begin=datetime.fromisoformat(start.replace("Z","+00:00"))
    if begin.utcoffset() is None or begin.utcoffset().total_seconds()!=0 or any((begin.hour,begin.minute,begin.second,begin.microsecond)):
        raise ValueError("Exact UTC midnight start needed")
    if days!=7:raise ValueError("Exactly seven contiguous full UTC days")
    if begin.year not in (2023,2025) or begin.month not in (1,7) or begin.day!=15 and begin.month==1 or begin.day!=1 and begin.month==7:
        raise ValueError("Reject data outside preregistered seasonal source windows")
    return begin

def summarize_all(rows):
    if len(rows)!=7*24*4:raise ValueError("Expected 672 BA-hour comparison rows")
    expected=7*24
    overall=[];daily=[]
    for ba in BAS:
        values=[r for r in rows if r["ba"]==ba]
        if len(values)!=expected:raise ValueError("Missing BA-week source rows")
        nums=[r["Census_minus_HIFLD_celsius"] for r in values]
        overall.append({"ba":ba,"observed_hours":expected,
             "mean_B_minus_A_c":round(statistics.mean(nums),6),
             "median_B_minus_A_c":round(statistics.median(nums),6),
             "min_B_minus_A_c":min(nums),"max_B_minus_A_c":max(nums),
             "negative_hours":sum(v<0 for v in nums),
             "positive_hours":sum(v>0 for v in nums),
             "historical_BA_geography_approved":False,"model_training_permitted":False})
        by_day=defaultdict(list)
        for row in values:by_day[row["timestamp_utc_start"][:10]].append(row["Census_minus_HIFLD_celsius"])
        if len(by_day)!=7 or any(len(vals)!=24 for vals in by_day.values()):
            raise ValueError("Missing BA/day source observations")
        for day,vals in sorted(by_day.items()):
            daily.append({"ba":ba,"utc_day":day,"N_hours":24,
                 "mean_B_minus_A_c":round(statistics.mean(vals),6),
                 "min_B_minus_A_c":min(vals),"max_B_minus_A_c":max(vals),
                 "negative_hours":sum(v<0 for v in vals),
                 "historical_BA_geography_approved":False})
    return overall,daily

def audit_and_run(start,days,afile,bfile,out):
    begin=check_window(start,days)
    if hashlib.sha256(Path(afile).read_bytes()).hexdigest()!=A_SHA:
        raise ValueError("Unverified frozen HIFLD candidate area weights")
    if hashlib.sha256(Path(bfile).read_bytes()).hexdigest()!=B_SHA:
        raise ValueError("Unverified frozen Census county candidate area weights")
    a=load_exploratory_weights(afile);b=load_exploratory_weights(bfile)
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    all_rows=[]
    for i in range(days):
        day=(begin+timedelta(days=i)).strftime("%Y-%m-%dT00:00:00Z")
        a_rows,a_meta=calculate_24(ds,a,day)
        b_rows,b_meta=calculate_24(ds,b,day)
        if a_meta["contiguous_UTC_hours_verified"] is not True or b_meta["contiguous_UTC_hours_verified"] is not True:
            raise ValueError("Source UTC continuity not proven")
        joined=match_days(a_rows,b_rows)
        if len(joined)!=96:raise ValueError("Incomplete one-day matching")
        all_rows.extend(joined)
        print("REAL_ERA5_AB_SEVEN_DAY_INCREMENT",json.dumps({"day":day,"BA_hour_comparisons":len(joined),
             "ERA5_source_grid_cells_each_hour_A":a_meta["source_grid_cells_per_hour"],
             "ERA5_source_grid_cells_each_hour_B":b_meta["source_grid_cells_per_hour"],
             "geometry_approved":False}),flush=True)
    counts={(r["ba"],r["timestamp_utc_start"]) for r in all_rows}
    if len(counts)!=len(all_rows):raise ValueError("Duplicate BA UTC source hour")
    expected={(ba,(begin+timedelta(hours=h)).isoformat()) for ba in BAS for h in range(7*24)}
    if counts!=expected:raise ValueError("Missing or out-of-window BA UTC hour")
    overall,daily=summarize_all(all_rows)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    def save(name,records):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    save("REAL_ERA5_7DAY_HIFLD_Census_AB_HOURLY_UNAPPROVED.csv",all_rows)
    save("REAL_ERA5_7DAY_BA_DELTA_STATISTICS_UNAPPROVED.csv",overall)
    save("REAL_ERA5_7DAY_BA_DAILY_DELTA_UNAPPROVED.csv",daily)
    manifest={"source_start_UTC":start,"days":days,"observed_BA_hours":len(all_rows),
      "original_public_ERA5_store":STORE,"HIFLD_A_weights_SHA256":A_SHA,"Census_B_weights_SHA256":B_SHA,
      "four_BA_statistics":overall,"N_daily_BA_diagnostics":len(daily),
      "2024_TIGER_county_geometry_used_for_other_years":True,
      "official_historical_BA_geography_approved":False,
      "model_training_permitted":False,"anthropogenic_climate_attribution_performed":False,
      "interpretation":"True ERA5 2m reanalysis spatial sensitivity for two UNAPPROVED geographic candidate area masks"}
    (out/"REAL_ERA5_7DAY_AB_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("REAL_ERA5_AB_7DAY_SUMMARY",json.dumps(manifest),flush=True)
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True);p.add_argument("--days",type=int,default=7)
    p.add_argument("--hifld-weights",required=True)
    p.add_argument("--county-weights",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    audit_and_run(a.start,a.days,a.hifld_weights,a.county_weights,a.out)
if __name__=="__main__":main()
