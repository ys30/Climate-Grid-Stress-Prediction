"""Discover U.S.-wide Control Areas ArcGIS features, WITHOUT approving BA polygon mappings.

Metadata and paged attribute records provide evidence for coverage and source vintage.
No polygons are silently transformed or admitted as historic BA territory.
"""
import argparse,hashlib,json,re,time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

SERVICE="https://services5.arcgis.com/HDRa0B57OVrv2E1q/ArcGIS/rest/services/Control_Areas/FeatureServer/0"
TARGETS={
 "AZPS":("ARIZONA PUBLIC SERVICE","ARIZONA PUBLIC SERV"),
 "BPAT":("BONNEVILLE POWER ADMINISTRATION","BONNEVILLE POWER"),
 "CISO":("CALIFORNIA INDEPENDENT SYSTEM OPERATOR","CALIFORNIA ISO"),
 "SRP":("SALT RIVER PROJECT","SALT RIVER"),
}
NAME_CANDIDATES=("NAME","NAME1","BA_NAME","CTRL_AREA","CONTROL_AREA","COMPANY","OWNER","UTILITY","ENTITY","BA","BA_NAME_1")
def match_names(attrs):
    """Conservatively match candidate BA names without inferring identity from arbitrary fields."""
    found=[]
    names=[(k,str(v or "")) for k,v in attrs.items()
           if k.upper() in NAME_CANDIDATES or "NAME" in k.upper()]
    for code,phrases in TARGETS.items():
        for field,value in names:
            if any(phrase in value.upper() for phrase in phrases):
                found.append({"ba_candidate":code,"name_field":field,"source_name":value})
                break
    return found

def request_json(path,params):
    url=path+"?"+urlencode(params)
    for retry in range(3):
        try:
            with urlopen(Request(url,headers={"User-Agent":"C2-research-audit/0.2"}),timeout=60) as response:
                raw=response.read()
            obj=json.loads(raw)
            if "error" in obj:raise ValueError(str(obj["error"])[:600])
            return obj,hashlib.sha256(raw).hexdigest(),len(raw)
        except (OSError,TimeoutError) as err:
            if retry==2:raise
            time.sleep(2**retry)

def discover(service=SERVICE):
    meta,meta_hash,meta_bytes=request_json(service,{"f":"json"})
    fields=[{"name":x["name"],"type":x.get("type")} for x in meta.get("fields",[])]
    oid=meta.get("objectIdField") or next((x["name"] for x in meta.get("fields",[]) if x.get("type")=="esriFieldTypeOID"),None)
    if not oid:raise ValueError("ArcGIS source without reliable OID")
    count,_,_=request_json(service+"/query",{"where":"1=1","returnCountOnly":"true","f":"json"})
    expected=count.get("count")
    if not isinstance(expected,int) or expected<1:raise ValueError("No verifiable feature count")
    page_size=min(500,meta.get("maxRecordCount",500))
    attr=[];page_sha=[]
    for offset in range(0,expected,page_size):
        page,digest,nbytes=request_json(service+"/query",{
            "where":"1=1","outFields":"*","returnGeometry":"false","orderByFields":oid,
            "resultOffset":offset,"resultRecordCount":page_size,"f":"json"})
        features=page.get("features")
        if not isinstance(features,list) or not features:raise ValueError("Empty page at "+str(offset))
        attr.extend(f.get("attributes",{}) for f in features)
        page_sha.append({"offset":offset,"count":len(features),"sha256":digest,"bytes":nbytes})
    ids=[str(row.get(oid)) for row in attr]
    if len(attr)!=expected or len(set(ids))!=expected:
        raise ValueError(f"Feature count/unique-ID audit failed {len(attr)} vs {expected}")
    candidates=[]
    for row in attr:
        for match in match_names(row):
            candidates.append({"oid":row.get(oid),**match,
                "source_attributes":row,"manual_crosswalk_approved":False})
    present=sorted({c["ba_candidate"] for c in candidates})
    return {"source_url":service,"source_layer_name":meta.get("name"),
        "source_description":str(meta.get("description") or "")[:1400],
        "metadata_sha256":meta_hash,"metadata_bytes":meta_bytes,
        "object_id_field":oid,"source_fields":fields,
        "source_total_features":expected,"paged_records":len(attr),
        "page_hashes":page_sha,"candidates":candidates,"codes_matched":present,
        "codes_unmatched":sorted(set(TARGETS)-set(present)),
        "all_four_names_found":len(present)==4,
        "geometry_downloaded":False,"vintage_approved":False,
        "code_crosswalk_approved":False,
        "ready_for_era5_weights":False,
        "note":"Discovery-only nationwide ArcGIS BA name evidence; not approved historic geography"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="outputs/e1_national_control_areas")
    a=p.parse_args()
    report=discover()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/"national_candidates.json").write_text(json.dumps(report,indent=2,default=str)+"\n")
    summary={k:report[k] for k in ("source_url","source_layer_name","source_total_features",
             "codes_matched","codes_unmatched","all_four_names_found",
             "geometry_downloaded","vintage_approved","ready_for_era5_weights")}
    print("NATIONAL_SOURCE_QA",json.dumps(summary))
    for candidate in report["candidates"]:
        print("BA_CANDIDATE",json.dumps({k:candidate[k] for k in
             ("ba_candidate","oid","name_field","source_name")}))
if __name__=="__main__":main()
