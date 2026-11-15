"""Cross-check observed state-limited BA→utility→county links against frozen BA counties.

An audited union of utility service counties is *not* customer allocation,
electricity load distribution, or a BA dispatch operating boundary.
"""
import argparse,csv,hashlib,json
from pathlib import Path

EXPECTED_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"
BAS=("AZPS","BPAT","CISO","SRP")
YEARS=range(2020,2026)
BRIDGE="EIA861_2020_25_fourBA_utility_state_counts_SOURCE_ONLY.csv"
OLD="2020_2025_EIA861_fourBA_yearly_county_FIPS_memberships_UNAPPROVED.csv"

def compare(bridge_rows,frozen_rows):
    original={}
    for x in frozen_rows:
        y=int(x["year"]);ba=x["eia930_BA_code"];fips=x["county_id_fips"]
        if y not in YEARS or ba not in BAS or len(fips)!=5 or not fips.isdigit():
            raise ValueError("Unknown BA/year/FIPS in original annual EIA-861 source")
        slot=original.setdefault((y,ba),set())
        if fips in slot:
            raise ValueError("Duplicate county membership in frozen BA/year source")
        slot.add(fips)
    if len(original)!=24:raise ValueError("Original BA-year snapshot must contain 24 slots")
    summary=[];observed=set()
    for x in bridge_rows:
        y=int(x["year"]);ba=x["BA"];key=(y,ba)
        if key not in original or key in observed:raise ValueError("Unexpected/duplicate utility-BA source year slot")
        observed.add(key)
        csvstr=x.get("candidate_union_FIPS_semicolon","")
        utility=set(csvstr.split(";")) if csvstr else set()
        if "" in utility or any(len(f)!=5 or not f.isdigit() for f in utility):
            raise ValueError("Invalid state-limited utility source FIPS")
        unrestricted=set(x.get("unrestricted_utility_union_FIPS_semicolon","").split(";")) if x.get("unrestricted_utility_union_FIPS_semicolon") else set()
        if "" in unrestricted or any(len(f)!=5 or not f.isdigit() for f in unrestricted):
            raise ValueError("Invalid unrestricted utility source FIPS")
        if not utility.issubset(unrestricted):
            raise ValueError("State-limited source set must be subset of unrestricted")
        association_count=int(x["source_utility_state_associations"])
        matched_count=int(x["associations_with_county_source"])
        unmatched_count=int(x["unmatched_associations"])
        if association_count<=0 or min(matched_count,unmatched_count)<0 or matched_count+unmatched_count!=association_count:
            raise ValueError("Utility association source coverage counts do not reconcile")
        if int(x["candidate_union_counties"])<0 or int(x["unrestricted_utility_union_counties"])<0 or int(x["unmatched_associations"])<0:
            raise ValueError("Negative county or unmatched association source count")
        if len(utility)!=int(x["candidate_union_counties"]) or len(unrestricted)!=int(x["unrestricted_utility_union_counties"]):
            raise ValueError("Source FIPS strings and source counts disagree")
        old=original[key];union=utility|old
        overlap=utility&old
        added=utility-old
        omitted=old-utility
        summary.append({"year":y,"BA":ba,
            "county_FIPS_in_frozen_BA_source":len(old),
            "county_FIPS_state_limited_utility_source":len(utility),
            "county_FIPS_overlap":len(overlap),
            "county_FIPS_only_in_utility_source":len(added),
            "county_FIPS_only_in_frozen_BA_source":len(omitted),
            "county_set_Jaccard":round(len(overlap)/len(union),6) if union else None,
            "unrestricted_utility_counties":len(unrestricted),
            "additional_cross_state_unique_counties":len(unrestricted-utility),
            "added_county_FIPS":";".join(sorted(added)),
            "missing_county_FIPS":";".join(sorted(omitted)),
            "utility_state_associations_total":association_count,
            "utility_state_associations_matched":matched_count,
            "utility_state_association_match_fraction":round(matched_count/association_count,6),
            "unmatched_utility_state_associations":int(x["unmatched_associations"]),
            "restricted_state_union_equals_frozen_BA_counties":utility==old,
            "utility_county_set_is_meter_or_BA_hourly_load":False,
            "operating_geography_approved":False,
            "model_training_permitted":False})
    if observed!=set(original):raise ValueError("Missing utility source BA-year comparisons")
    return sorted(summary,key=lambda x:(x["year"],x["BA"]))

def run(bridge,original,out):
    bridge=Path(bridge);original=Path(original)
    if hashlib.sha256(original.read_bytes()).hexdigest()!=EXPECTED_SHA:
        raise ValueError("Frozen BA source county membership SHA256 mismatch")
    with bridge.open(newline="",encoding="utf-8") as f:bt=list(csv.DictReader(f))
    with original.open(newline="",encoding="utf-8") as f:ot=list(csv.DictReader(f))
    rows=compare(bt,ot)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    file=out/"E1_24_BAYEARS_UTILITY_VS_BA_SOURCE_COUNTY_DIFFERENCES.csv"
    with file.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    summary={"source_year_BA_slots_verified":len(rows),
        "BA_utility_source_csv_SHA256":hashlib.sha256(bridge.read_bytes()).hexdigest(),
        "BA_county_versioned_PUDL_snapshot_SHA256":EXPECTED_SHA,
        "exact_county_set_matches":sum(r["restricted_state_union_equals_frozen_BA_counties"] for r in rows),
        "BA_year_slots_with_utility_source_counties_absent_from_frozen_BA_source":sum(r["county_FIPS_only_in_utility_source"]>0 for r in rows),
        "BA_year_slots_with_frozen_BA_counties_missing_from_utility_sources":sum(r["county_FIPS_only_in_frozen_BA_source"]>0 for r in rows),
        "total_missing_utility_state_associations":sum(r["unmatched_utility_state_associations"] for r in rows),
        "source_relationships_certify_customer_meter_location":False,
        "source_relationships_certify_true_BA_demand_location":False,
        "historical_BA_geography_approved":False,"E2_training_permitted":False}
    (out/"E1_UTILITY_VS_BA_COUNTY_RECONCILIATION_QA.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("E1_UTILITY_VS_BA_SOURCE_COUNTIES",json.dumps(summary),flush=True)
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--utility-source",required=True)
    p.add_argument("--BA-memberships",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.utility_source,a.BA_memberships,a.out)
if __name__=="__main__":main()
