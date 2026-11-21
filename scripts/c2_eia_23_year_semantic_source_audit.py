"""Real source-only EIA-930 content scan of all 23 canonical-pass BA-years.

Independent annual ZIPs must pass pinned SHA, canonical coverage manifest,
raw hour-ending clock alignment, and strict expected UTC key counts.
Flags zero demand and optional low-positive review; no value editing or
model fitting. AZPS2023 remains a distinct canonical source failure.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from pathlib import Path

BAS=("AZPS","BPAT","CISO","SRP")
YEARS=range(2020,2026)
LOW_REVIEW_MW=1000
WAVES=("WAVE1","WAVE2","WAVE3")

def digest(b):return hashlib.sha256(b).hexdigest()

def approved_cohorts(directory):
    entries={}
    for w in WAVES:
        data=json.loads((directory/f"E2_{w}_VERIFIED_STATUS.json").read_text())
        for c in data["cohorts"]:
            key=(c["ba"],int(c["year"]))
            if key in entries:raise ValueError("Duplicate BA-year in annual source ledger")
            entries[key]=c
    if ("CISO",2024) in entries:
        raise ValueError("CISO 2024 separate verified pilot double counted")
    entries[("CISO",2024)]={
        "ba":"CISO","year":2024,"gate_pass":True,
        "status":"independent_CISO2024_real_source_pilot",
        "csv_sha256":"375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c",
        "missing_hours":0,"missing_demand_rows":0,"valid_demand_hours":8784,
        "expected_hours":8784,"unique_hours":8784}
    if set(entries)!={(b,y) for b in BAS for y in YEARS}:
        raise ValueError("Expected four BAs over six years")
    passed={k:v for k,v in entries.items() if v.get("gate_pass") is True}
    if len(passed)!=23 or set(entries)-set(passed)!={("AZPS",2023)}:
        raise ValueError("23 canonical BA-year admission manifest changed")
    return passed

def check_year(archive,ba,year,c):
    base=f"eia930_{ba}_{year}"
    with zipfile.ZipFile(archive) as z:
        raw=z.read(f"raw/{base}_he.csv")
        shifted=z.read(f"utc_start/{base}_start.csv")
        rm=json.loads(z.read(f"raw/{base}_he.manifest.json"))
        cm=json.loads(z.read(f"utc_start/{base}_start.manifest.json"))
        qa=json.loads(z.read(f"audit/{base}_coverage.json"))
    if (digest(raw)!=rm.get("sha256_csv") or digest(shifted)!=cm.get("sha256_csv") or
        cm.get("input_sha256")!=digest(raw) or
        cm.get("sha256_csv")!=c["csv_sha256"] or
        qa.get("source_sha256")!=c["csv_sha256"] or qa.get("pass") is not True):
        raise ValueError(f"{base}: source sha or annual QA differs")
    if c.get("raw_sha256") is not None and c["raw_sha256"]!=digest(raw):
        raise ValueError(f"{base}: raw source differs from archived annual ledger")
    if c.get("expected_hours")!=qa.get("expected_hours") or (
        c.get("unique_hours")!=qa.get("unique_in_year")):
        raise ValueError(f"{base}: annual source coverage mismatch")
    raw_he={}
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        key=row["source_period_utc"]
        if key in raw_he:raise ValueError(f"{base}: duplicate original raw HE")
        raw_he[key]=row["reported_demand_mw"]
    observed=set();null=0;flags=[]
    for row in csv.DictReader(io.StringIO(shifted.decode("utf-8-sig"))):
        key=row["timestamp_utc"]
        if key in observed:raise ValueError(f"{base}: duplicate converted UTC key")
        observed.add(key)
        t=datetime.strptime(key,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        he=(t+timedelta(hours=1)).strftime("%Y-%m-%dT%H")
        v=row["demand_mw"]
        if row["ba"]!=ba or row["original_source_he_utc"]!=he or raw_he.get(he)!=v:
            raise ValueError(f"{base}: raw HE and derived converted demand disagreement")
        if not v.strip():
            null+=1;continue
        x=float(v)
        if not math.isfinite(x) or x<0:
            raise ValueError(f"{base}: invalid numeric despite canonical source QA")
        if x==0 or 0<x<LOW_REVIEW_MW:
            flags.append({"ba":ba,"year":year,"timestamp_utc":key,
                         "original_HE_utc":he,"reported_demand_mw":x,
                         "source_flag":"EIA_zero_demand_review" if x==0
                              else "exploratory_low_positive_review",
                         "low_threshold_official":False,
                         "model_eligible":False})
    first=datetime(year,1,1,tzinfo=timezone.utc)
    total=int((datetime(year+1,1,1,tzinfo=timezone.utc)-first).total_seconds()/3600)
    expected={(first+timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
              for i in range(total)}
    if not observed.issubset(expected):raise ValueError("Out-of-year converted time key")
    missing=len(expected-observed)
    if (total!=c["expected_hours"] or
        len(observed)!=c["unique_hours"] or
        null!=c["missing_demand_rows"] or missing!=c["missing_hours"]):
        raise ValueError(f"{base}: missing time keys and null demand rows not reconciled")
    return {"ba":ba,"year":year,"expected_hours":total,"observed_keys":len(observed),
            "absent_utc_keys":missing,"observed_null_demand":null,
            "zero_demand":sum(f["source_flag"]=="EIA_zero_demand_review" for f in flags),
            "low_positive_review":sum(f["source_flag"]=="exploratory_low_positive_review" for f in flags),
            "raw_sha256":digest(raw),"converted_sha256":digest(shifted)},flags

def scan(archives,ledger):
    cohorts=approved_cohorts(ledger)
    if set(archives)!=set(cohorts):raise ValueError("Expected exact 23 canonical-pass source ZIPs")
    results=[];flags=[]
    for (ba,year),entry in sorted(cohorts.items()):
        result,rows=check_year(archives[(ba,year)],ba,year,entry)
        results.append(result);flags.extend(rows)
    total=sum(r["expected_hours"] for r in results)
    if total!=201672 or sum(r["zero_demand"] for r in results)!=1 or sum(
        r["low_positive_review"] for r in results)!=2:
        raise ValueError("Original verified 23-year source semantic QA baseline changed")
    return {"status":"CANONICAL_SOURCE_COMPLETE_NOT_SEMANTIC_OR_MODEL_APPROVAL",
            "BA_years":23,"expected_hours":total,
            "observed_hours":sum(r["observed_keys"] for r in results),
            "absent_time_keys":sum(r["absent_utc_keys"] for r in results),
            "null_demand_rows":sum(r["observed_null_demand"] for r in results),
            "zero_demand_hours":1,"exploratory_low_positive_hours":2,
            "review_threshold_mw":LOW_REVIEW_MW,
            "review_threshold_is_official":False,
            "only_known_zero_low_cohort":"AZPS_2025",
            "source_values_modified":False,
            "historical_BA_geography_approved":False,
            "model_training_permitted":False,
            "2024_2025_used_for_model_selection":False,
            "per_BA_year":results,"review_rows":flags}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archives",type=Path,required=True,
                   help="Directory of 23 original ZIPs named BA_YEAR.zip")
    p.add_argument("--ledger",type=Path,default=Path("docs"))
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("No overwrite of observational evidence")
    cohorts=approved_cohorts(a.ledger)
    archives={(ba,y):a.archives/f"{ba}_{y}.zip" for ba,y in cohorts}
    result=scan(archives,a.ledger)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in (
        "BA_years","expected_hours","absent_time_keys","null_demand_rows",
        "zero_demand_hours","exploratory_low_positive_hours","model_training_permitted")},indent=2))

if __name__=="__main__":main()
