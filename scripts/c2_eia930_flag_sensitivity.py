#!/usr/bin/env python3
"""Join EIA-930 reported forecast daily peaks to original BALANCE day-quality flags.

Report all accepted days AND a sensitivity subset with no flagged source hours.
Never silently delete rows from the canonical daily result.
This is descriptive only; original forecast vintage is not independently certified.
"""
import argparse
import csv
import json
import math
from pathlib import Path

def sensitivity(daily_path,flags_path,*,ba="SRP",year=2025,month=7):
    flags=json.loads(Path(flags_path).read_text(encoding="utf-8"))
    if (flags.get("ba"),flags.get("year"),flags.get("month"))!=(ba,year,month):
        raise ValueError("bulk source quality report BA/year/month mismatch")
    raw_flags=flags.get("flagged_dates_utc")
    if not isinstance(raw_flags,list) or len(raw_flags)!=len(set(raw_flags)):
        raise ValueError("quality flagged_dates_utc missing or duplicated")
    flagged=set(raw_flags)
    prefix=f"{year:04d}-{month:02d}-"
    if any(not day.startswith(prefix) for day in flagged):
        raise ValueError("quality flag dates outside requested month")
    with Path(daily_path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        expected={"ba","date_utc","signed_peak_error_mw","paired_hours"}
        if not reader.fieldnames or expected-set(reader.fieldnames):
            raise ValueError("daily scorecard lacks mandatory columns")
        rows=list(reader)
    seen=set()
    retained=[]
    for r in rows:
        if r["ba"]!=ba or not r["date_utc"].startswith(prefix):
            continue
        day=r["date_utc"]
        if day in seen:raise ValueError("duplicate BA/date in daily scores")
        seen.add(day)
        if int(r["paired_hours"])!=24:
            raise ValueError("scored daily peak is not based on 24 paired hours")
        try: signed=float(r["signed_peak_error_mw"])
        except (ValueError,TypeError) as exc:raise ValueError("non-numeric signed peak error") from exc
        if not math.isfinite(signed):raise ValueError("non-finite signed peak error")
        retained.append({"ba":ba,"date_utc":day,"signed_peak_error_mw":signed,
                         "source_quality_flagged":day in flagged})
    def stats(sample):
        n=len(sample)
        return {"days":n,
                "mean_absolute_peak_error_mw":sum(abs(x["signed_peak_error_mw"]) for x in sample)/n if n else None,
                "mean_signed_peak_error_mw":sum(x["signed_peak_error_mw"] for x in sample)/n if n else None,
                "underforecast_fraction":sum(x["signed_peak_error_mw"]<0 for x in sample)/n if n else None}
    clean=[x for x in retained if not x["source_quality_flagged"]]
    flagged_rows=[x for x in retained if x["source_quality_flagged"]]
    return {"ba":ba,"year":year,"month":month,
            "all_scored_days":stats(retained),"clean_flag_sensitivity":stats(clean),
            "flagged_scored_days":stats(flagged_rows),
            "flagged_source_dates_without_complete_daily_score":sorted(flagged-seen),
            "day_records":sorted(retained,key=lambda x:x["date_utc"]),
            "interpretation":"Retrospective day-quality sensitivity only; not blind day-ahead forecast validation. 'Clean' means no flags in THIS audit, not verified raw data accuracy."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("daily_csv",type=Path)
    p.add_argument("raw_quality_flags_json",type=Path)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--ba",default="SRP")
    p.add_argument("--year",type=int,default=2025)
    p.add_argument("--month",type=int,default=7)
    a=p.parse_args()
    if a.output_dir.exists():p.error("output directory already exists")
    result=sensitivity(a.daily_csv,a.raw_quality_flags_json,ba=a.ba,year=a.year,month=a.month)
    a.output_dir.mkdir(parents=True)
    with (a.output_dir/"quality_tagged_days.csv").open("w",newline="",encoding="utf-8") as f:
        wr=csv.DictWriter(f,fieldnames=("ba","date_utc","signed_peak_error_mw","source_quality_flagged"))
        wr.writeheader();wr.writerows(result["day_records"])
    (a.output_dir/"quality_sensitivity.json").write_text(json.dumps({k:v for k,v in result.items() if k!="day_records"},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="day_records"},indent=2))

if __name__=="__main__":
    main()
