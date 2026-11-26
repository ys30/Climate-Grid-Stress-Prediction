#!/usr/bin/env python3
"""C2 paired high-load episode audit. Retrospective descriptive QA, NOT a forecast.

Input must contain pre-frozen episode IDs and precomputed model predictions.
This program never creates weather inputs, forecasts, thresholds or events.
"""
import argparse
import csv
import datetime as dt
import json
import math
import random
from collections import defaultdict
from pathlib import Path

REQUIRED = ("ba", "date", "target", "estimator", "event_category", "episode_id",
            "actual_mw", "calendar_pred_mw", "weather_pred_mw")
FLAG_TRUE = {"1", "true", "yes", "y", "flagged"}

def parse_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(REQUIRED).issubset(reader.fieldnames):
            raise ValueError("Missing required columns: " + ", ".join(sorted(set(REQUIRED) - set(reader.fieldnames or []))))
        seen = set()
        for line, raw in enumerate(reader, 2):
            try:
                date = dt.date.fromisoformat(raw["date"])
                vals = [float(raw[k]) for k in ("actual_mw", "calendar_pred_mw", "weather_pred_mw")]
                if not all(math.isfinite(x) for x in vals):
                    raise ValueError("nonfinite MW")
                ba, target, model, category, eid = (raw[k].strip() for k in
                    ("ba", "target", "estimator", "event_category", "episode_id"))
                if not all((ba, target, model, category, eid)):
                    raise ValueError("blank key")
                key = (ba, date, target, model, category)
                if key in seen:
                    raise ValueError("duplicate BA/date/target/model/category")
                seen.add(key)
                rows.append(dict(ba=ba, date=date, target=target, estimator=model,
                    event_category=category, episode_id=eid, actual=vals[0],
                    calendar=vals[1], weather=vals[2],
                    flagged=raw.get("source_flag", "").strip().lower() in FLAG_TRUE))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Invalid row {line}: {exc}") from exc
    if not rows:
        raise ValueError("No input observations")
    return rows

def quantile(values, q):
    if not values:
        return None
    v = sorted(values)
    p = (len(v)-1)*q
    i = int(p)
    return v[i] if i == len(v)-1 else v[i] + (v[i+1]-v[i])*(p-i)

def mean(values):
    return sum(values)/len(values) if values else None

def duration_bucket(n):
    return "2-3d" if n <= 3 else ("4-7d" if n <= 7 else "8+d")

def build_episodes(rows):
    episodes = defaultdict(list)
    for r in rows:
        episodes[(r["ba"],r["target"],r["estimator"],r["event_category"],r["episode_id"])].append(r)
    valid = []
    for key, days in episodes.items():
        days.sort(key=lambda r:r["date"])
        dates = [r["date"] for r in days]
        if len(set(dates)) != len(dates):
            raise ValueError(f"Duplicate date in episode {key}")
        if len({d.year for d in dates}) != 1:
            raise ValueError(f"Episode crosses year: {key}")
        if any(b-a != dt.timedelta(days=1) for a,b in zip(dates,dates[1:])):
            raise ValueError(f"Noncontiguous episode: {key}")
        if len(days) < 2:
            raise ValueError(f"Singleton is not a persistent event: {key}")
        valid.append((key,days))
    return valid

def describe(episodes, bootstrap=1200, seed=20261126):
    groups = defaultdict(list)
    for key, days in episodes:
        group = (*key[:4], duration_bucket(len(days)))
        groups[group].append(days)
    result = []
    for group in sorted(groups):
        eps = groups[group]
        days = [r for ep in eps for r in ep]
        ce = [r["calendar"]-r["actual"] for r in days]
        we = [r["weather"]-r["actual"] for r in days]
        ca = [abs(v) for v in ce]
        wa = [abs(v) for v in we]
        per_episode_delta = [mean([abs(r["weather"]-r["actual"])-abs(r["calendar"]-r["actual"]) for r in ep]) for ep in eps]
        rec = dict(zip(("ba","target","estimator","event_category","duration"),group))
        rec.update(episodes=len(eps), days=len(days),
            flagged_days=sum(r["flagged"] for r in days),
            calendar_mae_mw=mean(ca), weather_mae_mw=mean(wa),
            delta_mae_mw=mean(wa)-mean(ca),
            calendar_bias_mw=mean(ce), weather_bias_mw=mean(we),
            calendar_underforecast_rate=mean([v<0 for v in ce]),
            weather_underforecast_rate=mean([v<0 for v in we]),
            weather_underforecast_mean_mw=mean([-v for v in we if v<0]),
            weather_underforecast_p90_mw=quantile([-v for v in we if v<0],0.9),
            episode_mean_delta_mae_mw=mean(per_episode_delta),
            interval_type="descriptive_episode_cluster_bootstrap" if len(eps)>=8 else "withheld_fewer_than_8_episodes")
        if len(eps)>=8 and bootstrap:
            rng=random.Random(seed + sum(ord(c) for c in "|".join(group)))
            sampled=[]
            for _ in range(bootstrap):
                draw=[eps[rng.randrange(len(eps))] for _ in eps]
                rr=[r for ep in draw for r in ep]
                sampled.append(mean([abs(r["weather"]-r["actual"])-abs(r["calendar"]-r["actual"]) for r in rr]))
            rec["delta_mae_bootstrap_p025_mw"]=quantile(sampled,0.025)
            rec["delta_mae_bootstrap_p975_mw"]=quantile(sampled,0.975)
        else:
            rec["delta_mae_bootstrap_p025_mw"]=None
            rec["delta_mae_bootstrap_p975_mw"]=None
        result.append(rec)
    return result

def audit(input_csv, outdir, bootstrap=1200, seed=20261126):
    rows = parse_rows(input_csv)
    episodes = build_episodes(rows)
    result = describe(episodes,bootstrap=bootstrap,seed=seed)
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    with open(outdir/"episode_duration_metrics.csv","w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(result[0]))
        writer.writeheader()
        writer.writerows(result)
    manifest = {"input_csv":str(input_csv),"raw_rows":len(rows),
        "episodes":len(episodes),"groups":len(result),
        "note":"Retrospective descriptive audit. Actual test-year weather is hindsight, not forward forecast. Episodes are pre-frozen input labels. Sparse intervals withheld.",
        "bootstrap_draws":bootstrap,"seed":seed,
        "source_flagged_rows":sum(r["flagged"] for r in rows)}
    (outdir/"audit_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_csv",type=Path)
    p.add_argument("output_dir",type=Path)
    p.add_argument("--bootstrap",type=int,default=1200)
    p.add_argument("--seed",type=int,default=20261126)
    args=p.parse_args()
    if args.bootstrap<0:
        p.error("bootstrap must be nonnegative")
    print(json.dumps(audit(args.input_csv,args.output_dir,args.bootstrap,args.seed),indent=2))

if __name__=="__main__":
    main()
