#!/usr/bin/env python3
"""Four-BA authentic EIA930 daily peak/P95/mean target sensitivity (NONCAUSAL)."""
import argparse, gzip, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ARCHIVE_SHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
GZIP_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
MEMBER="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def estimate(g,target):
    g=g.copy()
    keys=["year","month"]
    g["response"]=g[target]-g.groupby(keys)[target].transform("mean")
    g["temp_anomaly"]=g.temp-g.groupby(keys).temp.transform("mean")
    for col,x in [("cold",np.maximum(-g.temp_anomaly,0.)),("warm",np.maximum(g.temp_anomaly,0.))]:
        g[col]=x-x.groupby([g.year,g.month]).transform("mean")
    X=g[["cold","warm"]].to_numpy(float)
    y=g.response.to_numpy(float)
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    rmse=float(np.sqrt(np.mean((y-X@beta)**2)))
    return float(beta[0]),float(beta[1]),rmse

def main(source,out):
    source=Path(source);out=Path(out)
    if out.exists(): raise FileExistsError("Refusing overwrite")
    if sha(source.read_bytes())!=ARCHIVE_SHA: raise ValueError("Source ZIP hash")
    with zipfile.ZipFile(source) as z:
        gz=z.read(MEMBER)
    if sha(gz)!=GZIP_SHA: raise ValueError("Source gzip hash")
    h=pd.read_csv(gzip.open(io.BytesIO(gz)),parse_dates=["timestamp_utc_start"])
    if len(h)!=210432 or h.duplicated(["ba","timestamp_utc_start"]).any():
        raise ValueError("Unexpected BA-hour count or duplicates")
    if h.geometry_historically_approved.any() or h.model_training_eligible.any():
        raise ValueError("Invalid exposure admission")
    h["day"]=h.timestamp_utc_start.dt.floor("D")
    d=h.groupby(["ba","day"],as_index=False).agg(
        count=("EIA930_original_demand_mw","count"),
        temperature_count=("ERA5_2m_candidate_area_temperature_c","count"),
        peak=("EIA930_original_demand_mw","max"),
        p95=("EIA930_original_demand_mw",lambda x:x.quantile(.95)),
        mean=("EIA930_original_demand_mw","mean"),
        temp=("ERA5_2m_candidate_area_temperature_c","mean"),
        flagged=("EIA930_anomaly_candidate_not_confirmed","any"))
    d=d[(d["count"]==24)&(d.temperature_count==24)].copy()
    d["year"]=d.day.dt.year;d["month"]=d.day.dt.month
    d["season"]=np.where(d.month.isin([11,12,1,2,3]),"winter_Nov_Mar","nonwinter_Apr_Oct")
    records=[]
    for (ba,season),g in d.groupby(["ba","season"]):
        for target in ("peak","p95","mean"):
            for scenario,sub in (("all_original_complete_days",g),
                   ("source_flagged_days_excluded_sensitivity",g[~g.flagged])):
                cold,warm,rmse=estimate(sub,target)
                records.append(dict(ba=ba,season=season,target=target,variant=scenario,
                    days=len(sub),cold_association_MW_per_C=cold,warm_association_MW_per_C=warm,
                    rmse_MW=rmse,causal=False,weather_geography_approved=False))
    if len(records)!=48:raise ValueError("Unexpected model grid")
    out.mkdir(parents=True)
    dst=out/"four_ba_daily_target_raw_vs_flagged_sensitivity.csv"
    pd.DataFrame(records).to_csv(dst,index=False)
    manifest=dict(source_zip_sha256=ARCHIVE_SHA,source_member_sha256=GZIP_SHA,
        source_hour_count=210432,verified_daily_analytic_days=len(d),model_scenarios=48,
        primary_observations_untouched=True,weather_geography_approved=False,
        causal_inference_permitted=False,model_training_permitted=False,
        output_csv_sha256=sha(dst.read_bytes()))
    (out/"SOURCE_MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    print(json.dumps(main(a.source_zip,a.out),indent=2))
