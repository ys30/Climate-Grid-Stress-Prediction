"""C2 E1 proxy C: Census Vintage 2025 estimated April 2020 population-weighted ERA5 area support.

Official Census Population Estimates Program ESTIMATESBASE2020 county population assigned at uniform
within-county density to 2024 TIGER county polygon x ERA5 0.25-deg intersections.
EIA861 BA-county membership establishes an *approximate* geographic proxy.
NO actual customers, NO demand weights, NO approved historic BA geography.
"""
import argparse,csv,hashlib,io,json,math,urllib.request
from collections import defaultdict
from pathlib import Path

from src.c2_census_tiger_county_proxy import (
    BAS,CENSUS_URL,source_memberships,county_geometries)
from src.c2_ba_era5_weights import RES,cell_centers

POP_SOURCE="https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv"
TIGER_SHA="04e668d3502757c837c13444730547cd967f28a2c49aeffb873d1792ab2cb97b"
EIA861_FIPS_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"

def parse_population_estimates_csv(raw,wanted):
    # ESTIMATESBASE2020 is Census's April 1, 2020 population *estimate base*,
    # NOT exact PL94-171 P1_001N counts or POPESTIMATE2020 (July 1).
    # The official CO-EST CSV may contain Windows-1252 county names (e.g. ñ).
    # Prefer UTF-8 when valid; decode all bytes reversibly with cp1252 only
    # when the published source is not valid UTF-8. Numeric fields stay strict.
    try:
        text=raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text=raw.decode("cp1252")
    reader=csv.DictReader(io.StringIO(text))
    needed={"SUMLEV","STATE","COUNTY","ESTIMATESBASE2020"}
    if not needed.issubset(reader.fieldnames or []):
        raise ValueError("Missing official Census county estimate fields")
    population={}
    for row in reader:
        if str(row["SUMLEV"]).strip().zfill(3)!="050":continue
        state=str(row["STATE"]).strip().zfill(2)
        county=str(row["COUNTY"]).strip().zfill(3)
        fips=state+county
        if fips not in wanted:continue
        if fips in population:raise ValueError("Duplicate official Census county FIPS")
        val=str(row["ESTIMATESBASE2020"]).strip()
        if not val.isdigit():raise ValueError("Missing/noninteger April 2020 Census population estimate base")
        population[fips]=int(val)
    missing=sorted(set(wanted)-set(population))
    if missing:raise ValueError("Census official estimated population missing county FIPS: "+str(missing[:15]))
    return {f:population[f] for f in sorted(wanted)}

def fetch_populations(fips):
    req=urllib.request.Request(POP_SOURCE,headers={"User-Agent":"C2-ERA5-ScientificSourceAudit/1.0"})
    with urllib.request.urlopen(req,timeout=90) as response:
        if response.status!=200:raise ValueError("Official Census bulk file HTTP status not 200")
        raw=response.read()
    if len(raw)<10000 or not raw[:100].lstrip().startswith((b"SUMLEV",b"REGION")):
        raise ValueError("Official Census population bulk response invalid")
    populations=parse_population_estimates_csv(raw,set(fips))
    digest=hashlib.sha256(raw).hexdigest()
    meta={"dataset":"CO-EST2025-alldata","source_url":POP_SOURCE,
          "source_file_sha256":digest,"download_bytes":len(raw),
          "population_variable":"ESTIMATESBASE2020",
          "population_variable_description":"April 1 2020 resident population estimate base (NOT PL94-171 actual decennial count)",
          "county_records_used":len(populations)}
    print("CENSUS_OFFICIAL_2025_VINTAGE_2020_BASE",json.dumps(meta),flush=True)
    return populations,[meta]

