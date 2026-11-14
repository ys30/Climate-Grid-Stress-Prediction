"""Read public PUDL/EIA-861 YEARLY BA county support, independently.

Not an admission of a historical balancing area polygon or load exposure.
This checks only published row-level county membership provenance, coverage
and BA ID availability, WITHOUT constructing or training a spatial model.
"""
import argparse,json,hashlib
from pathlib import Path
from collections import Counter,defaultdict

PUDL_SOURCE="s3://pudl.catalyst.coop/nightly/out_eia861__yearly_balancing_authority_service_territory.parquet"
NEEDED=("report_date","balancing_authority_id_eia","county_id_fips")

def assess(rows):
    group=defaultdict(set);year_id=defaultdict(set)
    for r in rows:
        year=int(str(r["report_date"])[:4])
        if year<2015 or year>2026:continue
        id_=r["balancing_authority_id_eia"]
        county=str(r["county_id_fips"])
        if id_ is None or county in ("None","nan",""):
            raise ValueError("BA county source must not have null ID/FIPS")
        key=(year,str(id_))
        group[key].add(county.zfill(5))
        year_id[year].add(str(id_))
    if not group:raise ValueError("No BA × county source records")
    return {
       "source_years":sorted(year_id),
       "source_BA_ID_count_by_year":{str(y):len(v) for y,v in sorted(year_id.items())},
       "county_membership_rows_per_year":{str(y):sum(len(c) for (yr,id_),c in group.items() if yr==y) for y in sorted(year_id)},
       "BA_id_count_total":len({key[1] for key in group}),
       "calendar_years_2020_2025_all_present":all(y in year_id for y in range(2020,2026)),
       "official_eia930_BA_code_to_id_mapping_established":False,
       "county_geo_mask_built":False,
       "model_geography_approved":False}

def run(out):
    import pandas as pd
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    df=pd.read_parquet(PUDL_SOURCE,columns=list(NEEDED),
      storage_options={"anon":True,"client_kwargs":{"region_name":"us-west-2"}})
    rows=df.to_dict(orient="records")
    info=assess(rows)
    info["source_url"]=PUDL_SOURCE
    info["source_data_product"]="PUDL out_eia861__yearly_balancing_authority_service_territory"
    info["data_source"]="EIA-861 annual territory-county relationships"
    info["fetched_actual_public_parquet_rows"]=len(rows)
    info["year_2025_source_unverified_if_absent"]=2025 not in info["source_years"]
    info["interpretation"]="COUNTY MEMBERSHIP is NOT a BA operating-area polygon nor parcel-level or load-weighted exposure"
    (p/"pudl_yearly_BA_county_source_inventory.json").write_text(json.dumps(info,indent=2)+"\n")
    print("PUDL_REAL_BA_COUNTY_SOURCE_INVENTORY",json.dumps(info))
    return info

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="outputs/e1_pudl_county_inventory")
    a=parser.parse_args()
    run(a.out)
if __name__=="__main__":main()
