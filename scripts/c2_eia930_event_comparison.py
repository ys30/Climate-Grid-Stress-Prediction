#!/usr/bin/env python3
"""Join pre-frozen C2 event days to EIA reported D/DF and original quality flags.

Strict on BA, dates, model selection and observed target compatibility.
No event inference, no new weather forecast, no missing EIA values imputed.
"""
import argparse
import csv
import datetime as dt
import json
import math
from collections import defaultdict
from pathlib import Path

def number(raw,label):
    try: value=float(raw)
    except (ValueError,TypeError) as exc:raise ValueError(f"invalid {label}") from exc
    if not math.isfinite(value):raise ValueError(f"nonfinite {label}")
    return value

def read_rows(path,required):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        reader=csv.DictReader(f)
        missing=set(required)-set(reader.fieldnames or ())
        if missing:raise ValueError(f"{path}: missing columns {sorted(missing)}")
        return list(reader)

def compare(events_csv,daily_csv,*,ba="SRP",target="peak",estimator="Huber",
            event_category="observed_high_load",abs_actual_tolerance_mw=1.0,
            quality_flags_json=None):
    events=read_rows(events_csv,["ba","date","target","estimator","event_category",
                                "episode_id","actual_mw","calendar_pred_mw","weather_pred_mw"])
    daily=read_rows(daily_csv,["ba","date_utc","paired_hours","actual_daily_peak_mw",
                               "signed_peak_error_mw","forecast_daily_peak_mw"])
    if abs_actual_tolerance_mw<0:raise ValueError("negative actual tolerance")
    operator={}
    for row in daily:
        if row["ba"]!=ba:continue
        day=dt.date.fromisoformat(row["date_utc"])
        if day in operator:raise ValueError("duplicate EIA BA/date")
        if int(row["paired_hours"])!=24:raise ValueError("EIA scored day lacks 24 hours")
        actual=number(row["actual_daily_peak_mw"],"EIA actual")
        forecast=number(row["forecast_daily_peak_mw"],"EIA forecast")
        signed=number(row["signed_peak_error_mw"],"EIA signed error")
        if abs((forecast-actual)-signed)>1e-5:raise ValueError("EIA signed-error identity mismatch")
        operator[day]=(actual,forecast,signed)
    flagged=set()
    if quality_flags_json:
        flags=json.loads(Path(quality_flags_json).read_text())
        if flags.get("ba")!=ba:raise ValueError("quality source BA mismatch")
        flagged=set(flags["flagged_dates_utc"])
        if len(flagged)!=len(flags["flagged_dates_utc"]):
            raise ValueError("duplicate source flagged date")
    selected={}
    for row in events:
        if row["ba"]!=ba or row["target"]!=target or row["estimator"]!=estimator or row["event_category"]!=event_category:
            continue
        day=dt.date.fromisoformat(row["date"])
        if day in selected:raise ValueError("duplicate frozen event day for selected estimator/category")
        selected[day]=row
    if not selected:raise ValueError("no matching pre-frozen event days; do not invent events")
    episodes=defaultdict(list)
    for day,row in selected.items():
        if not row["episode_id"]:raise ValueError("blank episode ID")
        episodes[row["episode_id"]].append(day)
    buckets={}
    for episode,dates in episodes.items():
        dates.sort()
        if len(dates)<2 or len({x.year for x in dates})!=1:
            raise ValueError("episode not persistent within a single year")
        if any((b-a).days!=1 for a,b in zip(dates,dates[1:])):
            raise ValueError("noncontiguous frozen episode")
        n=len(dates)
        buckets[episode]="2-3d" if n<=3 else ("4-7d" if n<=7 else "8+d")
    records=[]
    unmatched=[]
    for day,row in sorted(selected.items()):
        if day not in operator:
            unmatched.append(day.isoformat())
            continue
        obs,df,bias=operator[day]
        original=number(row["actual_mw"],"frozen event actual")
        if abs(obs-original)>abs_actual_tolerance_mw:
            raise ValueError(f"observed demand mismatch {day}: EIA={obs} vs frozen={original}")
        cal=number(row["calendar_pred_mw"],"calendar prediction")
        weather=number(row["weather_pred_mw"],"weather prediction")
        records.append({
            "ba":ba,"date_utc":day.isoformat(),"episode_id":row["episode_id"],
            "duration":buckets[row["episode_id"]],"actual_peak_mw":obs,
            "operator_pred_peak_mw":df,"calendar_pred_peak_mw":cal,
            "weather_pred_peak_mw":weather,"operator_signed_error_mw":bias,
            "calendar_signed_error_mw":cal-obs,
            "weather_signed_error_mw":weather-obs,
            "source_quality_flagged":day.isoformat() in flagged if quality_flags_json else None})
    def stats(items):
        def metric(key):return sum(abs(x[key]) for x in items)/len(items) if items else None
        def under(key):return sum(x[key]<0 for x in items)/len(items) if items else None
        return {"matched_days":len(items),
                "operator_peak_mae_mw":metric("operator_signed_error_mw"),
                "calendar_peak_mae_mw":metric("calendar_signed_error_mw"),
                "weather_peak_mae_mw":metric("weather_signed_error_mw"),
                "operator_underforecast_fraction":under("operator_signed_error_mw"),
                "calendar_underforecast_fraction":under("calendar_signed_error_mw"),
                "weather_underforecast_fraction":under("weather_signed_error_mw")}
    by_duration={name:stats([x for x in records if x["duration"]==name]) for name in ("2-3d","4-7d","8+d")}
    clean=[x for x in records if x["source_quality_flagged"] is False]
    return {"ba":ba,"target":target,"estimator":estimator,"event_category":event_category,
            "frozen_event_days":len(selected),"frozen_episodes":len(episodes),
            "matched_days":len(records),"unmatched_days":len(unmatched),
            "unmatched_dates":unmatched,"all_matched":stats(records),
            "by_duration":by_duration,"quality_unflagged_matched":stats(clean) if quality_flags_json else None,
            "records":records,
            "interpretation":"Descriptive overlap only; reported EIA DF issue-time vintage is not independently proven; realized weather is hindsight; missing dates never scored."}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("frozen_event_csv",type=Path)
    p.add_argument("eia_daily_csv",type=Path)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--ba",default="SRP")
    p.add_argument("--target",default="peak")
    p.add_argument("--estimator",default="Huber")
    p.add_argument("--event-category",default="observed_high_load")
    p.add_argument("--quality-flags",type=Path)
    a=p.parse_args()
    if a.output_dir.exists():p.error("output directory already exists")
    result=compare(a.frozen_event_csv,a.eia_daily_csv,ba=a.ba,target=a.target,
                   estimator=a.estimator,event_category=a.event_category,
                   quality_flags_json=a.quality_flags)
    a.output_dir.mkdir(parents=True)
    (a.output_dir/"event_df_comparison.json").write_text(
        json.dumps({k:v for k,v in result.items() if k!="records"},indent=2)+"\n",encoding="utf-8")
    fields=("ba","date_utc","episode_id","duration","actual_peak_mw",
            "operator_pred_peak_mw","calendar_pred_peak_mw","weather_pred_peak_mw",
            "operator_signed_error_mw","calendar_signed_error_mw","weather_signed_error_mw",
            "source_quality_flagged")
    with (a.output_dir/"event_df_matched_days.csv").open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(result["records"])
    print(json.dumps({k:v for k,v in result.items() if k!="records"},indent=2))
if __name__=="__main__":
    main()
