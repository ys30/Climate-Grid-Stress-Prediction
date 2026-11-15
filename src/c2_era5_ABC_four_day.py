"""Four complete real ERA5 diurnal days under three unapproved spatial proxies.

A=HIFLD 2018 area, B=TIGER 2024 EIA861 county area, C=Census CO-EST2025
2020 estimates-base county population (uniform within-county allocation).
No real customer/load weights, no BA geography certification, no modeling.
"""
import argparse,csv,hashlib,json,statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from src.c2_era5_24h_exploratory import calculate_24
from src.c2_era5_full_grid_one_hour import load_exploratory_weights
from src.c2_era5_public_probe import STORE
from src.c2_era5_AB_sevenday_sensitivity import BAS,A_SHA,B_SHA

DAYS=("2023-01-15T00:00:00Z","2023-07-01T00:00:00Z",
      "2025-01-15T00:00:00Z","2025-07-01T00:00:00Z")
C_SHA="741d9e1b1101b6a018311803dee6e42fda8b5dacf26ccf40e876171383335361"

def normalize_day(rows,day):
    if len(rows)!=3*4*24:raise ValueError("Missing one or more A/B/C source BA-hour")
    base=datetime.fromisoformat(day.replace("Z","+00:00"))
    bucket={}
    for r in rows:
        tag,sep,ba=r["ba"].partition("_")
        stamp=datetime.fromisoformat(r["timestamp_utc_start"].replace("Z","+00:00"))
        if tag not in "ABC" or not sep or ba not in BAS:
            raise ValueError("Unrecognized proxy or BA code")
        if r["historical_weather_exposure_approved"] is not False:
            raise ValueError("Source weather masks are NOT historically approved")
        key=(tag,ba,stamp)
        if key in bucket:raise ValueError("Duplicate A/B/C BA-hour")
        bucket[key]=float(r["weighted_temperature_celsius"])
    from datetime import timedelta
    expected={(tag,ba,base+timedelta(hours=h)) for tag in "ABC" for ba in BAS for h in range(24)}
    if set(bucket)!=expected:raise ValueError("ERA5 source hours incomplete or UTC shifted")
    output=[]
    for h in range(24):
        stamp=base+timedelta(hours=h)
        for ba in BAS:
            a,b,c=(bucket[(tag,ba,stamp)] for tag in "ABC")
            output.append({"UTC_timestamp":stamp.isoformat(),"BA":ba,
                "HIFLD_A_celsius":a,"TIGER_B_celsius":b,
                "population_C_celsius":c,
                "C_minus_B_celsius":round(c-b,6),
                "C_minus_A_celsius":round(c-a,6),
                "B_minus_A_celsius":round(b-a,6),
                "population_is_customer_weights":False,
                "historical_BA_geography_approved":False,
                "training_permitted":False})
    return output

def summarize(rows):
    if len(rows)!=4*24*4:raise ValueError("Four real 24h days × four BAs required")
    result=[]
    for ba in BAS:
        subset=[r for r in rows if r["BA"]==ba]
        if len(subset)!=96:raise ValueError("All BA source-hours required")
        cb=[r["C_minus_B_celsius"] for r in subset]
        ca=[r["C_minus_A_celsius"] for r in subset]
        result.append({"BA":ba,"N_hours":len(subset),
            "mean_C_minus_B_celsius":round(statistics.mean(cb),6),
            "min_C_minus_B_celsius":min(cb),"max_C_minus_B_celsius":max(cb),
            "hours_C_warmer_than_B":sum(x>0 for x in cb),
            "mean_C_minus_A_celsius":round(statistics.mean(ca),6),
            "historical_BA_geography_approved":False,
            "model_training_permitted":False})
    return result

def main():
    p=argparse.ArgumentParser()
    for key in ("A-hifld","B-county","C-population","C-manifest"):
        p.add_argument("--"+key,required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    paths=(args.A_hifld,args.B_county,args.C_population)
    digests=[hashlib.sha256(Path(path).read_bytes()).hexdigest() for path in paths]
    if digests!=[A_SHA,B_SHA,C_SHA]:raise ValueError("Frozen population/area source SHA256 differs")
    source=json.loads(Path(args.C_manifest).read_text())
    if (source.get("weight_csv_sha256")!=C_SHA or
        source.get("census2020_variable")!="ESTIMATESBASE2020" or
        source.get("population_is_original_decennial_PL_P1_001N") is not False or
        source.get("actual_customers_or_load_distribution_observed") is not False or
        source.get("model_training_permitted") is not False):
        raise ValueError("Population C source and scientific status not proven")
    groups={}
    for tag,path in zip("ABC",paths):
        one=load_exploratory_weights(path)
        groups.update({tag+"_"+ba:one[ba] for ba in BAS})
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    records=[]
    for day in DAYS:
        rows,meta=calculate_24(ds,groups,day)
        if meta.get("row_count")!=288 or meta.get("contiguous_UTC_hours_verified") is not True:
            raise ValueError("One-day ERA5 A/B/C input incomplete")
        matching=normalize_day(rows,day)
        records.extend(matching)
        print("REAL_ERA5_ABC_DIURNAL_DAY",json.dumps({"day":day,"N_BA_hours":len(matching),
              "actual_source_grid_cells_per_hour":meta["source_grid_cells_per_hour"],
              "geography_approved":False}),flush=True)
    summary=summarize(records)
    folder=Path(args.out);folder.mkdir(parents=True,exist_ok=True)
    for name,records_ in (("REAL_ERA5_ABC_FOUR_DAYS_384_BA_HOURS.csv",records),
                          ("REAL_ERA5_ABC_FOUR_DAYS_BA_SUMMARY.csv",summary)):
        with (folder/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records_[0]))
            w.writeheader();w.writerows(records_)
    provenance={"actual_sample_days":list(DAYS),"BA_hours":len(records),
                "frozen_weight_SHA256":dict(zip("ABC",digests)),
                "population_source":"Census CO-EST2025 ESTIMATESBASE2020 county proxy",
                "TIGER_geometry_vintage":2024,
                "source":"public ARCO ERA5 hourly 2m reanalysis",
                "BA_summary":summary,
                "geography_approved":False,"model_training_permitted":False,
                "independent_hourly_tests_assumed":False}
    (folder/"REAL_ERA5_ABC_4DAY_PROVENANCE.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("REAL_ERA5_ABC_DIURNAL_FOUR_DAY_SUMMARY",json.dumps(provenance),flush=True)
if __name__=="__main__":main()
