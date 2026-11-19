"""Retrieve one official CDS ERA5 monthly 2m-temperature NetCDF securely.

Needs CDSAPI_KEY configured via environment (provided by GH Actions secret)
and the user to have accepted the dataset licence in CDS. Never commits
credentials or data to the repository. The resulting grid sample is only a
spatial demonstrator, not a validated CISO BA weather series.
"""
from __future__ import annotations
import argparse,hashlib,json,os
from pathlib import Path
from scripts.c2_era5_official_pilot_request import DATASET,request

def retrieve(year:int,month:int,target:Path):
    import cdsapi
    target=Path(target)
    if target.exists() or target.with_suffix(".manifest.json").exists():
        raise FileExistsError("Existing original ERA5 source cannot be overwritten")
    # Validate and construct request before contacting CDS.
    req=request(year,month)
    if not os.environ.get("CDSAPI_KEY"):
        raise RuntimeError("CDSAPI_KEY not configured; official CDS data unavailable")
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=target.with_suffix(target.suffix+".partial")
    if temp.exists():
        raise FileExistsError("Stale ERA5 partial download")
    try:
        # CDS API client obtains its credential from CDSAPI_KEY environment.
        # Never log client config or embed key in source metadata.
        client=cdsapi.Client(url="https://cds.climate.copernicus.eu/api",
                             key=os.environ["CDSAPI_KEY"],
                             quiet=True)
        client.retrieve(DATASET,req,str(temp))
        sha=hashlib.sha256(temp.read_bytes()).hexdigest()
        if temp.stat().st_size<1000:
            raise RuntimeError("ERA5 retrieval unexpectedly small; not a valid NetCDF source")
        # Validate signature before moving immutable source into place.
        if not temp.read_bytes()[:4] in (b"CDF\x01",b"CDF\x02",b"\x89HDF"):
            raise RuntimeError("CDS output is not a recognized NetCDF/HDF5 file")
        temp.replace(target)
        m={"source_kind":"original_Copernicus_CDS_ERA5_NetCDF",
           "dataset":DATASET,"request":req,"sha256_netcdf":sha,
           "year":year,"month":month,
           "time_semantics":"UTC instantaneous 2m_temperature validity time",
           "spatial_semantics":"Sacramento area grid pilot, not CISO BA proxy",
           "claim_status":"official_source_retrieval_only_not_weather_join"}
        target.with_suffix(".manifest.json").write_text(json.dumps(m,indent=2)+"\n")
        return m
    finally:
        if temp.exists():
            temp.unlink()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    m=retrieve(a.year,a.month,a.output)
    print("CDS original ERA5 SHA256",m["sha256_netcdf"],"year",a.year,"month",a.month)

if __name__=="__main__":
    main()
