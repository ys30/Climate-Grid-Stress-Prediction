"""E1 source-only geographic partial identification of observed retail MWh.

Support-constrained county *bounds*, NOT measured county loads:
conditional on the PUDL reported FIPS membership being complete and
assuming a reporting utility's selected observed annual MWh is distributed
nonnegatively across those reported service counties. For each utility-year
with one FIPS, its full reported MWh is conditionally assigned to that county.
For >1 FIPS each county has [0, source MWh]. No county FIPS is unresolved.
These wide marginal intervals are correlated, NOT independently attainable.
"""
import argparse,csv,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path
SALES_SHA="996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe"
FIPS_MEMBER="C2_E1_2020_23_933_REAL_UTILITY_BA_YEAR_COUNTY_FIPS.csv"
FIPS_SHA=None
BAS=("AZPS","BPAT","CISO","SRP")
CLASSES={"residential","commercial","industrial","transportation","other","direct_connection","commercial_other"}

def fips_source(path):
    with zipfile.ZipFile(path) as z:raw=z.read(FIPS_MEMBER)
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows)!=933:raise ValueError("Expected original fixed-release 933 utility associations")
    out={}
    for r in rows:
        k=(int(r["year"]),r["BA"],int(r["utility_id_eia"]),r["state"].upper())
        if k in out:raise ValueError("Duplicated utility BA year state FIPS source")
        fs=tuple(f for f in r["source_county_FIPS"].split(";") if f)
        if len(fs)!=int(r["source_county_count"]) or len(fs)!=len(set(fs)):
            raise ValueError("Bad original source county enumeration")
        if any(not f.isdigit() or len(f)!=5 for f in fs):raise ValueError("Invalid original source FIPS")
        out[k]=(fs,r["utility_multi_BA_source"]=="True")
    return out,hashlib.sha256(raw).hexdigest()

def aggregate(records,links):
    # Stage one: actual annual source observed sales by source reporting unit.
    groups=defaultdict(float);unit_rows=Counter()
    for r in records:
        ba=str(r.get("balancing_authority_code_eia") or "").strip().upper()
        y=int(str(r.get("report_date") or "0000")[:4])
        if y not in range(2020,2024) or ba not in BAS:continue
        if str(r.get("data_observed")).lower() not in ("true","1"):continue
        if str(r.get("service_type") or "").lower()!="bundled":continue
        if str(r.get("customer_class") or "").lower() not in CLASSES:continue
        v=r.get("sales_mwh")
        if v is None:continue
        v=float(v)
        if not math.isfinite(v) or v<0:raise ValueError("Bad original MWh")
        k=(y,ba,int(r["utility_id_eia"]),str(r["state"]).upper())
        groups[k]+=v;unit_rows[k]+=1
    # Stage two: marginal geometric support bounds. No estimated weights.
    county=defaultdict(lambda:{"lower":0.0,"upper":0.0,"one_county_units":0,
                                "multi_county_units":0,"nonexclusive_source_units":0})
    summary=defaultdict(lambda:{"total":0.0,"forced_single":0.0,"ambiguous_multi":0.0,
                                "no_fips":0.0,"unlinked":0.0})
    details=[]
    for (y,ba,u,st),mwh in sorted(groups.items()):
        county_set,multi_ba=links.get((y,ba,u,st),((),False))
        bucket="unlinked" if (y,ba,u,st) not in links else (
            "no_fips" if len(county_set)==0 else "forced_single" if len(county_set)==1 else "ambiguous_multi")
        sums=summary[y,ba];sums["total"]+=mwh;sums[bucket]+=mwh
        details.append({"year":y,"BA":ba,"utility_id_eia":u,"state":st,
            "source_county_fips":";".join(county_set),"actual_sales_mwh":mwh,
            "county_support_cardinality":len(county_set),"source_status":bucket,
            "utility_nonexclusive_BA_source":multi_ba,
            "independently_observed_county_mwh":False})
        for f in county_set:
            x=county[y,ba,f]
            x["upper"]+=mwh
            if len(county_set)==1:
                x["lower"]+=mwh;x["one_county_units"]+=1
            else:x["multi_county_units"]+=1
            if multi_ba:x["nonexclusive_source_units"]+=1
    if len(summary)!=16:raise ValueError("Incomplete 16 BA-years")
    county_rows=[]
    for (y,ba,f),vals in sorted(county.items()):
        county_rows.append({"year":y,"BA":ba,"county_FIPS":f,
            "conditional_marginal_lower_MWh":vals["lower"],
            "conditional_marginal_upper_MWh":vals["upper"],
            "one_county_reporting_units":vals["one_county_units"],
            "multi_county_reporting_units":vals["multi_county_units"],
            "nonexclusive_source_reporting_units":vals["nonexclusive_source_units"],
            "interval_is_conditional_on_source_support_completeness":True,
            "bounds_are_jointly_independent":False,
            "is_observed_county_MWh":False,"E2_model_training_permitted":False})
    total_rows=[]
    for (y,ba),s in sorted(summary.items()):
        total_rows.append({"year":y,"BA":ba,"actual_selected_annual_sales_MWh":s["total"],
           "conditional_single_source_MWh":s["forced_single"],
           "multi_county_unallocated_MWh":s["ambiguous_multi"],
           "no_FIPS_MWh":s["no_fips"],"no_link_MWh":s["unlinked"],
           "county_lower_bounds_sum_MWh":sum(r["conditional_marginal_lower_MWh"]
                for r in county_rows if r["year"]==y and r["BA"]==ba),
           "county_intervals_are_not_observed":True,"E2_model_training_permitted":False})
        if not math.isclose(s["total"],sum(s[k] for k in ("forced_single","ambiguous_multi","no_fips","unlinked")),rel_tol=1e-12,abs_tol=0.001):
            raise ValueError("Actual MWh accounting failed")
    return details,county_rows,total_rows

