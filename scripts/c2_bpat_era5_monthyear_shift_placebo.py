#!/usr/bin/env python3
"""Exploratory temporal-shift placebo, real BPAT EIA930 × candidate ERA5 source."""
import hashlib,io,gzip,zipfile,json,argparse
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_ZIP_SHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
SOURCE_GZIP_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
SOURCE_MEMBER="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"

def mh(tables):
    ts=np.asarray(tables,dtype=float)
    n=ts.sum(axis=1)
    return float(np.sum(ts[:,0]*ts[:,3]/n)/np.sum(ts[:,1]*ts[:,2]/n))

def contingency(cold,high):
    return [np.sum(cold&high),np.sum(cold&~high),
            np.sum(~cold&high),np.sum(~cold&~high)]

def analyze(source_zip,output,seed=20261126,n_draws=2000):
    source_zip=Path(source_zip);output=Path(output)
    if output.exists():raise FileExistsError("Refuse to overwrite prior source result")
    if hashlib.sha256(source_zip.read_bytes()).hexdigest()!=SOURCE_ZIP_SHA:
        raise ValueError("Source archive SHA mismatch")
    with zipfile.ZipFile(source_zip) as z:raw=z.read(SOURCE_MEMBER)
    if hashlib.sha256(raw).hexdigest()!=SOURCE_GZIP_SHA:
        raise ValueError("Input source gzip SHA mismatch")
    all_ba=pd.read_csv(gzip.open(io.BytesIO(raw)),parse_dates=["timestamp_utc_start"])
    b=all_ba[all_ba.ba=="BPAT"].sort_values("timestamp_utc_start").copy()
    if len(b)!=52608 or not b.timestamp_utc_start.is_unique:
        raise ValueError("Invalid BPAT six-year UTC source coverage")
    b["demand"]=b.EIA930_original_demand_mw.astype(float)
    b["t"]=b.ERA5_2m_candidate_area_temperature_c.astype(float)
    b["year"]=b.timestamp_utc_start.dt.year
    b["month"]=b.timestamp_utc_start.dt.month
    b["hour"]=b.timestamp_utc_start.dt.hour
    b["cold"]=(b.t-b.groupby(["year","month","hour"]).t.transform("mean"))<=-5
    b["high"]=b.demand>b.groupby(["year","month"]).demand.transform(lambda x:x.quantile(.95))
    groups=[]
    for ym,g in b.groupby(["year","month"],sort=True):
        cold=g.cold.to_numpy(dtype=bool);high=g.high.to_numpy(dtype=bool)
        if len(cold)%24:raise ValueError("Incomplete days in source")
        days=len(cold)//24
        options=[contingency(np.roll(cold,lag*24),high)
                 for lag in range(7,days-6)]
        if not options:raise ValueError("Insufficient days for placebo")
        groups.append((contingency(cold,high),np.asarray(options)))
    observed=mh([r for r,_ in groups])
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(n_draws):
        null.append(mh([opts[rng.integers(len(opts))] for _,opts in groups]))
    null=np.asarray(null)
    result={"source_type":"real EIA930 load and candidate ERA5 temperature",
      "status":"EXPLORATORY_TEMPORAL_PLACEBO_NOT_CAUSAL",
      "observed_MH_OR":observed,"placebo_median_MH_OR":float(np.median(null)),
      "placebo_q025":float(np.quantile(null,.025)),
      "placebo_q975":float(np.quantile(null,.975)),
      "placebo_max":float(null.max()),
      "placebo_exceedance_draws":int(np.sum(null>=observed)),
      "corrected_exceedance_fraction":float((np.sum(null>=observed)+1)/(n_draws+1)),
      "placebo_draws":n_draws,"rng_seed":seed,
      "null_method":"independent within year-month circular shifts of candidate cold exposure 7..days-7 whole days; outcome fixed",
      "source_zip_sha256":SOURCE_ZIP_SHA,"source_gzip_sha256":SOURCE_GZIP_SHA,
      "candidate_BA_weather_geography_approved":False,
      "causal_or_confirmatory_p_value":False,
      "model_training_permitted":False,
      "limitations":"within-month wrapped shifts split real multi-day cold spells at month boundaries"}
    output.mkdir(parents=True)
    pd.DataFrame({"draw":np.arange(1,n_draws+1),"placebo_MH_OR":null}).to_csv(output/"placebo_draws.csv",index=False)
    (output/"SUMMARY.json").write_text(json.dumps(result,indent=2)+"\n")
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    print(json.dumps(analyze(args.source_zip,args.out),indent=2))
