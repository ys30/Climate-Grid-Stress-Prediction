"""E0 missingness episode and outlier quarantine report; no filling or winsorization.

Consumes reconciled raw EIA-930 BA-hour rows from the official three-file year boundary.
"""
import argparse,csv,json
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path
from src.c2_boundary_and_outlier_gate import load_records,flag_series
from src.c2_yearly_coverage import BAS,expected_hours

def episodes(data,year):
    first=datetime(year,1,1,tzinfo=__import__("datetime").timezone.utc)
    groups=[]
    for ba in BAS:
        s=data[ba];open_start=None;last=None;reasons=[]
        for i in range(expected_hours(year)):
            t=first+timedelta(hours=i)
            reason="absent" if t not in s else "blank" if s[t] is None else None
            if reason:
                if open_start is None:open_start=t
                reasons.append(reason)
                last=t
            elif open_start is not None:
                groups.append({"year":year,"ba":ba,"start_utc":open_start.isoformat(),
                   "end_utc_inclusive":last.isoformat(),"duration_hours":len(reasons),
                   "absent_hours":reasons.count("absent"),"blank_hours":reasons.count("blank")})
                open_start=None;reasons=[]
        if open_start is not None:
            groups.append({"year":year,"ba":ba,"start_utc":open_start.isoformat(),
               "end_utc_inclusive":last.isoformat(),"duration_hours":len(reasons),
               "absent_hours":reasons.count("absent"),"blank_hours":reasons.count("blank")})
    return groups

def training_status(data,year):
    _,_,flags=flag_series(data,year)
    by_key={(f["ba"],f["timestamp_utc_start"]):f for f in flags}
    statuses=[]
    for ba in BAS:
        for t,v in sorted(data[ba].items()):
            if v is None:continue
            key=(ba,t.isoformat())
            flag=by_key.get(key)
            statuses.append({"year":year,"ba":ba,"timestamp_utc_start":t.isoformat(),
              "raw_demand_mw":v,"quarantine":bool(flag),
              "reason":flag["candidate_reason"] if flag else "",
              "model_eligible":not bool(flag)})
    return statuses,flags

def dump_csv(path,records,fields):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader();w.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--year",required=True,type=int)
    p.add_argument("--source",required=True,nargs="+")
    p.add_argument("--out",default="outputs/e0_quarantine")
    a=p.parse_args()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    data,conflicts,snapshots=load_records(a.year,a.source)
    if conflicts:raise SystemExit("Conflicting source year-boundary records")
    eps=episodes(data,a.year)
    rows,flags=training_status(data,a.year)
    dump_csv(out/"missing_episodes.csv",eps,["year","ba","start_utc","end_utc_inclusive",
      "duration_hours","absent_hours","blank_hours"])
    dump_csv(out/"observed_values_with_quarantine.csv",rows,["year","ba",
      "timestamp_utc_start","raw_demand_mw","quarantine","reason","model_eligible"])
    summary={"year":a.year,"source_files":snapshots,"missing_episodes":len(eps),
       "missing_episode_max_hours":max([e["duration_hours"] for e in eps],default=0),
       "quarantined_candidate_points":len(flags),"model_eligible_observed_points":
       sum(x["model_eligible"] for x in rows),"raw_observed_points":len(rows),
       "training_executed":False,"imputation_performed":False}
    (out/"episode_quarantine_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("QUALITY_SUMMARY",json.dumps(summary))
    print("MISSING_EPISODES",json.dumps(eps[:100]))
    print("QUARANTINED_HEAD",json.dumps(flags[:12]))
if __name__=="__main__":main()
