"""C2 E0: source-boundary reconciliation and conservative raw-demand anomaly flags.

Does not impute, modify original measurements, or identify physical outages.
"""
import argparse,csv,hashlib,json,math
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_yearly_coverage import BAS,FMT,expected_hours

FIELDS=("Balancing Authority","UTC Time at End of Hour","Demand (MW)")

def load_records(year,files):
    first=datetime(year,1,1,tzinfo=timezone.utc)
    end=datetime(year+1,1,1,tzinfo=timezone.utc)
    by_ba={ba:{} for ba in BAS}
    conflicts=[]
    snapshots=[]
    for fn in files:
        file=Path(fn)
        digest=hashlib.sha256(file.read_bytes()).hexdigest()
        snapshots.append({"file":file.name,"sha256":digest,"bytes":file.stat().st_size})
        with file.open(newline="",encoding="utf-8-sig") as stream:
            rd=csv.DictReader(stream)
            if not set(FIELDS).issubset(rd.fieldnames or []):
                raise ValueError("Missing official stable EIA demand columns")
            for row in rd:
                ba=(row.get(FIELDS[0]) or "").strip()
                if ba not in BAS:continue
                stamp=datetime.strptime(row[FIELDS[1]].strip(),FMT).replace(tzinfo=timezone.utc)
                t=stamp-timedelta(hours=1)
                if not first<=t<end:continue
                raw=(row.get(FIELDS[2]) or "").strip()
                try:
                    value=float(raw)
                    if not math.isfinite(value) or value<0:value=None
                except ValueError:value=None
                old=by_ba[ba].get(t)
                if t in by_ba[ba]:
                    if old!=value:
                        conflicts.append({"ba":ba,"t":t.isoformat(),"prior":old,"next":value,"source_file":file.name})
                    # No silent resolution for divergent raw values.
                    continue
                by_ba[ba][t]=value
    return by_ba,conflicts,snapshots

def flag_series(data,year):
    result=[];missing=[];coverage=[]
    start=datetime(year,1,1,tzinfo=timezone.utc)
    for ba in BAS:
        series=data[ba]
        times=[start+timedelta(hours=i) for i in range(expected_hours(year))]
        absent=[t for t in times if t not in series]
        blanks=[t for t in times if t in series and series[t] is None]
        for t in absent:missing.append({"year":year,"ba":ba,"timestamp_utc_start":t.isoformat(),"reason":"absent"})
        for t in blanks:missing.append({"year":year,"ba":ba,"timestamp_utc_start":t.isoformat(),"reason":"blank"})
        valid=sum(v is not None for v in series.values())
        coverage.append({"year":year,"ba":ba,"expected":len(times),"valid":valid,
                         "absent":len(absent),"blank":len(blanks),
                         "coverage":round(valid/len(times),6)})
        for t,value in sorted(series.items()):
            if value is None:continue
            prev=series.get(t-timedelta(hours=1))
            nxt=series.get(t+timedelta(hours=1))
            if prev is None or nxt is None or prev<=0 or nxt<=0:continue
            ratio=value/((prev+nxt)/2)
            # Candidate flag (not automated correction): either isolated >2x or <0.5x.
            if ratio>2 or ratio<0.5:
                result.append({"year":year,"ba":ba,"timestamp_utc_start":t.isoformat(),
                               "raw_mw":value,"prev_mw":prev,"next_mw":nxt,
                               "neighbor_ratio":round(ratio,5),
                               "candidate_reason":"isolated_high" if ratio>2 else "isolated_low",
                               "training_status":"hold_until_source_review"})
    return coverage,missing,result

def write(path,rows,columns):
    with Path(path).open("w",newline="") as file:
        wr=csv.DictWriter(file,fieldnames=columns);wr.writeheader();wr.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--source",nargs="+",required=True)
    p.add_argument("--out",default="outputs/e0_boundary")
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    data,conflicts,sources=load_records(a.year,a.source)
    coverage,missing,flags=flag_series(data,a.year)
    write(out/"reconciled_coverage.csv",coverage,
          ["year","ba","expected","valid","absent","blank","coverage"])
    write(out/"exact_missing_after_boundary.csv",missing,
          ["year","ba","timestamp_utc_start","reason"])
    write(out/"candidate_outliers.csv",flags,
          ["year","ba","timestamp_utc_start","raw_mw","prev_mw","next_mw",
           "neighbor_ratio","candidate_reason","training_status"])
    write(out/"cross_source_conflicts.csv",conflicts,
          ["ba","t","prior","next","source_file"])
    manifest={"year":a.year,"original_files":sources,"cross_source_conflicts":len(conflicts),
              "coverage":coverage,"candidate_outliers":len(flags),
              "missing_or_blank":len(missing),"imputed":False,
              "model_training_accepted":False}
    (out/"boundary_audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))
    print("TOP_RAW_ANOMALIES",json.dumps(sorted(flags,key=lambda x:x["neighbor_ratio"],reverse=True)[:12]))
    print("FIRST_MISSING_KEYS",json.dumps(missing[:16]))
    if conflicts:
        raise SystemExit("Conflicting official source values at identical BA-hour keys")
if __name__=="__main__":main()
