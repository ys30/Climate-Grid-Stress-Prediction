"""True ARCO ERA5 A/B/C proxy temperature comparison at fixed real hourly UTC.

A 2018 HIFLD: polygon area, B 2024 TIGER county: polygon area,
C Census CO-EST2025 April-2020 county population estimate-base allocated uniformly within county x TIGER cells.
Three provisional weather proxies, none approved for EIA BA load models.
"""
import argparse,csv,hashlib,json
from pathlib import Path
from src.c2_era5_full_grid_one_hour import load_exploratory_weights,compute_from_loaded_grid
from src.c2_era5_public_probe import STORE,VARIABLE
from src.c2_era5_AB_sevenday_sensitivity import A_SHA,B_SHA,BAS

SAMPLES=("2023-01-15T12:00:00Z","2023-07-01T12:00:00Z",
         "2025-01-15T12:00:00Z","2025-07-01T12:00:00Z")

def threeway_source(groups,when,ds):
    import numpy as np
    from datetime import datetime
    stamp=datetime.fromisoformat(when.replace("Z","+00:00"))
    if stamp.minute or stamp.second or stamp.utcoffset().total_seconds()!=0:
        raise ValueError("Aligned UTC hour required")
    var=ds[VARIABLE]
    timekey="time" if "time" in var.dims else "valid_time"
    grid=var.sel({timekey:np.datetime64(stamp.replace(tzinfo=None),"ns")})
    all_cells=[c for ba in groups.values() for c in ba]
    latmin=min(x[0] for x in all_cells);latmax=max(x[0] for x in all_cells)
    lonmin=min(x[1] for x in all_cells);lonmax=max(x[1] for x in all_cells)
    descending=float(grid.latitude.values[0])>float(grid.latitude.values[-1])
    bounded=grid.sel(latitude=slice(latmax,latmin) if descending else slice(latmin,latmax),
                     longitude=slice(lonmin,lonmax))
    if bounded.size<1 or bounded.size>20000:
        raise ValueError("Source ERA5 bounding grid size exceeds safe range")
    results=compute_from_loaded_grid(bounded.load(),groups)
    by_key={r["ba"]:r for r in results}
    if set(by_key)!={tag+"_"+ba for tag in "ABC" for ba in BAS}:
        raise ValueError("Three proxy weather estimands for four BA missing")
    rows=[]
    for ba in BAS:
        a=by_key["A_"+ba]["weighted_temperature_celsius"]
        b=by_key["B_"+ba]["weighted_temperature_celsius"]
        c=by_key["C_"+ba]["weighted_temperature_celsius"]
        rows.append({"utc_timestamp":when,"ba":ba,
            "A_HIFLD2018_area_c":a,"B_TIGER2024_area_c":b,
            "C_Census2020_estimate_base_county_population_c":c,
            "B_minus_A_c":round(b-a,6),"C_minus_A_c":round(c-a,6),
            "C_minus_B_c":round(c-b,6),
            "ERA5_cells_A":by_key["A_"+ba]["grid_cells"],
            "ERA5_cells_B":by_key["B_"+ba]["grid_cells"],
            "ERA5_cells_C":by_key["C_"+ba]["grid_cells"],
            "census_pop_proxy_is_customer_count":False,
            "historical_BA_geography_approved":False,
            "model_training_permitted":False})
    return rows

def run(a_path,b_path,c_path,provenance_path,out):
    hashes={"A":hashlib.sha256(Path(a_path).read_bytes()).hexdigest(),
            "B":hashlib.sha256(Path(b_path).read_bytes()).hexdigest(),
            "C":hashlib.sha256(Path(c_path).read_bytes()).hexdigest()}
    if hashes["A"]!=A_SHA or hashes["B"]!=B_SHA:
        raise ValueError("Frozen source A/B candidate weight digest mismatch")
    csource=json.loads(Path(provenance_path).read_text())
    if csource.get("census2020_variable")!="ESTIMATESBASE2020" or csource.get("population_is_original_decennial_PL_P1_001N") is not False:
        raise ValueError("Proxy C must be explicitly labeled official Census 2025-vintage 2020 population estimate base")
    if hashes["C"]!=csource["weight_csv_sha256"]:
        raise ValueError("Population source C weights not provenance pinned")
    if (csource.get("model_training_permitted") is not False or
        csource.get("actual_customers_or_load_distribution_observed") is not False or
        csource.get("county_proxy_geography_approved") is not False):
        raise ValueError("Source C falsely certified")
    groups={}
    for tag,filename in (("A",a_path),("B",b_path),("C",c_path)):
        original=load_exploratory_weights(filename)
        groups.update({tag+"_"+ba:original[ba] for ba in BAS})
    import xarray as xr
    ds=xr.open_zarr(STORE,chunks=None,storage_options={"token":"anon"})
    observations=[]
    for when in SAMPLES:
        current=threeway_source(groups,when,ds)
        observations.extend(current)
        print("REAL_ERA5_THREE_PROXY_UTC",json.dumps({"when":when,"records":current}),flush=True)
    if len(observations)!=16:raise ValueError("Incomplete 4x4 BA-time source set")
    output=Path(out);output.mkdir(parents=True,exist_ok=True)
    file=output/"REAL_ERA5_FOUR_HOURS_THREE_GEOGRAPHY_PROXIES_UNAPPROVED.csv"
    with file.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(observations[0]));w.writeheader();w.writerows(observations)
    info={"actual_real_ERA5_BA_hours":16,"sample_UTC_times":list(SAMPLES),
       "source_weight_SHA256":hashes,
       "C_population_reference_year":2020,
       "C_population_source_vintage":"CO-EST2025 March 2026",
       "C_population_variable":"ESTIMATESBASE2020",
       "C_population_is_PL_2020_decennial_count":False,
       "B_and_C_TIGER_county_geometry_year":2024,
       "C_population_density_uniform_within_county":True,
       "population_weight_is_actual_electric_customers":False,
       "historical_BA_geography_approved":False,
       "model_training_permitted":False,"climate_attribution_performed":False}
    (output/"REAL_ERA5_THREE_GEO_PROXY_PROVENANCE.json").write_text(json.dumps(info,indent=2)+"\n")
    print("REAL_ERA5_THREE_PROXY_SOURCE_AUDIT",json.dumps(info),flush=True)
    return info

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--A-hifld",required=True)
    p.add_argument("--B-county",required=True)
    p.add_argument("--C-population",required=True)
    p.add_argument("--C-source-manifest",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    run(args.A_hifld,args.B_county,args.C_population,args.C_source_manifest,args.out)
if __name__=="__main__":main()
