"""C2 E1: within-filing sibling evidence for PUDL null sector rows.

Actual derived table only. Evidence of same filing containing other class sales
does not prove original null cell was structural/nonapplicable.
"""
import argparse,collections,csv,hashlib,json,math
from pathlib import Path

SHA="996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe"
BAS={"AZPS","BPAT","CISO","SRP"}
EXPECTED={"other":709,"transportation":386,"industrial":127,"commercial":52,"residential":47}
KEY=("utility_id_eia","state","report_date","balancing_authority_code_eia","business_model","service_type")

def is_observed_bundled(r):
    return (str(r.get("balancing_authority_code_eia") or "").upper() in BAS
            and str(r.get("report_date") or "")[:4].isdigit()
            and 2020<=int(str(r["report_date"])[:4])<=2025
            and str(r.get("data_observed")).lower() in ("true","1")
            and str(r.get("service_type") or "").lower()=="bundled")

def audit(records):
    groups=collections.defaultdict(list)
    for r in records:
        if is_observed_bundled(r):
            groups[tuple(str(r.get(c)) for c in KEY)].append(r)
    detail=[]
    for key,members in groups.items():
        for r in members:
            cls=str(r.get("customer_class") or "").lower()
            if cls not in EXPECTED or r.get("sales_mwh") is not None:continue
            siblings=[s for s in members if s is not r and str(s.get("customer_class") or "").lower() not in ("total",cls)]
            positive=[s for s in siblings if s.get("sales_mwh") is not None and math.isfinite(float(s["sales_mwh"])) and float(s["sales_mwh"])>0]
            any_nonnull=[s for s in siblings if s.get("sales_mwh") is not None]
            own_data=(r.get("customers"),r.get("sales_revenue"))
            detail.append({"BA":key[3],"year":int(str(r["report_date"])[:4]),
                "customer_class":cls,"utility_id_eia":key[0],"state":key[1],
                "business_model":key[4],"service_type":key[5],
                "other_class_positive_sales_same_filing":bool(positive),
                "other_class_nonnull_sales_same_filing":bool(any_nonnull),
                "positive_sibling_classes":";".join(sorted(set(str(s["customer_class"]) for s in positive))),
                "same_filing_other_class_count":len(siblings),
                "own_customers_null":own_data[0] is None,
                "own_revenue_null":own_data[1] is None,
                "is_original_raw_wide_cell_proven_structural":False,
                "model_training_permitted":False})
    classcounts=collections.Counter(r["customer_class"] for r in detail)
    if classcounts!=collections.Counter(EXPECTED):
        raise ValueError(f"Actual pinned missing class counts changed: {classcounts}")
    summary=[]
    for ba in sorted(BAS):
        for cls in EXPECTED:
            subset=[r for r in detail if r["BA"]==ba and r["customer_class"]==cls]
            summary.append({"BA":ba,"customer_class":cls,"missing_sales_mwh_rows":len(subset),
               "positive_sibling_sales_same_filing":sum(r["other_class_positive_sales_same_filing"] for r in subset),
               "nonnull_sibling_sales_same_filing":sum(r["other_class_nonnull_sales_same_filing"] for r in subset),
               "no_positive_sibling":sum(not r["other_class_positive_sales_same_filing"] for r in subset),
               "null_customers_and_revenue":sum(r["own_customers_null"] and r["own_revenue_null"] for r in subset),
               "original_raw_filing_slot_verified":False,"model_training_permitted":False})
    return summary,detail

def write(path,rows):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sales",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    h=hashlib.sha256()
    with open(a.sales,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    if h.hexdigest()!=SHA:raise ValueError("Source mismatch: PUDL v2026.10.0 parquet SHA256")
    import pyarrow.parquet as pq
    cols=list(KEY)+["customer_class","data_observed","sales_mwh","customers","sales_revenue"]
    tbl=pq.read_table(a.sales,columns=cols)
    summary,detail=audit(tbl.to_pylist())
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write(out/"C2_E1_MISSING_MWH_SIBLING_CLASS_SUMMARY.csv",summary)
    write(out/"C2_E1_MISSING_MWH_SAME_FILING_1321_ROWS.csv",detail)
    (out/"C2_E1_SIBLING_AUDIT_PROVENANCE.json").write_text(json.dumps({
        "PUDL_version":"v2026.10.0","source_parquet_sha256":SHA,
        "missing_rows":len(detail),
        "positive_sibling_rows":sum(r["other_class_positive_sales_same_filing"] for r in detail),
        "unresolved_without_original_raw_wide_filing":True,
        "2024_2025_sealed_hourly_demand_used":False,
        "model_training_permitted":False},indent=2)+"\n")
    print(json.dumps({"missing_rows":len(detail),"positive_sibling_rows":sum(r["other_class_positive_sales_same_filing"] for r in detail)}))

if __name__=="__main__":main()
