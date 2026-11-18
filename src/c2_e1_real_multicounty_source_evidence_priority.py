"""Rank *observed* source multi-county MWh for external evidence acquisition.

This does NOT allocate electricity to counties or estimate whether obtaining a
utility's service-map data will identify its meter locations. Priorities are
upper limits of source MWh that could become allocatable IF independently
verified county-specific MWh fractions became available.
"""
import argparse,csv,hashlib,io,json,math,zipfile
from collections import defaultdict
from pathlib import Path
SOURCE_MEMBER="C2_E1_UTILITY_MWH_ACTUAL_AND_COUNTY_SUPPORT.csv"
SOURCE_SHA256="05d0a092e2508d0fa8b092ae20faeca9f0b2c07859d9b96e165eddc3c0b79cbb"
SUMMARY_MEMBER="C2_E1_BA_YEAR_MWH_PARTIAL_IDENTIFICATION.csv"
SUMMARY_SHA256="d5cff3454db19781f0aa38eb034b8aae2d81d6c37541f9f43b67721b52870681"
BAS=("AZPS","BPAT","CISO","SRP")

def input_rows(path,member,expected):
    with zipfile.ZipFile(path) as archive:raw=archive.read(member)
    if hashlib.sha256(raw).hexdigest()!=expected:
        raise ValueError("Previously verified actual PUDL source artifact changed: "+member)
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def rank(sources,summary):
    expected=defaultdict(float)
    for row in summary:
        k=row["BA"]
        if k not in BAS or not 2020<=int(row["year"])<=2023:
            raise ValueError("Unexpected study BA/year")
        expected[k]+=float(row["multi_county_unallocated_MWh"])
    sums=defaultdict(float);annual=defaultdict(float)
    baseline=defaultdict(float);n_source=0
    for r in sources:
        ba=r["BA"]
        if ba not in BAS or not 2020<=int(r["year"])<=2023:
            raise ValueError("Wrong source scope")
        mwh=float(r["actual_sales_mwh"])
        if not math.isfinite(mwh) or mwh<0:raise ValueError("Invalid observed source MWh")
        if r["source_status"]!="ambiguous_multi":continue
        if int(r["county_support_cardinality"])<2:raise ValueError("Unqualified ambiguous multi-county source")
        if r["utility_nonexclusive_BA_source"]=="True":
            raise ValueError("Multi-county MWh share cannot be asserted BA-exclusive")
        key=(ba,int(r["utility_id_eia"]),r["state"])
        sums[key]+=mwh
        annual[key,int(r["year"])]+=mwh
        baseline[ba]+=mwh
        n_source+=1
    for ba in BAS:
        if not math.isclose(baseline[ba],expected[ba],abs_tol=.01,rel_tol=1e-12):
            raise ValueError("Source total mismatch versus original PUDL annual bounds")
    ranked=[];coverage=[]
    for ba in BAS:
        candidates=sorted((k,v) for k,v in sums.items() if k[0]==ba)
        candidates.sort(key=lambda kv:(-kv[1],kv[0][1],kv[0][2]))
        if not candidates:raise ValueError("No BA multi county sources")
        total=baseline[ba];cum=0
        for pos,(key,mwh) in enumerate(candidates,1):
            cum+=mwh
            ranked.append({"BA":ba,"rank":pos,"utility_id_eia":key[1],"state":key[2],
                "four_year_observed_multi_county_MWh":mwh,
                "share_of_BA_multi_county_observed_MWh":mwh/total,
                "cumulative_share_of_BA_multi_county_observed_MWh":cum/total,
                **{f"actual_sales_mwh_{y}":annual.get((key,y),0.0) for y in range(2020,2024)},
                "priority_only_not_existing_county_load_weights":True,
                "county_allocation_identified":False,"model_training_permitted":False})
        for k in (1,2,3,5,10):
            captured=sum(v for _,v in candidates[:k])
            coverage.append({"BA":ba,"top_k":k,"available_multi_county_sources":len(candidates),
                "BA_multi_county_observed_MWh":total,
                "top_k_multi_county_source_MWh":captured,
                "top_k_fraction_of_BA_multi_county_source_MWh":captured/total,
                "maximum_conditional_source_scope_if_all_top_k_independently_resolved_MWh":captured,
                "verified_county_MWh_fraction_from_these_sources":False,
                "model_training_permitted":False})
    return ranked,coverage,n_source

def save_csv(path,rows):
    with open(path,"w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--artifact",required=True);p.add_argument("--out",required=True)
    a=p.parse_args()
    actual=input_rows(a.artifact,SOURCE_MEMBER,SOURCE_SHA256)
    totals=input_rows(a.artifact,SUMMARY_MEMBER,SUMMARY_SHA256)
    ranked,coverage,n=rank(actual,totals)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    save_csv(out/"C2_E1_2020_23_UTILITY_MULTI_COUNTY_MWH_PRIORITY_RANKING.csv",ranked)
    save_csv(out/"C2_E1_2020_23_BA_TOP_K_COUNTY_SOURCE_PRIORITY_COVERAGE.csv",coverage)
    (out/"C2_E1_MULTI_COUNTY_PRIORITY_PROVENANCE.json").write_text(json.dumps({
        "actual_source":"PUDL v2026.10.0 original annual observed bundled retail MWh",
        "immutable_GitHub_artifact_id":14400293606,
        "source_member_SHA256":SOURCE_SHA256,
        "independent_annual_BA_source_member_SHA256":SUMMARY_SHA256,
        "source_multi_county_year_utility_rows":n,
        "ranked_utility_state_BA_sources":len(ranked),
        "ranking_is_observed_source_MWh_not_actual_county_location":True,
        "fraction_of_uncertainty_eliminated_by_getting_service_map":None,
        "county_MWh_fractions_observed":False,
        "NLR_modeled_population_county_profile_used":False,
        "model_training_permitted":False,
        "2024_25_hourly_demand_holdout_used":False
    },indent=2)+"\n")
    print(json.dumps(coverage,indent=2))
if __name__=="__main__":main()
