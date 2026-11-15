"""Audit observed EIA-861 BA-utility-state associations and utility counties.

Official, version-pinned PUDL tables. Never assert county customer counts, infer
hourly BA demand from annual association, or promote service counties to
official BA operating geography.
"""
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT="s3://pudl.catalyst.coop/v2026.10.0/"
ASSN="core_eia861__assn_balancing_authority.parquet"
TERRITORY="core_eia861__yearly_service_territory.parquet"
BAS={"AZPS":803,"BPAT":1738,"CISO":2775,"SRP":16572}
YEARS=set(range(2020,2026))

def assess(associations,territories):
    # Association is BA × utility × state, not a customer/county assignment.
    by_ba=defaultdict(set);utility_bas=defaultdict(set)
    for row in associations:
        year=int(str(row["report_date"])[:4])
        baid=int(row["balancing_authority_id_eia"])
        if year not in YEARS or baid not in set(BAS.values()):continue
        utility=int(row["utility_id_eia"]);state=str(row["state"]).strip()
        if not state or state.lower() in ("nan","none"):
            raise ValueError("BA-utility source missing state")
        by_ba[(year,baid)].add((utility,state))
        utility_bas[(year,utility,state)].add(baid)
    if set(by_ba)!={(year,baid) for year in YEARS for baid in BAS.values()}:
        raise ValueError("No complete 24 BA-year utility association slots")
    by_utility_counties=defaultdict(set)
    for row in territories:
        year=int(str(row["report_date"])[:4])
        if year not in YEARS:continue
        utility=int(row["utility_id_eia"])
        fips=str(row["county_id_fips"]).strip()
        if not fips or fips.lower() in ("nan","none") or len(fips)>5 or not fips.isdigit():
            raise ValueError("Missing/invalid utility county FIPS")
        by_utility_counties[(year,utility)].add(fips.zfill(5))
    counts=[];detail=[];ambiguous=[]
    for year in sorted(YEARS):
        for ba,baid in BAS.items():
            members=by_ba[(year,baid)]
            joined=set()
            found=0
            for utility,state in sorted(members):
                c=by_utility_counties.get((year,utility),set())
                if c:found+=1
                joined|=c
                if len(utility_bas[(year,utility,state)])>1:
                    ambiguous.append({"year":year,"utility_id_eia":utility,
                      "state":state,"BA_id_count":len(utility_bas[(year,utility,state)]),
                      "BA_ids":";".join(map(str,sorted(utility_bas[(year,utility,state)]))),
                      "not_exclusive_BA_customer_location":True})
                detail.append({"year":year,"BA":ba,"BA_id_eia":baid,
                  "utility_id_eia":utility,"state":state,
                  "utility_counties_reported":len(c),
                  "source_BA_association_is_actual_customer_allocation":False})
            counts.append({"year":year,"BA":ba,
              "source_utility_state_associations":len(members),
              "associations_with_county_source":found,
              "candidate_union_counties":len(joined),
              "unmatched_associations":len(members)-found,
              "utility_county_locations_are_hourly_BA_load":False,
              "operational_BA_geography_approved":False,
              "training_permitted":False})
    dedup={(x["year"],x["utility_id_eia"],x["state"]):x for x in ambiguous}
    return counts,detail,list(dedup.values())

def run(out):
    import pandas as pd,s3fs
    fs=s3fs.S3FileSystem(anon=True,client_kwargs={"region_name":"us-west-2"})
    pin={}
    for name in (ASSN,TERRITORY):
        with fs.open(ROOT+name,"rb") as f:raw=f.read()
        if len(raw)<100:raise ValueError("Empty original PUDL tagged Parquet")
        pin[name]={"path":ROOT+name,"sha256":hashlib.sha256(raw).hexdigest(),
            "bytes":len(raw)}
        print("E1_EIA861_UTILITY_ORIGINAL_SOURCE_SHA",json.dumps(pin[name]),flush=True)
    def table(name,columns):
        return pd.read_parquet(ROOT+name,columns=columns,
            storage_options={"anon":True,"client_kwargs":{"region_name":"us-west-2"}}).to_dict("records")
    assn=table(ASSN,["report_date","balancing_authority_id_eia","utility_id_eia","state"])
    territory=table(TERRITORY,["report_date","utility_id_eia","county_id_fips"])
    summaries,detail,ambiguous=assess(assn,territory)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,data,fields in (
        ("EIA861_2020_25_fourBA_utility_state_counts_SOURCE_ONLY.csv",summaries,list(summaries[0])),
        ("EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv",detail,list(detail[0])),
        ("EIA861_nonexclusive_utility_BA_associations_SOURCE_ONLY.csv",ambiguous,
         ["year","utility_id_eia","state","BA_id_count","BA_ids","not_exclusive_BA_customer_location"])):
        with (out/name).open("w",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
    summary={"original_PUDL_v2026_10_parquet_SHA256":pin,
       "BA_year_slots":len(summaries),
       "BA_utility_state_associations":len(detail),
       "unmatched_utility_state_associations":sum(x["unmatched_associations"] for x in summaries),
       "distinct_ambiguous_utility_year_state_assignments":len(ambiguous),
       "actual_county_customer_distribution_observed":False,
       "actual_hourly_county_load_observed":False,
       "geographic_model_admission":False,"model_training_permitted":False,
       "interpretation":"EIA-861 observed BA-utility-state and utility-county SOURCE relational proxy, not actual consumer meters or BA load location"}
    (out/"E1_EIA861_VERSIONED_UTILITY_SOURCE_ONLY_QA.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("E1_REAL_VERSIONED_BA_UTILITY_COUNTY_AUDIT",json.dumps(summary),flush=True)
    return summary

def main():
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    run(p.parse_args().out)
if __name__=="__main__":main()
