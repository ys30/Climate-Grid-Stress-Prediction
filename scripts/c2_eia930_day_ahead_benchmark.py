#!/usr/bin/env python3
"""EIA-930 reported day-ahead demand forecast (DF) vs demand (D).

Input: EIA API v2 electricity/rto/region-data CSV with columns:
period,respondent,type,value. Period is UTC hour-ending YYYY-MM-DDTHH.
Historical reported DF is NOT proof of the original issue-time vintage.
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

def parse_hour(s):
    try:
        return dt.datetime.strptime(s.strip(), "%Y-%m-%dT%H").replace(tzinfo=dt.timezone.utc)
    except ValueError as exc:
        raise ValueError(f"invalid UTC hour period: {s!r}") from exc

def read_pairs(path, requested_bas=None):
    raw=Path(path).read_bytes()
    lookup={}
    with Path(path).open(newline="", encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        required={"period","respondent","type","value"}
        if not reader.fieldnames or required-set(reader.fieldnames):
            raise ValueError("missing headers: "+str(sorted(required-set(reader.fieldnames or []))))
        for line,r in enumerate(reader,2):
            ba=r["respondent"].strip()
            kind=r["type"].strip()
            if not ba or kind not in ("D","DF"):
                raise ValueError(f"line {line}: invalid BA or type")
            if requested_bas and ba not in requested_bas:
                continue
            hour=parse_hour(r["period"])
            val=(r["value"] or "").strip()
            if not val:
                continue
            try:
                mw=float(val)
            except ValueError as exc:
                raise ValueError(f"line {line}: non-numeric MW") from exc
            if not math.isfinite(mw) or mw < 0:
                raise ValueError(f"line {line}: nonfinite or negative MW")
            key=(ba,hour,kind)
            if key in lookup:
                raise ValueError(f"line {line}: duplicate BA/UTC hour/type")
            lookup[key]=mw
    dates=defaultdict(dict)
    for (ba,hour,kind),value in lookup.items():
        # EIA hour-ending to UTC interval-start calendar day.
        start=hour-dt.timedelta(hours=1)
        dates[(ba,start.date().isoformat())].setdefault(start.hour,{})[kind]=value
    complete=[]
    excluded=[]
    for (ba,date),hours in sorted(dates.items()):
        if len(hours)!=24 or any(set(hours.get(h,{}))!={"D","DF"} for h in range(24)):
            excluded.append({"ba":ba,"date_utc":date,
                "paired_hours":sum(set(v)=={"D","DF"} for v in hours.values()),
                "reason":"missing D/DF or fewer than 24 complete UTC hours"})
            continue
        actual=[hours[h]["D"] for h in range(24)]
        forecast=[hours[h]["DF"] for h in range(24)]
        pa=max(actual);pf=max(forecast)
        peak_hour=actual.index(pa)
        error=[f-a for f,a in zip(forecast,actual)]
        complete.append({"ba":ba,"date_utc":date,
            "actual_daily_peak_mw":pa,"forecast_daily_peak_mw":pf,
            "signed_peak_error_mw":pf-pa,"peak_absolute_error_mw":abs(pf-pa),
            "forecast_at_actual_peak_hour_mw":forecast[peak_hour],
            "signed_actual_peak_hour_error_mw":forecast[peak_hour]-pa,
            "hourly_mae_mw":sum(abs(x) for x in error)/24,
            "hourly_mean_bias_mw":sum(error)/24,"paired_hours":24})
    meta={"source_sha256":hashlib.sha256(raw).hexdigest(),
        "observed_bas":sorted({x[0] for x in dates}),
        "requested_bas":sorted(requested_bas) if requested_bas else None,
        "complete_days":len(complete),"excluded_incomplete_days":len(excluded),
        "interpretation":"Retrospective EIA D vs reported DF; issue-time vintage not independently certified."}
    return complete,excluded,meta

def write_csv(path,rows,columns):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns)
        writer.writeheader();writer.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_csv",type=Path)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--ba",action="append",help="BA code; repeat for additional BAs")
    a=p.parse_args()
    rows,dropped,meta=read_pairs(a.input_csv,set(a.ba) if a.ba else None)
    if a.output_dir.exists():
        p.error("output directory already exists; use a fresh path")
    a.output_dir.mkdir(parents=True)
    write_csv(a.output_dir/"eia930_df_daily.csv",rows,
        ["ba","date_utc","actual_daily_peak_mw","forecast_daily_peak_mw",
        "signed_peak_error_mw","peak_absolute_error_mw",
        "forecast_at_actual_peak_hour_mw","signed_actual_peak_hour_error_mw",
        "hourly_mae_mw","hourly_mean_bias_mw","paired_hours"])
    write_csv(a.output_dir/"excluded_days.csv",dropped,
        ["ba","date_utc","paired_hours","reason"])
    (a.output_dir/"manifest.json").write_text(json.dumps(meta,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(meta,indent=2))

if __name__=="__main__":
    main()