def write(path,rows):
    if not rows:raise ValueError("No output records")
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sales",required=True);p.add_argument("--fips-artifact",required=True)
    p.add_argument("--out",required=True);a=p.parse_args()
    h=hashlib.sha256()
    with open(a.sales,"rb") as f:
        for chunk in iter(lambda:f.read(1048576),b""):h.update(chunk)
    if h.hexdigest()!=SALES_SHA:raise ValueError("Original PUDL annual sales SHA mismatch")
    import pyarrow.parquet as pq
    cols=["report_date","balancing_authority_code_eia","data_observed","service_type",
          "customer_class","sales_mwh","utility_id_eia","state"]
    links,source_sha=fips_source(a.fips_artifact)
    d,c,s=aggregate(pq.read_table(a.sales,columns=cols).to_pylist(),links)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write(out/"C2_E1_UTILITY_MWH_ACTUAL_AND_COUNTY_SUPPORT.csv",d)
    write(out/"C2_E1_COUNTY_CONDITIONAL_MARGINAL_MWH_BOUNDS_NOT_OBSERVED.csv",c)
    write(out/"C2_E1_BA_YEAR_MWH_PARTIAL_IDENTIFICATION.csv",s)
    (out/"SOURCE_ONLY_PROVENANCE.json").write_text(json.dumps({
        "original_2020_2023_PUDL_release":"v2026.10.0",
        "sales_source_sha256":SALES_SHA,"original_utility_FIPS_member_sha256":source_sha,
        "bounds_interpretation":"conditional on exhaustive source FIPS; marginal, not jointly attainable",
        "county_MWh_directly_observed":False,
        "fips_support_is_true_BA_operating_area":False,
        "missing_county_FIPS_MWh_distributed":False,
        "training_permitted":False,"2024_25_hourly_demand_holdout_accessed":False},indent=2)+"\n")
    print(json.dumps({"source_units":len(d),"county_BA_year_rows":len(c),
                       "BA_years":len(s)},indent=2))
if __name__=="__main__":main()
