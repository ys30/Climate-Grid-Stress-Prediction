"""Empirical sensitivity A (HIFLD 2018) versus B (Census TIGER 2024 counties).

Both geographic masks are UNAPPROVED. Calculate full polygon-cell overlap
weights then obtain genuine ARCO ERA5 2m temperatures at identical UTC hour.
Not EIA-930 training data and not a valid operational BA spatial estimand.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from src.c2_ba_era5_weights import build_weights
from src.c2_era5_full_grid_one_hour import load_exploratory_weights,fetch_real_hour

BAS={"AZPS","BPAT","CISO","SRP"}
def make_proxy_weights(geo,source_manifest):
    from shapely.geometry import shape
    feats=geo.get("features",[])
    if len(feats)!=4:raise ValueError("Exactly four BA experimental county features required")
    if {x["properties"]["ba"] for x in feats}!=BAS:
        raise ValueError("Four BA county feature codes must match")
    for feature in feats:
        props=feature["properties"]
        if props.get("geometry_approved") is not False or props.get("source_approved") is not False:
            raise ValueError("2024 Census county union must remain UNAPPROVED")
        if not shape(feature["geometry"]).is_valid:raise ValueError("No invalid Census union polygons")
    if source_manifest.get("TIGER_vintage")!=2024 or source_manifest.get("county_proxy_geography_approved") is not False:
        raise ValueError("Unexpected county source vintage or approval")
    # build_weights is geometric, not a scientific admission; do NOT call validate_meta.
    weights,summary=build_weights(geo,{})
    for item in weights:
        item["research_status"]="exploratory_unapproved_geometry"
    if not all(abs(z["weight_sum"]-1)<1e-8 for z in summary):
        raise ValueError("Area weight not normalized")
    return weights,summary

def difference(a,b):
    old={x["ba"]:x for x in a};new={x["ba"]:x for x in b}
    if set(old)!=BAS or set(new)!=BAS:raise ValueError("Four BAs required")
    return [{"ba":ba,
             "hifld2018_candidate_c":old[ba]["weighted_temperature_celsius"],
             "tiger2024_eia861_county_proxy_c":new[ba]["weighted_temperature_celsius"],
             "county_minus_hifld_c":round(
                 new[ba]["weighted_temperature_celsius"]-
                 old[ba]["weighted_temperature_celsius"],6),
             "hifld_cell_count":old[ba]["grid_cells"],
             "county_cell_count":new[ba]["grid_cells"],
             "historically_approved":False,"training_eligible":False}
            for ba in sorted(BAS)]

def run(geom_path,geom_manifest,old_weight_path,time,out_dir):
    geo_bytes=Path(geom_path).read_bytes()
    audit=json.loads(Path(geom_manifest).read_text())
    if hashlib.sha256(geo_bytes).hexdigest()!=audit["output_geojson_sha256"]:
        raise ValueError("TIGER 2024 candidate geometry digest does not match source artifact")
    geo=json.loads(geo_bytes)
    weights,summary=make_proxy_weights(geo,audit)
    output=Path(out_dir);output.mkdir(parents=True,exist_ok=True)
    bweights=output/"C2_TIGER2024_EIA861_COUNTY_ERA5_AREA_WEIGHTS_UNAPPROVED.csv"
    with bweights.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(weights[0]))
        writer.writeheader();writer.writerows(weights)
    # Use the exact same instant, public ARCO ERA5 source and area estimator.
    old=load_exploratory_weights(old_weight_path)
    new=load_exploratory_weights(bweights)
    a_real,a_meta=fetch_real_hour(old,time)
    b_real,b_meta=fetch_real_hour(new,time)
    comparison=difference(a_real,b_real)
    with (output/"REAL_ERA5_2023_HIFLD_VS_CENSUS_COUNTY_DIFFERENCES_UNAPPROVED.csv").open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
    report={"UTC_time":time,"real_ERA5_data_used":True,
      "source":"public ARCO ERA5 0.25 degree 2m temperature",
      "source_same_UTC_timestamp":a_meta["utc_timestamp"]==b_meta["utc_timestamp"],
      "TIGER_2024_source_zip_sha256":audit["TIGER_download_ZIP_sha256"],
      "Census_county_source_geometry_sha256":audit["output_geojson_sha256"],
      "county_grid_weight_file_sha256":hashlib.sha256(bweights.read_bytes()).hexdigest(),
      "hifld_candidate_weight_file_sha256":hashlib.sha256(Path(old_weight_path).read_bytes()).hexdigest(),
      "TIGER_vintage":2024,
      "HIFLD_vintage":2018,
      "BA_county_proxy_weight_summaries":summary,
      "comparison":comparison,
      "historically_approved":False,
      "year_specific_geography_admitted":False,
      "EIA_weather_load_models_trained":False,
      "climate_attribution_performed":False,
      "limitations":"Weather differences for two nonvalidated spatial proxy definitions; 2024 county boundaries on a 2023 example, NOT approved for BA demand modeling."}
    (output/"REAL_CENSUS_VS_HIFLD_ERA5_SPATIAL_SENSITIVITY_MANIFEST.json").write_text(json.dumps(report,indent=2)+"\n")
    print("REAL_HIFLD_VS_CENSUS_ERA5_SENSITIVITY",json.dumps(report),flush=True)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--county-geometry",required=True)
    p.add_argument("--county-manifest",required=True)
    p.add_argument("--hifld-weights",required=True)
    p.add_argument("--time",default="2023-07-01T12:00:00Z")
    p.add_argument("--out",default="outputs/e1_county_hifld_compare")
    args=p.parse_args()
    run(args.county_geometry,args.county_manifest,args.hifld_weights,args.time,args.out)
if __name__=="__main__":main()
