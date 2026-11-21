"""Independent EIA-930 AZPS 2025 observed-demand semantic QA (source-only).

Reads pinned official EIA-930 *raw HE* and UTC-start CSV from published
Actions ZIP. Never imputes, overwrites, estimates model skill, or admits
a weather-demand model. A zero is EIA's documented anomaly class;
positive values <1000 MW are review flags only, NOT proven errors.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,zipfile
from datetime import datetime,timedelta
from pathlib import Path

BA="AZPS"
YEAR=2025
SOURCE_SHA="f889acd93499bf9336b0447b0e7de650361f4730ae64c5cce7e023650da02110"
RAW_SHA="a4c1b381ff9ab3efe573fbc5a19643329ea572ab4c045eb1441f047dc659ee16"
LOW_REVIEW_MW=1000  # exploratory review queue only; not authoritative cutoff

def sha(data):
    return hashlib.sha256(data).hexdigest()

def audit(archive_path):
    with zipfile.ZipFile(archive_path) as z:
        base=f"eia930_{BA}_{YEAR}"
        raw=z.read(f"raw/{base}_he.csv")
        shifted=z.read(f"utc_start/{base}_start.csv")
        rawmeta=json.loads(z.read(f"raw/{base}_he.manifest.json"))
        shiftedmeta=json.loads(z.read(f"utc_start/{base}_start.manifest.json"))
        qa=json.loads(z.read(f"audit/{base}_coverage.json"))
    if (sha(raw)!=RAW_SHA or sha(shifted)!=SOURCE_SHA or
        rawmeta.get("sha256_csv")!=RAW_SHA or
        shiftedmeta.get("sha256_csv")!=SOURCE_SHA or
        shiftedmeta.get("input_sha256")!=RAW_SHA or
        qa.get("source_sha256")!=SOURCE_SHA):
        raise ValueError("Actual original EIA sources or manifests fail SHA contract")
    if not (qa.get("pass") is True and qa.get("rows")==8760
            and qa.get("unique_in_year")==8760 and qa.get("missing_hours")==0):
        raise ValueError("Original EIA annual source gate inconsistent")
    orig={}
    for row in csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))):
        label=row["source_period_utc"]
        if label in orig:
            raise ValueError("Duplicate raw HE time label")
        orig[label]=row["reported_demand_mw"]
    rows=list(csv.DictReader(io.StringIO(shifted.decode("utf-8-sig"))))
    if len(rows)!=8760:
        raise ValueError("Not complete AZPS 2025 source year")
    seen=set()
    flagged=[]
    for idx,row in enumerate(rows):
        t=row["timestamp_utc"]
        if t in seen:raise ValueError("Duplicate UTC-start time")
        seen.add(t)
        dt=datetime.strptime(t,"%Y-%m-%dT%H:%M:%SZ")
        source_he=(dt+timedelta(hours=1)).strftime("%Y-%m-%dT%H")
        if (row["ba"]!=BA or row["original_source_he_utc"]!=source_he
            or orig.get(source_he)!=row["demand_mw"]):
            raise ValueError("Raw EIA source and converted hourly demand differ")
        v=float(row["demand_mw"])
        if not math.isfinite(v) or v<0:
            raise ValueError("AZPS 2025 current original numeric assumption failed")
        kinds=[]
        if v==0:kinds.append("eia_zero_demand_anomaly")
        elif 0<v<LOW_REVIEW_MW:kinds.append("exploratory_low_positive_review_only")
        if kinds:
            prev=float(rows[idx-1]["demand_mw"]) if idx>0 else None
            nextval=float(rows[idx+1]["demand_mw"]) if idx+1<len(rows) else None
            flagged.append({"timestamp_utc":t,"reported_demand_mw":v,
                            "raw_hour_ending_label":source_he,
                            "prior_reported_demand_mw":prev,
                            "next_reported_demand_mw":nextval,
                            "flags":kinds})
    zero=sum("eia_zero_demand_anomaly" in r["flags"] for r in flagged)
    low=sum("exploratory_low_positive_review_only" in r["flags"] for r in flagged)
    if zero!=1:
        raise ValueError("Known zero-demand original source discrepancy changed")
    return {
        "project":"C2","status":"EIA_SOURCE_COVERAGE_PASS_SEMANTIC_QA_FAIL",
        "source_run_id":0, # source artifact identity pinned separately below
        "source_artifact_id":14497859928,
        "source_csv_sha256":SOURCE_SHA,
        "raw_csv_sha256":RAW_SHA,
        "year":YEAR,"ba":BA,
        "source_hourly_keys":len(rows),"source_year_coverage_pass":True,
        "eia_zero_demand_hours":zero,
        "low_positive_review_threshold_mw":LOW_REVIEW_MW,
        "low_positive_review_hours":low,
        "low_positive_threshold_is_an_official_EIA_gate":False,
        "content_based_model_eligibility_pass":False,
        "model_training_permitted":False,
        "model_test_years_examined_for_training_or_tuning":False,
        "source_data_modified":False,
        "observed_source_anomaly_review_queue":flagged,
        "revisions_mechanism_proven":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source_zip",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    if a.output.exists():raise FileExistsError("No overwrite of source-derived diagnostics")
    d=audit(a.source_zip)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({k:d[k] for k in ("status","eia_zero_demand_hours","low_positive_review_hours","model_training_permitted")},indent=2))

if __name__=="__main__":main()
