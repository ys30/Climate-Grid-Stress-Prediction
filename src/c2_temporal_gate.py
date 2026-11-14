"""Pre-declared temporal split and E0 source-admission gate.

Does not fit a model. Source rows or years cannot be silently reassigned.
"""
import argparse,csv,json
from pathlib import Path

SPLITS={"train":(2020,2021,2022),"validation":(2023,),"test":(2024,2025)}
BAS=("AZPS","BPAT","CISO","SRP")

def evaluate(rows,min_coverage=0.99):
    lookup={(int(r["year"]),r["ba"]):r for r in rows}
    result={}
    for label,years in SPLITS.items():
        checks=[]
        for year in years:
            for ba in BAS:
                r=lookup.get((year,ba))
                if r is None:
                    checks.append({"year":year,"ba":ba,"admitted":False,"reason":"not_audited"})
                    continue
                coverage=float(r["valid_coverage_ratio"])
                duplicate=int(r["duplicate_keys"])
                missing=int(r["missing_hour_keys"])
                ok=coverage>=min_coverage and duplicate==0 and missing<=int((1-min_coverage)*int(r["expected_hours"]))
                checks.append({"year":year,"ba":ba,"admitted":bool(ok),
                               "valid_coverage_ratio":coverage,"reason":"source_gate_pass" if ok else "coverage_or_duplicate_gate"})
        result[label]={"admitted":all(x["admitted"] for x in checks),"checks":checks}
    result["time_holdout_locked"]=True
    # A 99% source-hour coverage gate can never authorize model execution:
    # independent real ERA5, BA polygon geography and source anomalies remain.
    result["coverage_only_source_gate_passed"]=all(result[s]["admitted"] for s in SPLITS)
    result["historical_geography_approved"]=False
    result["ERA5_historical_full_panel_approved"]=False
    result["empirical_model_training_permitted"]=False
    result["note"]="E0 source-hour coverage ONLY, not final data admission. ERA5 source panel, geographies and anomaly QA are independent gates; never train based only on E0."
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--coverage",required=True)
    p.add_argument("--out",default="outputs/temporal_split_gate.json")
    a=p.parse_args()
    with open(a.coverage,newline="") as f:rows=list(csv.DictReader(f))
    report=evaluate(rows)
    target=Path(a.out);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"train_admitted":report["train"]["admitted"],
                      "validation_admitted":report["validation"]["admitted"],
                      "test_admitted":report["test"]["admitted"],
                      "coverage_only_source_gate_passed":report["coverage_only_source_gate_passed"],
                      "training_permitted":report["empirical_model_training_permitted"]},indent=2))
if __name__=="__main__":main()
