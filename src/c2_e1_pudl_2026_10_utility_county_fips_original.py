"""Original PUDL v2026.10.0 year-utility-state-BA *FIPS sets* source audit.

An actual EIA-861 service-territory reported county is NOT a county's
electricity load share. A utility serving multiple BAs is nonexclusive.
"""
import argparse,csv,hashlib,json,zipfile,io
from collections import defaultdict,Counter
from pathlib import Path

BAS={"AZPS","BPAT","CISO","SRP"}
YEARS=range(2020,2024)
BRIDGE_NAME="EIA861_fourBA_utility_state_association_SOURCE_ONLY.csv"
BRIDGE_SHA="957d54d8b9ac1ec757d579d9ea9df47c2221548860adea2fba6b522821fbecef"

def bridge_rows(archive):
    with zipfile.ZipFile(archive) as z:raw=z.read(BRIDGE_NAME)
    if hashlib.sha256(raw).hexdigest()!=BRIDGE_SHA:raise ValueError("Frozen PUDL BA-utility bridge SHA mismatch")
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows)!=1418:raise ValueError("Wrong original bridge population")
    return rows

def as_year(date):
    s=str(date)
    if len(s)<4 or not s[:4].isdigit():raise ValueError("Invalid report_date")
    return int(s[:4])

def normalize_fips(value):
    if value is None:raise ValueError("Null county FIPS")
    s=str(value).strip()
    if s.lower() in ("none","nan",""):raise ValueError("Null county FIPS")
    if s.endswith(".0"):s=s[:-2]
    if not s.isdigit() or len(s)>5:raise ValueError("Malformed county FIPS")
    return s.zfill(5)

def summarize(bridge,territory):
    counties=defaultdict(set)
    for r in territory:
        y=as_year(r["report_date"])
        if y not in YEARS:continue
        u=str(int(r["utility_id_eia"]));st=str(r["state"]).strip()
        f=normalize_fips(r["county_id_fips"])
        if not st or st.lower() in ("nan","none"):raise ValueError("Null territory state")
        counties[y,u,st].add(f)
    entity={};multiba=defaultdict(set)
    for row in bridge:
        y=int(row["year"]);ba=row["BA"]
        if y not in YEARS:continue
        if ba not in BAS:raise ValueError("Unknown BA")
        u=str(int(row["utility_id_eia"]));st=row["state"]
        key=(y,ba,u,st)
        if key in entity:raise ValueError("Duplicate original BA-utility link")
        entity[key]=row
        multiba[y,u,st].add(ba)
    if len(entity)!=933:raise ValueError(f"Expected 933 original 2020-23 BA utility links, got {len(entity)}")
    records=[]
    for (y,ba,u,st),meta in sorted(entity.items()):
        fs=counties.get((y,u,st),set())
        expected=int(meta["utility_counties_reported"])
        if len(fs)!=expected:raise ValueError(f"Original source county-count mismatch {y,ba,u,st}: {len(fs)} vs {expected}")
        records.append({"year":y,"BA":ba,"utility_id_eia":u,"state":st,
           "source_county_FIPS":";".join(sorted(fs)),
           "source_county_count":len(fs),
           "utility_multi_BA_source":len(multiba[y,u,st])>1,
           "associated_BAs":";".join(sorted(multiba[y,u,st])),
           "FIPS_set_sha256":hashlib.sha256(";".join(sorted(fs)).encode()).hexdigest(),
           "source_reports_actual_county_MWh":False,
           "geographic_model_admission":False})
    pairs=[];seen=set()
    for rec in records:
        key=(rec["year"],rec["utility_id_eia"],rec["state"])
        if key in seen:continue
        seen.add(key);bas=sorted(multiba[key])
        if len(bas)>1:
            fs=counties.get(key,set())
            pairs.append({"year":key[0],"utility_id_eia":key[1],"state":key[2],
              "associated_BAs":";".join(bas),
              "source_county_FIPS":";".join(sorted(fs)),
              "counties_requiring_nonexclusive_allocation":len(fs),
              "load_share_among_BAs_known":False})
    summary=[]
    for ba in sorted(BAS):
        subset=[r for r in records if r["BA"]==ba]
        union=set()
        for r in subset:union.update(filter(None,r["source_county_FIPS"].split(";")))
        summary.append({"BA":ba,"utility_state_year_source_links":len(subset),
           "links_without_county_source":sum(r["source_county_count"]==0 for r in subset),
           "links_with_county_source":sum(r["source_county_count"]>0 for r in subset),
           "nonexclusive_BA_links":sum(r["utility_multi_BA_source"] for r in subset),
           "unique_year_union_county_FIPS":len(union),
           "true_annual_county_MWh_allocation_observed":False,
           "historical_BA_footprint_approved":False,
           "E2_training_permitted":False})
    return records,pairs,summary

def save_csv(path,data,fields=None):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields or list(data[0]));w.writeheader();w.writerows(data)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bridge",required=True);ap.add_argument("--territory",required=True)
    ap.add_argument("--out",required=True);a=ap.parse_args()
    import pyarrow.parquet as pq
    raw=Path(a.territory).read_bytes()
    territory=pq.read_table(a.territory,columns=["report_date","utility_id_eia","state","county_id_fips"]).to_pylist()
    links,pairs,summary=summarize(bridge_rows(a.bridge),territory)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    save_csv(out/"C2_E1_2020_23_933_REAL_UTILITY_BA_YEAR_COUNTY_FIPS.csv",links)
    save_csv(out/"C2_E1_2020_23_REAL_NONEXCLUSIVE_UTILITY_BA_COUNTY_FIPS.csv",pairs,
             ["year","utility_id_eia","state","associated_BAs","source_county_FIPS","counties_requiring_nonexclusive_allocation","load_share_among_BAs_known"])
    save_csv(out/"C2_E1_2020_23_FOUR_BA_UTILITY_TERRITORY_SOURCE_SUMMARY.csv",summary)
    (out/"SOURCE_ONLY_PROVENANCE.json").write_text(json.dumps({
        "source_release":"PUDL v2026.10.0",
        "territory_s3_uri":"s3://pudl.catalyst.coop/v2026.10.0/core_eia861__yearly_service_territory.parquet",
        "territory_sha256":hashlib.sha256(raw).hexdigest(),
        "bridge_member_sha256":BRIDGE_SHA,
        "source_link_rows":len(links),"nonexclusive_utility_state_year_groups":len(pairs),
        "load_county_MWh_observed":False,
        "utility_counties_are_BA_operational_polygons":False,
        "GEO_HISTORICAL_BA_FOOTPRINT":False,
        "GEO_LOAD_RELEVANCE":False,
        "LOAD_QUALITY_HOLDOUT_PROTOCOL":False,
        "model_training_permitted":False,
        "sealed_2024_2025_hourly_demand_used":False
    },indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
