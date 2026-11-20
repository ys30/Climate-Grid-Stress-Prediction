"""Prepare official Copernicus CDS ERA5 2m-temperature pilot request.

No credentials are loaded or submitted by this module. ERA5 t2m is an
instantaneous hourly *validity time*, not EIA-930 hour-ending. Pilot grid
near Sacramento is a SINGLE GRID-CELL DEMONSTRATOR, not an established
geographic / load-weighted proxy for the whole CISO balancing authority.
"""
from __future__ import annotations
import argparse
import calendar
import json
from pathlib import Path

DATASET = "reanalysis-era5-single-levels"
PILOT_AREA = [38.75, -121.75, 38.25, -121.25]  # N,W,S,E; illustrative Sacramento area


def request(year: int, month: int) -> dict:
    if year not in range(2020, 2026) or month not in range(1, 13):
        raise ValueError("ERA5 pilot year must be 2020–2025 and month 1–12")
    return {
        "product_type": ["reanalysis"],
        "variable": ["2m_temperature"],
        "year": [str(year)],
        "month": [f"{month:02d}"],
        "day": [f"{d:02d}" for d in range(1, calendar.monthrange(year, month)[1] + 1)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": PILOT_AREA,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--year",type=int,required=True)
    p.add_argument("--month",type=int,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result={"dataset":DATASET,"request":request(a.year,a.month),
            "source":"Copernicus CDS official ERA5 hourly single levels",
            "clock":"UTC instantaneous valid time, no EIA HE shift",
            "spatial_claim":"illustrative near-Sacramento grid cell only; not a CISO-wide proxy",
            "claim_status":"REQUEST_PLAN_ONLY_NO_DOWNLOAD"}
    if a.output.exists():
        p.error("Output exists")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
