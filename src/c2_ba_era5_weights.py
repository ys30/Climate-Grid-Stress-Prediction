"""ERA5 0.25-degree cell-area weights from *supplied, provenance-audited* BA polygons.

No embedded or invented BA footprints. Input GeoJSON must have explicit source
vintage and independently reviewed BA-code crosswalk. This is NOT load weighting.
"""
import argparse,csv,hashlib,json,math
from collections import defaultdict
from pathlib import Path

BAS=("AZPS","BPAT","CISO","SRP")
RES=0.25

def cell_centers(minimum,maximum):
    lo=math.ceil((minimum-1e-10)/RES)*RES
    hi=math.floor((maximum+1e-10)/RES)*RES
    n=max(0,int(round((hi-lo)/RES))+1)
    return [round(lo+i*RES,6) for i in range(n)]

def validate_meta(meta,geom_bytes):
    required=("source_url","source_vintage","license","geometry_sha256","code_crosswalk_reviewed")
    if any(not meta.get(k) for k in required):
        raise ValueError("Missing required provenance metadata or unreviewed BA code crosswalk")
    if hashlib.sha256(geom_bytes).hexdigest()!=meta["geometry_sha256"]:
        raise ValueError("BA geometry SHA256 does not match supplied GeoJSON")
    if meta["code_crosswalk_reviewed"] is not True:
        raise ValueError("BA crosswalk explicitly must be reviewed")
    if meta.get("geometry_is_illustrative",False):
        raise ValueError("Illustrative boundaries cannot be admitted")
    # Historic polygon vintage, AZPS/SRP overlap, and prior invalid geometry
    # require separate scientific sign-off; exploratory weights use another CLI.
    for gate in ("historical_vintage_reviewed","spatial_overlap_reviewed",
                 "topology_repair_reviewed","exposure_interpretation_reviewed"):
        if meta.get(gate) is not True:
            raise ValueError("BA geography model-use gate not approved: "+gate)
    for evidence in ("historical_vintage_review_reference",
                     "spatial_overlap_review_reference",
                     "topology_repair_review_reference",
                     "exposure_interpretation_review_reference"):
        ref=meta.get(evidence)
        if not isinstance(ref,str) or not ref.strip():
            raise ValueError("BA geography review evidence missing: "+evidence)

def build_weights(geojson,meta):
    from shapely.geometry import shape,box
    from shapely.ops import transform
    from pyproj import Transformer
    raw=json.dumps(geojson)
    to_area=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    features=geojson.get("features",[])
    polygons=defaultdict(list)
    for feat in features:
        ba=feat.get("properties",{}).get("ba")
        if ba not in BAS:raise ValueError(f"Unrecognized or unmapped BA ID: {ba}")
        geom=shape(feat["geometry"])
        if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("Invalid or unsupported BA polygon geometry")
        if geom.bounds[0]<-180 or geom.bounds[2]>0 or geom.bounds[1]<20 or geom.bounds[3]>55:
            raise ValueError("Polygon outside validated contiguous western-US study domain")
        polygons[ba].append(geom)
    if set(polygons)!=set(BAS):raise ValueError("Exactly four explicit BA geometries required")
    result=[];summaries=[]
    for ba in BAS:
        from shapely.ops import unary_union
        poly=unary_union(polygons[ba])
        projected_poly=transform(to_area,poly)
        minlon,minlat,maxlon,maxlat=poly.bounds
        weighted=[]
        for lat in cell_centers(minlat-RES/2,maxlat+RES/2):
            if not -90<=lat<=90:continue
            for lon in cell_centers(minlon-RES/2,maxlon+RES/2):
                if not -180<=lon<=180:continue
                cell=box(lon-RES/2,lat-RES/2,lon+RES/2,lat+RES/2)
                if not poly.intersects(cell):continue
                # Clip in the valid geographic CRS BEFORE projecting; a highly
                # detailed polygon can acquire ring conflicts under projection.
                # This is geometric integration, not a repair to the raw source.
                clipped=poly.intersection(cell)
                area=transform(to_area,clipped).area
                if area>0:weighted.append((lat,lon,area))
        total=sum(a for _,_,a in weighted)
        if not total:raise ValueError(f"No intersected ERA5 cells for {ba}")
        for lat,lon,area in weighted:
            result.append({"ba":ba,"latitude":lat,"longitude_0_360":round(lon%360,6),
                           "intersection_area_m2":round(area,3),"weight":area/total,
                           "exposure_method":"ba_area_weighted_era5"})
        summaries.append({"ba":ba,"intersected_cells":len(weighted),
                          "polygon_projected_area_m2":round(projected_poly.area,3),
                          "weight_sum":sum(a/total for _,_,a in weighted)})
    return result,summaries

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--geometry",required=True)
    p.add_argument("--metadata",required=True)
    p.add_argument("--out",default="outputs/e1_weights")
    a=p.parse_args()
    raw=Path(a.geometry).read_bytes()
    meta=json.loads(Path(a.metadata).read_text())
    validate_meta(meta,raw)
    rows,summary=build_weights(json.loads(raw),meta)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    with (out/"ba_era5_grid_weights.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)
    audit={"source":meta,"geography":summary,"grid_resolution_degrees":RES,
           "projection":"EPSG:5070 equal-area","weighting":"polygon-overlap area only, NOT demand-weighted",
           "no_weather_fetched":True,"not_a_model_result":True}
    (out/"weights_manifest.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
