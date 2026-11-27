#!/usr/bin/env python3
"""Verify downloaded EIA-930 D/DF source against collection manifest.

Fail closed before model/forecast score computation. No external API requests.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
from collections import Counter
from pathlib import Path

NEEDED = {"period", "respondent", "type", "value"}

def verify(source_csv, source_manifest):
    source_csv=Path(source_csv)
    source_manifest=Path(source_manifest)
    payload=source_csv.read_bytes()
    digest=hashlib.sha256(payload).hexdigest()
    meta=json.loads(source_manifest.read_text(encoding="utf-8"))
    issues=[]
    if digest != meta.get("source_sha256"):
        issues.append("source SHA-256 differs from acquisition manifest")
    specs={(x["ba"],int(x["year"]),int(x["month"])):x for x in meta.get("month_ba_manifest",[])}
    counts=Counter()
    seen=set()
    rows=0
    with source_csv.open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        missing=NEEDED-set(reader.fieldnames or [])
        if missing:
            raise ValueError("missing CSV columns: "+", ".join(sorted(missing)))
        for line,r in enumerate(reader,2):
            rows+=1
            try:
                hour=dt.datetime.strptime(r["period"].strip(),"%Y-%m-%dT%H")
                ba=r["respondent"].strip()
                kind=r["type"].strip()
                if kind not in ("D","DF"):
                    raise ValueError("unexpected type")
                key=(ba,hour,kind)
                if key in seen:
                    raise ValueError("duplicate BA/hour/type")
                seen.add(key)
                if r["value"] is not None and r["value"].strip()!="":
                    value=float(r["value"])
                    import math
                    if not math.isfinite(value) or value<0:
                        raise ValueError("negative/nonfinite MW")
                # UTC hour-ending at 00 belongs to the preceding UTC date.
                day=(hour-dt.timedelta(hours=1)).date()
                monthkey=(ba,day.year,day.month)
                if monthkey not in specs:
                    raise ValueError("hour outside manifest BA/calendar-month windows")
                counts[monthkey]+=1
            except (ValueError,TypeError,AttributeError) as ex:
                issues.append(f"row {line}: {ex}")
    if rows!=int(meta.get("row_count",-1)):
        issues.append(f"CSV rows {rows} != recorded manifest rows {meta.get('row_count')}")
    if rows!=sum(int(x["rows"]) for x in specs.values()):
        issues.append("manifest monthly row count sum differs from CSV")
    for key,info in specs.items():
        if counts[key]!=int(info["rows"]):
            issues.append(f"month {key}: actual rows {counts[key]} != {info['rows']}")
        if meta.get("origin")=="bulk":
            if "api_total" in info:
                issues.append(f"month {key}: bulk manifest cannot claim API page totals")
            if not meta.get("original_bulk_sha256"):
                issues.append("bulk export missing original source SHA-256")
        else:
            if "api_total" not in info or int(info["api_total"]) != int(info["rows"]):
                issues.append(f"month {key}: API reported total disagrees")
    if not rows:
        issues.append("zero source rows")
    return {"passed":not issues,"issues":issues,"rows":rows,"source_sha256":digest,
            "manifest_months":len(specs),"month_row_counts":{
                "/".join(map(str,k)):v for k,v in sorted(counts.items())},
            "interpretation":"EIA export integrity only; does not certify upstream API values, forecast issue-time vintage or model skill."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_csv",type=Path)
    p.add_argument("source_manifest",type=Path)
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=verify(args.input_csv,args.source_manifest)
    output=json.dumps(report,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding="utf-8")
    print(output,end="")
    if not report["passed"]:
        raise SystemExit(2)

if __name__=="__main__":
    main()
