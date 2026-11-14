"""C2 E1 alternative *unapproved* BA weather masks from 2024 Census TIGER counties.

Spatial proxy B = union of Census 2024 TIGER/Line (non-simplified) county
geometries selected by independently fetched EIA-861/PUDL BA county memberships.
No exclusive BA territory assumption, no load weighting, no official admission.
"""
import argparse,csv,hashlib,io,json,math,urllib.request,zipfile
from collections import defaultdict
from pathlib import Path

CENSUS_URL="https://www2.census.gov/geo/tiger/TIGER2024/COUNTY/tl_2024_us_county.zip"
BAS=("AZPS","BPAT","CISO","SRP")
def source_memberships(path,year=2024):
    groups=defaultdict(set)
    with open(path,newline="",encoding="utf-8") as handle:
        reader=csv.DictReader(handle)
        needed={"year","eia930_BA_code","county_id_fips","model_ready"}
        if not needed.issubset(reader.fieldnames or []):
            raise ValueError("Expected provenance-audited annual BA/county FIPS fields")
        for row in reader:
            if int(row["year"])!=year:continue
            if row["eia930_BA_code"] not in BAS:
                raise ValueError("Non-study BA code in annual source")
            if row["model_ready"]!="False":raise ValueError("Unapproved county proxy must remain NOT model ready")
            fips=row["county_id_fips"].zfill(5)
            if len(fips)!=5 or not fips.isdigit():raise ValueError("Malformed county FIPS")
            groups[row["eia930_BA_code"]].add(fips)
    if set(groups)!=set(BAS):raise ValueError("Missing county membership for a study BA")
    return dict(groups)

def county_geometries(zip_bytes,wanted):
    import shapefile
    from shapely.geometry import shape
    out={}
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        members=archive.namelist()
        def member(ext):
            matching=[p for p in members if p.lower().endswith(ext)]
            if len(matching)!=1:raise ValueError("TIGER shapefile ZIP missing one "+ext)
            return io.BytesIO(archive.read(matching[0]))
        reader=shapefile.Reader(shp=member(".shp"),shx=member(".shx"),dbf=member(".dbf"))
        columns=[x[0] for x in reader.fields[1:]]
        if "GEOID" not in columns:raise ValueError("Official TIGER county GEOID absent")
        idx=columns.index("GEOID")
        for record in reader.iterShapeRecords():
            fips=str(record.record[idx]).zfill(5)
            if fips not in wanted:continue
            if fips in out:raise ValueError("Duplicate national Census county GEOID")
            geom=shape(record.shape.__geo_interface__)
            if not geom.is_valid or geom.is_empty or geom.geom_type not in ("Polygon","MultiPolygon"):
                raise ValueError("TIGER geometry invalid or empty: "+fips)
            out[fips]=geom
        reader.close()
    missing=sorted(wanted-set(out))
    if missing:raise ValueError("TIGER 2024 county GEOIDs missing: "+str(missing[:15]))
    return out

def build_county_features(membership,geometries):
    from shapely.ops import unary_union
    from shapely.geometry import mapping
    result=[];summary=[]
    for ba in BAS:
        ids=sorted(membership[ba])
        missing=set(ids)-set(geometries)
        if missing:raise ValueError("Missing county geometries: "+str(missing))
        union=unary_union([geometries[fips] for fips in ids])
        if not union.is_valid or union.is_empty or union.geom_type not in ("Polygon","MultiPolygon"):
            raise ValueError("County geometry union must be valid for "+ba)
        if (union.bounds[0]<-180 or union.bounds[2]>0 or union.bounds[1]<20 or union.bounds[3]>55):
            raise ValueError("County-set geography outside western contiguous US domain for "+ba)
        result.append({"type":"Feature","properties":{"ba":ba,
          "proxy":"EIA-861 county membership plus 2024 TIGER county geometry",
          "geometry_approved":False,"source_approved":False,
          "source_member_count":len(ids)},
          "geometry":mapping(union)})
        summary.append({"ba":ba,"counties":len(ids),"geometry_valid":True})
    return {"type":"FeatureCollection","features":result},summary

def run(memberships,output):
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    member_bytes=Path(memberships).read_bytes()
    m=source_memberships(memberships,year=2024)
    req=urllib.request.Request(CENSUS_URL,headers={"User-Agent":"C2-ResearchSourceAudit/1.0"})
    with urllib.request.urlopen(req,timeout=180) as response:raw=response.read()
    zip_digest=hashlib.sha256(raw).hexdigest()
    geom=county_geometries(raw,set().union(*m.values()))
    geo,summaries=build_county_features(m,geom)
    geo_bytes=(json.dumps(geo,sort_keys=True,separators=(",",":"))+"\n").encode()
    (out/"EIA861_TIGER2024_FOUR_BA_COUNTY_PROXY_UNAPPROVED.geojson").write_bytes(geo_bytes)
    audit={"TIGER_census_source":CENSUS_URL,"TIGER_vintage":2024,
      "TIGER_download_ZIP_sha256":zip_digest,"TIGER_zip_bytes":len(raw),
      "PUDL_annual_membership_source_SHA256":hashlib.sha256(member_bytes).hexdigest(),
      "county_membership_year_used":2024,
      "BA_county_union_summary":summaries,
      "county_feature_count":len(geom),
      "output_geojson_sha256":hashlib.sha256(geo_bytes).hexdigest(),
      "all_six_year_historical_TIGER_masks_constructed":False,
      "county_proxy_geography_approved":False,
      "geographic_weather_exposure_approved":False,
      "training_permitted":False,
      "disclaimer":"County union is NOT a historic BA operating-area polygon or verified load service area."}
    (out/"TIGER2024_C2_FOUR_BA_COUNTY_PROXY_PROVENANCE.json").write_text(json.dumps(audit,indent=2)+"\n")
    print("REAL_CENSUS_TIGER_COUNTY_PROXY",json.dumps(audit),flush=True)
    return audit
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--memberships",required=True)
    p.add_argument("--out",default="outputs/e1_tiger_proxy")
    a=p.parse_args()
    run(a.memberships,a.out)
if __name__=="__main__":main()
