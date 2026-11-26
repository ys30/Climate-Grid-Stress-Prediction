#!/usr/bin/env python3
"""Cross-check historical Bonneville FERC714 respondent identity against pinned PUDL glue.

Historical respondent-name CSV is a public third-party copy of legacy FERC data.
PUDL glue is a separate maintained cross-era mapping. Does NOT download hourly
data or certify current v2026.10.0 respondents or BA operational territory.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path

LEGACY_BLOB="2472dfbd531857969cfaf16e6dbc2d0fba6552bd"
PUDL_BLOB="3eb0291e51502df9a5fca38e9f3ac4ebf3526ad7"
LEGACY_FIELDS=("respondent_id","respondent_name","eia_code","nerc")
PUDL_FIELDS=("respondent_id_ferc714","respondent_id_ferc714_xbrl",
             "respondent_id_ferc714_csv","Source","Notes")

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()

def parse_rows(raw, expected):
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if tuple(reader.fieldnames or ()) != expected:
        raise ValueError("Unexpected published source headers")
    rows=list(reader)
    if any(None in r or any(k not in expected for k in r) for r in rows):
        raise ValueError("Malformed source CSV")
    return rows

def reconcile(legacy_rows, pudl_rows):
    # Require a unique real-world name + historical ID + numeric EIA reference.
    match=[r for r in legacy_rows if "BONNEVILLE POWER ADMINISTRATION" in r["respondent_name"].upper()]
    if len(match)!=1:
        raise ValueError("Legacy Bonneville respondent must have exactly one source row")
    old=match[0]
    if old["respondent_id"].strip()!="122" or old["eia_code"].strip()!="1738":
        raise ValueError("Unexpected historical Bonneville FERC/EIA identity")
    candidates=[r for r in pudl_rows
                if r["respondent_id_ferc714_csv"].strip()==old["respondent_id"].strip()]
    if len(candidates)!=1:
        raise ValueError("Legacy respondent ID maps to zero or multiple PUDL respondents")
    cur=candidates[0]
    if cur["respondent_id_ferc714"].strip()!="21" or cur["respondent_id_ferc714_xbrl"].strip()!="C002357":
        raise ValueError("Unexpected published cross-era mapping for Bonneville")
    return {
        "name":old["respondent_name"].strip(),"ferc714_csv_respondent_id":122,
        "eia_numeric_id":1738,"pudl_respondent_id_ferc714":21,
        "ferc714_xbrl_respondent_id":"C002357",
        "eia930_BA_code":"BPAT",
        "eia930_BA_code_source":"EPA eGRID code lookup, cross-reference by Bonneville name",
        "legacy_source_provenance":"third-party archived copy of historic FERC714 IDs",
        "pudl_crosswalk_provenance":"PUDL fixed Git commit respondent glue CSV",
        "historical_cross_format_candidate_correspondence_supported":True,
        "pudl_2026_10_core_respondent_metadata_verified":False,
        "2020_2025_hourly_FERC714_available_verified":False,
        "operational_BA_scope_equivalence_verified":False,
        "model_training_permitted":False,
    }

def audit(legacy_bytes,pudl_bytes):
    if git_blob(legacy_bytes)!=LEGACY_BLOB:
        raise ValueError("Historical FERC respondent source Git blob does not match pinned")
    if git_blob(pudl_bytes)!=PUDL_BLOB:
        raise ValueError("PUDL respondent glue Git blob does not match pinned")
    legacy=parse_rows(legacy_bytes,LEGACY_FIELDS)
    pudl=parse_rows(pudl_bytes,PUDL_FIELDS)
    result=reconcile(legacy,pudl)
    result.update({
        "source_legacy_git_blob_sha1":LEGACY_BLOB,
        "source_pudl_glue_git_blob_sha1":PUDL_BLOB,
        "legacy_archive_rows":len(legacy),
        "pudl_glue_rows":len(pudl),
        "source_legacy_sha256":hashlib.sha256(legacy_bytes).hexdigest(),
        "source_pudl_sha256":hashlib.sha256(pudl_bytes).hexdigest(),
    })
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--legacy",type=Path,default=Path("data/source_only/FERC714_Respondent_IDs_historical_tdeetjen_84f14fa.csv"))
    p.add_argument("--pudl",type=Path,default=Path("data/source_only/PUDL_ferc714_respondent_csv_xbrl_glue_97874c2.csv"))
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():
        raise FileExistsError("Never overwrite a prior source audit")
    result=audit(a.legacy.read_bytes(),a.pudl.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
