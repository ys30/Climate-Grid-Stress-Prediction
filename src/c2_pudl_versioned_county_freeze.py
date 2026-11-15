"""Compare frozen versioned PUDL EIA861 BA-county source vs historic nightly-derived snapshot.

This checks SOURCE lineage, not whether counties approximate operational BA
territory. It does not change existing geographic weather weights or authorize
E2 demand modeling.
"""
import argparse,csv,hashlib,json
from collections import defaultdict
from pathlib import Path

ROOT="s3://pudl.catalyst.coop/v2026.10.0/"
CODE_FILE="core_eia861__yearly_balancing_authority.parquet"
COUNTY_FILE="out_eia861__yearly_balancing_authority_service_territory.parquet"
BAS=("AZPS","BPAT","CISO","SRP")
YEARS=tuple(range(2020,2026))
OLD_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"

def get_original_snapshot(path):
    p=Path(path)
    if hashlib.sha256(p.read_bytes()).hexdigest()!=OLD_SHA:
        raise ValueError("Nightly-derived frozen membership SHA256 mismatch")
    with p.open(newline="",encoding="utf-8") as f:raw=list(csv.DictReader(f))
    mapping={};ids={}
    for row in raw:
        key=(int(row["year"]),row["eia930_BA_code"])
        if key[0] not in YEARS or key[1] not in BAS:
            raise ValueError("Snapshot has unexpected original BA-year")
        fips=row["county_id_fips"]
        if len(fips)!=5 or not fips.isdigit():raise ValueError("Invalid original county FIPS")
        mapping.setdefault(key,set()).add(fips)
        ids[key]=str(row["EIA861_balancing_authority_id"])
    if set(mapping)!={(y,b) for y in YEARS for b in BAS}:
        raise ValueError("Original snapshot missing 24 BA-year slots")
    return mapping,ids

def build_new_crosswalk(code_rows,county_rows):
    ids={}
    for row in code_rows:
        year=int(str(row["report_date"])[:4]);code=str(row["balancing_authority_code_eia"]).strip()
        if year not in YEARS or code not in BAS:continue
        key=(year,code);value=str(row["balancing_authority_id_eia"])
        if key in ids and ids[key]!=value:
            raise ValueError("Ambiguous versioned PUDL BA source identity")
        ids[key]=value
    if set(ids)!={(y,b) for y in YEARS for b in BAS}:
        raise ValueError("Versioned PUDL missing BA IDs for 2020–25")
    by_id=defaultdict(set)
    for row in county_rows:
        year=int(str(row["report_date"])[:4])
        if year not in YEARS:continue
        val=str(row["county_id_fips"]).strip()
        if val.lower() in ("nan","none","") or len(val)>5 or not val.isdigit():
            raise ValueError("Invalid versioned county FIPS")
        by_id[(year,str(row["balancing_authority_id_eia"]))].add(val.zfill(5))
    mapping={(y,ba):by_id.get((y,ids[(y,ba)]),set()) for y in YEARS for ba in BAS}
    if any(not fips for fips in mapping.values()):
        raise ValueError("Versioned PUDL BA year has zero counties")
    return mapping,ids

def compare_source(original,original_ids,versioned,versioned_ids):
    result=[]
    for year in YEARS:
        for ba in BAS:
            old=original[(year,ba)];new=versioned[(year,ba)]
            additions=sorted(new-old);removals=sorted(old-new)
            result.append({"year":year,"BA":ba,
                "old_BA_ID":original_ids[(year,ba)],
                "versioned_BA_ID":versioned_ids[(year,ba)],
                "old_county_count":len(old),"versioned_county_count":len(new),
                "added_FIPS":",".join(additions),"removed_FIPS":",".join(removals),
                "identical_BA_ID":original_ids[(year,ba)]==versioned_ids[(year,ba)],
                "identical_county_membership":old==new,
                "operational_BA_geography_approved":False})
    return result

def run(original,outdir):
    import pandas as pd,s3fs
    snap,old_ids=get_original_snapshot(original)
    fs=s3fs.S3FileSystem(anon=True,client_kwargs={"region_name":"us-west-2"})
    source={}
    for filename in (CODE_FILE,COUNTY_FILE):
        path=ROOT+filename
        with fs.open(path,"rb") as f:
            raw=f.read()
        if len(raw)<100:raise ValueError("Unexpected empty official versioned Parquet")
        source[filename]={"versioned_url":path,"raw_sha256":hashlib.sha256(raw).hexdigest(),
                          "raw_bytes":len(raw)}
        print("PUDL_VERSIONED_SOURCE_PIN",json.dumps(source[filename]),flush=True)
    codes=pd.read_parquet(ROOT+CODE_FILE,
           columns=["report_date","balancing_authority_id_eia","balancing_authority_code_eia"],
           storage_options={"anon":True,"client_kwargs":{"region_name":"us-west-2"}})
    counties=pd.read_parquet(ROOT+COUNTY_FILE,
           columns=["report_date","balancing_authority_id_eia","county_id_fips"],
           storage_options={"anon":True,"client_kwargs":{"region_name":"us-west-2"}})
    new,ids=build_new_crosswalk(codes.to_dict("records"),counties.to_dict("records"))
    diff=compare_source(snap,old_ids,new,ids)
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    with (out/"PUDL_2026_10_VS_NIGHTLY_SNAPSHOT_24_BA_YEAR_AUDIT.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(diff[0]))
        w.writeheader();w.writerows(diff)
    with (out/"PUDL_v2026_10_YEAR_BA_COUNTY_MEMBERSHIPS.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["year","BA","county_id_fips","BA_ID","model_training_permitted"])
        w.writeheader()
        for (y,ba),fips in sorted(new.items()):
            for c in sorted(fips):
                w.writerow({"year":y,"BA":ba,"county_id_fips":c,
                    "BA_ID":ids[(y,ba)],"model_training_permitted":False})
    status={
        "pudl_fixed_release":"v2026.10.0","versioned_original_parquet":source,
        "nightly_derived_snapshot_SHA256":OLD_SHA,
        "year_BA_slots_compared":24,
        "total_year_BA_membership_agreements":sum(r["identical_county_membership"] for r in diff),
        "total_year_BA_identity_agreements":sum(r["identical_BA_ID"] for r in diff),
        "all_BA_ID_and_county_memberships_equal":all(
            r["identical_county_membership"] and r["identical_BA_ID"] for r in diff),
        "year_BA_differences":[x for x in diff
            if not x["identical_county_membership"] or not x["identical_BA_ID"]],
        "source_release_pin_verified":True,
        "original_snapshot_overwritten":False,
        "operational_BA_geography_approved":False,
        "model_training_permitted":False}
    (out/"PUDL_FIXED_RELEASE_V2026_10_PROVENANCE.json").write_text(json.dumps(status,indent=2)+"\n")
    print("PUDL_FIXED_RELEASE_COMPARISON",json.dumps(status),flush=True)
    return status

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--old-memberships",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    run(a.old_memberships,a.out)
if __name__=="__main__":main()
