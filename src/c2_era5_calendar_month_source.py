"""Fetch precisely one *actual calendar month* ERA5/EIA930 source window.

Source-hour audit only. Historical BA geometries are explicitly UNAPPROVED,
even when weather coverage is complete; modeling and attribution are prohibited.
"""
import argparse,calendar,json
from pathlib import Path
from src.c2_era5_seasonal_source_audit import run

def month_days(year,month):
    if year not in range(2020,2026) or month not in range(1,13):
        raise ValueError("Only C2 2020-2025 calendar months allowed")
    return calendar.monthrange(year,month)[1]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True)
    p.add_argument("--weights",required=True)
    p.add_argument("--eia-files",nargs="+",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    days=month_days(a.year,a.month)
    start=f"{a.year}-{a.month:02d}-01T00:00:00Z"
    run(start,days,a.weights,a.eia_files,a.out,allow_source_gaps=True)
    audit_path=Path(a.out)/"seasonal_source_audit.json"
    audit=json.loads(audit_path.read_text())
    expected=days*24*4
    if audit["source_BA_hour_slots"]!=expected or audit["weather_source_rows"]!=expected:
        raise ValueError("Calendar-month ERA5 coverage failed")
    if audit["paired_source_rows"]+audit["source_missing_demand_hours"]!=expected:
        raise ValueError("Calendar-month demand gaps do not reconcile")
    if not audit["all_weather_hours_present"] or audit["historical_geometry_approved"] is not False:
        raise ValueError("Actual ERA5 coverage or geography admission failed")
    if audit["training_or_validation_permitted"] is not False or audit["no_imputation"] is not True:
        raise ValueError("Forbidden modeling or imputation flag")
    audit["calendar_month"]=a.month
    audit["calendar_year"]=a.year
    audit["calendar_month_days"]=days
    audit["month_ERA5_weather_complete"]=True
    audit["month_EIA_load_complete"]=audit["source_missing_demand_hours"]==0
    audit["empirical_model_ready"]=False
    audit_path.write_text(json.dumps(audit,indent=2)+"\n")
    print("REAL_CALENDAR_MONTH_SOURCE_QA",json.dumps({
        "year":a.year,"month":a.month,"days":days,
        "BA_weather_hours":expected,"observed_demand_weather_pairs":audit["paired_source_rows"],
        "missing_EIA_hours":audit["source_missing_demand_hours"],
        "anomaly_candidates":audit["eia_candidate_anomaly_flags_in_window"],
        "model_ready":False}),flush=True)
if __name__=="__main__":main()
