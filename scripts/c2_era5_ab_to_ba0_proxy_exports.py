#!/usr/bin/env python3
"""Export two explicitly unapproved BA weather proxies from verified four-month ERA5 A/B archive.

Input must be output by src.c2_era5_AB_fourmonth_aggregate. No hourly
values are imputed, no CISO/other BA operational footprint is certified.
This bridge DOES NOT unlock any historical model.
"""
import argparse
import calendar
import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

BAS = ("CISO", "AZPS", "BPAT", "SRP")
MONTHS = ((2023,1),(2023,7),(2025,1),(2025,7))
COLUMNS = {
    "A_HIFLD_2018": "HIFLD_2018_candidate_celsius",
    "B_TIGER_2024": "Census_2024_county_proxy_celsius",
}

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(hourly, evidence):
    if evidence.get("geography_approved") is not False or evidence.get("training_permitted") is not False:
        raise ValueError("Source evidence must fail-closed on geography and training")
    if evidence.get("independently_verified_BA_hours") != 11904 or evidence.get("verified_months") != 4:
        raise ValueError("Missing complete four-month source provenance")
    required_months = [f"{year:04}-{month:02}-01T00:00:00Z" for year, month in MONTHS]
    if evidence.get("source_months") != required_months:
        raise ValueError("Wrong seasonal source months or their order")
    results = evidence.get("BA_results", [])
    if not isinstance(results, list) or len(results) != 4 or {r.get("ba") for r in results} != set(BAS):
        raise ValueError("Missing or duplicated BA source provenance")
    if any(r.get("historical_geometry_approved") is not False or
           r.get("training_allowed") is not False or
           r.get("real_ERA5_hours") != 2976 for r in results):
        raise ValueError("BA source statistics are not unapproved and complete")
    if any(not isinstance(evidence.get(k), str) or len(evidence[k]) != 64 or
           any(ch not in "0123456789abcdef" for ch in evidence[k])
           for k in ("A_weights_SHA256", "B_weights_SHA256")):
        raise ValueError("Full lowercase SHA256 weight source identities required")
    with Path(hourly).open(newline="", encoding="utf-8-sig") as stream:
        source=list(csv.DictReader(stream))
    expected=set()
    for ba in BAS:
        for year,month in MONTHS:
            first=datetime(year,month,1,tzinfo=timezone.utc)
            expected.update((ba,(first+timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ"))
                            for h in range(calendar.monthrange(year,month)[1]*24))
    if len(source)!=11904 or len(expected)!=11904:
        raise ValueError("Four-month BA hourly count mismatch")
    found=set()
    output={kind:[] for kind in COLUMNS}
    for row in source:
        original=row["timestamp_utc_start"]
        try:
            timestamp=datetime.fromisoformat(original.replace("Z","+00:00"))
        except ValueError as err:
            raise ValueError("Malformed source UTC timestamp") from err
        if timestamp.utcoffset()!=timedelta(0) or (timestamp.minute,timestamp.second,timestamp.microsecond)!=(0,0,0):
            raise ValueError("Non-UTC or non-hourly source timestamp")
        canonical=timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
        key=(row["ba"],canonical)
        if key not in expected or key in found:
            raise ValueError("Duplicate, wrong or out-of-month UTC BA-hour")
        found.add(key)
        if row.get("historical_geography_approved")!="False" or row.get("training_permitted")!="False":
            raise ValueError("Unexpected source geography/model authorization")
        a=float(row[COLUMNS["A_HIFLD_2018"]])
        b=float(row[COLUMNS["B_TIGER_2024"]])
        delta=float(row["Census_minus_HIFLD_celsius"])
        if not all(map(math.isfinite,(a,b,delta))) or abs((b-a)-delta)>0.000002:
            raise ValueError("Nonfinite/inconsistent source temperature")
        for kind,value in (("A_HIFLD_2018",a),("B_TIGER_2024",b)):
            output[kind].append({"ba":key[0],"utc_start":key[1],"weather_value":f"{value:.6f}"})
    if found!=expected: raise ValueError("Incomplete UTC source hours")
    return output

def export(hourly,provenance,out):
    out=Path(out)
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Refuse to overwrite existing weather proxy products")
    evidence=json.loads(Path(provenance).read_text(encoding="utf-8"))
    payload=validate(hourly,evidence)
    out.mkdir(parents=True,exist_ok=True)
    result={"source_sha256":sha(hourly),"source_provenance_sha256":sha(provenance),
            "weather_proxy_qualified":False,"geography_approved":False,
            "model_training_permitted":False,"year_months":[f"{y:04}-{m:02}" for y,m in MONTHS],
            "source_rows":11904,"exports":{}}
    for name,rows in payload.items():
        file=out/(name+"_BA_HOUR_WEATHER_PROXY_UNAPPROVED.csv")
        with file.open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=("ba","utc_start","weather_value"))
            w.writeheader();w.writerows(rows)
        result["exports"][name]={"file":file.name,"sha256":sha(file),"rows":len(rows),
                                  "units":"degrees_C","proxy_type":name,
                                  "is_load_weighted_BA_exposure":False}
    (out/"UNAPPROVED_WEATHER_PROXY_EXPORT_MANIFEST.json").write_text(
        json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--hourly",required=True,type=Path)
    p.add_argument("--provenance",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(export(a.hourly,a.provenance,a.out),indent=2))

if __name__=="__main__":main()
