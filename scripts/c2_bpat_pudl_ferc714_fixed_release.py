#!/usr/bin/env python3
"""Source-only FERC714 PUDL v2026.10.0 fixed-release BPAT retrieval.

Read immutable published Parquet bytes and keep original hashes. No inference:
metadata respondent candidate(s) must be reviewed by a human before extracting
a single planning-area series; output is never operator-original certified.
"""
import argparse
import hashlib
import json
import re
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

RELEASE = "v2026.10.0"
BASE = "https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/" + RELEASE + "/"
TABLES = ("core_ferc714__respondent_id", "core_ferc714__hourly_planning_area_demand")
NAME = re.compile(r"BONNEVILLE|\bBPA\b", re.IGNORECASE)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for buf in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()

def download(name, root):
    if name not in TABLES:
        raise ValueError("Unapproved original table")
    url = BASE + name + ".parquet"
    dst = root / (name + ".parquet")
    if dst.exists():
        raise FileExistsError("Refuse to overwrite source-original Parquet")
    part = root / (name + ".download-partial")
    if part.exists():
        raise FileExistsError("Partial previous download needs manual cleanup")
    try:
        with urllib.request.urlopen(urllib.request.Request(
                url, headers={"User-Agent": "C2-PUDL-FERC714-audit/1.0"}), timeout=90) as response, part.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk: break
                out.write(chunk)
        if part.stat().st_size < 1000 or part.open("rb").read(4) != b"PAR1":
            raise ValueError("Downloaded bytes are not Parquet")
        with part.open("rb") as fh:
            fh.seek(-4, 2)
            if fh.read(4) != b"PAR1":
                raise ValueError("Incomplete parquet footer")
        part.rename(dst)
        return {"url":url, "sha256":digest(dst), "bytes":dst.stat().st_size,
                "name":dst.name}
    except Exception:
        # Keep failed bytes for explicit diagnosis, but never mark as acquired.
        raise

def audit(respondents, hours, reviewed_respondent_id=None):
    import pyarrow.parquet as pq
    rt = pq.read_table(respondents, columns=[
        "respondent_id_ferc714", "respondent_name_ferc714",
        "respondent_id_ferc714_csv","respondent_id_ferc714_xbrl","eia_code"])
    metadata = rt.to_pylist()
    candidates = [r for r in metadata if NAME.search(str(r.get("respondent_name_ferc714") or ""))]
    # Discovery output is not silently promoted to a unique verified BPAT ID.
    if reviewed_respondent_id is None:
        return {"candidates":candidates, "status":"respondent_review_required",
                "hourly_rows":None,"model_training_permitted":False}
    valid = [r for r in candidates if str(r["respondent_id_ferc714"]) == str(reviewed_respondent_id)]
    if len(valid) != 1:
        raise ValueError("Reviewed respondent ID must uniquely match a BPA-named source record")
    ht = pq.ParquetFile(hours)
    required = {"respondent_id_ferc714", "datetime_utc", "demand_mwh","report_date"}
    if not required <= set(ht.schema.names):
        raise ValueError("FERC core hourly schema missing fields")
    count = Counter()
    missing = Counter()
    seen = set()
    first = None
    last = None
    samples = []
    for batch in ht.iter_batches(batch_size=150000, columns=list(sorted(required))):
        for row in batch.to_pylist():
            if str(row["respondent_id_ferc714"]) != str(reviewed_respondent_id):
                continue
            stamp = row["datetime_utc"]
            if stamp is None:
                raise ValueError("Matched respondent has null time")
            if stamp.tzinfo is not None:
                stamp = stamp.replace(tzinfo=None)
            year = stamp.year
            if year < 2020 or year > 2025:
                continue
            key = stamp.isoformat()
            if key in seen:
                raise ValueError("Duplicate UTC hour in reviewed respondent")
            seen.add(key)
            count[year] += 1
            if row["demand_mwh"] is None: missing[year] += 1
            if first is None or stamp < first: first = stamp
            if last is None or stamp > last: last = stamp
            if len(samples) < 5:
                samples.append({"utc":key, "reported_mwh":row["demand_mwh"]})
    return {"candidates":candidates, "approved_respondent_id":reviewed_respondent_id,
            "status":"PUDL_curated_core_coverage_not_operator_original",
            "hourly_rows":dict(count), "missing_demand":dict(missing),
            "unique_matched_UTC_hours":len(seen),
            "first_UTC":first.isoformat() if first else None,
            "last_UTC":last.isoformat() if last else None,
            "first_five_rows":samples,
            "model_training_permitted":False,
            "bpa_original_XLSX_verified":False,
            "EIA930_full_hourly_comparison_completed":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--reviewed-respondent-id", type=int)
    a=ap.parse_args()
    if a.out.exists():
        raise FileExistsError("Source snapshot directory must not exist")
    a.out.mkdir(parents=True)
    originals=[]
    result={"release":RELEASE,"official_source_pudl":True,
            "bpa_original_XLSX_verified":False,
            "model_training_permitted":False,"download_complete":False,
            "source_originals":[]}
    try:
        for table in TABLES:
            original=download(table,a.out)
            originals.append(original)
            result["source_originals"]=originals
        result["audit"]=audit(a.out/(TABLES[0]+".parquet"),
                             a.out/(TABLES[1]+".parquet"),a.reviewed_respondent_id)
        result["download_complete"]=True
    finally:
        (a.out/"PUDL_FERC714_BPAT_SOURCE_AUDIT_MANIFEST.json").write_text(
            json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
    if a.reviewed_respondent_id is None:
        print("Source metadata obtained; respondent must be explicitly reviewed")
    else:
        print(json.dumps(result["audit"],indent=2,default=str))
if __name__=="__main__":
    main()
