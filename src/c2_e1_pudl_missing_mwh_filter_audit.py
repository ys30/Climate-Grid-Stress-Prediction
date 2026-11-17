"""Source-only audit of missing annual EIA861 sales MWh by exact filter stage.

The previous 1,321 missing-MWh count is AFTER excluding unobserved and
non-bundled rows; it must never be assumed equivalent to 1,321 missing
observed-bundled valid-customer-class MWh records.
"""
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path

SHA="996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe"
BAS={"AZPS","BPAT","CISO","SRP"}
VALID={"residential","commercial","industrial","other","transportation","direct_connection","commercial_other"}

def classify(row):
    observed=str(row.get("data_observed") or "").lower() in ("true","1")
    service=str(row.get("service_type") or "").strip().lower()
    cls=str(row.get("customer_class") or "").strip().lower()
    missing=row.get("sales_mwh") is None or str(row.get("sales_mwh")).strip()==""
    if not observed:return "01_unobserved"
    if service!="bundled":return "02_not_bundled"
    if cls not in VALID:return "03_total_or_unknown_class"
    if missing:return "04_eligible_bundled_missing_mwh"
    return "05_selected_nonmissing_mwh"

def summarize(records):
    rowcounts=Counter(); cross=Counter(); source=Counter()
    for r in records:
        ba=str(r.get("balancing_authority_code_eia") or "").strip().upper()
        date=str(r.get("report_date") or "")
        if ba not in BAS or len(date)<4 or not date[:4].isdigit():continue
        year=int(date[:4])
        if not 2020<=year<=2025:continue
        status=classify(r)
        service=str(r.get("service_type") or "NULL")
        customer_class=str(r.get("customer_class") or "NULL")
        model=str(r.get("business_model") or "NULL")
        key=(year,ba,status)
        rowcounts[key]+=1
        cross[(year,ba,status,service,customer_class,model)]+=1
        source[status]+=1
    if sum(source.values())!=5180:raise ValueError("Pinned PUDL four-BA six-year row count mismatch")
    expected={"01_unobserved":350,"02_not_bundled":1285,
              "04_eligible_bundled_missing_mwh":1321,
              "05_selected_nonmissing_mwh":2224}
    for stage,n in expected.items():
        if source[stage]!=n:raise ValueError(f"Actual source count drift for {stage}: {source[stage]}")
    a=[dict(year=year,BA=ba,classification=stage,source_rows=n)
       for (year,ba,stage),n in sorted(rowcounts.items())]
    b=[dict(year=year,BA=ba,classification=stage,service_type=service,
            customer_class=cls,business_model=model,source_rows=n)
       for (year,ba,stage,service,cls,model),n in sorted(cross.items())]
    return a,b,dict(source)

def write(path,rows):
    if not rows:raise ValueError("Empty actual annual sales QA output")
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sales",required=True);p.add_argument("--output",required=True)
    a=p.parse_args()
    h=hashlib.sha256()
    with open(a.sales,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    if h.hexdigest()!=SHA:raise ValueError("Pinned actual PUDL annual Parquet SHA256 mismatch")
    import pyarrow.parquet as pq
    # Avoid loading columns irrelevant to this specific missingness audit.
    cols=["report_date","balancing_authority_code_eia","data_observed","service_type",
          "customer_class","business_model","sales_mwh"]
    annual,by_class,counts=summarize(pq.read_table(a.sales,columns=cols).to_pylist())
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    write(out/"C2_E1_MISSING_MWH_BA_YEAR_STAGE.csv",annual)
    write(out/"C2_E1_MISSING_MWH_BY_SERVICE_CLASS_BUSINESS.csv",by_class)
    (out/"C2_E1_MISSING_MWH_AUDIT.json").write_text(json.dumps({
        "pudl_version":"v2026.10.0","sales_sha256":SHA,
        "four_ba_2020_2025_source_records":5180,"counts_by_sequential_filter":counts,
        "missing_mwh_has_known_mwh_value":False,"model_training_permitted":False,
        "sealed_2024_2025_hourly_demand_used":False},indent=2)+"\n")
    print(json.dumps(counts,sort_keys=True))

if __name__=="__main__":main()
