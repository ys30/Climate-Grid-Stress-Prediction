"""Nonwrapped paired-sample cold-load lag sensitivity on SHA-pinned original BPAT sources.

Method only: real source, unapproved ERA5 BA geography; not causal inference.
"""
import argparse,gzip,hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd

ARCHIVE_SHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
MEMBER="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"
MEMBER_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"

def mh(tables):
    x=np.asarray(tables,dtype=float)
    n=x.sum(axis=1)
    return float((x[:,0]*x[:,3]/n).sum()/(x[:,1]*x[:,2]/n).sum())

def table(c,h):
    return [int(np.sum(c&h)),int(np.sum(c&~h)),int(np.sum(~c&h)),int(np.sum(~c&~h))]

def analyze(source,out):
    source=Path(source);out=Path(out)
    if out.exists():raise FileExistsError("Refuse previous source result overwrite")
    if hashlib.sha256(source.read_bytes()).hexdigest()!=ARCHIVE_SHA:
        raise ValueError("Source ZIP SHA-256 mismatch")
    with zipfile.ZipFile(source) as z:raw=z.read(MEMBER)
    if hashlib.sha256(raw).hexdigest()!=MEMBER_SHA:
        raise ValueError("Original source gzip SHA-256 mismatch")
    df=pd.read_csv(gzip.open(io.BytesIO(raw)),parse_dates=["timestamp_utc_start"])
    b=df[df.ba=="BPAT"].sort_values("timestamp_utc_start").copy()
    if len(b)!=52608 or not b.timestamp_utc_start.is_unique:
        raise ValueError("BPAT source incomplete or duplicate UTC hour")
    b["year"]=b.timestamp_utc_start.dt.year
    b["month"]=b.timestamp_utc_start.dt.month
    b["hour"]=b.timestamp_utc_start.dt.hour
    b["temp"]=b.ERA5_2m_candidate_area_temperature_c.astype(float)
    b["load"]=b.EIA930_original_demand_mw.astype(float)
    b["cold"]=(b.temp-b.groupby(["year","month","hour"]).temp.transform("mean")<=-5)
    b["high"]=b.load>b.groupby(["year","month"]).load.transform(lambda x:x.quantile(.95))
    groups=[(x.cold.to_numpy(bool),x.high.to_numpy(bool))
            for _,x in b.groupby(["year","month"])]
    results=[]
    for days in (3,5,7,10,14):
        for direction in (-1,1):
            zero=[];shifted=[];matched=0;high_hours=0;step=24*days
            for c,h in groups:
                if direction==1:
                    x=c[:-step];y=h[step:];z=c[step:]
                else:
                    x=c[step:];y=h[:-step];z=c[:-step]
                zero.append(table(z,y));shifted.append(table(x,y))
                matched+=len(y);high_hours+=int(y.sum())
            raw_or=mh(zero);offset_or=mh(shifted)
            results.append(dict(offset_days=days*direction,matched_hours=matched,
                matched_high_hours=high_hours,paired_zero_lag_MH_OR=raw_or,
                nonwrapped_shift_MH_OR=offset_or,zero_lag_div_shift=raw_or/offset_or,
                spatial_proxy_approved=False))
    out.mkdir(parents=True)
    dfout=pd.DataFrame(results)
    dfout.to_csv(out/"nonwrapped_lag_pairs.csv",index=False)
    (out/"MANIFEST.json").write_text(json.dumps({
        "source_zip_sha256":ARCHIVE_SHA,"member_gzip_sha256":MEMBER_SHA,
        "source_rows":len(b),"method":"Within each year-month use ±3/5/7/10/14 days, never wrap; compare lag and zero-lag OR on same load-hour support",
        "spatial_proxy_approved":False,"causal_attribution_approved":False,
        "results":results},indent=2)+"\n")
    return results

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",required=True)
    p.add_argument("--out",required=True)
    x=p.parse_args()
    print(json.dumps(analyze(x.source_zip,x.out),indent=2))
