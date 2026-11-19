"""Download *raw* EIA RTO region-data with provenance; DO NOT infer interval start.

EIA API endpoint: https://api.eia.gov/v2/electricity/rto/region-data/data/
The API's 'period' is retained unchanged as source_period_utc. This script does
not assert that its hour label represents interval-start (or interval-end).
No synthetic data, interpolation, county allocation or weather joins.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ENDPOINT = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
ALLOWED_BAS = {"CISO", "AZPS", "BPAT", "SRP"}
PAGE_SIZE = 5000


def fetch_page(api_key: str, ba: str, start: str, end: str, offset: int) -> dict:
    params = [
        ("api_key", api_key), ("frequency", "hourly"), ("data[0]", "value"),
        ("facets[respondent][]", ba), ("facets[type][]", "D"),
        ("start", start), ("end", end),
        ("sort[0][column]", "period"), ("sort[0][direction]", "asc"),
        ("offset", str(offset)), ("length", str(PAGE_SIZE)),
    ]
    url = ENDPOINT + "?" + urlencode(params)
    # EIA requires an API key in its query. The request URL must never be
    # included in exception messages or tracebacks because it contains the key.
    try:
        with urlopen(Request(url, headers={"User-Agent": "Climate-Grid-C2-source-audit/1.0"}), timeout=60) as resp:
            return json.load(resp)
    except HTTPError as exc:
        raise RuntimeError(f"EIA API HTTP status {exc.code}; request URL and key withheld") from None
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        raise RuntimeError(f"EIA API transport or JSON error ({type(exc).__name__}); credentials withheld") from None


def collect(api_key: str, ba: str, start: str, end: str) -> list[dict]:
    if ba not in ALLOWED_BAS:
        raise ValueError(f"BA must be one of {sorted(ALLOWED_BAS)}")
    rows = []
    total = None
    while total is None or len(rows) < total:
        payload = fetch_page(api_key, ba, start, end, len(rows))
        if payload.get("error"):
            raise RuntimeError(f"EIA API error for BA {ba}")
        response = payload.get("response")
        if not isinstance(response, dict) or "data" not in response or "total" not in response:
            raise RuntimeError("Unexpected EIA API response schema")
        count = int(response["total"])
        if total is None:
            total = count
        if count != total:
            raise RuntimeError("EIA pagination total changed mid-request; refetch with pinned source")
        page = response["data"]
        if not isinstance(page, list):
            raise RuntimeError("EIA API data must be an array")
        if not page and len(rows) < total:
            raise RuntimeError("Empty EIA page before expected total")
        for r in page:
            if r.get("respondent") != ba or r.get("type") != "D":
                raise RuntimeError("Unexpected BA or measurement type in EIA source response")
            p = r.get("period")
            if not isinstance(p, str) or not p:
                raise RuntimeError("Missing original EIA period")
            try:
                demand = float(r["value"])
            except (TypeError, ValueError, KeyError) as exc:
                raise RuntimeError(f"Invalid EIA demand value for {ba} {p}") from exc
            if not (demand >= 0 and demand < float("inf")):
                raise RuntimeError(f"Nonfinite or negative EIA demand: {ba} {p}")
            rows.append({"ba": ba, "source_period_utc": p,
                         "measurement_type": "D", "reported_demand_mw": r["value"],
                         "source": "EIA API electricity/rto/region-data"})
        if len(rows) > total:
            raise RuntimeError("EIA API pagination exceeded response total")
    if len(rows) != total:
        raise RuntimeError("EIA API pagination count does not reconcile")
    periods = [r["source_period_utc"] for r in rows]
    if len(periods) != len(set(periods)):
        raise RuntimeError("Duplicate EIA source hours: refuse silent deduplication")
    if not rows:
        raise RuntimeError(f"No source data returned for {ba} between {start} and {end}")
    if periods != sorted(periods):
        raise RuntimeError("EIA source hours not ordered; verify pagination")
    return rows


def save(rows: list[dict], output: Path, *, ba: str, start: str, end: str) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists() or output.with_suffix(".manifest.json").exists():
        raise FileExistsError("Output already exists; preserve source vintage rather than overwrite")
    tmp = output.with_suffix(output.suffix + ".partial")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["ba", "source_period_utc", "measurement_type",
                                                   "reported_demand_mw", "source"])
        writer.writeheader()
        writer.writerows(rows)
    digest = hashlib.sha256(tmp.read_bytes()).hexdigest()
    manifest = {"source": ENDPOINT, "source_kind": "official_EIA_930_API",
                "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                "ba": ba, "type": "D", "start_requested": start,
                "end_requested": end, "row_count": len(rows),
                "first_source_period": rows[0]["source_period_utc"],
                "last_source_period": rows[-1]["source_period_utc"],
                "sha256_csv": digest, "clock_status": "source_label_unconverted",
                "claim_status": "raw_api_retrieval_only_not_hourly_model_eligible",
                "caveat": "EIA API period convention and source revisions require separate audit"}
    tmp.rename(output)
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ba", choices=sorted(ALLOWED_BAS), required=True)
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 2019 <= args.year <= 2026:
        parser.error("This C-2 intake restricts requested years to 2019..2026")
    key = os.environ.get("EIA_API_KEY", "").strip()
    if not key:
        parser.error("EIA_API_KEY environment variable is required; never commit the key")
    # Official EIA-930 reports hour-ending. To cover all target-year UTC
    # interval-start hours, fetch through NEXT Jan 1 00:00 inclusive.
    # Keep Jan 1 00:00 of the target year as audit context; the HE converter
    # filters output by interval-start year without inventing a final hour.
    start = f"{args.year}-01-01T00"
    end = f"{args.year + 1}-01-01T00"
    rows = collect(key, args.ba, start, end)
    print(json.dumps(save(rows, args.output, ba=args.ba, start=start, end=end), indent=2))


if __name__ == "__main__":
    main()
