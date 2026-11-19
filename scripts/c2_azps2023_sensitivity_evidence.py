"""Verify the AZPS 2023 noncanonical sensitivity Actions artifact and source audit.

Does not grant canonical source pass. Only derived sensitivity CSV hash + exact
exclusion manifest are admissible. No ERA5, forecast skill, or attribution.
"""
from __future__ import annotations
import argparse, hashlib, io, json, os, zipfile
from scripts.c2_eia_wave1_artifact_audit import REPO, request
from scripts.c2_azps2023_negative_sensitivity import SOURCE_SHA, FLAGS, OUTPUT_KIND

WORKFLOW = "c2-azps2023-sensitivity.yml"


def report(token):
    p = request(f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=10", token)
    runs = p.get("workflow_runs", [])
    if not runs:
        return {"status":"sensitivity_run_missing","sensitivity_verified":False,
                "canonical_source_gate_pass":False}
    r = runs[0]
    run_id = r["id"]
    base = {"run_id":run_id, "run_url":r.get("html_url"),
            "head_sha":r.get("head_sha"),
            "canonical_source_gate_pass":False,
            "sensitivity_verified":False}
    if r.get("status") != "completed":
        return {**base, "status":"sensitivity_run_pending"}
    arts = request(f"/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100", token)
    expected = f"c2-azps2023-noncanonical-sensitivity-{run_id}"
    candidates = [a for a in arts.get("artifacts",[])
                  if a.get("name") == expected and not a.get("expired")]
    if len(candidates) != 1:
        return {**base, "status":"sensitivity_artifact_missing"}
    raw_zip = request(f"/repos/{REPO}/actions/artifacts/{candidates[0]['id']}/zip",token,binary=True)
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as z:
        names = z.namelist()
        csv_files = [n for n in names if n.endswith("azps_2023_EXCLUDE_2_NEGATIVE_NONCANONICAL.csv")]
        manifest_files = [n for n in names if n.endswith("azps_2023_EXCLUDE_2_NEGATIVE_NONCANONICAL.manifest.json")]
        if len(csv_files) != 1 or len(manifest_files) != 1:
            return {**base,"status":"sensitivity_files_missing"}
        m=json.loads(z.read(manifest_files[0]))
        sha=hashlib.sha256(z.read(csv_files[0])).hexdigest()
        expected_flags=[{"timestamp_utc":k,"reported_demand_mw":v} for k,v in FLAGS.items()]
        ok = (
            m.get("source_kind") == OUTPUT_KIND
            and m.get("canonical_source_gate_pass") is False
            and m.get("source_sha256") == SOURCE_SHA
            and m.get("derived_sha256") == sha
            and m.get("retained_real_hourly_rows") == 8758
            and m.get("excluded_real_hourly_rows") == expected_flags
        )
        return {**base,"status":"sensitivity_artifact_verified" if ok else "sensitivity_evidence_mismatch",
                "sensitivity_verified":ok,
                "derived_sha256":sha if ok else None,
                "artifact_id":candidates[0]["id"]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    token=os.environ.get("GH_TOKEN")
    if not token:
        p.error("GH_TOKEN required")
    data=report(token)
    with open(a.output,"w") as f:
        json.dump(data,f,indent=2)
        f.write("\n")
    print(data["status"],"noncanonical",data["sensitivity_verified"])


if __name__=="__main__":
    main()
