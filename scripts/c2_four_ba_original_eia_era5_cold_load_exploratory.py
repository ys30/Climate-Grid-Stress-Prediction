#!/usr/bin/env python3
"""Source-locked multi-BA exploratory cold-load analysis; NOT causal."""
import argparse, gzip, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ARCHIVE_SHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
GZIP_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
MEMBER="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"

def mh(df):
    numer=denom=0.0;informative=0
    for _,g in df.groupby(["year","month"]):
        c=g["cold"].to_numpy(bool);h=g["high"].to_numpy(bool)
        a=int(np.sum(c&h));b=int(np.sum(c&~h))
        cc=int(np.sum(~c&h));d=int(np.sum(~c&~h))
        n=a+b+cc+d
        if min(a+b,cc+d,a+cc,b+d)==0:continue
        informative+=1;numer+=a*d/n;denom+=b*cc/n
    return (numer/denom if denom>0 else None),informative

def summary(df,ba,variant,original):
    df=df[df.EIA930_original_demand_mw.notna()]
    c=df.cold;h=df.high
    winter=df[df.month.isin([11,12,1,2,3])]
    estimate,n=mh(df);winter_estimate,wn=mh(winter)
    return dict(ba=ba,variant=variant,source_rows=len(original),
        valid_demand_hours=len(df),
        missing_demand_hours=int(original.EIA930_original_demand_mw.isna().sum()),
        cold_hours=int(c.sum()),high_load_hours=int(h.sum()),
        cold_high_load_hours=int((c&h).sum()),
        cold_high_rate=float((c&h).sum()/c.sum()) if c.sum() else None,
        noncold_high_rate=float((~c&h).sum()/(~c).sum()) if (~c).sum() else None,
        MH_OR_monthyear=estimate,informative_monthyears=n,
        winter_MH_OR_monthyear=winter_estimate,
        winter_informative_monthyears=wn,
        geography_approved=False,causal=False)

def analyze(source_zip,out_dir):
    source_zip=Path(source_zip);out_dir=Path(out_dir)
    if out_dir.exists():raise FileExistsError("Refuse overwrite")
    if hashlib.sha256(source_zip.read_bytes()).hexdigest()!=ARCHIVE_SHA:
        raise ValueError("Archived source hash mismatch")
    with zipfile.ZipFile(source_zip) as z:raw=z.read(MEMBER)
    if hashlib.sha256(raw).hexdigest()!=GZIP_SHA:
        raise ValueError("Archived source member mismatch")
    df=pd.read_csv(gzip.open(io.BytesIO(raw)),parse_dates=["timestamp_utc_start"])
    if len(df)!=210432 or set(df.ba)!={"AZPS","BPAT","CISO","SRP"}:
        raise ValueError("Source 4-BA cohort coverage changed")
    if df.duplicated(["ba","timestamp_utc_start"]).any():
        raise ValueError("Duplicate BA-UTC hour")
    if df.geometry_historically_approved.any() or df.model_training_eligible.any():
        raise ValueError("Unexpected source scientific admission state")
    if df.ERA5_2m_candidate_area_temperature_c.isna().any():
        raise ValueError("Temperature source missing")
    df["year"]=df.timestamp_utc_start.dt.year
    df["month"]=df.timestamp_utc_start.dt.month
    df["hour"]=df.timestamp_utc_start.dt.hour
    df["cold"]=(df.ERA5_2m_candidate_area_temperature_c -
        df.groupby(["ba","year","month","hour"]).ERA5_2m_candidate_area_temperature_c.transform("mean")<=-5)
    df["threshold95"]=df.groupby(["ba","year","month"]).EIA930_original_demand_mw.transform(
        lambda x:x.quantile(.95))
    df["high"]=df.EIA930_original_demand_mw>df.threshold95
    summaries=[];leave_year=[]
    for ba,b in df.groupby("ba"):
        summaries.append(summary(b,ba,"original_all_valid_source_hours",b))
        summaries.append(summary(b[~b.EIA930_anomaly_candidate_not_confirmed],
                 ba,"source_anomaly_candidates_excluded_exploratory_only",b))
        for yr in range(2020,2026):
            leave_year.append(summary(b[b.year!=yr],ba,"omit_year_"+str(yr),b))
    out_dir.mkdir(parents=True)
    pd.DataFrame(summaries).to_csv(out_dir/"four_BA_cold_load_monthyear_stratified.csv",index=False)
    pd.DataFrame(leave_year).to_csv(out_dir/"four_BA_leave_one_year_out.csv",index=False)
    quality=df.groupby("ba").agg(
        source_hours=("ba","size"),
        missing_demand=("EIA930_original_demand_mw",lambda v:int(v.isna().sum())),
        flagged_anomaly_candidates=("EIA930_anomaly_candidate_not_confirmed","sum"),
        temp_missing=("ERA5_2m_candidate_area_temperature_c",lambda v:int(v.isna().sum())))
    quality.to_csv(out_dir/"four_BA_original_source_quality.csv")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out_dir.glob("*.csv")}
    (out_dir/"SOURCE_AND_LIMITATIONS.json").write_text(json.dumps(dict(
        source_archive_sha256=ARCHIVE_SHA,
        source_member_sha256=GZIP_SHA,source_rows=len(df),
        output_sha256=hashes,geography_approved=False,
        causal_inference_permitted=False,model_training_permitted=False),indent=2)+"\n")
    return summaries

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(analyze(a.source_zip,a.out),indent=2))
