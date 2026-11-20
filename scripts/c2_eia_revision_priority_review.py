"""Flag high-impact historical EIA source-vintage differences, QA only.

Consumes the authentic 23-cohort changed-row CSV, independently verifies its
pinned digest, and prepares a *review queue*. Thresholds are investigative
priorities, never winsorization, correction, source pass, or model selection.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

PINNED_SHA="6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480"
VALID_CLASSES={"numeric_changed","both_null","old_null_to_new_numeric","old_numeric_to_new_null"}
PRIORITY_ABS_DELTA_MW=1000.0

def screen(input_csv,output_json,*,expected_sha=PINNED_SHA):
    src=Path(input_csv);out=Path(output_json)
    if src.resolve()==out.resolve() or out.exists():
        raise FileExistsError("Refuse to overwrite input or previous source-review report")
    source_sha=hashlib.sha256(src.read_bytes()).hexdigest()
    if source_sha!=expected_sha:
        raise ValueError("Archived changed-row CSV SHA mismatch")
    reviewed=[];counts=Counter();by_cohort=defaultdict(Counter);seen=set()
    with src.open(newline="",encoding="utf-8-sig") as f:
        rows=csv.DictReader(f)
        needed={"ba","year","timestamp_utc","classification",
                "frozen_eia930_demand_mw","new_api_eia930_demand_mw","delta_mw"}
        if not needed.issubset(rows.fieldnames or []):
            raise ValueError("Wrong original audit schema")
        for r in rows:
            key=(r["ba"],r["year"],r["timestamp_utc"])
            if key in seen:raise ValueError("Duplicate audited BA/year/UTC key")
            seen.add(key)
            if r["classification"] not in VALID_CLASSES:
                raise ValueError("Unknown source-revision classification")
            counts[r["classification"]]+=1
            by_cohort[(r["ba"],r["year"])][r["classification"]]+=1
            priority=[]
            if r["classification"]=="numeric_changed":
                before=float(r["frozen_eia930_demand_mw"])
                after=float(r["new_api_eia930_demand_mw"])
                delta=float(r["delta_mw"])
                if not all(map(math.isfinite,(before,after,delta))) or abs((after-before)-delta)>1e-6:
                    raise ValueError("Invalid old/new demand delta arithmetic")
                if abs(delta)>=PRIORITY_ABS_DELTA_MW:
                    counts["high_impact_1000mw"]+=1
                    by_cohort[(r["ba"],r["year"])]["high_impact_1000mw"]+=1
                    priority.append("large_numeric_revision_review")
                if after==0 and before>0:
                    counts["new_zero_demand_after_positive"]+=1
                    priority.append("zero_demand_in_new_source_review")
            if r["classification"] in {"old_null_to_new_numeric","old_numeric_to_new_null"}:
                priority.append("missingness_revision_review")
            if priority:
                reviewed.append({"ba":r["ba"],"year":int(r["year"]),
                                 "timestamp_utc":r["timestamp_utc"],
                                 "old_reported_mw":r["frozen_eia930_demand_mw"],
                                 "new_reported_mw":r["new_api_eia930_demand_mw"],
                                 "priority_reasons":priority})
    report={
        "status":"SOURCE_REVISION_PRIORITY_NOT_MODEL_QUALITY_APPROVAL",
        "matched_BA_years":23,
        "source_changed_rows_sha256":source_sha,
        "numeric_revision_review_threshold_abs_mw":PRIORITY_ABS_DELTA_MW,
        "counts":dict(counts),
        "priority_rows":reviewed,
        "per_cohort":{f"{ba}_{year}":dict(v) for (ba,year),v in sorted(by_cohort.items())},
        "threshold_is_scientific_filter":False,
        "source_error_proven":False,
        "source_values_replaced":False,
        "model_training_permitted":False,
        "test_years_used_for_model_selection":False
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("changed_rows_csv",type=Path)
    p.add_argument("output_json",type=Path)
    a=p.parse_args()
    d=screen(a.changed_rows_csv,a.output_json)
    print(json.dumps({"counts":d["counts"],"training_permitted":False},indent=2))

if __name__=="__main__":
    main()
