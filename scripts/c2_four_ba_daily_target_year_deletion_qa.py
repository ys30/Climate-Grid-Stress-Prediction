#!/usr/bin/env python3
"""C2 four-BA 336-fit year-deletion sensitivity. Original source, NOT forecast validation."""
import argparse,gzip,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
ZSHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
GSHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
MEM="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"
def sha(b):return hashlib.sha256(b).hexdigest()
def estimate(g,k):
    group=["year","month"]
    y=(g[k]-g.groupby(group)[k].transform("mean")).to_numpy(float)
    t=g.temp-g.groupby(group).temp.transform("mean")
    cold=np.maximum(-t,0);warm=np.maximum(t,0)
    cold=cold-cold.groupby([g.year,g.month]).transform("mean")
    warm=warm-warm.groupby([g.year,g.month]).transform("mean")
    x=np.column_stack([cold.to_numpy(),warm.to_numpy()])
    beta=np.linalg.lstsq(x,y,rcond=None)[0]
    return float(beta[0]),float(beta[1]),float(np.sqrt(np.mean((y-x@beta)**2)))
def run(source,out):
    source=Path(source);out=Path(out)
    if out.exists():raise FileExistsError("Cannot overwrite original evidence")
    if sha(source.read_bytes())!=ZSHA:raise ValueError("Wrong source ZIP hash")
    with zipfile.ZipFile(source) as f:blob=f.read(MEM)
    if sha(blob)!=GSHA:raise ValueError("Wrong original source member hash")
    h=pd.read_csv(gzip.open(io.BytesIO(blob)),parse_dates=["timestamp_utc_start"])
    if len(h)!=210432 or h.duplicated(["ba","timestamp_utc_start"]).any():
        raise ValueError("Unexpected original source BA-hour cohort")
    if h.geometry_historically_approved.any() or h.model_training_eligible.any():
        raise ValueError("Data source not eligible for model admission")
    h["utc_date"]=h.timestamp_utc_start.dt.floor("D")
    d=h.groupby(["ba","utc_date"],as_index=False).agg(
       n=("EIA930_original_demand_mw","count"),nt=("ERA5_2m_candidate_area_temperature_c","count"),
       peak=("EIA930_original_demand_mw","max"),
       p95=("EIA930_original_demand_mw",lambda s:s.quantile(.95)),
       mean=("EIA930_original_demand_mw","mean"),
       temp=("ERA5_2m_candidate_area_temperature_c","mean"),
       flag=("EIA930_anomaly_candidate_not_confirmed","any"))
    d=d[(d.n==24)&(d.nt==24)].copy()
    d["year"]=d.utc_date.dt.year;d["month"]=d.utc_date.dt.month
    d["season"]=np.where(d.month.isin([11,12,1,2,3]),"winter_Nov_Mar","nonwinter_Apr_Oct")
    rows=[]
    for (ba,season),g in d.groupby(["ba","season"]):
      for target in ("peak","p95","mean"):
       for variant,group in (("original",g),("exclude_source_flagged_days_sensitivity",g[~g.flag])):
        full=estimate(group,target)
        for omitted in (None,2020,2021,2022,2023,2024,2025):
         sub=group if omitted is None else group[group.year!=omitted]
         co=estimate(sub,target)
         rows.append(dict(ba=ba,season=season,target=target,variant=variant,
           omitted_year="NONE" if omitted is None else str(omitted),
           n_days=len(sub),cold_MW_per_C=co[0],warm_MW_per_C=co[1],
           rmse_MW=co[2],cold_delta_vs_full=co[0]-full[0],
           weather_mask_approved=False,causal=False))
    if len(rows)!=336:raise ValueError("Unexpected estimator grid")
    out.mkdir(parents=True)
    dest=out/"four_ba_daily_target_leave_one_year_out_336.csv"
    pd.DataFrame(rows).to_csv(dest,index=False,float_format="%.10g")
    manifest=dict(zip_sha256=ZSHA,member_gzip_sha256=GSHA,source_hours=210432,
       valid_UTC_days=len(d),fits=336,original_untouched=True,
       year_deletion_is_blind_forecast_validation=False,weather_mask_approved=False,
       causal_estimation_permitted=False,output_sha256=sha(dest.read_bytes()))
    (out/"MANIFEST.json").write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--source-zip",required=True);a.add_argument("--out",required=True)
    x=a.parse_args();print(json.dumps(run(x.source_zip,x.out),indent=2))
