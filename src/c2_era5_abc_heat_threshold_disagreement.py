"""Real ERA5 A/B/C high-temperature classification disagreement (source-only).

Input: archived 384 matched BA-hour CSV from successful E1 Actions run 43666836001.
Do not interpret high-temperature proxy as electric grid stress or admit E2 training.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from collections import defaultdict

BAS={"AZPS","BPAT","CISO","SRP"}
DATES={"2023-01-15","2023-07-01","2025-01-15","2025-07-01"}
TEMPS=("HIFLD_A_celsius","TIGER_B_celsius","population_C_celsius")
THRESHOLDS=(25,30,35)

def run(source,out):
    raw=Path(source).read_bytes()
    data=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(data)!=384:raise ValueError("Expected 384 real ERA5 BA-hour records")
    unique=set(); groups=defaultdict(list)
    for row in data:
        ba=row["BA"];utc=row["UTC_timestamp"]
        if ba not in BAS or utc[:10] not in DATES or (ba,utc) in unique:
            raise ValueError("Unknown/duplicate BA hour or unexpected sample date")
        unique.add((ba,utc))
        if any(row[k]!="False" for k in ("population_is_customer_weights",
            "historical_BA_geography_approved","training_permitted")):
            raise ValueError("Unapproved geography erroneously model-admitted")
        temperatures=tuple(float(row[col]) for col in TEMPS)
        if abs(temperatures[2]-temperatures[1]-float(row["C_minus_B_celsius"]))>2.1e-6:
            raise ValueError("ERA5 difference violates actual source")
        groups[ba].append(temperatures)
    if any(len(groups[ba])!=96 for ba in BAS):raise ValueError("BA-hour sample incomplete")
    rows=[]
    for ba in sorted(BAS):
        for threshold in THRESHOLDS:
            flags=[tuple(v>=threshold for v in temps) for temps in groups[ba]]
            counts=[sum(z[i] for z in flags) for i in range(3)]
            disagreement=sum(any(z) and not all(z) for z in flags)
            rows.append({"BA":ba,"threshold_c":threshold,"source_hours":96,
                "A_hot_hours":counts[0],"B_hot_hours":counts[1],
                "C_hot_hours":counts[2],"classification_disagreement_hours":disagreement,
                "historical_geography_approved":False,
                "model_training_permitted":False,
                "actual_grid_stress_observed":False})
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    target=output/"C2_ERA5_ABC_12_THRESHOLD_SUMMARIES_SOURCE_ONLY.csv"
    with target.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
    metadata={"input_sha256":hashlib.sha256(raw).hexdigest(),"n_source_BA_hours":len(data),
        "thresholds_c":list(THRESHOLDS),"test_period_demand_used":False,
        "historical_load_geography_approved":False,"model_training_permitted":False}
    (output/"C2_ERA5_ABC_HEAT_THRESHOLD_SOURCE_ONLY_PROVENANCE.json").write_text(
        json.dumps(metadata,indent=2)+"\n")
    return rows,metadata

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",default="outputs/c2_spatial_thresholds")
    args=p.parse_args()
    rows,meta=run(args.source,args.out)
    print(json.dumps({"results":rows,"source":meta},indent=2))

if __name__=="__main__":main()
