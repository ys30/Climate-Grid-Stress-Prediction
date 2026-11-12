"""Discover candidate historical HIFLD control-area polygons; do NOT auto-approve BA mapping.

Source is a 2025 vintage snapshot, not a certified BA territory for 2020–2025.
"""
import argparse,hashlib,json,re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

SERVICE="https://services.arcgis.com/uUvqNMGPm7axC2dD/arcgis/rest/services/Control_Areas_OR/FeatureServer/0/query"
CANDIDATE_PATTERNS={
    "AZPS":re.compile(r"ARIZONA PUBLIC SERVICE",re.I),
    "BPAT":re.compile(r"BONNEVILLE POWER",re.I),
    "CISO":re.compile(r"CALIFORNIA INDEPENDENT SYSTEM OPERATOR|CALIFORNIA ISO",re.I),
    "SRP":re.compile(r"SALT RIVER PROJECT",re.I),
}

def candidate_names(feature_collection):
    if feature_collection.get("type")!="FeatureCollection":raise ValueError("Expected ArcGIS GeoJSON features")
    found=[]
    for feat in feature_collection.get("features",[]):
        p=feat.get("properties") or {}
        name=str(p.get("NAME") or "")
        matches=[ba for ba,pattern in CANDIDATE_PATTERNS.items() if pattern.search(name)]
        if matches:
            found.append({"candidate_bas":matches,"source_name":name,
                          "source_id":p.get("ID"),"source_year":p.get("YEAR"),
                          "source_date":p.get("SOURCEDATE"),
                          "geometry_type":(feat.get("geometry") or {}).get("type"),
                          "no_auto_mapping":True})
    return found

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="outputs/e1_geography_discovery")
    a=p.parse_args()
    params={"where":"1=1","outFields":"ID,NAME,SOURCE,SOURCEDATE,VAL_DATE,YEAR",
            "returnGeometry":"true","outSR":"4326","f":"geojson"}
    url=SERVICE+"?"+urlencode(params)
    with urlopen(Request(url,headers={"User-Agent":"ClimateGridC2/0.1"}),timeout=90) as r:
        raw=r.read()
    doc=json.loads(raw)
    if "error" in doc:raise ValueError("HIFLD query error: "+str(doc["error"]))
    matches=candidate_names(doc)
    found_bas=sorted({ba for m in matches for ba in m["candidate_bas"]})
    missing_bas=sorted(set(CANDIDATE_PATTERNS)-set(found_bas))
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    report={"source_service":SERVICE,"requested_query":params,
      "source_file_sha256":hashlib.sha256(raw).hexdigest(),"source_bytes":len(raw),
      "source_vintage":"2025 HIFLD Control_Areas_OR",
      "features_returned":len(doc.get("features",[])),
      "candidate_matches":matches,
      "candidate_ba_codes_found":found_bas,
      "candidate_ba_codes_missing":missing_bas,
      "all_four_BA_geometries_available":len(missing_bas)==0,
      "bau_code_mapping_approved":False,
      "weather_exposure_approved":False,
      "historical_boundary_stationarity_assumed":False,
      "note":"Candidate area shapes ONLY; no manual identity/vintage review completed."}
    (out/"geometry_candidate_review.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
