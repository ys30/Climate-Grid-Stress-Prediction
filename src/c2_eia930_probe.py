"""E0 live EIA-930 data probe. No imputation; never interpreted as an outage model."""
import argparse
import csv
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
BAS = ("AZPS", "BPAT", "CISO", "SRP")

def build_url(start, end, ba, key=None):
    params = [("frequency", "hourly"), ("data[0]", "value"),
              ("facets[respondent][]", ba), ("facets[type][]", "D"),
              ("start", start), ("end", end), ("offset", "0"),
              ("length", "5000"), ("sort[0][column]", "period"),
              ("sort[0][direction]", "asc")]
    if key:
        params.append(("api_key", key))
    return BASE + "?" + urlencode(params)

def summarize(rows, start, end):
    """Check reported hour-ending labels; count duplicates, missing, nulls."""
    d0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
    d1 = datetime.fromisoformat(end.replace("Z", "+00:00"))
    if d0.tzinfo is None:
        d0 = d0.replace(tzinfo=timezone.utc)
    if d1.tzinfo is None:
        d1 = d1.replace(tzinfo=timezone.utc)
    # Query labels are hour-ending: requested start/end are first/last EIA labels.
    expected = set()
    t = d0
    while t <= d1:
        expected.add(t)
        t += timedelta(hours=1)
    seen = set()
    duplicates = 0
    nulls = 0
    invalid = 0
    for row in rows:
        try:
            stamp = datetime.fromisoformat(str(row["period"]).replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                stamp = stamp.replace(tzinfo=timezone.utc)
            else:
                stamp = stamp.astimezone(timezone.utc)
            if stamp in seen:
                duplicates += 1
            seen.add(stamp)
            if row.get("value") is None or row.get("value") == "":
                nulls += 1
            else:
                val = float(row["value"])
                if not 0 <= val < float("inf"):
                    invalid += 1
        except (ValueError, TypeError, KeyError):
            invalid += 1
    return {"expected_hour_ending_labels": len(expected), "rows": len(rows),
            "unique_periods": len(seen), "duplicates": duplicates, "nulls": nulls,
            "invalid": invalid, "missing_expected_hours": len(expected - seen),
            "extra_hours": len(seen - expected), "coverage_complete":
            len(rows) == len(expected) and not (duplicates or nulls or invalid or (expected - seen) or (seen - expected))}

def probe(start, end, outdir):
    output = Path(outdir)
    output.mkdir(parents=True, exist_ok=True)
    statuses = []
    rows_out = []
    for ba in BAS:
        url = build_url(start, end, ba, os.getenv("EIA_API_KEY"))
        # Never print token-bearing URL
        with urlopen(Request(url, headers={"User-Agent": "ClimateGridStressC2/0.1",
                                            "Accept": "application/json"}), timeout=90) as response:
            raw = response.read()
        doc = json.loads(raw)
        if doc.get("error"):
            raise RuntimeError(f"EIA API error for {ba}: {doc['error']}")
        obj = doc.get("response", {})
        records = obj.get("data", [])
        if not isinstance(records, list):
            raise RuntimeError(f"Bad EIA response data for {ba}")
        total = int(obj.get("total", len(records)))
        if total != len(records):
            raise RuntimeError(f"Unfetched pagination for {ba}: total={total}, received={len(records)}")
        if any(str(x.get("respondent")) != ba or str(x.get("type")) != "D" for x in records):
            raise RuntimeError(f"Unexpected BA or series for {ba}")
        stat = summarize(records, start, end)
        stat.update({"ba": ba, "source": BASE, "response_sha256": hashlib.sha256(raw).hexdigest(),
                     "source_series": "EIA-930 reported actual demand D",
                     "source_clock": "EIA hour-ending UTC, convert to interval start by subtracting 1h"})
        statuses.append(stat)
        for item in records:
            rows_out.append({"ba": ba, "period_hour_ending_utc": item.get("period"),
                             "demand_hourly_mwh": item.get("value"),
                             "record_type": item.get("type")})
    with (output / "eia930_probe_rows.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["ba", "period_hour_ending_utc",
                                              "demand_hourly_mwh", "record_type"])
        writer.writeheader()
        writer.writerows(rows_out)
    report = {"status": "source_probe_only_not_climate_attribution_or_predictive_validation",
              "query_start_hour_ending": start, "query_end_hour_ending": end,
              "source": BASE, "ba_quality": statuses,
              "all_ba_coverage_complete": all(x["coverage_complete"] for x in statuses)}
    (output / "e0_source_probe_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2024-07-01T01")
    parser.add_argument("--end", default="2024-07-02T00")
    parser.add_argument("--out", default="outputs/e0")
    a = parser.parse_args()
    result = probe(a.start, a.end, a.out)
    if not result["all_ba_coverage_complete"]:
        raise SystemExit("Source completeness gate not passed; consult artifact")

if __name__ == "__main__":
    main()
