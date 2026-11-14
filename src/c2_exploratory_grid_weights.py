"""Exploratory four-BA polygon overlaps and 0.25-degree ERA5 intersection weights.

All outputs are explicitly UNAPPROVED. Never use these candidate geometry
weights as validated BA weather exposures or permit model training.
"""
import argparse,csv,json,hashlib
from pathlib import Path
from itertools import combinations
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
from src.c2_ba_era5_weights import build_weights

BAS={"AZPS","BPAT","CISO","SRP"}

def calculate(geo):
    features=geo.get("features",[])
    if len(features)!=4:raise ValueError("Expected four candidate polygons")
    polys={}
    for feature in features:
        props=feature.get("properties") or {}
        ba=props.get("ba")
        if ba not in BAS or ba in polys:raise ValueError("Duplicate/unmapped BA")
        if props.get("geometry_approved") is not False or props.get("source_approved") is not False:
            raise ValueError("Input must remain explicitly UNAPPROVED")
        poly=shape(feature["geometry"])
        if poly.is_empty or not poly.is_valid:raise ValueError("Only valid derived polygon candidates")
        polys[ba]=poly
    if set(polys)!=BAS:raise ValueError("BA coverage mismatch")
    project=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    areas={ba:transform(project,p).area for ba,p in polys.items()}
    overlaps=[]
    for a,b in combinations(sorted(BAS),2):
        intersection=polys[a].intersection(polys[b])
        area=transform(project,intersection).area if not intersection.is_empty else 0.
        overlaps.append({"ba_a":a,"ba_b":b,"intersection_km2":round(area/1e6,3),
          "fraction_of_a":round(area/areas[a],7),"fraction_of_b":round(area/areas[b],7)})
    weights,summary=build_weights(geo,{})
    for row in weights:
        row["research_status"]="exploratory_unapproved_geometry"
    for s in summary:
        s["research_status"]="exploratory_unapproved_geometry"
    return weights,summary,overlaps

def dump(path,rows,cols):
    with Path(path).open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--candidate-geojson",required=True)
    p.add_argument("--source-audit",required=True)
    p.add_argument("--out",default="outputs/e1_provisional_weights")
    args=p.parse_args()
    raw=Path(args.candidate_geojson).read_bytes()
    audit=json.loads(Path(args.source_audit).read_text())
    if audit.get("automatic_model_approval") is not False:
        raise ValueError("Repair candidate source permission contract missing")
    geo=json.loads(raw)
    weights,summary,overlaps=calculate(geo)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    dump(out/"exploratory_BA_grid_weights_UNAPPROVED.csv",weights,
         ["ba","latitude","longitude_0_360","intersection_area_m2","weight",
          "exposure_method","research_status"])
    dump(out/"overlap_sensitivity.csv",overlaps,
         ["ba_a","ba_b","intersection_km2","fraction_of_a","fraction_of_b"])
    report={"candidate_geometry_sha256":hashlib.sha256(raw).hexdigest(),
      "source_original_geometry_sha256":audit["source_geojson_sha256"],
      "grid_resolution_degrees":0.25,"equal_area_crs":"EPSG:5070",
      "four_BA_weight_quality":summary,"BA_pairwise_overlap":overlaps,
      "candidate_geography_approved":False,"weights_admitted_for_model":False,
      "weather_data_fetched":False,"weather_demand_joined":False,
      "future_prediction_performed":False,
      "interpretation":"Sensitivity-only weights; vintage, overlapping zones and make_valid effects pending review"}
    (out/"exploratory_spatial_weight_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print("EXPLORATORY_SPATIAL_AUDIT",json.dumps(report))
if __name__=="__main__":main()
