"""Non-model EIA-930 × real ERA5 24-h timestamp alignment audit.

Produces a factual paired-source DIAGNOSTIC only; ERA5 area exposures use
historically unapproved candidate BA polygons and MUST NOT be trained.
"""
import argparse,csv,hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_boundary_and_outlier_gate import load_records,flag_series
BAS=("AZPS","BPAT","CISO","SRP")
def pair_audit(demand_by_ba,flags,weather_rows,start="2023-07-01T00:00:00+00:00"):
    begin=datetime.fromisoformat(start)
    if begin.utcoffset() is None or begin.utcoffset().total_seconds()!=0:
        raise ValueError("UTC aware interval-start is required")
    quarantine={(x["ba"],x["timestamp_utc_start"]) for x in flags}
    w={}
    for row in weather_rows:
        if row["ba"] not in BAS:raise ValueError("Unknown BA weather")
        t=datetime.fromisoformat(row["timestamp_utc_start"])
        key=(row["ba"],t)
        if key in w:raise ValueError("Duplicate hour weather")
        if row.get("experimental_geography_only") not in ("True",True):
            raise ValueError("Must retain experimental source label")
        if row.get("historical_weather_exposure_approved") not in ("False",False):
            raise ValueError("Prohibit asserting experimental weather is approved")
        val=float(row["weighted_temperature_celsius"])
        if not math.isfinite(val):raise ValueError("Nonfinite weather")
        w[key]=val
    out=[]
    for ba in BAS:
        d=demand_by_ba[ba]
        for hour in range(24):
            t=begin+timedelta(hours=hour)
            val=d.get(t)
            temp=w.get((ba,t))
            if val is None or temp is None:raise ValueError(f"Incomplete exact-hour pair {ba} {t}")
            key=(ba,t.isoformat())
            out.append({"ba":ba,"timestamp_utc_start":t.isoformat(),
              "raw_observed_demand_mw":val,"real_era5_candidate_area_temp_c":temp,
              "EIA_930_source_quarantine_flag":key in quarantine,
              "candidate_geography_approved":False,
              "model_training_eligible":False})
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--eia-files",nargs="+",required=True)
    p.add_argument("--weather",required=True)
    p.add_argument("--out",default="outputs/e1_pairing")
    args=p.parse_args()
    data,conflicts,sources=load_records(2023,args.eia_files)
    if conflicts:raise ValueError("Conflicting EIA sources")
    _,_,flags=flag_series(data,2023)
    with open(args.weather,newline="") as f:weather=list(csv.DictReader(f))
    rows=pair_audit(data,flags,weather)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    with (out/"24h_REAL_SOURCE_UTC_PAIRED_NOT_MODEL.csv").open("w",newline="") as f:
        fields=list(rows[0])
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)
    report={"year":2023,"utc_day":"2023-07-01",
      "rows_paired":len(rows),"exact_hourly_EIA930_and_ERA5_matched":len(rows)==96,
      "source_eia930_shas":[{"file":x["file"],"sha256":x["sha256"]} for x in sources],
      "real_weather_source":"ARCO-ERA5","candidate_area_weather_geography_approved":False,
      "quarantine_flags_in_day":sum(x["EIA_930_source_quarantine_flag"] for x in rows),
      "raw_demand_imputed":False,"weather_imputed":False,
      "no_model_or_causal_inference":True}
    (out/"real_24h_pairing_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_24H_SOURCE_PAIRING",json.dumps(report))
    for ba in BAS:
        vals=[x["raw_observed_demand_mw"] for x in rows if x["ba"]==ba]
        print("DAY_DEMAND_RANGE",json.dumps({"ba":ba,"min_raw_mw":min(vals),"max_raw_mw":max(vals)}))
if __name__=="__main__":main()
