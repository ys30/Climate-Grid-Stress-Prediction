"""Aggregate exactly six real July full-month source audits, no model admission."""
import argparse,csv,json
from pathlib import Path
from collections import Counter

YEARS=set(range(2020,2026))
EXPECTED_WEIGHTS="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"
def consolidate(items):
    found={}
    for m in items:
        year=int(str(m["utc_start"])[:4])
        if year in found or year not in YEARS:
            raise ValueError("Duplicate or unsupported year")
        if (m.get("days"),m.get("hours_per_BA"),m.get("source_BA_hour_slots"))!=(31,744,2976):
            raise ValueError("Not a full July audit")
        if (m.get("weather_source_rows")!=2976 or m.get("all_weather_hours_present") is not True
            or m.get("source_dataset")!="ARCO ERA5 real 2m temperature"):
            raise ValueError("ERA5 full monthly source not verified")
        missing=m.get("source_missing_demand_hours")
        paired=m.get("paired_source_rows")
        if not isinstance(missing,int) or not isinstance(paired,int) or missing+paired!=2976:
            raise ValueError("Demand observed/missing accounting mismatch")
        if m.get("weights_sha256")!=EXPECTED_WEIGHTS:
            raise ValueError("Changed experimental geographic weights")
        if (m.get("training_or_validation_permitted") is not False
            or m.get("historical_geometry_approved") is not False
            or m.get("no_imputation") is not True):
            raise ValueError("Unexpected model admission or interpolation")
        if len(m.get("missing_demand_BA_hours",[]))!=missing:
            raise ValueError("Missing source hour list inconsistent")
        found[year]=m
    if set(found)!=YEARS:raise ValueError("Require all six years")
    rows=[{"year":year,"total_source_BA_hours":2976,
           "real_ERA5_BA_hours":2976,
           "real_ERA5_EIA_demand_pairs":found[year]["paired_source_rows"],
           "missing_EIA930_demand_BA_hours":found[year]["source_missing_demand_hours"],
           "original_EIA930_anomaly_candidates":found[year]["eia_candidate_anomaly_flags_in_window"],
           "data_model_eligible":False} for year in sorted(YEARS)]
    summary={"years":sorted(YEARS),"months_per_year_verified":1,
        "one_calendar_month":"July","all_source_slots":6*2976,
        "real_ERA5_BA_hours":sum(r["real_ERA5_BA_hours"] for r in rows),
        "observed_EIA_weather_pairs":sum(r["real_ERA5_EIA_demand_pairs"] for r in rows),
        "missing_source_demand_hours":sum(r["missing_EIA930_demand_BA_hours"] for r in rows),
        "original_demand_anomaly_candidate_count":sum(r["original_EIA930_anomaly_candidates"] for r in rows),
        "all_years_complete":False,"geography_approved":False,
        "training_permitted":False,"anthropogenic_attribution_performed":False}
    return rows,summary
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifests",required=True,nargs="+")
    p.add_argument("--out",default="outputs/e1_six_julys")
    a=p.parse_args()
    rows,report=consolidate([json.loads(Path(x).read_text()) for x in a.manifests])
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    with (out/"july_source_quality_2020_2025.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/"july_source_quality_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print("SIX_JULYS_SOURCE_QA",json.dumps(report))
if __name__=="__main__":main()
