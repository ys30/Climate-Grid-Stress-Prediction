"""Strict frozen-source reconciliation of four REAL 24h ERA5 geo-proxy comparisons.

This is meteorological spatial-estimand sensitivity only; neither mask is
approved for an EIA BA operating-area weather-demand model.
"""
import argparse,csv,json,hashlib,statistics
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path

BAS=("AZPS","BPAT","CISO","SRP")
TIMES=("2023-01-15T00:00:00Z","2023-07-01T00:00:00Z",
       "2025-01-15T00:00:00Z","2025-07-01T00:00:00Z")
A_SHA="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"
B_SHA="6526de6271ead635293f9d3d7165ea15c3e750a725788eb9b4d5a3d5eb5db0c8"
DATA_NAME="REAL_ERA5_24h_Census_minus_HIFLD_spatial_sensitivity.csv"
META_NAME="REAL_ERA5_24h_A_B_geography_provenance.json"

def consolidate(directories):
    found={};all_rows=[]
    for path in directories:
        folder=Path(path)
        meta=json.loads((folder/META_NAME).read_text())
        t=meta["UTC_start"]
        if t not in TIMES or t in found:raise ValueError("Unexpected/duplicate real source day")
        if meta["source_HIFLD_weight_SHA256"]!=A_SHA or meta["source_Census_weight_SHA256"]!=B_SHA:
            raise ValueError("Archived source geometry digests do not match frozen masks")
        if (meta.get("BA_geography_approved") is not False or
            meta.get("weather_load_model_fitted") is not False or
            meta.get("anthropogenic_attribution_performed") is not False):
            raise ValueError("Unexpected source geography/model authorization")
        if meta.get("BA_hour_comparisons")!=96 or meta.get("all_24_UTC_hours_present") is not True:
            raise ValueError("Incomplete source UTC day")
        with (folder/DATA_NAME).open(newline="") as f:rows=list(csv.DictReader(f))
        if len(rows)!=96:raise ValueError("Not 96 real BA-hour comparisons")
        base=datetime.fromisoformat(t.replace("Z","+00:00"))
        actual=set()
        for row in rows:
            if row["ba"] not in BAS:raise ValueError("Unmapped BA")
            ts=datetime.fromisoformat(row["timestamp_utc_start"].replace("Z","+00:00"))
            if not (base<=ts<base+timedelta(days=1)) or ts.minute or ts.second:
                raise ValueError("Bad timestamp or out-of-day observation")
            key=(row["ba"],ts)
            if key in actual:raise ValueError("Duplicate UTC BA-hour")
            actual.add(key)
            if row.get("historical_geography_approved")!="False" or row.get("training_permitted")!="False":
                raise ValueError("Provisional weather falsely model-admitted")
            left=float(row["HIFLD_2018_candidate_celsius"])
            right=float(row["Census_2024_county_proxy_celsius"])
            delta=float(row["Census_minus_HIFLD_celsius"])
            if abs((right-left)-delta)>0.000002:
                raise ValueError("Reported proxy delta does not match actual source weather")
            row["source_day"]=t[:10]
            all_rows.append(row)
        expected={(ba,base+timedelta(hours=h)) for ba in BAS for h in range(24)}
        if actual!=expected:raise ValueError("Missing real BA×UTC hour")
        found[t]=meta
    if set(found)!=set(TIMES):raise ValueError("Require exactly four source-valid days")
    summary=[]
    for ba in BAS:
        values=[float(r["Census_minus_HIFLD_celsius"]) for r in all_rows if r["ba"]==ba]
        if len(values)!=96:raise ValueError("BA not complete across days")
        summary.append({"ba":ba,"real_weather_hours_compared":len(values),
          "mean_delta_c":round(statistics.mean(values),6),
          "median_delta_c":round(statistics.median(values),6),
          "min_delta_c":min(values),"max_delta_c":max(values),
          "negative_hours":sum(x<0 for x in values),
          "positive_hours":sum(x>0 for x in values),
          "training_permitted":False})
    return sorted(all_rows,key=lambda r:(r["source_day"],r["timestamp_utc_start"],r["ba"])),summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-folders",nargs="+",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    rows,summary=consolidate(a.source_folders)
    dest=Path(a.out);dest.mkdir(parents=True,exist_ok=True)
    for filename,contents in (("REAL_ERA5_384_hourly_HIFLD_TIGER_proxy_delta.csv",rows),
                              ("REAL_ERA5_384_hourly_4BA_summary.csv",summary)):
        with (dest/filename).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(contents[0]))
            w.writeheader();w.writerows(contents)
    result={"days":list(TIMES),"four_BA_hourly_observations":len(rows),
        "BA_results":summary,"A_hifld_sha256":A_SHA,"B_county_sha256":B_SHA,
        "data_source":"actual public ARCO ERA5 2m temperature","four_days_not_full_year":True,
        "BA_historical_operating_geography_approved":False,
        "training_permitted":False,
        "climate_attribution_performed":False}
    (dest/"REAL_ERA5_384_AB_SUMMARY_PROVENANCE.json").write_text(json.dumps(result,indent=2)+"\n")
    print("REAL_ERA5_384_HOUR_AB_SUMMARY",json.dumps(result),flush=True)
if __name__=="__main__":main()
