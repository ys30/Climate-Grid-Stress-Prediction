#!/usr/bin/env python3
"""Strict BPAT original EIA930 vs non-imputed PUDL FERC714 respondent 21 comparison.
Diagnostic only. FERC source remains unverified until authentic rows are obtained.
"""
import argparse,csv,hashlib,json,math
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path

EIA_SHA="65e51c15227eb9aae84ce65b35038ea458fd8e2fdb6c9608211268e8291761bc"
YEARS={2020:8784,2021:8760,2022:8760,2023:8760,2024:8784,2025:8760}
EIA_FIELDS={"timestamp_utc_start","EIA930_original_demand_mw",
            "EIA930_demand_missing","EIA930_anomaly_candidate_not_confirmed"}
FERC_FIELDS={"respondent_id_ferc714","report_date","datetime_utc","demand_mwh"}

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as fh:
        for buf in iter(lambda:fh.read(1048576),b""):h.update(buf)
    return h.hexdigest()

def utc(value):
    t=datetime.fromisoformat(str(value).replace("Z","+00:00"))
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)

def read_eia(path):
    if sha256(path)!=EIA_SHA:
        raise ValueError("Archived EIA-930 baseline SHA-256 mismatch")
    hourly={};years=Counter()
    with open(path,encoding="utf-8",newline="") as fh:
        rd=csv.DictReader(fh)
        if not EIA_FIELDS.issubset(rd.fieldnames or []):
            raise ValueError("EIA-930 schema mismatch")
        for row in rd:
            stamp=utc(row["timestamp_utc_start"])
            if stamp.minute or stamp.second or stamp.microsecond or stamp in hourly:
                raise ValueError("Duplicate or non-hourly EIA UTC timestamp")
            value=float(row["EIA930_original_demand_mw"])
            if (not math.isfinite(value) or value<=0 or
                row["EIA930_demand_missing"]!="False" or
                row["EIA930_anomaly_candidate_not_confirmed"]!="False"):
                raise ValueError("EIA demand invalid or source-flagged")
            hourly[stamp]=value;years[stamp.year]+=1
    if dict(years)!=YEARS or len(hourly)!=52608:
        raise ValueError("EIA-930 six-year coverage mismatch")
    return hourly

def read_ferc(path):
    hourly={};counts=Counter();nulls=Counter();spill=Counter()
    with open(path,encoding="utf-8",newline="") as fh:
        rd=csv.DictReader(fh)
        if not FERC_FIELDS.issubset(rd.fieldnames or []):
            raise ValueError("FERC-714 core schema mismatch")
        for row in rd:
            if str(row["respondent_id_ferc714"]).strip()!="21":
                raise ValueError("FERC respondent other than pinned historical BPA ID 21")
            report_year=int(str(row["report_date"])[:4])
            if report_year not in YEARS:
                raise ValueError("FERC outside 2020-2025 reporting cohort")
            stamp=utc(row["datetime_utc"])
            if stamp.minute or stamp.second or stamp.microsecond:
                raise ValueError("Non-hour FERC timestamp")
            key=(report_year,stamp)
            if key in hourly:
                raise ValueError("Duplicate FERC report-year/UTC hour")
            raw=row["demand_mwh"]
            val=None if raw is None or not raw.strip() else float(raw)
            if val is not None and (not math.isfinite(val) or val<0):
                raise ValueError("Invalid FERC demand")
            hourly[key]=val;counts[report_year]+=1
            nulls[report_year]+=int(val is None)
            spill[report_year]+=int(stamp.year!=report_year)
    return hourly,counts,nulls,spill

def calculate(eia,ferc,counts,nulls,spill,eia_hash,ferc_hash,source_url):
    if not source_url.startswith(("https://","s3://")):
        raise ValueError("FERC original/curated source URL required")
    diagnostics=[]
    for yr in sorted(YEARS):
        rows=[(t,val) for (y,t),val in ferc.items() if y==yr and val is not None]
        record={"report_year":yr,"expected_hours":YEARS[yr],
                "FERC_rows":counts[yr],"FERC_missing_demand":nulls[yr],
                "FERC_UTC_year_spillover":spill[yr],
                "FERC_complete_source_hours":counts[yr]==YEARS[yr] and nulls[yr]==0}
        for shift in (-1,0,1):
            pairs=[(val,eia[t+timedelta(hours=shift)]) for t,val in rows
                   if t+timedelta(hours=shift) in eia]
            tag={-1:"minus1h",0:"zero_shift",1:"plus1h"}[shift]
            record[tag+"_matched_hours"]=len(pairs)
            record[tag+"_mae_mw"]=(sum(abs(a-b) for a,b in pairs)/len(pairs) if pairs else None)
            record[tag+"_ferc_minus_eia_bias_mw"]=(sum(a-b for a,b in pairs)/len(pairs) if pairs else None)
        diagnostics.append(record)
    return {"EIA_source_sha256":eia_hash,"FERC_source_sha256":ferc_hash,
            "FERC_source_url":source_url,"FERC_pudl_respondent_id":21,
            "cohort":"FERC report_date year; UTC spillover reported separately",
            "EIA_time_basis":"UTC hour start",
            "FERC_time_basis":"PUDL-normalized UTC, native hour interpretation pending",
            "reference_shift_hours":0,"sensitivity_shift_hours":[-1,1],
            "automatically_select_best_shift":False,
            "FERC_actual_source_independently_authenticated":False,
            "EIA_BA_FERC_planning_area_equivalence_approved":False,
            "model_training_permitted":False,
            "annual_diagnostics":diagnostics}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--eia",type=Path,required=True)
    ap.add_argument("--ferc",type=Path,required=True)
    ap.add_argument("--ferc-source-url",required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError("Refuse to overwrite scientific comparison")
    result=calculate(read_eia(a.eia),*read_ferc(a.ferc),sha256(a.eia),
                     sha256(a.ferc),a.ferc_source_url)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"annual_rows":len(result["annual_diagnostics"]),
                      "model_training_permitted":False},indent=2))
if __name__=="__main__":main()
