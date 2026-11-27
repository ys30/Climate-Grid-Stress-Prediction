#!/usr/bin/env python3
"""EIA-930 official six-month BALANCE CSV -> audited normalized SRP D/DF.

No API key required. Source columns and input file checksum are preserved in
manifest; this is a HISTORICAL EIA bulk export, not an original forecast vintage.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import shutil
import tempfile
import urllib.request
from pathlib import Path

ROOT="https://www.eia.gov/electricity/gridmonitor/sixMonthFiles/"
COLUMNS={"ba":"Balancing Authority","period":"UTC Time at End of Hour",
         "D":"Demand (MW)","DF":"Demand Forecast (MW)"}
OUTPUT=("period","respondent","type","value")

def csv_to_month(source, destination, ba="SRP", year=2025, month=7, source_url=None):
    source=Path(source);destination=Path(destination)
    if destination.exists(): raise ValueError("output folder already exists")
    raw_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    start=dt.datetime(year,month,1)
    end=dt.datetime(year+(month==12),month%12+1,1)
    count=0
    target=destination.parent
    target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="c2_bulk_",dir=target) as root:
        folder=Path(root)
        original=folder/"EIA930_BALANCE_original.csv"
        shutil.copyfile(source, original)
        normalized=folder/"eia930_D_DF_hourly.csv"
        with source.open(newline="",encoding="utf-8-sig") as f, normalized.open("w",newline="",encoding="utf-8") as out:
            reader=csv.DictReader(f)
            headers=set(reader.fieldnames or [])
            missing=set(COLUMNS.values())-headers
            if missing: raise ValueError("Unsupported BALANCE schema, missing "+str(sorted(missing)))
            writer=csv.DictWriter(out,fieldnames=OUTPUT)
            writer.writeheader()
            seen=set()
            for line,r in enumerate(reader,2):
                if (r[COLUMNS["ba"]] or "").strip()!=ba: continue
                raw=(r[COLUMNS["period"]] or "").strip()
                stamp=None
                for fmt in ("%m/%d/%Y %I:%M:%S %p",
                            "%m/%d/%Y %H:%M:%S",
                            "%Y-%m-%d %H:%M:%S",
                            "%Y-%m-%dT%H:%M:%S"):
                    try:
                        stamp=dt.datetime.strptime(raw,fmt)
                        break
                    except ValueError:
                        pass
                if stamp is None or stamp.minute!=0 or stamp.second!=0:
                    raise ValueError(f"row {line}: unparseable or non-hourly UTC hour-ending {raw!r}")
                if not start < stamp <= end:continue
                for field in ("D","DF"):
                    value=(r[COLUMNS[field]] or "").replace(",","").strip()
                    if value and value not in ("NA","N/A","-"):
                        num=float(value)
                        if not math.isfinite(num) or num<0:
                            raise ValueError(f"row {line}: invalid {field} MW")
                    else:
                        value=""
                    key=(ba,stamp.strftime("%Y-%m-%dT%H"),field)
                    if key in seen:raise ValueError("duplicate BA/UTC hour/type in bulk file")
                    seen.add(key)
                    writer.writerow(dict(period=key[1],respondent=ba,type=field,value=value))
                    count+=1
        if count==0:raise ValueError("No matching BA/month records in EIA BALANCE file")
        metadata={"source_url":source_url,"source_format":"EIA930_BALANCE_6MONTH",
                  "origin":"bulk","original_bulk_sha256":raw_hash,
                  "original_bulk_file":original.name,
                  "source_sha256":hashlib.sha256(normalized.read_bytes()).hexdigest(),
                  "row_count":count,"month_ba_manifest":[dict(ba=ba,year=year,month=month,rows=count)],
                  "utc_clock":"EIA UTC Time at End of Hour",
                  "note":"Official EIA historical bulk D/DF; not authenticated original issue-time forecast vintage"}
        (folder/"source_manifest.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
        folder.rename(destination)
    return metadata

def download_bulk(path, year, month):
    period="Jan_Jun" if month<=6 else "Jul_Dec"
    url=ROOT+f"EIA930_BALANCE_{year}_{period}.csv"
    path=Path(path)
    if path.exists():raise ValueError("raw bulk file exists")
    req=urllib.request.Request(url,headers={"User-Agent":"C2-ClimateGridResearch/0.1"})
    with urllib.request.urlopen(req,timeout=90) as resp, path.open("wb") as output:
        import shutil
        shutil.copyfileobj(resp,output)
    return url

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--year",type=int,default=2025)
    p.add_argument("--month",type=int,default=7,choices=range(1,13))
    p.add_argument("--ba",default="SRP")
    p.add_argument("--bulk-file",type=Path,help="Use previously downloaded original EIA CSV instead of network")
    args=p.parse_args()
    if args.bulk_file:
        meta=csv_to_month(args.bulk_file,args.output_dir,args.ba,args.year,args.month)
    else:
        with tempfile.TemporaryDirectory(prefix="c2_original_bulk_") as root:
            bulk=Path(root)/"original_EIA930_BALANCE.csv"
            url=download_bulk(bulk,args.year,args.month)
            meta=csv_to_month(bulk,args.output_dir,args.ba,args.year,args.month,source_url=url)
    print(json.dumps(meta,indent=2))

if __name__=="__main__":
    main()
