"""Pre-declared temporal split and E0 source-admission gate.

Does not fit a model. Source rows or years cannot be silently reassigned.
"""
import argparse,csv,json,math
from datetime import datetime, timezone
from pathlib import Path

SPLITS={"train":(2020,2021,2022),"validation":(2023,),"test":(2024,2025)}
BAS=("AZPS","BPAT","CISO","SRP")

def _expected_hours(year):
    first=datetime(year,1,1,tzinfo=timezone.utc)
    end=datetime(year+1,1,1,tzinfo=timezone.utc)
    return int((end-first).total_seconds()/3600)

def _checked_coverage(row):
    year=int(row["year"])
    ba=row["ba"]
    if year not in range(2020,2026) or ba not in BAS:
        raise ValueError("Unexpected BA-year in source coverage")
    expected=int(row["expected_hours"])
    observed=int(row["observed_keys"])
    valid=int(row["valid_values"])
    blanks=int(row["blank_or_invalid"])
    missing=int(row["missing_hour_keys"])
    duplicates=int(row["duplicate_keys"])
    ratio=float(row["valid_coverage_ratio"])
    if expected!=_expected_hours(year):
        raise ValueError("Incorrect leap-year/hour count")
    if any(v<0 for v in (observed,valid,blanks,missing,duplicates)):
        raise ValueError("Negative count in EIA-930 coverage")
    if observed>expected or observed+missing!=expected or valid+blanks!=observed:
        raise ValueError("EIA-930 coverage count arithmetic does not reconcile")
    if not math.isfinite(ratio) or not 0<=ratio<=1 or abs(ratio-valid/expected)>1.1e-6:
        raise ValueError("Invalid or inconsistent source coverage ratio")
    return {"expected":expected,"duplicate":duplicates,"missing":missing,"coverage":ratio}

def evaluate(rows,min_coverage=0.99):
    if not math.isfinite(min_coverage) or not 0<min_coverage<=1:
        raise ValueError("Invalid minimum coverage threshold")
    lookup={}
    for row in rows:
        key=(int(row["year"]),row["ba"])
        if key in lookup:
            raise ValueError("Duplicate BA/year source coverage row")
        _checked_coverage(row)
        lookup[key]=row
    result={}
    for label,years in SPLITS.items():
        checks=[]
        for year in years:
            for ba in BAS:
                r=lookup.get((year,ba))
                if r is None:
                    checks.append({"year":year,"ba":ba,"admitted":False,"reason":"not_audited"})
                    continue
                qa=_checked_coverage(r)
                # The eligible valid-hour threshold includes null and invalid values,
                # not merely observed hourly timestamp keys.
                ok=(qa["coverage"]>=min_coverage and qa["duplicate"]==0
                    and qa["missing"]<=int((1-min_coverage)*qa["expected"]))
                checks.append({"year":year,"ba":ba,"admitted":bool(ok),
                               "valid_coverage_ratio":qa["coverage"],
                               "reason":"source_gate_pass" if ok else "coverage_or_duplicate_gate"})
        result[label]={"admitted":all(x["admitted"] for x in checks),"checks":checks}
    result["time_holdout_locked"]=True
    result["coverage_only_source_gate_passed"]=all(result[s]["admitted"] for s in SPLITS)
    result["historical_geography_approved"]=False
    result["ERA5_historical_full_panel_approved"]=False
    result["empirical_model_training_permitted"]=False
    result["note"]="E0 source-hour coverage ONLY; geography, weather, anomaly QA and 2024-25 holdout remain independent blockers."
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
