"""C2 E1 proxy C: 2020 Census county-population-weighted ERA5 area support.

Public Census PL94-171 P1_001N county total population assigned at uniform
within-county density to 2024 TIGER county polygon x ERA5 0.25-deg intersections.
EIA861 BA-county membership establishes an *approximate* geographic proxy.
NO actual customers, NO demand weights, NO approved historic BA geography.
"""
import argparse,csv,hashlib,json,math,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path

from src.c2_census_tiger_county_proxy import (
    BAS,CENSUS_URL,source_memberships,county_geometries)
from src.c2_ba_era5_weights import RES,cell_centers

POP_SOURCE="https://api.census.gov/data/2020/dec/pl"
TIGER_SHA="04e668d3502757c837c13444730547cd967f28a2c49aeffb873d1792ab2cb97b"
EIA861_FIPS_SHA="6c61f82541393c8cbe5fdeae31fc0ceca86d59b71be1ba7a8aae3543db282d68"

def parse_population_table(data,state):
    if not isinstance(data,list) or len(data)<2:
        raise ValueError("Census P1 response missing or incomplete")
    header=data[0]
    if not all(s in header for s in ("P1_001N","state","county")):
        raise ValueError("Unexpected Census total population API fields")
    idx={x:header.index(x) for x in ("P1_001N","state","county")}
    out={}
    for row in data[1:]:
        fips=str(row[idx["state"]]).zfill(2)+str(row[idx["county"]]).zfill(3)
        if fips[:2]!=state or fips in out:
            raise ValueError("Census county state mismatch or duplicate")
        raw=str(row[idx["P1_001N"]])
        if not raw.isdigit() or int(raw)<0:raise ValueError("Noninteger county source population")
        out[fips]=int(raw)
    return out

def fetch_populations(fips):
    states=sorted({x[:2] for x in fips})
    combined={};sources=[]
    for state in states:
        query=urllib.parse.urlencode({"get":"P1_001N","for":"county:*","in":"state:"+state})
        url=POP_SOURCE+"?"+query
        req=urllib.request.Request(url,headers={"User-Agent":"C2-ERA5-ScientificSourceAudit/1.0"})
        with urllib.request.urlopen(req,timeout=60) as response:raw=response.read()
        part=parse_population_table(json.loads(raw.decode()),state)
        combined.update(part)
        sources.append({"state":state,"query_url":url,"response_sha256":hashlib.sha256(raw).hexdigest(),
                        "county_records":len(part)})
        print("CENSUS_2020_PL_COUNTY_POP_SOURCE",json.dumps(sources[-1]),flush=True)
    missing=sorted(set(fips)-set(combined))
    if missing:raise ValueError("2020 Census population missing county FIPS: "+str(missing[:12]))
    return {x:combined[x] for x in sorted(fips)},sources

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
                 "exposure_method":"2020_census_county_population_uniform_within_county_UNAPPROVED",
                 "research_status":"exploratory_unapproved_geometry"})
        sums=sum(r["weight"] for r in rows if r["ba"]==ba)
        if abs(sums-1)>1e-9:raise ValueError("Population weights not normalized")
        summaries.append({"ba":ba,"member_counties":len(members[ba]),
            "2020_census_county_population":total_population,
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
    pop_file=p/"CENSUS2020_COUNTY_POPULATION_SOURCE.csv"
    with pop_file.open("w",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=["county_id_fips","census2020_total_population"])
        writer.writeheader()
        writer.writerows({"county_id_fips":f,"census2020_total_population":count} for f,count in pop.items())
    meta={"population_source":POP_SOURCE,"census2020_variable":"P1_001N",
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
