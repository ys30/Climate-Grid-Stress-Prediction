"""C2 E1 real PUDL sales null-MWh evidence audit; source-only, fail closed.

Positive customers and positive revenue are reported separately; neither implies
a quantity of missing MWh. Historical 'other' class stays unadjudicated.
"""
import argparse,csv,hashlib,json,math
from collections import Counter
from pathlib import Path

SOURCE_SHA="996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe"
BA={"AZPS","BPAT","CISO","SRP"}
CLASSES={"residential","commercial","industrial","other","transportation","direct_connection","commercial_other"}
EXPECTED_MISSING={"other":709,"transportation":386,"industrial":127,"commercial":52,"residential":47}

def state(x):
    if x is None:return "missing"
    if isinstance(x,str) and not x.strip():return "missing"
    try:v=float(x)
    except (ValueError,TypeError):return "invalid"
    if not math.isfinite(v):return "invalid"
    if v<0:return "negative"
    return "positive" if v>0 else "zero"

def eligible_missing(row):
    if str(row.get("balancing_authority_code_eia") or "").upper() not in BA:return False
    date=str(row.get("report_date") or "")
    if not date[:4].isdigit() or not 2020<=int(date[:4])<=2025:return False
    if str(row.get("data_observed")).lower() not in ("true","1"):return False
    if str(row.get("service_type") or "").lower()!="bundled":return False
    if str(row.get("customer_class") or "").lower() not in CLASSES:return False
    return row.get("sales_mwh") is None or str(row.get("sales_mwh")).strip()==""

def analyze(records):
    categories=Counter();counts=Counter();detailed=Counter()
    for r in records:
        if not eligible_missing(r):continue
        ba=str(r["balancing_authority_code_eia"]).upper()
        year=int(str(r["report_date"])[:4])
        cls=str(r["customer_class"]).lower()
        customer=state(r.get("customers"));revenue=state(r.get("sales_revenue"))
        short=str(r.get("short_form") if r.get("short_form") is not None else "NULL").lower()
        maturity=str(r.get("data_maturity") or "NULL")
        if customer in ("negative","invalid") or revenue in ("negative","invalid"):
            raise ValueError("Unexpected invalid customer or revenue amount")
        categories[cls]+=1
        counts[ba,cls]+=1
        detailed[ba,year,cls,short,maturity,customer,revenue]+=1
    for cls,n in EXPECTED_MISSING.items():
        if categories[cls]!=n:raise ValueError(f"Real pinned missing count changed for {cls}")
    if sum(categories.values())!=1321:raise ValueError("Expected 1321 original null sales rows")
    summary=[]
    for ba in sorted(BA):
        for cls in sorted(EXPECTED_MISSING):
            subset=[(key,n) for key,n in detailed.items() if key[0]==ba and key[2]==cls]
            summary.append({"BA":ba,"customer_class":cls,"missing_MWh_records":sum(n for _,n in subset),
              "positive_customers":sum(n for k,n in subset if k[5]=="positive"),
              "positive_revenue":sum(n for k,n in subset if k[6]=="positive"),
              "both_positive":sum(n for k,n in subset if k[5]=="positive" and k[6]=="positive"),
              "either_positive":sum(n for k,n in subset if k[5]=="positive" or k[6]=="positive"),
              "both_missing":sum(n for k,n in subset if k[5]=="missing" and k[6]=="missing"),
              "short_form_true":sum(n for k,n in subset if k[3]=="true"),
              "short_form_false":sum(n for k,n in subset if k[3]=="false"),
              "short_form_unknown":sum(n for k,n in subset if k[3] not in ("true","false")),
              "missing_MWh_amount_known":False,"other_class_proven_structural_zero":False,
              "model_training_permitted":False})
    detail=[{"BA":k[0],"year":k[1],"customer_class":k[2],
      "short_form":k[3],"data_maturity":k[4],"customers_state":k[5],
      "revenue_state":k[6],"source_records":n,
      "positive_revenue_not_equivalent_to_sales_MWh":True}
      for k,n in sorted(detailed.items())]
    return summary,detail,dict(categories)

def output_csv(path,rows):
    with Path(path).open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sales",required=True);p.add_argument("--out",required=True)
    args=p.parse_args()
    h=hashlib.sha256()
    with open(args.sales,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    if h.hexdigest()!=SOURCE_SHA:raise ValueError("PUDL Parquet source hash changed")
    import pyarrow.parquet as pq
    columns=["balancing_authority_code_eia","report_date","data_observed","service_type",
      "customer_class","sales_mwh","customers","sales_revenue","short_form","data_maturity"]
    table=pq.read_table(args.sales,columns=columns)
    summary,detail,counts=analyze(table.to_pylist())
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    output_csv(dest/"C2_E1_MISSING_MWH_CUSTOMER_REVENUE_BY_BA_CLASS.csv",summary)
    output_csv(dest/"C2_E1_MISSING_MWH_REPORTING_EVIDENCE_STRATA.csv",detail)
    (dest/"C2_E1_MISSING_MWH_REPORTING_EVIDENCE_PROVENANCE.json").write_text(
      json.dumps({"pinned_pudl_sales_sha256":SOURCE_SHA,"missing_class_source_counts":counts,
        "missing_mwh_imputed":False,"customer_or_revenue_used_to_estimate_mwh":False,
        "historical_other_nulls_resolved":False,"E2_training_permitted":False,
        "sealed_2024_25_hourly_demand_accessed":False},indent=2)+"\n")
    print(json.dumps({"source_counts":counts,
      "non_other_positive_customers":sum(r["positive_customers"] for r in summary if r["customer_class"]!="other"),
      "non_other_positive_revenue":sum(r["positive_revenue"] for r in summary if r["customer_class"]!="other"),
      "other_positive_customers":sum(r["positive_customers"] for r in summary if r["customer_class"]=="other"),
      "other_positive_revenue":sum(r["positive_revenue"] for r in summary if r["customer_class"]=="other")},indent=2))
if __name__=="__main__":main()
