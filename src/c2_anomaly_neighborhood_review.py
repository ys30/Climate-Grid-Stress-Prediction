"""Review EIA930 source anomaly candidates against nearby *original* demand hours.

This is a reproducible triage of candidate anomalies, NOT confirmation of
measurement error, NOT demand imputation, and NOT forecast model training.
"""
import argparse,csv,gzip,json,math,statistics
from collections import defaultdict,Counter
from datetime import datetime,timedelta
from pathlib import Path

def utc(t):
    stamp=datetime.fromisoformat(t.replace("Z","+00:00"))
    if stamp.utcoffset() is None or stamp.utcoffset().total_seconds()!=0:
        raise ValueError("UTC only")
    return stamp

def review_hourly(rows,window=3):
    if window<1 or window>24:raise ValueError("Bound neighbor window")
    by_ba=defaultdict(dict); flagged=[]
    for row in rows:
        ba=row["ba"];t=utc(row["timestamp_utc_start"])
        key=(ba,t)
        if t in by_ba[ba]:raise ValueError("Duplicate source BA-hour")
        if row["model_training_eligible"]!="False" or row["geometry_historically_approved"]!="False":
            raise ValueError("Source archive falsely approved for models")
        raw=row["EIA930_original_demand_mw"]
        val=float(raw) if raw!="" else None
        if val is not None and not math.isfinite(val):raise ValueError("Nonfinite source demand")
        source_flag=row["EIA930_anomaly_candidate_not_confirmed"]
        if source_flag not in ("True","False"):raise ValueError("Invalid raw anomaly flag")
        by_ba[ba][t]=(val,source_flag)
        if source_flag=="True":flagged.append((ba,t,val))
    result=[]
    for ba,t,val in sorted(flagged):
        neighbors=[]
        for delta in range(-window,window+1):
            if delta==0:continue
            n=by_ba[ba].get(t+timedelta(hours=delta))
            if n and n[0] is not None and n[1]=="False" and n[0]>0:
                neighbors.append(n[0])
        median=statistics.median(neighbors) if neighbors else None
        ratio=val/median if median and val is not None else None
        if val is None:category="flagged_but_original_demand_missing"
        elif val<=0:category="nonpositive_original_demand"
        elif len(neighbors)<2:category="insufficient_clean_local_neighbors"
        elif ratio>=3:category="large_positive_relative_to_neighbors"
        elif ratio<=1/3:category="large_negative_relative_to_neighbors"
        elif ratio>=1.5 or ratio<=2/3:category="moderate_local_discontinuity"
        else:category="flagged_without_large_local_discontinuity"
        result.append({"ba":ba,"timestamp_utc_start":t.isoformat(),
          "original_demand_mw":val,"available_unflagged_neighbor_hours":len(neighbors),
          "median_nearby_unflagged_demand_mw":median,
          "source_to_neighborhood_ratio":round(ratio,6) if ratio is not None else None,
          "triage_class":category,"flag_is_confirmed_data_error":False,
          "automatic_imputation":False,"model_training_eligible":False})
    return result

def run(inp,out):
    with gzip.open(inp,"rt",newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=210432:
        raise ValueError("Expected exact frozen six-year source archive of 210432 BA hours")
    reviews=review_hourly(rows)
    count=Counter(x["triage_class"] for x in reviews)
    if len(reviews)!=70:
        raise ValueError("Expected 70 original-source anomaly candidates; source archive changed")
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    fields=list(reviews[0])
    with (output/"EIA930_70_SOURCE_ANOMALY_NEIGHBORHOOD_REVIEW.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(reviews)
    meta={"source_hour_rows":len(rows),"candidate_hours":len(reviews),
      "candidate_classes":dict(sorted(count.items())),
      "all_candidates_confirmed_errors":False,
      "automated_data_edits":0,"source_imputation_performed":False,
      "geographic_exposure_approved":False,"forecast_training_performed":False,
      "triage_method":"Original demand compared with median of up to three preceding and three subsequent unflagged, nonmissing hours in same BA"}
    (output/"EIA930_70_SOURCE_ANOMALY_REVIEW_MANIFEST.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("REAL_70_ANOMALY_SOURCE_REVIEW",json.dumps(meta))
    for row in reviews:
        print("REVIEW_CANDIDATE",json.dumps({k:row[k] for k in ("ba","timestamp_utc_start","original_demand_mw","triage_class","source_to_neighborhood_ratio")}))
    return meta

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--input-gzip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.input_gzip,a.out)
if __name__=="__main__":main()
