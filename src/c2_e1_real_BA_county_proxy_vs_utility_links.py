"""Compare source-only BA county FIPS proxy and annual utility geographic links.

Nightly-era BA FIPS source was frozen *after extraction*; not a fixed
historical BA polygon, and never a load-weight or E2 admission artifact.
"""
import argparse,csv,hashlib,io,json,zipfile
from pathlib import Path
from collections import defaultdict

COUNTY_NAME="2020_2025_EIA861_fourBA_yearly_county_FIPS_memberships_UNAPPROVED.csv"
COUNTY_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"
UTILITY_NAME="EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv"
UTILITY_SHA="957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef"
BAS=("AZPS","BPAT","CISO","SRP")

def read(archive,member,sha):
    with zipfile.ZipFile(archive) as z:raw=z.read(member)
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Frozen source member SHA mismatch")
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def analyze(counties,utilities):
    fips=defaultdict(set)
    for r in counties:
        y=int(r["year"]);ba=r["eia930_BA_code"];f=r["county_id_fips"]
        if y not in range(2020,2026) or ba not in BAS or len(f)!=5 or not f.isdigit():
            raise ValueError("Invalid source year/BA/FIPS")
        if r["model_ready"]!="False" or r["historically_approved_BA_polygon"]!="False":
            raise ValueError("Unapproved proxy claims approval")
        if f in fips[y,ba]:raise ValueError("Duplicate annual BA FIPS")
        fips[y,ba].add(f)
    if len(counties)!=1110:raise ValueError("Unexpected BA FIPS source rows")
    records=defaultdict(list);associations=defaultdict(set)
    for r in utilities:
        y=int(r["year"]);ba=r["BA"];u=r["utility_id_eia"];st=r["state"]
        if y not in range(2020,2026) or ba not in BAS:raise ValueError("Invalid source utility link")
        n=int(r["utility_counties_reported"]);cross=int(r["other_state_counties_excluded"])
        if min(n,cross)<0:raise ValueError("Negative county counts")
        records[y,ba].append((u,st,n,cross))
        associations[y,u,st].add(ba)
    if len(utilities)!=1418:raise ValueError("Unexpected original utility bridge count")
    yearly=[];overlap=[]
    for y in range(2020,2024):
        for ba in BAS:
            subset=records[y,ba];county=fips[y,ba]
            if not subset or not county:raise ValueError("Missing BA-year")
            yearly.append(dict(year=y,BA=ba,county_source_count=len(county),
               county_set_sha256=hashlib.sha256(";".join(sorted(county)).encode()).hexdigest(),
               utility_state_links=len(subset),
               no_county_links=sum(n==0 for u,st,n,c in subset),
               nonexclusive_utility_BA_links=sum(len(associations[y,u,st])>1 for u,st,n,c in subset),
               out_state_exclusion_links=sum(c>0 for u,st,n,c in subset),
               historical_BA_footprint_approved=False,valid_county_load_weights=False,
               E2_training_permitted=False))
        for i,a in enumerate(BAS):
            for b in BAS[i+1:]:
                common=fips[y,a]&fips[y,b]
                overlap.append(dict(year=y,BA_A=a,BA_B=b,
                    shared_county_FIPS=";".join(sorted(common)),shared_count=len(common),
                    share_A=len(common)/len(fips[y,a]),share_B=len(common)/len(fips[y,b]),
                    county_source_is_exclusive_partition=False,
                    shared_county_MWh_known=False))
    summary=[]
    for ba in BAS:
        sub=[r for r in yearly if r["BA"]==ba]
        n=sub[0]["county_source_count"]
        if len({r["county_set_sha256"] for r in sub})!=1:
            raise ValueError("Unexpected original annual county set change")
        summary.append(dict(BA=ba,counties_each_year=n,
            same_exact_FIPS_all_four_years=True,
            utility_state_year_links=sum(r["utility_state_links"] for r in sub),
            no_county_source_links=sum(r["no_county_links"] for r in sub),
            nonexclusive_BA_links=sum(r["nonexclusive_utility_BA_links"] for r in sub),
            out_state_county_exclusion_links=sum(r["out_state_exclusion_links"] for r in sub),
            original_nightly_source_pinned_to_release=False,
            BA_polygon_approved=False,county_load_allocation_verified=False,
            model_training_permitted=False))
    if {r["BA"]:r["counties_each_year"] for r in summary}!={"AZPS":15,"BPAT":109,"CISO":58,"SRP":3}:
        raise ValueError("County source vintage changed")
    for r in overlap:
        if r["shared_count"]!=(3 if {r["BA_A"],r["BA_B"]}=={"AZPS","SRP"} else 0):
            raise ValueError("Unexpected cross BA overlap")
    return yearly,overlap,summary

def write(path,rows):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser();p.add_argument("--counties",required=True)
    p.add_argument("--utilities",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    y,o,s=analyze(read(a.counties,COUNTY_NAME,COUNTY_SHA),
                  read(a.utilities,UTILITY_NAME,UTILITY_SHA))
    write(out/"C2_16_BA_YEAR_FIPS_VS_UTILITY_SOURCE.csv",y)
    write(out/"C2_24_BA_PAIR_FIPS_OVERLAP.csv",o)
    write(out/"C2_4_BA_GEO_SOURCE_LIMITATION.csv",s)
    (out/"SOURCE_ONLY_PROVENANCE.json").write_text(json.dumps({
      "BA_FIPS_member_sha256":COUNTY_SHA,"utility_association_member_sha256":UTILITY_SHA,
      "BA_FIPS_extraction_from_nightly_not_tag_pinned":True,
      "historical_BA_operating_territory_validated":False,
      "county_level_retail_MWh_allocated":False,"model_training_permitted":False,
      "sealed_2024_2025_hourly_demand_accessed":False},indent=2)+"\n")
    print(json.dumps(s,indent=2))
if __name__=="__main__":main()
