"""Seasonal 48-hour REAL ERA5/EIA-930 source pairing; never model-ready.

This is an empirical reproducibility and temporal coverage experiment using
UNAPPROVED 2018-era candidate BA polygons. It does not train or infer climate impacts.
"""
import argparse,csv,hashlib,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_boundary_and_outlier_gate import load_records,flag_series
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_public_probe import STORE

BAS=("AZPS","BPAT","CISO","SRP")

def seasonal_source_pair(weather_rows,demand,flagged,start,days,allow_missing_demand=False):
    begin=datetime.fromisoformat(start.replace("Z","+00:00"))
    if begin.utcoffset() is None or begin.utcoffset().total_seconds()!=0:
        raise ValueError("UTC start required")
    total=24*days
    if len(weather_rows)!=total*4:raise ValueError("Missing ERA5 rows for a BA hour")
    flagged_keys={(x["ba"],x["timestamp_utc_start"]) for x in flagged}
    observed={}
    for x in weather_rows:
        if x.get("historical_weather_exposure_approved") is not False:
            raise ValueError("Weather geographic review falsely authorized")
        key=(x["ba"],x["timestamp_utc_start"])
        if key in observed:raise ValueError("Duplicate BA-hour weather key")
        observed[key]=x
    result=[]
    for ba in BAS:
        for h in range(total):
            t=begin+timedelta(hours=h)
            key=(ba,t.isoformat())
            w=observed.get(key)
            if w is None:raise ValueError("Missing exact UTC weather "+str(key))
            val=demand[ba].get(t)
            if val is None and not allow_missing_demand:
                raise ValueError("Missing original EIA-930 demand "+str(key))
            result.append({"ba":ba,"timestamp_utc_start":t.isoformat(),
                           "demand_mw_raw":val,
                           "temperature_c_experimental_area":w["weighted_temperature_celsius"],
                           "demand_spike_candidate":key in flagged_keys,
                           "demand_observed":val is not None,
                           "source_missing_demand":val is None,
                           "historical_BA_area_approved":False,
                           "train_or_validate_eligible":False})
    return result

def run(start,days,weights,eia_sources,out_dir,allow_source_gaps=False):
    import xarray as xr
    if days not in (2,3,7):raise ValueError("Limit source smoke study to 2, 3 or 7 days")
    begin=datetime.fromisoformat(start.replace("Z","+00:00"))
    if begin.tzinfo is None or begin.utcoffset().total_seconds()!=0 or begin.hour!=0:
        raise ValueError("UTC midnight required")
    if (begin+timedelta(days=days)).year!=begin.year:
        raise ValueError("This pilot must not cross year boundary")
    groups=load_exploratory_weights(weights)
    data,conflicts,sources=load_records(begin.year,eia_sources)
    if conflicts:raise ValueError("Conflicting EIA-930 timestamps")
    _,_,flags=flag_series(data,begin.year)
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    weather=[]
    for day in range(days):
        at=(begin+timedelta(days=day)).isoformat()
        rows,qa=calculate_24(ds,groups,at)
        if qa["row_count"]!=96 or not qa["contiguous_UTC_hours_verified"]:
            raise ValueError("24-hour weather data incomplete")
        weather.extend(rows)
    paired=seasonal_source_pair(weather,data,flags,begin.isoformat(),days,allow_missing_demand=allow_source_gaps)
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    def write_csv(name,items):
        with (out/name).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(items[0]))
            writer.writeheader();writer.writerows(items)
    write_csv("REAL_ERA5_48h_or_more_UNAPPROVED.csv",weather)
    write_csv("REAL_EIA_ERA5_48h_or_more_PAIRED_NOT_MODEL.csv",paired)
    missing_rows=[x for x in paired if x["source_missing_demand"]]
    if missing_rows:
        write_csv("REAL_EIA930_MISSING_DEMAND_EPISODES.csv",missing_rows)
    summary={"utc_start":begin.isoformat(),"days":days,"hours_per_BA":days*24,
             "paired_source_rows":len(paired)-len(missing_rows),
             "source_BA_hour_slots":len(paired),
             "source_missing_demand_hours":len(missing_rows),
             "weather_source_rows":len(weather),
             "BAs":list(BAS),"source_dataset":"ARCO ERA5 real 2m temperature",
             "weights_sha256":hashlib.sha256(Path(weights).read_bytes()).hexdigest(),
             "eia_original_sources":[{"file":x["file"],"sha256":x["sha256"]} for x in sources],
             "eia_candidate_anomaly_flags_in_window":
                 sum(x["demand_spike_candidate"] for x in paired),
             "all_source_hours_present":len(missing_rows)==0 and len(paired)==days*24*4,
             "all_weather_hours_present":len(weather)==days*24*4,
             "historical_geometry_approved":False,"no_imputation":True,
             "training_or_validation_permitted":False}
    (out/"seasonal_source_audit.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("REAL_SEASONAL_48H_SOURCE_AUDIT",json.dumps(summary))
    for ba in BAS:
        subset=[r for r in paired if r["ba"]==ba and r["demand_observed"]]
        print("SEASON_BA_SOURCE_RANGE",json.dumps({"ba":ba,
              "demand_mw_min":min(r["demand_mw_raw"] for r in subset),
              "demand_mw_max":max(r["demand_mw_raw"] for r in subset),
              "ERA5_area_candidate_min_c":min(r["temperature_c_experimental_area"] for r in subset),
              "ERA5_area_candidate_max_c":max(r["temperature_c_experimental_area"] for r in subset)}))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True)
    p.add_argument("--days",type=int,default=2)
    p.add_argument("--weights",required=True)
    p.add_argument("--eia-files",nargs="+",required=True)
    p.add_argument("--out",default="outputs/e1_seasonal")
    p.add_argument("--allow-source-gaps",action="store_true",
                   help="Audit missing observed EIA demand without filling or allowing training")
    a=p.parse_args()
    run(a.start,a.days,a.weights,a.eia_files,a.out,allow_source_gaps=a.allow_source_gaps)
if __name__=="__main__":main()
