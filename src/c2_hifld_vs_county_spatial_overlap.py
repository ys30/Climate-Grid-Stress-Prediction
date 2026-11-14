"""Geographic support sensitivity: EIA-861 Census county union versus HIFLD.

Compare physically meaningful geometric overlap *before* examining hourly
temperature. Both unapproved masks, no weather/demand fitted and no admission.
"""
import argparse,csv,json,hashlib
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
BAS=("AZPS","BPAT","CISO","SRP")

def compare(hifld_geo,census_geo):
    polys={}
    for name,fc in [("HIFLD2018",hifld_geo),("CENSUS2024",census_geo)]:
        layer={}
        for feature in fc.get("features",[]):
            props=feature.get("properties",{})
            ba=props.get("ba")
            if ba not in BAS or ba in layer:
                raise ValueError("Four BA codes must be unique and recognized")
            if props.get("geometry_approved") is not False or props.get("source_approved") is not False:
                raise ValueError("Never accept approved status in exploratory mask comparison")
            polygon=shape(feature["geometry"])
            if not polygon.is_valid or polygon.is_empty:
                raise ValueError("Invalid source mask "+name+" "+ba)
            layer[ba]=polygon
        if set(layer)!=set(BAS):raise ValueError("Missing BA mask")
        polys[name]=layer
    equal=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    rows=[]
    for ba in BAS:
        a=polys["HIFLD2018"][ba]
        b=polys["CENSUS2024"][ba]
        # For common/intersection area, perform lon/lat clipping first to
        # avoid projected invalid-ring problems, just like ERA5 cell weights.
        common=a.intersection(b)
        intersection=transform(equal,common).area if not common.is_empty else 0.
        area_a=transform(equal,a).area;area_b=transform(equal,b).area
        if min(area_a,area_b)<=0 or intersection<0:
            raise ValueError("Empty BA mask projected area")
        union_area=area_a+area_b-intersection
        if union_area<=0 or intersection>min(area_a,area_b)*(1+1e-7):
            raise ValueError("Projected BA mask area accounting invalid")
        rows.append({"ba":ba,
          "HIFLD2018_area_km2":round(area_a/1e6,3),
          "Census2024_county_area_km2":round(area_b/1e6,3),
          "intersection_km2":round(intersection/1e6,3),
          "spatial_jaccard_intersection_over_union":round(intersection/union_area,7),
          "hifld_area_covered_by_county_fraction":round(intersection/area_a,7),
          "county_area_covered_by_hifld_fraction":round(intersection/area_b,7),
          "HIFLD2020_2025_approved":False,
          "Census2020_2025_approved":False,
          "model_ready":False})
    return rows

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--hifld",required=True)
    p.add_argument("--county",required=True)
    p.add_argument("--out",default="outputs/e1_spatial_geometry_sensitivity")
    args=p.parse_args()
    a=Path(args.hifld).read_bytes();b=Path(args.county).read_bytes()
    rows=compare(json.loads(a),json.loads(b))
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    with (out/"four_BA_HIFLD_Census_source_mask_overlap_UNAPPROVED.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    meta={"hifld_candidate_geojson_sha256":hashlib.sha256(a).hexdigest(),
          "TIGER_county_proxy_geojson_sha256":hashlib.sha256(b).hexdigest(),
          "equal_area_projection":"EPSG:5070",
          "all_four_geometries_valid":True,
          "actual_hourly_ERA5_queried":False,
          "approved_for_BA_demand_weather_model":False,
          "note":"Equal-area geometric overlap only; no operating territory inference"}
    (out/"BA_mask_spatial_sensitivity_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("REAL_MASK_SPATIAL_SENSITIVITY",json.dumps({"BA_masks":rows,**meta}),flush=True)
if __name__=="__main__":main()
