#!/usr/bin/env python3
"""EIA API v2 D/DF monthly exporter; preserves historical source values, no modeling."""
import argparse
import calendar
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import tempfile
import urllib.parse
import urllib.request

ENDPOINT = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
BAS = ("CISO", "AZPS", "BPAT", "SRP")
FIELDS = ("period", "respondent", "type", "value")

def month_window(year, month):
    last = calendar.monthrange(year, month)[1]
    return f"{year:04d}-{month:02d}-01T00", f"{year:04d}-{month:02d}-{last:02d}T23"

def _get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent":"C2-ClimateGridResearch/0.1"})
    with urllib.request.urlopen(request, timeout=45) as response:
        return json.load(response)

def request_page(ba, year, month, api_key, fetch=None):
    fetch = fetch or _get_json
    start, end = month_window(year,month)
    offset, rows, reported_total = 0, [], None
    while True:
        params = [("frequency","hourly"),("data[0]","value"),
                  ("facets[respondent][]",ba),("facets[type][]","D"),
                  ("facets[type][]","DF"),("start",start),("end",end),
                  ("sort[0][column]","period"),("sort[0][direction]","asc"),
                  ("sort[1][column]","type"),("sort[1][direction]","asc"),
                  ("offset",str(offset)),("length","5000")]
        if api_key:
            params.append(("api_key",api_key))
        response = fetch(ENDPOINT+"?"+urllib.parse.urlencode(params))
        if "error" in response:
            raise RuntimeError(f"EIA API error for {ba} {year}-{month:02d}: {response['error']}")
        body = response.get("response",{})
        total = int(body.get("total",-1))
        page = body.get("data",[])
        if total < 0 or not isinstance(page,list):
            raise ValueError("EIA response lacks total or data")
        if reported_total is not None and total != reported_total:
            raise ValueError("EIA pagination total changed")
        reported_total=total
        if not page and offset < total:
            raise ValueError("EIA pagination ended before all records retrieved")
        for item in page:
            if not all(k in item for k in FIELDS):
                raise ValueError("Incomplete EIA response row")
            if item["respondent"]!=ba or item["type"] not in ("D","DF"):
                raise ValueError("Unexpected respondent or type")
            if not start <= item["period"] <= end:
                raise ValueError("Returned period outside requested month")
            rows.append({k:item[k] for k in FIELDS})
        offset+=len(page)
        if offset >= total: break
    if len(rows)!=reported_total:
        raise ValueError("Unreconciled EIA total")
    if len({(r["period"],r["respondent"],r["type"]) for r in rows})!=len(rows):
        raise ValueError("Duplicate EIA respondent/period/type")
    return rows, {"ba":ba,"year":year,"month":month,"start":start,"end":end,
                  "rows":len(rows),"api_total":reported_total}

def collect(outdir,start_year=2023,end_year=2025,bas=BAS,api_key=None,fetch=None):
    outdir=Path(outdir)
    if outdir.exists():
        raise ValueError("Output directory exists; refuse overwrite")
    if start_year>end_year or not bas or any(b not in BAS for b in bas):
        raise ValueError("Invalid years or BA selection")
    outdir.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="c2_eia_stage_",dir=outdir.parent) as tmp:
        path=Path(tmp)
        csv_path=path/"eia930_D_DF_hourly.csv"
        index=[]
        with csv_path.open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            for year in range(start_year,end_year+1):
                for month in range(1,13):
                    for ba in bas:
                        rows,record=request_page(ba,year,month,api_key,fetch=fetch)
                        writer.writerows(rows)
                        index.append(record)
        meta={"source_url":ENDPOINT,"frequency":"hourly","types":["D","DF"],
              "bas":list(bas),"years":[start_year,end_year],
              "retrieved_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
              "source_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),
              "row_count":sum(r["rows"] for r in index),
              "month_ba_manifest":index,
              "note":"Historical EIA DF; original issue-time vintage not independently certified."}
        (path/"source_manifest.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
        path.rename(outdir)
    return meta

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--start-year",type=int,default=2023)
    p.add_argument("--end-year",type=int,default=2025)
    p.add_argument("--ba",action="append",choices=BAS)
    args=p.parse_args()
    meta=collect(args.output_dir,args.start_year,args.end_year,
                 tuple(args.ba or BAS),api_key=os.environ.get("EIA_API_KEY"))
    print(json.dumps({k:v for k,v in meta.items() if k!="month_ba_manifest"},indent=2))

if __name__=="__main__":
    main()
