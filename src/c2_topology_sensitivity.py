"""Explore, NEVER approve, topology repair effects on four national BA source shapes.

Source GeoJSON is immutable. This script saves Shapely make_valid derivations
and their geometry-type/area changes for scientific review; it never updates
geometry provenance approval or trains models.
"""
import argparse,hashlib,json
from pathlib import Path

def assess(raw_geojson):
    from shapely.geometry import shape,mapping
    from shapely.validation import explain_validity
    from shapely import make_valid
    from shapely.ops import transform
    from pyproj import Transformer
    project=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    reviewed=[];derived=[]
    for feat in raw_geojson["features"]:
        ba=feat["properties"]["ba"]
        original=shape(feat["geometry"])
        repaired=make_valid(original)
        # Some make_valid outputs include LineStrings or points. Drop them
        # ONLY from the exploratory polygon candidate; disclose their existence.
        polygons=[]
        def collect(g):
            if g.geom_type=="Polygon":polygons.append(g)
            elif hasattr(g,"geoms"):
                for sub in g.geoms:collect(sub)
        collect(repaired)
        from shapely.ops import unary_union
        polygonal=unary_union(polygons) if polygons else None
        source_projected_area=transform(project,original).area
        derived_area=transform(project,polygonal).area if polygonal else 0.
        change=abs(derived_area-source_projected_area)/max(source_projected_area,1.)
        row={"ba":ba,"original_valid":bool(original.is_valid),
            "original_issue":explain_validity(original),
            "original_type":original.geom_type,
            "make_valid_type":repaired.geom_type,
            "polygon_component_count":len(polygons),
            "polygon_only_valid":bool(polygonal and polygonal.is_valid),
            "nonpolygon_parts_present":repaired.geom_type=="GeometryCollection",
            "original_raw_area_km2_untrusted":round(source_projected_area/1e6,3),
            "candidate_polygon_area_km2":round(derived_area/1e6,3),
            "area_change_fraction_vs_untrusted_original":round(change,8),
            "geom_repair_approved":False,
            "historical_use_approved":False}
        reviewed.append(row)
        if polygonal is not None:
            derived.append({"type":"Feature","properties":{"ba":ba,
                "derived_via":"shapely.make_valid polygonal parts only",
                "geometry_approved":False,"source_approved":False},
                "geometry":mapping(polygonal)})
    return reviewed,{"type":"FeatureCollection","features":derived}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True)
    p.add_argument("--out",default="outputs/e1_topology")
    a=p.parse_args()
    raw=Path(a.source).read_bytes()
    geo=json.loads(raw)
    if len(geo.get("features",[]))!=4:raise ValueError("Require exactly four national candidate features")
    report,repaired=assess(geo)
    if {x["ba"] for x in report}!={"AZPS","BPAT","CISO","SRP"}:
        raise ValueError("Expected four BA candidates")
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    (out/"candidate_geometric_repairs_UNAPPROVED.geojson").write_text(json.dumps(repaired))
    manifest={"source_geojson_sha256":hashlib.sha256(raw).hexdigest(),
              "repair_engine":"Shapely make_valid, polygonal components",
              "comparisons":report,
              "all_candidate_polygons_valid":all(x["polygon_only_valid"] for x in report),
              "automatic_model_approval":False,"model_join_executed":False,
              "note":"Original invalid geometry areas are noncanonical: relative changes are diagnostics only."}
    (out/"topology_sensitivity_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("TOPOLOGY_SENSITIVITY",json.dumps(manifest))
if __name__=="__main__":main()
