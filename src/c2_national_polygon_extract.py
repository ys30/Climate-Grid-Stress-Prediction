"""Fetch four independently identified national control-area polygons.

Output is strictly PROVISIONAL geographic evidence, never an automatically
approved historical BA exposure. Preserve original geometry in GeoJSON artifact.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
from src.c2_national_control_area_discovery import SERVICE

IDS={"BPAT":4,"CISO":11,"AZPS":23,"SRP":36}
NAMES={"BPAT":"BONNEVILLE POWER ADMINISTRATION",
       "CISO":"CALIFORNIA INDEPENDENT SYSTEM OPERATOR",
       "AZPS":"ARIZONA PUBLIC SERVICE COMPANY","SRP":"SALT RIVER PROJECT"}
def fetch_candidate_polygons(service=SERVICE):
    query={"objectIds":",".join(str(IDS[b]) for b in sorted(IDS)),
           "outFields":"*","returnGeometry":"true","outSR":"4326","f":"geojson"}
    url=service+"/query?"+urlencode(query)
    with urlopen(Request(url,headers={"User-Agent":"C2-geometry-audit/0.2"}),timeout=90) as f:
        raw=f.read()
    doc=json.loads(raw)
    if "error" in doc:raise ValueError("GeoJSON service query failed: "+repr(doc["error"])[:500])
    if doc.get("type")!="FeatureCollection":raise ValueError("Query did not return GeoJSON")
    from shapely.geometry import shape
    from shapely.validation import explain_validity
    from pyproj import Transformer
    from shapely.ops import transform
    project=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    features=[];audit=[]
    id_to_ba={v:k for k,v in IDS.items()}
    for ft in doc.get("features",[]):
        props=ft.get("properties") or {}
        oid=props.get("OBJECTID_1")
        ba=id_to_ba.get(int(oid)) if oid is not None else None
        if ba is None:raise ValueError("Unexpected OID in nationwide query")
        name=(props.get("NAME") or "").upper().strip()
        if name!=NAMES[ba]:raise ValueError(f"OID/name crosswalk changed {oid} {name}")
        poly=shape(ft["geometry"])
        valid=poly.is_valid and not poly.is_empty and poly.geom_type in ("Polygon","MultiPolygon")
        bbox=[round(x,6) for x in poly.bounds]
        area=transform(project,poly).area if valid else None
        validity_reason="Valid Geometry" if valid else explain_validity(poly)
        vertex_count=len(str(ft.get("geometry") or ""))
        audit.append({"ba_candidate":ba,"oid":oid,"name":name,"geometry_type":poly.geom_type,
                      "is_valid":bool(valid),"validity_reason":validity_reason,
                      "geometry_json_chars":vertex_count,"bounds_lonlat":bbox,
                      "area_km2_estimated":round(area/1e6,2) if area else None,
                      "data_source_year":props.get("YEAR"),"source_date":props.get("SOURCEDATE"),
                      "validation_date":props.get("VAL_DATE"),
                      "model_admission_approved":False})
        ft["properties"]={"ba":ba,"source_oid":oid,"source_name":name,
                          "historical_geometry_approved":False,
                          "source_year":props.get("YEAR")}
        features.append(ft)
    if len(features)!=4 or {x["ba_candidate"] for x in audit}!=set(IDS):
        raise ValueError("Exactly four expected features required")
    return {"type":"FeatureCollection","features":features},audit,raw,url

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="outputs/e1_national_geometries")
    a=p.parse_args()
    geo,audit,raw,url=fetch_candidate_polygons()
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    formatted=json.dumps(geo,separators=(",",":"),ensure_ascii=False)+"\n"
    (out/"four_ba_candidate_UNAPPROVED.geojson").write_text(formatted)
    (out/"geometry_audit.json").write_text(json.dumps({
         "source_request_url":url,"raw_response_sha256":hashlib.sha256(raw).hexdigest(),
         "extracted_geojson_sha256":hashlib.sha256(formatted.encode()).hexdigest(),
         "features":audit,"codes":[x["ba_candidate"] for x in audit],
         "geometry_count":len(audit),
         "all_original_geometries_valid":all(x["is_valid"] for x in audit),
         "invalid_ba_codes":[x["ba_candidate"] for x in audit if not x["is_valid"]],
         "historical_vintage_approved":False,
         "crosswalk_manually_reviewed":False,"exposure_weights_authorized":False,
         "no_training_or_ERA5_join":True},indent=2)+"\n")
    print("POLYGON_CANDIDATE_AUDIT",json.dumps(audit))
    print("GEOGRAPHY_APPROVED_FOR_MODEL",False)
    if not all(x["is_valid"] for x in audit):
        print("SOURCE_TOPOLOGY_GATE_FAIL: unaltered polygon GeoJSON and detailed error report saved")
if __name__=="__main__":main()
