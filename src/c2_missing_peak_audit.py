"""Inspect exact EIA-930 missing BA-hours and candidate spike events.

Read original official half-year BALANCE CSV files. Preserve original values.
Do not automatically correct, clip, or impute records.
"""
import argparse,csv,json,collections
from datetime import datetime,timedelta,timezone
from pathlib import Path
from src.c2_yearly_coverage import BAS,FMT,expected_hours

def inspect(paths,year,top_n=12):
    first=datetime(year,1,1,tzinfo=timezone.utc)
    final=datetime(year+1,1,1,tzinfo=timezone.utc)
    obs={ba:{} for ba in BAS}
    dup=collections.Counter()
    for path in paths:
        with open(path,newline="",encoding="utf-8-sig") as f:
            reader=csv.DictReader(f)
            required={"Balancing Authority","UTC Time at End of Hour","Demand (MW)"}
            if not required.issubset(reader.fieldnames or []):
                raise ValueError("Official EIA-930 fields absent")
            for row in reader:
                ba=(row.get("Balancing Authority") or "").strip()
                if ba not in BAS:continue
                end=datetime.strptime(row["UTC Time at End of Hour"].strip(),FMT).replace(tzinfo=timezone.utc)
                t=end-timedelta(hours=1)
                if not first<=t<final:continue
                if t in obs[ba]:
                    dup[ba]+=1
                    continue
                raw=(row.get("Demand (MW)") or "").strip()
                try:
                    val=float(raw)
                    if not 0<=val<float("inf"):val=None
                except ValueError:val=None
                obs[ba][t]=val
    qa=[];anomalies=[];missing=[]
    for ba in BAS:
        records=obs[ba]
        clock=[first+timedelta(hours=i) for i in range(expected_hours(year))]
        absent=[t for t in clock if t not in records]
        blanks=[t for t in clock if t in records and records[t] is None]
        for kind,items in [("missing_source_timestamp",absent),("blank_or_invalid_demand",blanks)]:
            missing.extend({"ba":ba,"year":year,"timestamp_utc_start":t.isoformat(),"reason":kind} for t in items)
        vals=[(t,v) for t,v in records.items() if v is not None]
        vals.sort(key=lambda tv:tv[1],reverse=True)
        for t,v in vals[:top_n]:
            prev=records.get(t-timedelta(hours=1))
            nex=records.get(t+timedelta(hours=1))
            neighbors=[x for x in (prev,nex) if x is not None and x>0]
            ratio=v/(sum(neighbors)/len(neighbors)) if neighbors else None
            anomalies.append({"year":year,"ba":ba,"timestamp_utc_start":t.isoformat(),
                              "demand_mw_raw":v,"prev_demand_mw":prev,
                              "next_demand_mw":nex,"ratio_to_neighbor_mean":round(ratio,5) if ratio else None,
                              "candidate_spike":ratio is not None and ratio>2})
        qa.append({"year":year,"ba":ba,"missing_keys":len(absent),"blank_keys":len(blanks),
                   "duplicates":dup[ba],"max_raw_demand_mw":vals[0][1] if vals else None,
                   "maximum_timestamp_utc_start":vals[0][0].isoformat() if vals else None,
                   "max_observation_unverified":True})
    return qa,anomalies,missing

def write_csv(path,rows,fields):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--csv",nargs="+",required=True)
    p.add_argument("--out",default="outputs/e0_diagnostics")
    args=p.parse_args()
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    qa,a,m=inspect(args.csv,args.year)
    write_csv(out/"annual_quality.csv",qa,list(qa[0]))
    write_csv(out/"raw_peak_candidates.csv",a,list(a[0]))
    write_csv(out/"exact_missing_hour_keys.csv",m,["ba","year","timestamp_utc_start","reason"])
    report={"year":args.year,"quality":qa,"exact_missing_rows":len(m),
            "max_peaks_unverified":True,"automated_filling":False,
            "not_an_outage_or_grid_stress_validation":True}
    (out/"quality_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
