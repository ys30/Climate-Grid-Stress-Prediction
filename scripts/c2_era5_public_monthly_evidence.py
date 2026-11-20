"""Independently verify the latest real ARCO ERA5 February source artifact.

Reports a queued/failed job honestly; never converts a job success into
a weather-data success absent a complete CSV and matching SHA manifest.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
import zipfile
from datetime import datetime, timedelta, timezone

from scripts.c2_eia_wave1_artifact_audit import REPO, request

WORKFLOW = "c2-era5-public-february-pilot.yml"
BASE = "arco_2024_02_sacramento_single_gridcell"


def audit(token):
    result = request(f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=10", token)
    runs = result.get("workflow_runs", [])
    if not runs:
        return {"status": "no_monthly_run", "monthly_verified": False}
    run = runs[0]
    run_id = run["id"]
    base = {"run_id": run_id, "url": run.get("html_url"),
            "head_sha": run.get("head_sha"), "monthly_verified": False}
    if run.get("status") != "completed":
        return {**base, "status": "monthly_run_pending",
                "run_status": run.get("status")}
    if run.get("conclusion") != "success":
        return {**base, "status": "monthly_run_failed",
                "run_conclusion": run.get("conclusion")}
    archives = request(f"/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100", token)
    name = f"c2-real-arco-era5-february-2024-{run_id}"
    found = [a for a in archives.get("artifacts", [])
             if a.get("name") == name and not a.get("expired")]
    if len(found) != 1:
        return {**base, "status": "monthly_source_artifact_missing"}
    data = request(f"/repos/{REPO}/actions/artifacts/{found[0]['id']}/zip",
                   token, binary=True)
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        paths = z.namelist()
        csv_names = [p for p in paths if p.endswith("/" + BASE + ".csv")
                     or p == BASE + ".csv"]
        json_names = [p for p in paths if p.endswith("/" + BASE + ".manifest.json")
                      or p == BASE + ".manifest.json"]
        if len(csv_names) != 1 or len(json_names) != 1:
            return {**base, "status": "monthly_source_files_missing"}
        raw = z.read(csv_names[0])
        m = json.loads(z.read(json_names[0]))
    digest = hashlib.sha256(raw).hexdigest()
    records = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    first = datetime(2024, 2, 1, tzinfo=timezone.utc)
    times = [(first + timedelta(hours=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
             for i in range(696)]
    valid = (
        m.get("sha256_csv") == digest
        and m.get("n_unique_hours") == 696
        and m.get("source_kind") == "public_ARCO_ERA5_Zarr_single_gridcell_month"
        and m.get("is_CISO_BA_weather_exposure") is False
        and m.get("eia_join_executed") is False
        and m.get("clock") == "UTC_instantaneous_valid_time_not_EIA_hour_ending"
        and len(records) == 696
        and [r["timestamp_utc"] for r in records] == times
    )
    return {**base, "status": "source_month_authenticated" if valid else
            "source_month_evidence_failed",
            "monthly_verified": bool(valid), "artifact_id": found[0]["id"],
            "csv_sha256": digest if valid else None,
            "observed_hours": len(records),
            "weather_scope": "Single public ERA5 gridcell, not CISO BA-wide"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN")
    if not token:
        parser.error("GH_TOKEN required")
    report = audit(token)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(report["status"], report.get("observed_hours"),
          report.get("monthly_verified"))


if __name__ == "__main__":
    main()
