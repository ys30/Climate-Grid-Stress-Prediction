"""Read the newest AZPS 2023 diagnostic GitHub Actions artifact safely.

Diagnostic CI success is NOT source QA pass. Preserve the anomalous source
value in the existing artifact, publish only limited audit metadata.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
import zipfile
from datetime import datetime, timezone
from scripts.c2_eia_wave1_artifact_audit import REPO, request

WORKFLOW = "c2-eia-azps2023-diagnostic.yml"
TARGET = ("AZPS", 2023)


def diagnose(token: str, run_id: int | None = None) -> dict:
    if run_id is None:
        p = request(f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=10", token)
        runs = p.get("workflow_runs", [])
        if not runs:
            return {"status": "diagnostic_run_absent", "source_gate_pass": False}
        run_id = runs[0]["id"]
    r = request(f"/repos/{REPO}/actions/runs/{run_id}", token)
    base = {"run_id": run_id, "run_url": r.get("html_url"),
            "head_sha": r.get("head_sha"),
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "source_gate_pass": False}
    if r.get("status") != "completed":
        return {**base, "status": "diagnostic_run_not_completed", "run_status": r.get("status")}
    arts = request(f"/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100", token)
    label = f"c2-azps2023-source-anomaly-diagnostic-{run_id}"
    found = [a for a in arts.get("artifacts", []) if a.get("name") == label and not a.get("expired")]
    if len(found) != 1:
        return {**base, "status": "diagnostic_evidence_absent"}
    blob = request(f"/repos/{REPO}/actions/artifacts/{found[0]['id']}/zip", token, binary=True)
    required = [
        "raw/eia930_AZPS_2023_he.csv",
        "raw/eia930_AZPS_2023_he.manifest.json",
        "utc_start/eia930_AZPS_2023_start.csv",
        "utc_start/eia930_AZPS_2023_start.manifest.json",
        "audit/eia930_AZPS_2023_coverage.json",
    ]
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        if not set(required) <= set(z.namelist()):
            return {**base, "status": "diagnostic_files_incomplete"}
        raw, raw_m, derived, derived_m, audit = required
        rm = json.loads(z.read(raw_m))
        dm = json.loads(z.read(derived_m))
        a = json.loads(z.read(audit))
        raw_sha = hashlib.sha256(z.read(raw)).hexdigest()
        derived_sha = hashlib.sha256(z.read(derived)).hexdigest()
        authentic = (
            rm.get("sha256_csv") == raw_sha == dm.get("input_sha256")
            and dm.get("sha256_csv") == derived_sha == a.get("source_sha256")
            and rm.get("source_kind") == "official_EIA_930_API"
            and dm.get("source_kind") == "derived_from_official_EIA_930_API"
            and dm.get("target_year") == 2023
            and a.get("ba") == "AZPS" and a.get("year") == 2023
        )
        if not authentic:
            return {**base, "status": "diagnostic_provenance_failed"}
        # Audit examples are 20 or fewer and are original reported values.
        # They are public observations, not credential data.
        return {
            **base, "status": "diagnostic_artifact_authenticated",
            "source_gate_pass": a.get("pass") is True and a.get("invalid_rows") == 0,
            "artifact_id": found[0]["id"],
            "raw_sha256": raw_sha, "utc_start_sha256": derived_sha,
            "expected_hours": a.get("expected_hours"),
            "source_hours": a.get("unique_in_year"),
            "missing_timestamp_hours": a.get("missing_hours"),
            "missing_demand_rows": a.get("missing_demand_rows"),
            "invalid_numeric_rows": a.get("invalid_rows"),
            "valid_demand_hours": a.get("valid_demand_hours"),
            "valid_coverage": a.get("coverage"),
            "annual_audit_pass": a.get("pass"),
            "anomalies_max20": a.get("invalid_numeric_examples_max20", []),
            "limitation": "A completed diagnostic workflow does not waive the strict invalid-row EIA source gate."
        }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", type=int)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    token = os.environ.get("GH_TOKEN")
    if not token:
        p.error("GH_TOKEN Actions-read credential required")
    result = diagnose(token, run_id=args.run_id)
    with open(args.output, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print("Diagnostic:", result["status"], "source gate pass:", result["source_gate_pass"])


if __name__ == "__main__":
    main()
