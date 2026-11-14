"""Extract actual UTC candidate anomaly events from archived C2 E1 source rows.

Inspect source QA flags, do not relabel those flags as confirmed errors.
Never treat experimental BA meteorology as a model-ready training predictor.
"""
import argparse,csv,json,math
from pathlib import Path
from datetime import datetime,timedelta,timezone

FILENAME="REAL_EIA_ERA5_48h_or_more_PAIRED_NOT_MODEL.csv"

def check_rows(rows,manifest):
    expected=manifest["source_BA_hour_slots"]
    expected_missing=manifest["source_missing_demand_hours"]
    expected_flags=manifest["eia_candidate_anomaly_flags_in_window"]
    if len(rows)!=expected:
        raise ValueError("Missing archived per-hour source pairing rows")
    start=datetime.fromisoformat(manifest["utc_start"])
    if start.utcoffset() is None or start.utcoffset().total_seconds()!=0:
        raise ValueError("Archived source month does not start at UTC")
    end=start+timedelta(hours=manifest["days"]*24)
    seen=set();events=[];missing=[];observed_count=0
    for r in rows:
        key=(r.get("ba"),r.get("timestamp_utc_start"))
        if key in seen:raise ValueError("Duplicate original BA-hour key")
        seen.add(key)
        if key[0] not in ("AZPS","BPAT","CISO","SRP"):raise ValueError("Unrecognized BA")
        t=datetime.fromisoformat(key[1].replace("Z","+00:00"))
        if t.utcoffset() is None or t.utcoffset().total_seconds()!=0:
            raise ValueError("UTC timestamp missing or shifted")
        if not (start<=t<end) or t.minute or t.second or t.microsecond:
            raise ValueError("Source record lies outside expected UTC calendar-month hours")
        if r.get("train_or_validate_eligible")!="False" or r.get("historical_BA_area_approved")!="False":
            raise ValueError("Unapproved geographic data falsely admitted")
        if r.get("source_missing_demand") not in ("True","False") or r.get("demand_spike_candidate") not in ("True","False"):
            raise ValueError("Unparseable source QA booleans")
        is_missing=r["source_missing_demand"]=="True"
        demand=r.get("demand_mw_raw","")
        temperature=r.get("temperature_c_experimental_area","")
        if not temperature or not math.isfinite(float(temperature)):
            raise ValueError("Missing or nonfinite source weather")
        if is_missing:
            if demand.strip():raise ValueError("Source gap was covertly filled")
            missing.append({"ba":key[0],"timestamp_utc_start":key[1]})
        else:
            if not demand or not math.isfinite(float(demand)):
                raise ValueError("Unparseable observed EIA original demand")
            observed_count+=1
        if r["demand_spike_candidate"]=="True":
            events.append({"ba":key[0],"timestamp_utc_start":key[1],
                "demand_mw_raw":demand or None,
                "real_ERA5_candidate_area_c":temperature,
                "source_missing_demand":is_missing,
                "flag_status":"candidate_needs_review_not_confirmed_error",
                "historical_geography_approved":False,
                "model_eligible":False})
    # Ensure each BA contributes every requested UTC hour exactly once.
    # A total of 4*N rows can otherwise hide one duplicated BA and one
    # completely missing BA from an undetected source export.
    expected_keys={(ba,(start+timedelta(hours=h)).isoformat())
                   for ba in ("AZPS","BPAT","CISO","SRP")
                   for h in range(manifest["days"]*24)}
    if seen!=expected_keys:
        raise ValueError("A BA-hour is absent or an unexpected BA-hour was included")
    if observed_count!=manifest["paired_source_rows"]:
        raise ValueError("Observed demand count violates source manifest")
    if len(missing)!=expected_missing or len(events)!=expected_flags:
        raise ValueError("Raw source gaps or anomaly candidate event count mismatch")
    return events,missing

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--inputs",required=True)
    p.add_argument("--out",default="outputs/e1_event_qa")
    a=p.parse_args()
    root=Path(a.inputs)
    manifests=sorted(root.rglob("seasonal_source_audit.json"))
    all_flags=[];all_missing=[]
    if len(manifests)!=72:raise ValueError("Require exactly 72 real source month manifests")
    for mf in manifests:
        data_path=mf.parent/FILENAME
        if not data_path.exists():raise ValueError("Missing raw BA-hour source CSV: "+str(data_path))
        with data_path.open(newline="") as f:rows=list(csv.DictReader(f))
        m=json.loads(mf.read_text())
        events,missing=check_rows(rows,m)
        prefix={"source_month":m["utc_start"][:7]}
        all_flags.extend([{**prefix,**x} for x in events])
        all_missing.extend([{**prefix,**x} for x in missing])
    output=Path(a.out);output.mkdir(parents=True,exist_ok=True)
    def write(name,rows,cols):
        with (output/name).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows(rows)
    write("source_EIA930_anomaly_candidates_NOT_CONFIRMED.csv",
        all_flags,["source_month","ba","timestamp_utc_start","demand_mw_raw",
                   "real_ERA5_candidate_area_c","source_missing_demand","flag_status",
                   "historical_geography_approved","model_eligible"])
    write("source_EIA930_missing_demand_hours_NO_IMPUTATION.csv",
        all_missing,["source_month","ba","timestamp_utc_start"])
    summary={"source_months":len(manifests),"anomaly_candidate_events":len(all_flags),
             "missing_original_EIA930_hours":len(all_missing),
             "candidate_flags_are_confirmed_errors":False,
             "weather_geography_historically_approved":False,"model_training_permitted":False}
    (output/"event_qa_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("REAL_EIA930_CANDIDATE_EVENT_AUDIT",json.dumps(summary))
if __name__=="__main__":main()
