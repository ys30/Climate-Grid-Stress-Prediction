"""C-2: fixed-day run-length classification under A/B/C ERA5 proxy temperature.

Source only: 384 BA-hours from pinned E1 four-day artifact. This does not
validate a real BA electric load exposure or imply physical heat-grid stress.
"""
import argparse,csv,hashlib,json,math
from collections import defaultdict
from datetime import datetime,timedelta
from pathlib import Path

PINNED_SOURCE_SHA256="9ebeb843f3364d6e6726844253934a34fdc6acac0c4627c17ec207e8105cb179"
BAS=("AZPS","BPAT","CISO","SRP")
DATES=("2023-01-15","2023-07-01","2025-01-15","2025-07-01")
COLS=("HIFLD_A_celsius","TIGER_B_celsius","population_C_celsius")
THRESHOLDS=(25,30,35)

def longest_run(flags):
    current=longest=0
    for flag in flags:
        current=current+1 if flag else 0
        longest=max(longest,current)
    return longest

def run(source,out):
    raw=Path(source).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=PINNED_SOURCE_SHA256:
        raise ValueError("Pinned original source SHA256 mismatch")
    records=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    expected={(ba,datetime.fromisoformat(day+"T00:00:00+00:00")+timedelta(hours=h))
              for ba in BAS for day in DATES for h in range(24)}
    data={}
    for r in records:
        ts=datetime.fromisoformat(r["UTC_timestamp"].replace("Z","+00:00"))
        key=(r["BA"],ts)
        if ts.tzinfo is None or ts.utcoffset()!=timedelta(0) or key not in expected or key in data:
            raise ValueError("Unexpected, duplicate or non-UTC BA-hour")
        if any(r[col]!="False" for col in
               ("historical_BA_geography_approved","population_is_customer_weights","training_permitted")):
            raise ValueError("Unapproved weather geography falsely admitted")
        temp=tuple(float(r[col]) for col in COLS)
        if not all(math.isfinite(t) for t in temp):
            raise ValueError("Nonfinite actual ERA5 source temperature")
        for col,diff in (("B_minus_A_celsius",temp[1]-temp[0]),
                         ("C_minus_B_celsius",temp[2]-temp[1]),
                         ("C_minus_A_celsius",temp[2]-temp[0])):
            val=float(r[col])
            if not math.isfinite(val) or abs(val-diff)>2.1e-6:
                raise ValueError("Original ERA5 source arithmetic mismatch")
        data[key]=temp
    if set(data)!=expected:raise ValueError("Four full UTC days x four BAs required")
    days=[]
    for ba in BAS:
        for day in DATES:
            start=datetime.fromisoformat(day+"T00:00:00+00:00")
            temperatures=[data[ba,start+timedelta(hours=i)] for i in range(24)]
            for threshold in THRESHOLDS:
                flags=[tuple(t>=threshold for t in triple) for triple in temperatures]
                counts=[sum(f[i] for f in flags) for i in range(3)]
                runs=[longest_run([f[i] for f in flags]) for i in range(3)]
                anyhot=sum(any(f) for f in flags)
                allhot=sum(all(f) for f in flags)
                days.append({"BA":ba,"UTC_day":day,"threshold_c":threshold,
                  "A_hot_hours":counts[0],"B_hot_hours":counts[1],"C_hot_hours":counts[2],
                  "A_max_contiguous_hot_hours":runs[0],"B_max_contiguous_hot_hours":runs[1],
                  "C_max_contiguous_hot_hours":runs[2],"any_proxy_hot_hours":anyhot,
                  "all_three_hot_hours":allhot,"classification_disagreement_hours":anyhot-allhot,
                  "model_training_permitted":False})
    summaries=[]
    for ba in BAS:
        for threshold in THRESHOLDS:
            sample=[r for r in days if r["BA"]==ba and r["threshold_c"]==threshold]
            summaries.append({"BA":ba,"threshold_c":threshold,"sampled_days":4,
              "classification_disagreement_hours":sum(r["classification_disagreement_hours"] for r in sample),
              **{f"days_with_4hour_hot_run_{letter}":sum(
                  r[f"{letter}_max_contiguous_hot_hours"]>=4 for r in sample)
                 for letter in "ABC"},
              "days_with_4hour_label_disagreement":sum(
                len({r[f"{letter}_max_contiguous_hot_hours"]>=4 for letter in "ABC"})>1
                for r in sample),
              "model_training_permitted":False})
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    for filename,rows in (("C2_ABC_48_BA_DAY_HEAT_RUNS.csv",days),
                          ("C2_ABC_12_BA_THRESHOLD_CONSENSUS.csv",summaries)):
        with (output/filename).open("w",newline="") as stream:
            w=csv.DictWriter(stream,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    (output/"source_provenance.json").write_text(json.dumps({
        "original_source_sha256":PINNED_SOURCE_SHA256,
        "observed_source_BA_hours":len(data),
        "source_only":True,"actual_grid_stress_observed":False,
        "historical_load_geography_approved":False,
        "model_training_permitted":False,
        "interpretation":"UTC-day boundaries may truncate continuous heat events; nonrandom four sampled days"
    },indent=2)+"\n")
    return summaries

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.source,a.out),indent=2))
