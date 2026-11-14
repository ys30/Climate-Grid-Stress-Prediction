"""Independently inspect four EIA-930 BA identities in PUDL EIA-861 annual county data.

This is a county-level YEAR-SPECIFIC proxy, not a validated operating-area
boundary or actual weather-demand exposure. No geometric partition is assumed.
"""
import argparse,json
from pathlib import Path
from itertools import combinations

ROOT="s3://pudl.catalyst.coop/nightly/"
CODES=ROOT+"core_eia861__yearly_balancing_authority.parquet"
COUNTIES=ROOT+"out_eia861__yearly_balancing_authority_service_territory.parquet"
BAS=("AZPS","BPAT","CISO","SRP")
YEARS=range(2020,2026)

def analyze_codes(code_rows,county_rows):
    ids={};counties={}
    for r in code_rows:
        y=int(str(r["report_date"])[:4]);code=str(r["balancing_authority_code_eia"]).strip()
        if y not in YEARS or code not in BAS:continue
        key=(y,code);identity=str(r["balancing_authority_id_eia"])
        if key in ids and ids[key]!=identity:
            raise ValueError("Ambiguous annual EIA code to BA ID mapping "+str(key))
        ids[key]=identity
    all_c={}
    for r in county_rows:
        y=int(str(r["report_date"])[:4])
        if y not in YEARS:continue
        key=(y,str(r["balancing_authority_id_eia"]))
        fips=str(r["county_id_fips"]).strip()
        if fips in ("","nan","None"):raise ValueError("Null county FIPS")
        if len(fips)>5 or not fips.isdigit():
            raise ValueError("Nonstandard county FIPS "+fips)
        all_c.setdefault(key,set()).add(fips.zfill(5))
    rows=[];overlaps=[];changes=[]
    for y in YEARS:
        year_sets={}
        for code in BAS:
            key=(y,code);id_=ids.get(key)
            county_set=all_c.get((y,id_),set()) if id_ is not None else set()
            year_sets[code]=county_set
            rows.append({"year":y,"eia930_BA_code":code,"EIA861_balancing_authority_id":id_,
                "county_FIPS_membership_count":len(county_set),
                "annual_code_mapping_found":id_ is not None,
                "annual_county_source_present":len(county_set)>0,
                "proxy_is_authorized_BA_boundary":False,
                "model_training_permitted":False})
            if y>2020:
                prev=all_c.get((y-1,ids.get((y-1,code))),set())
                union=prev|county_set
                changes.append({"year":y,"ba":code,
                    "prior_year_count":len(prev),"current_count":len(county_set),
                    "county_membership_added":len(county_set-prev),
                    "county_membership_removed":len(prev-county_set),
                    "county_jaccard":round(len(prev&county_set)/len(union),7) if union else None})
        for a,b in combinations(BAS,2):
            common=year_sets[a]&year_sets[b]
            overlaps.append({"year":y,"BA_a":a,"BA_b":b,
                "county_FIPS_intersection_count":len(common),
                "fraction_of_a_counties":round(len(common)/len(year_sets[a]),7) if year_sets[a] else None,
                "fraction_of_b_counties":round(len(common)/len(year_sets[b]),7) if year_sets[b] else None,
                "county_membership_is_exclusive_partition":False})
    summary={"annual_BA_code_year_slots":24,
       "observed_annual_code_ID_mappings":sum(r["annual_code_mapping_found"] for r in rows),
       "observed_yearly_BA_county_membership_slots":sum(r["annual_county_source_present"] for r in rows),
       "source_years":list(YEARS),
       "county_overlap_does_not_mean_double_counted_EIA930_demand":True,
       "no_official_operating_area_polygon_identified":True,
       "county_proxy_temperature_computed":False,
       "geography_historically_approved":False,"model_training_permitted":False}
    return rows,overlaps,changes,summary

def run(out):
    import pandas as pd
    kwargs={"storage_options":{"anon":True,"client_kwargs":{"region_name":"us-west-2"}}}
    codes=pd.read_parquet(CODES,columns=["report_date","balancing_authority_id_eia",
                          "balancing_authority_code_eia","balancing_authority_name_eia"],**kwargs)
    counties=pd.read_parquet(COUNTIES,columns=["report_date","balancing_authority_id_eia",
                                               "county_id_fips"],**kwargs)
    rows,overlaps,changes,summary=analyze_codes(
        codes.to_dict(orient="records"),counties.to_dict(orient="records"))
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    def csvfile(name,arr):
        import csv
        with (out/name).open("w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(arr[0]))
            writer.writeheader();writer.writerows(arr)
    csvfile("2020_2025_real_BA_code_ID_county_crosswalk_UNAPPROVED.csv",rows)
    csvfile("2020_2025_year_specific_BA_county_intersections.csv",overlaps)
    csvfile("2020_2025_BA_county_membership_year_to_year_changes.csv",changes)
    summary.update({"PUDL_code_table":CODES,"PUDL_county_table":COUNTIES,
        "actual_EIA861_code_records_read":len(codes),"actual_EIA861_county_records_read":len(counties)})
    (out/"BA_annual_county_provenance_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("REAL_2020_2025_EIA861_BA_COUNTY_CROSSWALK",json.dumps(summary))
    for row in rows:print("ANNUAL_BA_COUNTIES",json.dumps(row))
    for row in overlaps:
        if row["county_FIPS_intersection_count"]:
            print("ANNUAL_BA_COUNTY_OVERLAP",json.dumps(row))
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="outputs/e1_pudl_county_crosswalk")
    args=p.parse_args();run(args.out)
if __name__=="__main__":main()
