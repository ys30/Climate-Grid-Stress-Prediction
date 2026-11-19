"""Audit completed Wave 1 BA-year GitHub Actions artifacts using Actions read token.

No EIA API credential needed. Never claims completion from job 'success' alone:
annual gate JSON and converted CSV SHA chain must both be verifiable.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import urllib.error
import urllib.request
import urllib.parse
import zipfile
from datetime import datetime, timezone

REPO = "ys30/Climate-Grid-Stress-Prediction"
WORKFLOW = "c2-eia-expansion-wave1.yml"
EXPECTED = {("CISO", year) for year in (2020, 2021, 2022, 2023, 2025)} | {
    (ba, 2024) for ba in ("AZPS", "BPAT", "SRP")
}


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and urllib.parse.urlsplit(req.full_url).netloc != urllib.parse.urlsplit(newurl).netloc:
            redirected.remove_header("Authorization")
            redirected.remove_header("X-GitHub-Api-Version")
        return redirected


def request(path, token, *, binary=False):
    url = "https://api.github.com" + path
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "C2-E2-evidence-auditor",
               "Authorization": "Bearer " + token,
               "X-GitHub-Api-Version": "2022-11-28"}
    try:
        with urllib.request.build_opener(SafeRedirect()).open(urllib.request.Request(url, headers=headers), timeout=90) as r:
            content = r.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        # Never expose the OAuth credential, response body, or redirected URL.
        raise RuntimeError("GitHub Actions evidence API request failed (" + type(exc).__name__ + ")") from None
    return content if binary else json.loads(content)


def get_latest_run(token):
    payload = request(f"/repos/{REPO}/actions/workflows/{WORKFLOW}/runs?per_page=25", token)
    runs = payload.get("workflow_runs", [])
    if not runs:
        return None
    # Latest completed run, not a queued or in-progress run.
    return next((r for r in runs if r.get("status") == "completed"), None)


def report(token, run_id=None):
    if run_id is None:
        run = get_latest_run(token)
        if not run:
            return {"status": "no_completed_wave1_run", "expected_ba_years": 8}
        run_id = run["id"]
    run = request(f"/repos/{REPO}/actions/runs/{run_id}", token)
    if run.get("status") != "completed":
        return {"status": "wave1_not_yet_completed", "run_id": run_id}
    jobs = request(f"/repos/{REPO}/actions/runs/{run_id}/jobs?per_page=100", token)
    artifacts = request(f"/repos/{REPO}/actions/runs/{run_id}/artifacts?per_page=100", token)
    results = {}
    for ba, year in sorted(EXPECTED):
        label = f"c2-eia-wave1-{ba}-{year}-{run_id}"
        matches = [a for a in artifacts.get("artifacts", []) if a.get("name") == label and not a.get("expired")]
        record = {"ba": ba, "year": year, "gate_pass": False}
        results[(ba, year)] = record
        if len(matches) != 1:
            record["status"] = "artifact_absent_or_expired"
            continue
        blob = request(f"/repos/{REPO}/actions/artifacts/{matches[0]['id']}/zip", token, binary=True)
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names = set(z.namelist())
            audit_path = f"audit/eia930_{ba}_{year}_coverage.json"
            csv_path = f"utc_start/eia930_{ba}_{year}_start.csv"
            manifest_path = f"utc_start/eia930_{ba}_{year}_start.manifest.json"
            raw_path = f"raw/eia930_{ba}_{year}_he.csv"
            raw_manifest_path = f"raw/eia930_{ba}_{year}_he.manifest.json"
            if not {audit_path, csv_path, manifest_path, raw_path, raw_manifest_path} <= names:
                record["status"] = "artifact_missing_required_files"
                continue
            a = json.loads(z.read(audit_path))
            m = json.loads(z.read(manifest_path))
            rm = json.loads(z.read(raw_manifest_path))
            digest = hashlib.sha256(z.read(csv_path)).hexdigest()
            raw_digest = hashlib.sha256(z.read(raw_path)).hexdigest()
            ok = (
                a.get("pass") is True and a.get("ba") == ba and a.get("year") == year
                and a.get("missing_hours", -1) >= 0 and a.get("duplicate_hours") == 0
                and a.get("source_he_mismatch_rows") == 0
                and a.get("invalid_rows") == 0
                and a.get("coverage", 0) >= a.get("coverage_threshold", 0.98)
                and a.get("source_sha256") == digest == m.get("sha256_csv")
                and m.get("input_sha256") == raw_digest == rm.get("sha256_csv")
                and m.get("source_kind") == "derived_from_official_EIA_930_API"
                and rm.get("source_kind") == "official_EIA_930_API"
                and m.get("target_year") == year
            )
            record.update(status="artifact_hash_and_annual_gate_pass" if ok else "artifact_evidence_mismatch",
                          gate_pass=ok, coverage=a.get("coverage"),
                          expected_hours=a.get("expected_hours"),
                          unique_hours=a.get("unique_in_year"),
                          missing_hours=a.get("missing_hours"),
                          missing_demand_rows=a.get("missing_demand_rows"),
                          valid_demand_hours=a.get("valid_demand_hours"),
                          source_hour_coverage=a.get("source_hour_coverage"),
                          csv_sha256=digest if ok else None,
                          raw_sha256=raw_digest if ok else None,
                          artifact_id=matches[0]["id"])
    summaries = list(results.values())
    n = sum(x["gate_pass"] for x in summaries)
    return {"status": "wave1_artifact_verified" if n == 8 else "wave1_partial_or_failed",
            "run_id": run_id,
            "run_url": "https://github.com/" + REPO + f"/actions/runs/{run_id}",
            "run_conclusion": run.get("conclusion"),
            "verified_at_utc": datetime.now(timezone.utc).isoformat(),
            "expected_ba_years": 8, "verified_ba_years": n,
            "jobs_successful": sum(j.get("conclusion") == "success" for j in jobs.get("jobs", [])),
            "jobs_total": len(jobs.get("jobs", [])),
            "cohorts": summaries,
            "limitations": "EIA source-only verification; no ERA5 joint coverage or model validation"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run-id", type=int)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        p.error("GH_TOKEN Actions token required")
    result = report(token, run_id=args.run_id)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print("Wave 1:", result["status"], "verified:", result.get("verified_ba_years", 0),
          "/8; run:", result.get("run_id", "unavailable"))


if __name__ == "__main__":
    main()
