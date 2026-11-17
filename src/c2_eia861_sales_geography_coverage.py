"""PUDL v2026.10 annual EIA-861 observed bundled sales / county-source join.

Source-only association coverage; never spatially allocates hourly demand.
"""
import argparse,csv,hashlib,io,json,math,zipfile
from collections import defaultdict,Counter
from datetime import date
from pathlib import Path

BRIDGE_SHA="0e3d5ac5556b155456deb79bbb78be4b707907043764faca29edf1552721385e"
BRIDGE_MEMBER="EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv"
BRIDGE_MEMBER_SHA="957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef"
BAS={"AZPS","BPAT","CISO","SRP"}
CLASSES={"residential","commercial","industrial","other","transportation","direct_connection","commercial_other"}
PRIMARY=("utility_id_eia","state","report_date","balancing_authority_code_eia","customer_class","business_model","service_type")

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def load_bridge(path):
    with zipfile.ZipFile(path) as archive:
        content=archive.read(BRIDGE_MEMBER)
    if hashlib.sha256(content).hexdigest()!=BRIDGE_MEMBER_SHA:
        raise ValueError("Original PUDL association inner CSV SHA256 mismatch")
    rows=list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    if len(rows)!=1418:raise ValueError("Expected 1,418 verified original associations")
    index={}
    for row in rows:
        key=(int(row["year"]),row["BA"],int(row["utility_id_eia"]),row["state"].upper())
        if key in index:raise ValueError("Duplicate source association")
        if key[1] not in BAS or not 2020<=key[0]<=2025:
            raise ValueError("Out-of-scope source association")
        index[key]=row
    return index

def nonnegative(value,name):
    if value is None or str(value).strip()=="":return None
    number=float(value)
    if not math.isfinite(number) or number<0:raise ValueError("Invalid "+name)
    return number

def analyze(bridge,records):
    seen=set()
    values=defaultdict(lambda:{"mwh":0.0,"customers":0.0,"n":0,"n_customer":0})
    excluded=Counter()
    for r in records:
        ba=str(r["balancing_authority_code_eia"] or "").strip().upper()
        year=int(str(r["report_date"])[:4])
        if ba not in BAS or not 2020<=year<=2025:continue
        pk=tuple(str(r.get(k) or "").strip() for k in PRIMARY)
        if pk in seen:raise ValueError("Duplicate original sales primary key")
        seen.add(pk)
        excluded["BA_year_in_scope_rows"]+=1
        if str(r["data_observed"]).lower() not in ("true","1"):
            excluded["not_observed"]+=1;continue
        if str(r["service_type"]).strip().lower()!="bundled":
            excluded["not_bundled"]+=1;continue
        cls=str(r["customer_class"]).strip().lower()
        if cls not in CLASSES:
            excluded["aggregate_or_unknown_customer_class"]+=1;continue
        mwh=nonnegative(r["sales_mwh"],"sales_mwh")
        if mwh is None:excluded["missing_sales_mwh"]+=1;continue
        customers=nonnegative(r["customers"],"customers")
        link=bridge.get((year,ba,int(r["utility_id_eia"]),str(r["state"]).upper()))
        status="no_utility_association"
        if link is not None:
            status=("county_source_matched" if int(link["utility_counties_reported"])>0
                    else "association_without_county_source")
        business=str(r["business_model"] or "unspecified")
        slot=values[year,ba,business,status]
        slot["mwh"]+=mwh;slot["n"]+=1
        if customers is not None:
            slot["customers"]+=customers;slot["n_customer"]+=1
        excluded["selected_observed_bundled_non_total_rows"]+=1
    detail=[]
    for (year,ba,business,status),v in sorted(values.items()):
        detail.append({"year":year,"BA":ba,"business_model":business,"association_status":status,
                       "selected_sales_mwh":v["mwh"],"selected_customer_count":v["customers"] if v["n_customer"]==v["n"] else None,
                       "source_rows":v["n"],"nonmissing_customer_rows":v["n_customer"]})
    groups=defaultdict(list)
    for row in detail:groups[row["year"],row["BA"],row["business_model"]].append(row)
    summary=[]
    for (year,ba,business),members in sorted(groups.items()):
        denom=sum(v["selected_sales_mwh"] for v in members)
        num=sum(v["selected_sales_mwh"] for v in members if v["association_status"]=="county_source_matched")
        complete=all(v["selected_customer_count"] is not None for v in members)
        customer_den=sum(v["selected_customer_count"] for v in members) if complete else None
        customer_num=sum(v["selected_customer_count"] for v in members if v["association_status"]=="county_source_matched") if complete else None
        summary.append({"year":year,"BA":ba,"business_model":business,
            "selected_observed_bundled_sales_mwh":denom,"county_matched_sales_mwh":num,
            "county_matched_share_of_selected_sales":num/denom if denom else None,
            "customer_coverage_computable":complete,
            "selected_observed_customers":customer_den,
            "county_matched_customers":customer_num,
            "county_matched_customer_share":customer_num/customer_den if complete and customer_den else None,
            "actual_county_load_weights_validated":False,"model_training_permitted":False})
    return detail,summary,dict(excluded)

def write_csv(path,rows):
    if not rows:raise ValueError("No selected EIA-861 sales records")
    with Path(path).open("w",newline="") as stream:
        w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bridge",required=True)
    p.add_argument("--sales",required=True)
    p.add_argument("--pinned-sales-sha256",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    source_sha=digest(a.sales)
    if source_sha!=a.pinned_sales_sha256:raise ValueError("Sales Parquet pinned SHA256 mismatch")
    bridge=load_bridge(a.bridge)
    import pyarrow.parquet as pq
    table=pq.read_table(a.sales)
    records=table.to_pylist()
    detail,summary,excluded=analyze(bridge,records)
    output=Path(a.output);output.mkdir(parents=True,exist_ok=True)
    write_csv(output/"C2_E1_EIA861_SELECTED_SALES_ASSOCIATION_DETAIL.csv",detail)
    write_csv(output/"C2_E1_EIA861_BA_YEAR_SALES_COVERAGE.csv",summary)
    audit={"sales_parquet_sha256":source_sha,"bridge_source_member_sha256":BRIDGE_MEMBER_SHA,
           "bridge_download_zip_sha256":digest(a.bridge),
           "sales_source_records":len(records),"bridge_associations":len(bridge),
           "scope":"Observed bundled non-total customer classes, stratified business model",
           "sales_record_exclusions":excluded,"groups":len(summary),
           "spatial_load_weights_validated":False,"model_training_permitted":False,
           "sealed_2024_2025_demand_test_accessed":False}
    (output/"C2_E1_EIA861_SALES_COVERAGE_PROVENANCE.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit))

if __name__=="__main__":main()
