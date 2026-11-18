"""Audit real 2020–2023 EIA861 utility/state/BA county-source temporal stability.

County-source presence is NOT historical BA footprint or load allocation.
"""
import csv,hashlib,io,json,zipfile,argparse
from pathlib import Path
from collections import defaultdict
SOURCE="EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv"
SHA="957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef"
BAS=("AZPS","BPAT","CISO","SRP")

def read_source(artifact):
    with zipfile.ZipFile(artifact) as z:raw=z.read(SOURCE)
    if hashlib.sha256(raw).hexdigest()!=SHA:
        raise ValueError("Original frozen EIA861 bridge inner CSV SHA256 mismatch")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows)!=1418:raise ValueError("Expected 1418 original PUDL BA-utility-state associations")
    return rows

def audit(rows):
    source={};multi=defaultdict(set)
    for r in rows:
        y=int(r["year"]);ba=r["BA"];utility=int(r["utility_id_eia"]);st=r["state"]
        if ba not in BAS or not 2020<=y<=2025:raise ValueError("Unexpected BA/year scope")
        key=(y,ba,utility,st)
        if key in source:raise ValueError("Duplicated source association")
        n=int(r["utility_counties_reported"]);cross=int(r["other_state_counties_excluded"])
        if min(n,cross)<0:raise ValueError("Negative county counts")
        source[key]=(n,cross)
        multi[y,utility,st].add(ba)
    by_entity=defaultdict(list)
    for (y,ba,utility,st),(n,cross) in source.items():
        if y<=2023:by_entity[ba,utility,st].append((y,n,cross,len(multi[y,utility,st])>1))
    detail=[]
    for (ba,u,st),observations in sorted(by_entity.items()):
        vals=sorted(observations);counts=[x[1] for x in vals]
        detail.append(dict(BA=ba,utility_id_eia=u,state=st,
            observed_years=len(vals),years=";".join(str(x[0]) for x in vals),
            complete_four_year_panel=len(vals)==4,
            zero_county_all_observed_years=all(n==0 for n in counts),
            county_presence_switch=min(counts)==0 and max(counts)>0,
            county_count_varies=min(counts)!=max(counts),
            county_count_min=min(counts),county_count_max=max(counts),
            year_associations_nonexclusive=sum(x[3] for x in vals),
            any_excluded_out_state_counties=any(x[2]>0 for x in vals),
            valid_customer_county_allocation=False,valid_BA_footprint=False,
            model_training_permitted=False))
    summary=[]
    for ba in BAS:
        sub=[r for r in detail if r["BA"]==ba]
        complete=[r for r in sub if r["complete_four_year_panel"]]
        summary.append(dict(BA=ba,utility_state_entities=len(sub),
            complete_four_year_entities=len(complete),
            complete_four_year_share=len(complete)/len(sub),
            zero_county_all_year_entities=sum(x["zero_county_all_observed_years"] for x in sub),
            presence_switch_entities=sum(x["county_presence_switch"] for x in sub),
            county_count_changed_complete_four_year=sum(x["county_count_varies"] for x in complete),
            any_nonexclusive_BA_entities=sum(x["year_associations_nonexclusive"]>0 for x in sub),
            any_cross_state_county_exclusion_entities=sum(x["any_excluded_out_state_counties"] for x in sub),
            annual_MWh_county_allocated=False,historical_BA_footprint_approved=False,
            load_weight_validation_approved=False,E2_training_permitted=False))
    if len(summary)!=4:raise ValueError("Expected 4 BA summaries")
    return detail,summary

def write(path,rows):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument("--artifact",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();rows=read_source(a.artifact);detail,summary=audit(rows)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write(out/"C2_2020_2023_REAL_UTILITY_STATE_GEO_TEMPORAL_STABILITY.csv",detail)
    write(out/"C2_2020_2023_REAL_FOUR_BA_GEO_SOURCE_STABILITY_SUMMARY.csv",summary)
    (out/"SOURCE_ONLY_PROVENANCE.json").write_text(json.dumps({
        "original_EIA861_source_rows":len(rows),"original_bridge_inner_sha256":SHA,
        "period":"2020-2023","utility_county_source_is_BA_territory":False,
        "county_count_is_load_location_weight":False,
        "model_training_permitted":False,"sealed_2024_25_hourly_demand_used":False},indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
