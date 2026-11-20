"""Forensic consistency audit: original newer EIA HE vs UTC-start and source-vintage revisions.

This audit confirms whether changed/blank values already exist in the
newer raw EIA source. It does NOT prove why vintage revisions happened,
and does not authorize removal, imputation, fitting or held-out evaluation.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path

OLD_NEW_DIFF_SHA="6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480"
TARGETS={"AZPS2025":169,"BPAT2021":26,"BPAT2023":24}


def sha(data):return hashlib.sha256(data).hexdigest()


def episodes(timestamps):
    dates=sorted(datetime.strptime(s,"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                 for s in timestamps)
    if len(dates)!=len(set(dates)):raise ValueError("Duplicate changed UTC timestamps")
    spans=[]
    for t in dates:
        if not spans or t-spans[-1]["last"]!=timedelta(hours=1):
            spans.append({"first":t,"last":t,"hours":1})
        else:
            spans[-1]["last"]=t
            spans[-1]["hours"]+=1
    return [{"start_utc":p["first"].strftime("%Y-%m-%dT%H:%M:%SZ"),
             "end_utc":p["last"].strftime("%Y-%m-%dT%H:%M:%SZ"),
             "hours":p["hours"]} for p in spans]


def verify_one(zip_path,ba,year,changed):
    with zipfile.ZipFile(zip_path) as z:
        folder=f"eia930_{ba}_{year}"
        raw=z.read(f"raw/{folder}_he.csv")
        shifted=z.read(f"utc_start/{folder}_start.csv")
        rawmeta=json.loads(z.read(f"raw/{folder}_he.manifest.json"))
        shiftmeta=json.loads(z.read(f"utc_start/{folder}_start.manifest.json"))
    if sha(raw)!=rawmeta.get("sha256_csv") or sha(shifted)!=shiftmeta.get("sha256_csv"):
        raise ValueError("Source artifact changed: SHA mismatch")
    raw_rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    shifted_rows=list(csv.DictReader(io.StringIO(shifted.decode("utf-8-sig"))))
    raw_lookup={}
    for r in raw_rows:
        t=r["source_period_utc"]
        if t in raw_lookup:raise ValueError("Duplicate source HE time")
        raw_lookup[t]=r["reported_demand_mw"]
    shifted_lookup={}
    for r in shifted_rows:
        t=r["timestamp_utc"]
        if t in shifted_lookup:raise ValueError("Duplicate converted UTC time")
        shifted_lookup[t]=r
    disagreements=[]
    neighboring_old_matches=Counter()
    for r in changed:
        stamp=r["timestamp_utc"]
        target=shifted_lookup.get(stamp)
        if target is None:
            raise ValueError("Changed UTC timestamp missing from authentic newer source")
        # Validate HE timestamp semantics independently, not just matching string fields.
        source_label=target["original_source_he_utc"]
        t=datetime.strptime(stamp,"%Y-%m-%dT%H:%M:%SZ")
        expected_he=(t+timedelta(hours=1)).strftime("%Y-%m-%dT%H")
        if source_label!=expected_he:raise ValueError("Original hour-ending to UTC-start mapping invalid")
        v=raw_lookup.get(source_label)
        if v!=target["demand_mw"] or v!=r["new_api_eia930_demand_mw"]:
            disagreements.append(stamp)
        if r["classification"]=="numeric_changed":
            old=r["frozen_eia930_demand_mw"]
            for shift in (-2,-1,1,2):
                neigh=(t+timedelta(hours=shift)).strftime("%Y-%m-%dT%H:%M:%SZ")
                if shifted_lookup.get(neigh,{}).get("demand_mw")==old:
                    neighboring_old_matches[str(shift)]+=1
    return {
        "source_raw_sha256":sha(raw),
        "source_utc_start_sha256":sha(shifted),
        "nonidentical_rows_checked":len(changed),
        "raw_to_shifted_mismatches":len(disagreements),
        "mismatch_sample":disagreements[:10],
        "neighbor_old_numeric_matches_shift_hours":dict(neighboring_old_matches),
        "episodes":episodes([r["timestamp_utc"] for r in changed]),
        "source_mechanism_established":False,
    }


def audit(diffs_csv,zips,*,expected_sha=OLD_NEW_DIFF_SHA,strict_counts=True):
    content=Path(diffs_csv).read_bytes()
    if sha(content)!=expected_sha:raise ValueError("Pinned genuine old/new changed-row CSV SHA mismatch")
    entries=list(csv.DictReader(io.StringIO(content.decode("utf-8-sig"))))
    result={}
    for key,target_count in TARGETS.items():
        ba,year=key[:-4],int(key[-4:])
        selected=[r for r in entries if r["ba"]==ba and int(r["year"])==year
                  and r["classification"]!="both_null"]
        if strict_counts and len(selected)!=target_count:
            raise ValueError(f"{key} changed source count is no longer pinned")
        result[key]=verify_one(zips[key],ba,year,selected)
        if result[key]["raw_to_shifted_mismatches"]:
            raise ValueError(f"{key} changed rows not reproduced from raw HE source")
    return {"status":"SOURCE_RAW_HE_REPRODUCED_NO_REVISION_CAUSE_INFERRED",
            "source_changed_row_sha256":expected_sha,
            "tested_cohorts":list(TARGETS),"results":result,
            "test_years_used_for_model_selection":False,
            "model_training_permitted":False,
            "no_original_values_modified":True}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--diffs",type=Path,required=True)
    p.add_argument("--azps2025",type=Path,required=True)
    p.add_argument("--bpat2021",type=Path,required=True)
    p.add_argument("--bpat2023",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.diffs,{"AZPS2025":a.azps2025,
                          "BPAT2021":a.bpat2021,"BPAT2023":a.bpat2023})
    if a.output.exists():raise FileExistsError("Never replace existing source audit")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
                      "checked":sum(v["nonidentical_rows_checked"] for v in result["results"].values()),
                      "model_training_permitted":False},indent=2))


if __name__=="__main__":main()
