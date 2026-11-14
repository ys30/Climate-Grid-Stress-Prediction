"""Strictly consolidate 72 independent actual-source monthly BA-hour audits.

Data provenance and source temporal completeness ONLY. Source polygon masks
remain unapproved; this audit cannot authorize model training or attribution.
"""
import argparse,calendar,csv,json
from pathlib import Path

YEARS=tuple(range(2020,2026))
BAS=("AZPS","BPAT","CISO","SRP")
SOURCE_WEIGHTS_SHA="e4e0990cd47e8517d01731231eb4ed3da06649840c99c5e87baadeee7c5b8cb3"

def reconcile(manifests):
    by_month={}
    for m in manifests:
        stamp=m.get("utc_start","")
        try:
            year=int(stamp[:4]);month=int(stamp[5:7])
        except Exception as e:raise ValueError("Missing UTC month stamp") from e
        if year not in YEARS or month not in range(1,13):
            raise ValueError("Outside six-year monthly scope")
        key=(year,month)
        if key in by_month:raise ValueError("Duplicate actual source month")
        if stamp not in (f"{year}-{month:02d}-01T00:00:00+00:00",
                         f"{year}-{month:02d}-01T00:00:00Z"):
            raise ValueError("Source month must begin at UTC midnight day 1")
        expected_days=calendar.monthrange(year,month)[1]
        expected=expected_days*24*len(BAS)
        if m.get("days")!=expected_days or m.get("hours_per_BA")!=24*expected_days:
            raise ValueError("Actual month days mismatch, including leap years")
        if m.get("source_BA_hour_slots")!=expected or m.get("weather_source_rows")!=expected:
            raise ValueError("Actual ERA5 four-BA cell-hour coverage incomplete")
        if m.get("all_weather_hours_present") is not True:
            raise ValueError("Some full-region ERA5 hours missing")
        if m.get("BAs")!=list(BAS) or m.get("weights_sha256")!=SOURCE_WEIGHTS_SHA:
            raise ValueError("BA scope or experimental geography snapshot changed")
        missing=m.get("source_missing_demand_hours")
        paired=m.get("paired_source_rows")
        if type(missing) is not int or type(paired) is not int or missing<0 or paired<0 or missing+paired!=expected:
            raise ValueError("Demand / source gap counts inconsistent")
        episodes=m.get("missing_demand_BA_hours",[])
        if not isinstance(episodes,list) or len(episodes)!=missing:
            raise ValueError("Missing exact UTC source gap list")
        if (m.get("no_imputation") is not True
            or m.get("historical_geometry_approved") is not False
            or m.get("training_or_validation_permitted") is not False):
            raise ValueError("Invalid training or geometry permission")
        anomaly=m.get("eia_candidate_anomaly_flags_in_window")
        if type(anomaly) is not int or anomaly<0 or anomaly>expected:
            raise ValueError("Unusable EIA anomaly candidate counter")
        by_month[key]=m
    expected_keys={(year,month) for year in YEARS for month in range(1,13)}
    if set(by_month)!=expected_keys:
        missing=sorted(expected_keys-set(by_month))
        extra=sorted(set(by_month)-expected_keys)
        raise ValueError(f"Expected 72 true-source audited months; missing={missing} extra={extra}")
    rows=[]; missing_episodes=[]
    for year,month in sorted(by_month):
        m=by_month[year,month]
        expected=m["source_BA_hour_slots"]
        rows.append({"year":year,"month":month,"days":m["days"],
            "expected_BA_hour_slots":expected,"actual_ERA5_BA_hours":m["weather_source_rows"],
            "real_demand_weather_pairs":m["paired_source_rows"],
            "original_demand_missing_hours":m["source_missing_demand_hours"],
            "demand_anomaly_candidates":m["eia_candidate_anomaly_flags_in_window"],
            "experimental_geography_only":True,"training_permitted":False})
        for gap in m["missing_demand_BA_hours"]:
            missing_episodes.append({"year":year,"month":month,
                "ba":gap["ba"],"utc":gap["utc"]})
    totals={"actual_months":len(rows),"years":list(YEARS),
       "all_twelve_months_observed_each_year":True,
       "total_real_ERA5_BA_hours":sum(r["actual_ERA5_BA_hours"] for r in rows),
       "total_observed_EIA_ERA5_pairs":sum(r["real_demand_weather_pairs"] for r in rows),
       "total_missing_original_demand_BA_hours":len(missing_episodes),
       "total_original_demand_anomaly_candidates":sum(r["demand_anomaly_candidates"] for r in rows),
       "BA_geography_historical_approval":False,
       "training_permitted":False,
       "climate_change_attribution_performed":False,
       "warning":"Year-round real candidate-area ERA5 does not validate historical BA polygon masks or qualify a model fit."}
    totals["yearly_source_quality"]=[
        {"year":year,
         "expected_weather_BA_hours":sum(r["expected_BA_hour_slots"] for r in rows if r["year"]==year),
         "observed_weather_BA_hours":sum(r["actual_ERA5_BA_hours"] for r in rows if r["year"]==year),
         "observed_load_weather_pairs":sum(r["real_demand_weather_pairs"] for r in rows if r["year"]==year),
         "original_load_missing_hours":sum(r["original_demand_missing_hours"] for r in rows if r["year"]==year),
         "source_anomaly_candidate_flags":sum(r["demand_anomaly_candidates"] for r in rows if r["year"]==year),
         "training_permitted":False} for year in YEARS]
    totals["original_load_missing_counts_by_BA"]={
        ba:sum(e["ba"]==ba for e in missing_episodes)
        for ba in BAS}
    totals["source_anomaly_flags_are_confirmed_errors"]=False
    if totals["total_real_ERA5_BA_hours"]!=totals["total_observed_EIA_ERA5_pairs"]+len(missing_episodes):
        raise ValueError("Six-year original demand missingness accounting failed")
    return rows,missing_episodes,totals

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--manifests",required=True,nargs="+")
    p.add_argument("--out",default="outputs/e1_full_year_candidate")
    a=p.parse_args()
    inputs=[json.loads(Path(f).read_text()) for f in a.manifests]
    rows,missing,report=reconcile(inputs)
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    def csv_out(path,data,fields):
        with (output/path).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    csv_out("2020_2025_monthly_actual_source_QA.csv",rows,list(rows[0]))
    csv_out("2020_2025_all_original_EIA930_missing_hours.csv",missing,
            ["year","month","ba","utc"])
    (output/"2020_2025_72_month_source_QA_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_72_MONTH_SOURCE_QA",json.dumps(report))
if __name__=="__main__":main()
