"""Summarize independently archived real January+July sources 2020–25.

Twenty-four calendar-month/year combos are NOT implied: 12 observed month
windows only. Experimental polygon geography remains unapproved.
"""
import argparse,csv,json
from collections import Counter
from datetime import datetime
from pathlib import Path

YEARS=set(range(2020,2026))
MONTHS={1,7}
EXPECTED_WEIGHT="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"
def validate_months(manifests):
    checked={}
    for m in manifests:
        start=datetime.fromisoformat(m["utc_start"])
        key=(start.year,start.month)
        if start.year not in YEARS or start.month not in MONTHS or start.day!=1 or key in checked:
            raise ValueError("Unsupported or duplicate month/year")
        if m.get("days")!=31 or m.get("hours_per_BA")!=744 or m.get("source_BA_hour_slots")!=2976:
            raise ValueError("Not exactly 31 days per four BAs")
        if m.get("BAs")!=["AZPS","BPAT","CISO","SRP"]:
            raise ValueError("BA reporting scope changed")
        if m.get("weights_sha256")!=EXPECTED_WEIGHT:
            raise ValueError("Unapproved BA candidate spatial weight digest changed")
        if m.get("weather_source_rows")!=2976 or m.get("all_weather_hours_present") is not True:
            raise ValueError("Incomplete actual ERA5 31-day weather coverage")
        demand=m.get("paired_source_rows")
        missing=m.get("source_missing_demand_hours")
        if not isinstance(demand,int) or not isinstance(missing,int) or demand+missing!=2976:
            raise ValueError("Observed demand/missing demand accounting failure")
        if len(m.get("missing_demand_BA_hours",[]))!=missing:
            raise ValueError("Original load-missing episode count mismatch")
        if (m.get("historical_geometry_approved") is not False or
            m.get("training_or_validation_permitted") is not False or
            m.get("no_imputation") is not True):
            raise ValueError("Unreviewed geography, training or imputations introduced")
        checked[key]=m
    if set(checked)!={(y,mo) for y in YEARS for mo in MONTHS}:
        raise ValueError("Require all 12 source month-year combinations")
    rows=[]
    for (y,mo),m in sorted(checked.items()):
        rows.append({"year":y,"month":mo,"actual_ERA5_hours":2976,
           "original_EIA_demand_pairs":m["paired_source_rows"],
           "missing_original_demand_BA_hours":m["source_missing_demand_hours"],
           "original_load_anomaly_candidates":m["eia_candidate_anomaly_flags_in_window"],
           "spatial_geography_approved":False,"model_admitted":False})
    report={"source_month_count":12,"observed_years":sorted(YEARS),
        "months_audited_in_each_year":[1,7],
        "total_real_ERA5_BA_hours":sum(x["actual_ERA5_hours"] for x in rows),
        "total_observed_demand_weather_pairs":sum(x["original_EIA_demand_pairs"] for x in rows),
        "total_EIA_demand_missing_hours":sum(x["missing_original_demand_BA_hours"] for x in rows),
        "original_demand_anomaly_candidates":sum(x["original_load_anomaly_candidates"] for x in rows),
        "all_12_months_each_year_verified":False,
        "historical_BA_geography_approved":False,"training_permitted":False,
        "causal_climate_attribution_performed":False}
    return rows,report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifests",nargs="+",required=True)
    p.add_argument("--out",default="outputs/e1_jan_july_summary")
    a=p.parse_args()
    rows,summary=validate_months([json.loads(Path(x).read_text()) for x in a.manifests])
    d=Path(a.out);d.mkdir(parents=True,exist_ok=True)
    with (d/"actual_january_july_2020_2025_source_QA.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (d/"actual_january_july_source_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("REAL_JAN_JULY_SOURCE_SUMMARY",json.dumps(summary))
if __name__=="__main__":main()
