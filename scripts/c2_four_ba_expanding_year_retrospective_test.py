#!/usr/bin/env python3
"""C2 chronological cross-year LOAD scores (not blind climate forecasts)."""
import argparse, gzip, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error,mean_squared_error

ZIP_SHA="bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504"
GZIP_SHA="88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac"
MEMBER="C2_REAL_ERA5_EIA930_2020_2025_ALL_HOURS_GEOGRAPHY_UNAPPROVED.csv.gz"

def sha(b):return hashlib.sha256(b).hexdigest()

def features(d,reference,weather):
    x=[np.ones(len(d)),d.trend.to_numpy(float),d.weekend.to_numpy(float)]
    m=d.month.to_numpy(int)
    x.extend((m==i).astype(float) for i in range(2,13))
    if weather:
        a=d.temp.to_numpy(float)-np.array([reference[int(i)] for i in m])
        x.extend([np.maximum(-a,0),np.maximum(a,0)])
    return np.column_stack(x)

def predict(train,test,target,weather):
    reference=train.groupby("month").temp.mean().to_dict()
    if len(reference)!=12:raise ValueError("Missing training climatology")
    x=features(train,reference,weather);t=features(test,reference,weather)
    scale=StandardScaler()
    x[:,1:]=scale.fit_transform(x[:,1:]);t[:,1:]=scale.transform(t[:,1:])
    model=Ridge(alpha=10.0,fit_intercept=False)
    model.fit(x,train[target].to_numpy(float))
    return model.predict(t)

def run(source,out):
    source=Path(source);out=Path(out)
    if out.exists():raise FileExistsError(out)
    if sha(source.read_bytes())!=ZIP_SHA:raise ValueError("Source ZIP SHA")
    with zipfile.ZipFile(source) as z:raw=z.read(MEMBER)
    if sha(raw)!=GZIP_SHA:raise ValueError("Original member gzip SHA")
    h=pd.read_csv(gzip.open(io.BytesIO(raw)),parse_dates=["timestamp_utc_start"])
    if len(h)!=210432 or h.duplicated(["ba","timestamp_utc_start"]).any():
        raise ValueError("Invalid original source BA-hour cohort")
    if h.geometry_historically_approved.any() or h.model_training_eligible.any():
        raise ValueError("Invalid data admission metadata")
    h["day"]=h.timestamp_utc_start.dt.floor("D")
    d=h.groupby(["ba","day"],as_index=False).agg(
        nload=("EIA930_original_demand_mw","count"),
        ntemp=("ERA5_2m_candidate_area_temperature_c","count"),
        peak=("EIA930_original_demand_mw","max"),
        p95=("EIA930_original_demand_mw",lambda v:v.quantile(.95)),
        mean=("EIA930_original_demand_mw","mean"),
        temp=("ERA5_2m_candidate_area_temperature_c","mean"),
        flagged=("EIA930_anomaly_candidate_not_confirmed","any"))
    d=d[(d.nload==24)&(d.ntemp==24)].copy()
    d["year"]=d.day.dt.year;d["month"]=d.day.dt.month
    d["weekend"]=(d.day.dt.dayofweek>=5).astype(int)
    d["trend"]=(d.day-pd.Timestamp("2020-01-01",tz="UTC")).dt.total_seconds()/(365.25*86400)
    rows=[]
    for ba,b in d.groupby("ba"):
        for testyear in (2023,2024,2025):
            train=b[b.year<testyear];test=b[b.year==testyear]
            if train.empty or test.empty or train.year.max()>=testyear:
                raise ValueError("Temporal leakage")
            for target in ("peak","p95","mean"):
                for weather in (False,True):
                    y=test[target].to_numpy(float)
                    pred=predict(train,test,target,weather)
                    rows.append(dict(ba=ba,test_year=testyear,
                        train_year_last=int(train.year.max()),n_train_days=len(train),
                        n_test_days=len(test),target=target,
                        model="calendar_trend_plus_candidate_ERA5" if weather else "calendar_trend_baseline",
                        test_MAE_MW=float(mean_absolute_error(y,pred)),
                        test_RMSE_MW=float(np.sqrt(mean_squared_error(y,pred))),
                        blind_holdout=False,independent_weather_forecast=False,
                        spatial_proxy_approved=False))
    if len(rows)!=72:raise ValueError("Expected 72 scores")
    out.mkdir(parents=True)
    dst=out/"retrospective_scores.csv"
    pd.DataFrame(rows).to_csv(dst,index=False)
    meta={"origin":"actual original EIA930 and candidate ERA5", "source_zip_SHA256":ZIP_SHA,
        "source_member_SHA256":GZIP_SHA,"scored_rows":72,
        "train_only_climatology_and_scaler":True,
        "previously_inspected_years":True,"blind_forecast":False,
        "weather_geography_approved":False,"formal_model_admission":False,
        "results_SHA256":sha(dst.read_bytes())}
    (out/"MANIFEST.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source-zip",required=True);p.add_argument("--out",required=True)
    a=p.parse_args();print(json.dumps(run(a.source_zip,a.out),indent=2))
