"""Full calendar-month real ERA5 A/B geographic support sensitivity.

Read each actual ARCO ERA5 24-hour bounding grid ONCE for both provisional
geographies. EIA-930 reporting areas have not been geographically certified.
"""
import argparse,csv,hashlib,json,statistics,calendar
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_AB_24hour_sensitivity import match_days
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_public_probe import STORE
from src.c2_era5_AB_sevenday_sensitivity import BAS,A_SHA,B_SHA

def build_joint_source_groups(old,new):
    if set(old)!=set(BAS) or set(new)!=set(BAS):
        raise ValueError("Four study BAs required in both source masks")
    groups={"A_"+ba:old[ba] for ba in BAS}
    groups.update({"B_"+ba:new[ba] for ba in BAS})
    return groups

def split_one_read(rows):
    if len(rows)!=24*8:raise ValueError("Eight proxy BA-area series x 24 UTC hours required")
    a=[];b=[]
    for r in rows:
        key=r["ba"];prefix,sep,ba=key.partition("_")
        if sep!="_" or prefix not in ("A","B") or ba not in BAS:
            raise ValueError("Unexpected proxy key in real ERA5 grid result")
        (a if prefix=="A" else b).append({**r,"ba":ba})
    return match_days(a,b)

def check_month(start):
    dt=datetime.fromisoformat(start.replace("Z","+00:00"))
    if (dt.year not in (2023,2025) or dt.month not in (1,7) or dt.day!=1
        or dt.utcoffset() is None or dt.utcoffset().total_seconds()!=0
        or any((dt.hour,dt.minute,dt.second,dt.microsecond))):
        raise ValueError("Only preregistered 2023/2025 January/July UTC calendar months")
    return dt,calendar.monthrange(dt.year,dt.month)[1]

def month_stats(rows,days):
    if len(rows)!=days*24*len(BAS):
        raise ValueError("Missing real monthly BA-hour geographical comparisons")
    overall=[];daily=[]
    for ba in BAS:
        arr=[r for r in rows if r["ba"]==ba]
        if len(arr)!=days*24:raise ValueError("Missing source hour for "+ba)
        deltas=[float(r["Census_minus_HIFLD_celsius"]) for r in arr]
        by_date=defaultdict(list)
        for r in arr:by_date[r["timestamp_utc_start"][:10]].append(r["Census_minus_HIFLD_celsius"])
        if len(by_date)!=days or any(len(v)!=24 for v in by_date.values()):
            raise ValueError("Each BA must have full 24h ERA5 days")
        daily_means=[]
        for date,values in sorted(by_date.items()):
            mean=statistics.mean(values)
            daily_means.append(mean)
            daily.append({"ba":ba,"utc_date":date,"hours":24,
               "mean_B_minus_A_c":round(mean,6),
               "min_B_minus_A_c":min(values),"max_B_minus_A_c":max(values),
               "hours_B_colder":sum(v<0 for v in values),
               "approved_historical_BA_geography":False})
        overall.append({"ba":ba,"actual_ERA5_hours":days*24,
            "mean_B_minus_A_c":round(statistics.mean(deltas),6),
            "median_B_minus_A_c":round(statistics.median(deltas),6),
            "min_B_minus_A_c":min(deltas),"max_B_minus_A_c":max(deltas),
            "hours_B_colder":sum(v<0 for v in deltas),
            "days_with_negative_daily_mean":sum(v<0 for v in daily_means),
            "daily_mean_min_c":round(min(daily_means),6),
            "daily_mean_max_c":round(max(daily_means),6),
            "historical_BA_geography_approved":False,
            "weather_load_model_permitted":False})
    return overall,daily

def run(start,afile,bfile,outdir):
    begin,days=check_month(start)
    if hashlib.sha256(Path(afile).read_bytes()).hexdigest()!=A_SHA:
        raise ValueError("HIFLD weight SHA256 not frozen")
    if hashlib.sha256(Path(bfile).read_bytes()).hexdigest()!=B_SHA:
        raise ValueError("TIGER county weight SHA256 not frozen")
    old=load_exploratory_weights(afile);new=load_exploratory_weights(bfile)
    combined=build_joint_source_groups(old,new)
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    output=Path(outdir);output.mkdir(parents=True,exist_ok=True)
    raw_path=output/"REAL_ERA5_MONTH_HIFLD_A_VS_TIGER_COUNTY_B_4BA_HOURLY_UNAPPROVED.csv"
    records=0;all_rows=[];source_cells_per_hour=None
    with raw_path.open("w",newline="") as stream:
        writer=None
        for d in range(days):
            at=(begin+timedelta(days=d)).strftime("%Y-%m-%dT00:00:00Z")
            both,qa=calculate_24(ds,combined,at)
            if qa["row_count"]!=192 or qa["contiguous_UTC_hours_verified"] is not True:
                raise ValueError("Real source hour coverage failure")
            rows=split_one_read(both)
            if len(rows)!=96:raise ValueError("24*4 real BA pairs missing")
            if writer is None:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
                writer.writeheader()
            writer.writerows(rows);stream.flush()
            all_rows.extend(rows);records+=len(rows)
            source_cells_per_hour=qa["source_grid_cells_per_hour"]
            print("REAL_ERA5_AB_MONTH_DAY",json.dumps({
               "UTC_date":at[:10],"rows":len(rows),
               "one_common_source_grid_cells_per_hour":source_cells_per_hour,
               "model_training_permitted":False}),flush=True)
    expected={(ba,(begin+timedelta(hours=h)).isoformat())
              for ba in BAS for h in range(days*24)}
    actual={(r["ba"],r["timestamp_utc_start"]) for r in all_rows}
    if len(actual)!=records or actual!=expected:
        raise ValueError("BA-hour monthly exact UTC coverage failed")
    overall,daily=month_stats(all_rows,days)
    with (output/"REAL_ERA5_MONTH_BA_STATISTICS_UNAPPROVED.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(overall[0]));w.writeheader();w.writerows(overall)
    with (output/"REAL_ERA5_MONTH_BA_DAILY_MEANS_UNAPPROVED.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(daily[0]));w.writeheader();w.writerows(daily)
    manifest={"UTC_month_start":start,"days":days,"actual_ERA5_BA_hour_pairs":records,
      "actual_ERA5_source_grid_cells_per_hour":source_cells_per_hour,
      "source":"public ARCO ERA5 hourly reanalysis 2m T 0.25 degree",
      "single_source_grid_read_for_both_area_weight_proxies":True,
      "A_hifld2018_weights_sha256":A_SHA,"B_TIGER2024_county_weights_sha256":B_SHA,
      "raw_hourly_CSV_sha256":hashlib.sha256(raw_path.read_bytes()).hexdigest(),
      "BA_results":overall,"daily_summary_records":len(daily),
      "fixed_2024_TIGER_counties_used_outside_2024":True,
      "BA_operational_geography_approved":False,
      "weather_load_model_training_permitted":False,
      "climate_attribution_performed":False,
      "temporal_independence_of_hours_assumed":False}
    (output/"REAL_ERA5_MONTH_AB_SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("REAL_ERA5_MONTH_AB_SUMMARY",json.dumps(manifest),flush=True)
    return manifest

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True)
    p.add_argument("--hifld-weights",required=True)
    p.add_argument("--county-weights",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.start,a.hifld_weights,a.county_weights,a.out)
if __name__=="__main__":main()
