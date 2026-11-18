"""E1 source-only: quantify sales MWh by utility county geolocation identifiability.

Pin two actual PUDL v2026.10.0 objects and an immutable 933-row FIPS artifact.
A one-county source association is NOT BA load-location certification.
"""
import argparse,csv,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path
SALES_SHA="996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe"
FIPS_MEMBER="C2_E1_2020_23_933_REAL_UTILITY_BA_YEAR_COUNTY_FIPS.csv"
BAS=("AZPS","BPAT","CISO","SRP")
VALID={"residential","commercial","industrial","transportation","other","direct_connection","commercial_other"}

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as stream:
        for part in iter(lambda:stream.read(1024*1024),b""):h.update(part)
    return h.hexdigest()

def read_fips(path):
    with zipfile.ZipFile(path) as z:data=z.read(FIPS_MEMBER)
    rows=list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    if len(rows)!=933:raise ValueError("Expected exactly 933 original utility county FIPS links")
    index={}
    for r in rows:
        key=(int(r["year"]),r["BA"],int(r["utility_id_eia"]),r["state"].upper())
        if key in index:raise ValueError("Duplicate FIPS link")
        fips=[s for s in r["source_county_FIPS"].split(";") if s]
        if len(fips)!=int(r["source_county_count"]) or len(fips)!=len(set(fips)):
            raise ValueError("FIPS count or uniqueness disagreement")
        if any(len(s)!=5 or not s.isdigit() for s in fips):
            raise ValueError("Invalid source FIPS")
        index[key]=r
    return index,hashlib.sha256(data).hexdigest()

def value(x):
    if x is None or str(x).strip()=="":return None
    n=float(x)
    if not math.isfinite(n) or n<0:raise ValueError("Invalid actual sales")
    return n

def analyze(sales,fips):
    total=Counter()
    output=defaultdict(lambda:{"sales_mwh":0.0,"record_count":0,
                               "customers_nonmissing":0,"customers_sum":0.0})
    for r in sales:
        ba=str(r.get("balancing_authority_code_eia") or "").strip().upper()
        year=int(str(r.get("report_date") or "0000")[:4])
        if ba not in BAS or year not in range(2020,2024):continue
        total["all_source_rows"]+=1
        if str(r.get("data_observed")).lower() not in ("true","1"):continue
        if str(r.get("service_type") or "").strip().lower()!="bundled":continue
        if str(r.get("customer_class") or "").strip().lower() not in VALID:continue
        mwh=value(r.get("sales_mwh"))
        if mwh is None:continue
        key=(year,ba,int(r["utility_id_eia"]),str(r["state"]).upper())
        link=fips.get(key)
        n=None if link is None else int(link["source_county_count"])
        label=("no_utility_link" if n is None else
               "no_county_FIPS" if n==0 else
               "exactly_one_county_FIPS" if n==1 else "multiple_county_FIPS")
        multi=bool(link is not None and link["utility_multi_BA_source"]=="True")
        business=str(r.get("business_model") or "unspecified")
        slot=output[year,ba,business,label,multi]
        slot["sales_mwh"]+=mwh
        slot["record_count"]+=1
        customers=value(r.get("customers"))
        if customers is not None:
            slot["customers_nonmissing"]+=1
            slot["customers_sum"]+=customers
        total["eligible_observed_bundled_nonnull_MWh_records"]+=1
    detail=[]
    for (year,ba,business,label,multi),v in sorted(output.items()):
        detail.append(dict(year=year,BA=ba,business_model=business,county_source_status=label,
                           nonexclusive_utility_BA=multi,observed_retail_sales_mwh=v["sales_mwh"],
                           sales_source_rows=v["record_count"],
                           customers_complete=v["customers_nonmissing"]==v["record_count"],
                           observed_customers=v["customers_sum"] if v["customers_nonmissing"]==v["record_count"] else None,
                           utility_county_source_is_verified_MWh_allocation=False,
                           E2_training_permitted=False))
    summaries=[]
    for year in range(2020,2024):
        for ba in BAS:
            sub=[r for r in detail if r["year"]==year and r["BA"]==ba]
            denom=sum(r["observed_retail_sales_mwh"] for r in sub)
            if denom<=0:raise ValueError("Missing observed BA-year sales")
            measures={name:sum(r["observed_retail_sales_mwh"] for r in sub if r["county_source_status"]==name)
                for name in ("exactly_one_county_FIPS","multiple_county_FIPS","no_county_FIPS","no_utility_link")}
            nonexc=sum(r["observed_retail_sales_mwh"] for r in sub if r["nonexclusive_utility_BA"])
            if not math.isclose(sum(measures.values()),denom,rel_tol=1e-10):
                raise ValueError("Actual selected MWh accounting failed")
            summaries.append(dict(year=year,BA=ba,selected_observed_bundled_MWh=denom,
                exactly_one_county_source_MWh=measures["exactly_one_county_FIPS"],
                multiple_county_unallocated_MWh=measures["multiple_county_FIPS"],
                zero_county_source_MWh=measures["no_county_FIPS"],
                no_utility_source_link_MWh=measures["no_utility_link"],
                one_county_source_share=measures["exactly_one_county_FIPS"]/denom,
                multiple_county_unallocated_share=measures["multiple_county_FIPS"]/denom,
                no_county_or_link_share=(measures["no_county_FIPS"]+measures["no_utility_link"])/denom,
                multi_BA_source_MWh=nonexc,multi_BA_source_share=nonexc/denom,
                zero_or_many_county_MWh_allocated_to_counties=False,
                single_county_source_is_verified_BA_operating_load_location=False,
                model_training_permitted=False))
    return detail,summaries,dict(total)

def write(path,rows):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--sales",required=True)
    ap.add_argument("--original-fips-artifact",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    if sha(a.sales)!=SALES_SHA:raise ValueError("Original annual PUDL sales Parquet SHA mismatch")
    import pyarrow.parquet as pq
    columns=["report_date","balancing_authority_code_eia","data_observed","service_type",
      "customer_class","sales_mwh","utility_id_eia","state","business_model","customers"]
    fips,member_sha=read_fips(a.original_fips_artifact)
    detail,summaries,counts=analyze(pq.read_table(a.sales,columns=columns).to_pylist(),fips)
    if len(summaries)!=16:raise ValueError("Expected 16 four-BA source-year summary rows")
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write(out/"C2_2020_23_OBSERVED_MWH_BY_COUNTY_IDENTIFIABILITY.csv",detail)
    write(out/"C2_16_BAYEAR_OBSERVED_MWH_COUNTY_IDENTIFIABILITY.csv",summaries)
    (out/"SOURCE_ONLY_PROVENANCE.json").write_text(json.dumps({
        "fixed_pudl_version":"v2026.10.0",
        "original_sales_sha256":SALES_SHA,
        "original_utility_FIPS_artifact_member_sha256":member_sha,
        "source_row_filter_counts":counts,"observed_county_MWh_allocation_exists":False,
        "historical_BA_operating_area_certified":False,"GEO_LOAD_RELEVANCE_approved":False,
        "GEO_HISTORICAL_BA_FOOTPRINT_approved":False,
        "LOAD_QUALITY_HOLDOUT_PROTOCOL_approved":False,
        "model_training_permitted":False,"sealed_2024_25_hourly_demand_accessed":False},indent=2)+"\n")
    print(json.dumps(summaries,indent=2))
if __name__=="__main__":main()
