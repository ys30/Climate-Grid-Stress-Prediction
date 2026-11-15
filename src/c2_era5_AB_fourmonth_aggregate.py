"""Independently verify full-calendar-month real ERA5 proxy A/B experiments.

Rows represent geographically distinct area means of the SAME ERA5 grid, not
independent BA weather instruments. No model/geographic approval is implied.
"""
import argparse,calendar,csv,hashlib,json,statistics
from datetime import datetime,timedelta
from pathlib import Path
from collections import defaultdict
from src.c2_era5_AB_sevenday_sensitivity import BAS,A_SHA,B_SHA

MONTHS=("2023-01-01T00:00:00Z","2023-07-01T00:00:00Z",
        "2025-01-01T00:00:00Z","2025-07-01T00:00:00Z")
FILE="REAL_ERA5_MONTH_HIFLD_A_VS_TIGER_COUNTY_B_4BA_HOURLY_UNAPPROVED.csv"
MANIFEST="REAL_ERA5_MONTH_AB_SOURCE_MANIFEST.json"

def reconcile(folders):
    found={};full=[]
    for folder in folders:
        path=Path(folder)
        info=json.loads((path/MANIFEST).read_text())
        when=info["UTC_month_start"]
        if when not in MONTHS or when in found:
            raise ValueError("Unknown or duplicate original calendar month")
        days=calendar.monthrange(int(when[:4]),int(when[5:7]))[1]
        expected=days*24*4
        if (info.get("days")!=days or info.get("actual_ERA5_BA_hour_pairs")!=expected
            or info.get("A_hifld2018_weights_sha256")!=A_SHA
            or info.get("B_TIGER2024_county_weights_sha256")!=B_SHA
            or info.get("single_source_grid_read_for_both_area_weight_proxies") is not True
            or info.get("BA_operational_geography_approved") is not False
            or info.get("weather_load_model_training_permitted") is not False
            or info.get("climate_attribution_performed") is not False):
            raise ValueError("Inconsistent actual ERA5 source-month provenance")
        file=path/FILE
        if hashlib.sha256(file.read_bytes()).hexdigest()!=info["raw_hourly_CSV_sha256"]:
            raise ValueError("Original real source CSV SHA256 mismatch")
        with file.open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        if len(rows)!=expected:raise ValueError("Source monthly BA-hour count mismatch")
        begin=datetime.fromisoformat(when.replace("Z","+00:00"))
        observed=set()
        for row in rows:
            stamp=datetime.fromisoformat(row["timestamp_utc_start"].replace("Z","+00:00"))
            ba=row["ba"]
            key=(ba,stamp)
            if ba not in BAS or key in observed:
                raise ValueError("Unrecognized or duplicate monthly BA-hour key")
            observed.add(key)
            if row["historical_geography_approved"]!="False" or row["training_permitted"]!="False":
                raise ValueError("One of the source geographic masks falsely model-admitted")
            delta=float(row["Census_minus_HIFLD_celsius"])
            if abs(delta-(float(row["Census_2024_county_proxy_celsius"])-float(row["HIFLD_2018_candidate_celsius"])))>0.000002:
                raise ValueError("Actual ERA5 proxy temperature delta inconsistent")
            full.append({"calendar_month":when[:7],**row})
        expected_set={(ba,begin+timedelta(hours=h)) for ba in BAS for h in range(days*24)}
        if observed!=expected_set:raise ValueError("Original calendar month UTC source hours are not exhaustive")
        found[when]=info
    if set(found)!=set(MONTHS):raise ValueError("Require four independently verified full calendar source months")
    ba_summary=[];month_summary=[];day_summary=[]
    for ba in BAS:
        allrows=[r for r in full if r["ba"]==ba]
        deltas=[float(r["Census_minus_HIFLD_celsius"]) for r in allrows]
        if len(deltas)!=4*31*24:raise ValueError("Each BA needs four complete January/July 31-day sources")
        daygroups=defaultdict(list)
        for row in allrows:
            daygroups[row["timestamp_utc_start"][:10]].append(float(row["Census_minus_HIFLD_celsius"]))
        if len(daygroups)!=124 or any(len(v)!=24 for v in daygroups.values()):
            raise ValueError("Expected 124 full daily BA source estimates")
        ba_summary.append({"ba":ba,"real_ERA5_hours":len(deltas),
            "mean_B_minus_A_c":round(statistics.mean(deltas),6),
            "median_B_minus_A_c":round(statistics.median(deltas),6),
            "minimum_B_minus_A_c":min(deltas),"maximum_B_minus_A_c":max(deltas),
            "negative_hours":sum(v<0 for v in deltas),
            "negative_daily_means":sum(statistics.mean(v)<0 for v in daygroups.values()),
            "daily_mean_units_not_independent_hourly_tests":True,
            "historical_geometry_approved":False,
            "training_allowed":False})
        for date,vals in sorted(daygroups.items()):
            day_summary.append({"ba":ba,"date_UTC":date,"daily_mean_B_minus_A_c":round(statistics.mean(vals),6),
              "hours":len(vals),"training_allowed":False})
        for month in MONTHS:
            subset=[r for r in allrows if r["calendar_month"]==month[:7]]
            v=[float(r["Census_minus_HIFLD_celsius"]) for r in subset]
            if len(v)!=744:raise ValueError("Month partial for BA")
            month_summary.append({"ba":ba,"month_UTC":month[:7],
              "mean_B_minus_A_c":round(statistics.mean(v),6),
              "min_B_minus_A_c":min(v),"max_B_minus_A_c":max(v),
              "negative_hours":sum(x<0 for x in v),
              "historical_geography_approved":False})
    return full,ba_summary,month_summary,day_summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-folders",nargs="+",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    data,BA,monthly,daily=reconcile(a.source_folders)
    target=Path(a.out);target.mkdir(parents=True,exist_ok=True)
    for name,records in (("REAL_ERA5_11904_HOURLY_FOUR_BA_AB.csv",data),
                         ("REAL_ERA5_4_MONTH_AB_BA_SUMMARY.csv",BA),
                         ("REAL_ERA5_4_MONTH_AB_MONTHLY_COMPARISON.csv",monthly),
                         ("REAL_ERA5_4_MONTH_AB_DAILY_MEANS.csv",daily)):
        with (target/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=list(records[0]))
            w.writeheader();w.writerows(records)
    report={"source_months":list(MONTHS),"independently_verified_BA_hours":len(data),
      "verified_months":4,"verified_daily_UTC_BA_observations":len(daily),
      "BA_results":BA,"A_weights_SHA256":A_SHA,"B_weights_SHA256":B_SHA,
      "source":"public actual ARCO ERA5 2m reanalysis 0.25-degree hourly",
      "2024_Census_county_geometry_fixed_across_years":True,
      "hours_are_serially_correlated":True,
      "geography_approved":False,"training_permitted":False,"ALL_NAT_attribution_performed":False}
    (target/"REAL_ERA5_FOUR_MONTH_AB_PROVENANCE.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_ERA5_4MONTH_AB_SUMMARY",json.dumps(report),flush=True)
if __name__=="__main__":main()