def county_population_overlap_weights(members,geometries,populations):
    from shapely.geometry import box
    from shapely.ops import transform
    from pyproj import Transformer
    to_area=Transformer.from_crs("EPSG:4326","EPSG:5070",always_xy=True).transform
    if set(members)!=set(BAS):raise ValueError("Four BA county memberships required")
    required=set().union(*members.values())
    if required-set(geometries) or required-set(populations):
        raise ValueError("Some source county geometries or population counts missing")
    precomputed={}
    for fips in sorted(required):
        polygon=geometries[fips]
        if not polygon.is_valid or polygon.is_empty:
            raise ValueError("Invalid full TIGER source county polygon")
        area=transform(to_area,polygon).area
        if area<=0:raise ValueError("Zero county area")
        n=populations[fips]
        if not isinstance(n,int) or n<0:raise ValueError("Negative or invalid 2020 census population")
        precomputed[fips]=(polygon,area,n)
    rows=[];summaries=[]
    for ba in BAS:
        cell_masses=defaultdict(float)
        total_population=sum(precomputed[f][2] for f in members[ba])
        if total_population<=0:raise ValueError("BA county population source total zero")
        for fips in sorted(members[ba]):
            polygon,county_area,pop=precomputed[fips]
            if pop==0:continue
            west,south,east,north=polygon.bounds
            for lat in cell_centers(south-RES/2,north+RES/2):
                for lon in cell_centers(west-RES/2,east+RES/2):
                    if not (-180<=lon<=180 and 20<=lat<=55):continue
                    cell=box(lon-RES/2,lat-RES/2,lon+RES/2,lat+RES/2)
                    if not polygon.intersects(cell):continue
                    intersection=polygon.intersection(cell)
                    if intersection.is_empty:continue
                    area=transform(to_area,intersection).area
                    if area>0:cell_masses[(lat,round(lon%360,6))]+=pop*area/county_area
        mass=sum(cell_masses.values())
        if mass<=0 or abs(mass-total_population)/total_population>0.002:
            raise ValueError("Census county population was lost in ERA5 grid intersections")
        for (lat,lon),value in sorted(cell_masses.items()):
            rows.append({"ba":ba,"latitude":lat,"longitude_0_360":lon,
                 "weight":value/mass,
                 "population_mass_in_cell_proxy":round(value,5),
                 "exposure_method":"2020_Census_estimates_base_county_population_uniform_within_county_UNAPPROVED",
                 "research_status":"exploratory_unapproved_geometry"})
        sums=sum(r["weight"] for r in rows if r["ba"]==ba)
        if abs(sums-1)>1e-9:raise ValueError("Population weights not normalized")
        summaries.append({"ba":ba,"member_counties":len(members[ba]),
            "2020_census_estimates_base_county_population":total_population,
            "area_allocated_population":round(mass,3),
            "ERA5_cells":len(cell_masses),"weight_sum":sums,
            "approved_for_utility_customer_exposure":False})
    return rows,summaries

def run(membership_file,outdir):
    p=Path(outdir);p.mkdir(parents=True,exist_ok=True)
    source=Path(membership_file).read_bytes()
    if hashlib.sha256(source).hexdigest()!=EIA861_FIPS_SHA:
        raise ValueError("EIA861 annual county membership source SHA256 drift")
    members=source_memberships(membership_file,year=2024)
    wanted=set().union(*members.values())
    pop,pop_sources=fetch_populations(wanted)
    request=urllib.request.Request(CENSUS_URL,headers={"User-Agent":"C2-ERA5-ScientificSourceAudit/1.0"})
    with urllib.request.urlopen(request,timeout=180) as response:raw=response.read()
    if hashlib.sha256(raw).hexdigest()!=TIGER_SHA:
        raise ValueError("Official 2024 TIGER county ZIP changed from frozen source")
    shapes=county_geometries(raw,wanted)
    weights,info=county_population_overlap_weights(members,shapes,pop)
    path=p/"C2_ERA5_PROXY_C_CENSUS2020_COUNTY_POPULATION_UNAPPROVED.csv"
    with path.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(weights[0]))
        writer.writeheader();writer.writerows(weights)
    pop_file=p/"CENSUS2020_ESTIMATES_BASE_COUNTY_POPULATION_SOURCE.csv"
    with pop_file.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=["county_id_fips","census2020_estimates_base_population"])
        writer.writeheader()
        writer.writerows({"county_id_fips":f,"census2020_estimates_base_population":count} for f,count in pop.items())
    meta={"population_source":POP_SOURCE,"census2020_variable":"ESTIMATESBASE2020","source_vintage":"CO-EST2025-alldata March 2026",
      "population_is_original_decennial_PL_P1_001N":False,
      "population_source_states":pop_sources,
      "census_total_population_counties":len(pop),
      "census2020_raw_population_csv_sha256":hashlib.sha256(pop_file.read_bytes()).hexdigest(),
      "TIGER_2024_sha256":TIGER_SHA,
      "EIA861_yearly_membership_input_sha256":EIA861_FIPS_SHA,
      "weight_csv_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
      "BA_weight_summary":info,
      "geographic_vintage_2024_census_population_vintage_2020":True,
      "uniform_population_within_each_county_assumed":True,
      "actual_customers_or_load_distribution_observed":False,
      "county_proxy_geography_approved":False,
      "model_training_permitted":False,
      "weather_load_regression_performed":False}
    (p/"C2_PROXY_C_POPULATION_SOURCE_PROVENANCE.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("REAL_CENSUS_COUNTY_POPULATION_PROXY_C",json.dumps(meta),flush=True)
    return meta

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--memberships",required=True)
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    run(args.memberships,args.out)
if __name__=="__main__":main()
