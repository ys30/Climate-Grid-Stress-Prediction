#!/usr/bin/env python3
"""Source-only CEC 1305 / 1306A joint-evidence gate for C-2.

This is a *conditional* ID join diagnostic, NOT proof that public releases
have these columns, NOT an authorized hourly BA spatial exposure.
Never run on synthetic/unverified data as though an official CEC record.
"""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

BAS = {"AZPS", "BPAT", "CISO", "SRP"}
FILE_KEYS = ("membership_1305", "county_consumption_1306A", "udc_eia_crosswalk", "cec_county_crosswalk")


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for block in iter(lambda: fh.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def read_table(path, required):
    with Path(path).open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None or not set(required).issubset(reader.fieldnames):
            raise ValueError(f"Missing exact required fields: {path}")
        return list(reader)


def _year_month(row):
    year, month = int(row["year"]), int(row["month"])
    if year not in range(2020, 2026) or month not in range(1, 13):
        raise ValueError("Source date outside project 2020-2025 scope")
    return year, month


def inspect(membership, consumption, crosswalk, county_map, manifest):
    """Return strictly non-admitted source identity and join diagnostics."""
    meta = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if meta.get("research_only") is not True or meta.get("training_permitted") is not False:
        raise ValueError("Source manifest must explicitly prohibit model use")
    for key in FILE_KEYS:
        item = meta.get("files", {}).get(key, {})
        path = {"membership_1305": membership, "county_consumption_1306A": consumption,
                "udc_eia_crosswalk": crosswalk, "cec_county_crosswalk": county_map}[key]
        sha = item.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64 or digest(path) != sha:
            raise ValueError(f"Missing or changed original input SHA256: {key}")
        if not isinstance(item.get("source_release"), str) or not item["source_release"].strip():
            raise ValueError(f"Unversioned source or crosswalk: {key}")
        if key in ("membership_1305", "county_consumption_1306A") and item.get("source_kind") != "official_original":
            raise ValueError("Observed source must document official-original provenance")
    m = read_table(membership, ("year", "month", "ba", "udc_id", "membership_effective_whole_month"))
    c = read_table(consumption, ("year", "month", "cec_county_number", "county_fips", "udc_id", "sector", "gwh"))
    w = read_table(crosswalk, ("udc_id", "eia_utility_id", "reviewed"))
    county_rows = read_table(county_map, ("cec_county_number", "county_fips", "reviewed"))
    if not m or not c or not w:
        raise ValueError("Empty observed source or identity crosswalk")
    county_links = {}
    used_fips = set()
    for item in county_rows:
        code = item["cec_county_number"].strip()
        fips = item["county_fips"].strip()
        if not code.isdigit() or not 1 <= int(code) <= 58 or code != str(int(code)):
            raise ValueError("Invalid or special CEC county number; 00/99 cannot become FIPS")
        if len(fips) != 5 or not fips.isdigit() or not fips.startswith("06"):
            raise ValueError("CEC 1306A county must map to reviewed California FIPS")
        if item["reviewed"] != "True":
            raise ValueError("CEC county number to FIPS must be independently reviewed")
        if code in county_links or fips in used_fips:
            raise ValueError("Nonunique CEC county-to-FIPS conversion")
        county_links[code] = fips
        used_fips.add(fips)
    if not county_links:
        raise ValueError("CEC county-to-FIPS mapping missing")
    identities = {}
    for row in w:
        udc = row["udc_id"].strip()
        eid = row["eia_utility_id"].strip()
        if not udc or udc in identities:
            raise ValueError("Duplicate or blank UDC crosswalk key")
        if row["reviewed"] not in ("True", "False"):
            raise ValueError("Crosswalk review must be explicit")
        if eid and not eid.isdigit():
            raise ValueError("Invalid EIA utility identifier")
        identities[udc] = (eid, row["reviewed"] == "True")
    members = defaultdict(set)
    time_uncertain = set()
    seen = set()
    for row in m:
        ym = _year_month(row)
        ba = row["ba"].strip()
        udc = row["udc_id"].strip()
        if ba not in BAS or not udc:
            raise ValueError("Unexpected BA or blank member UDC ID")
        key = (ym, ba, udc)
        if key in seen:
            raise ValueError("Duplicate 1305 BA membership record")
        seen.add(key)
        whole_month = row["membership_effective_whole_month"].strip()
        if whole_month not in ("True", "False"):
            raise ValueError("Whole-month membership certification must be explicit")
        if whole_month == "False":
            time_uncertain.add((ym, udc))
        members[ym, udc].add(ba)
    count = Counter()
    totals = defaultdict(float)
    candidate = defaultdict(float)
    seen_consumption = set()
    for row in c:
        ym = _year_month(row)
        udc = row["udc_id"].strip()
        county = row["county_fips"].strip()
        sector = row["sector"].strip()
        county_number = row["cec_county_number"].strip()
        if len(county) != 5 or not county.isdigit() or not county.startswith("06") or not sector or not udc:
            raise ValueError("Bad source county FIPS, UDC or sector")
        if county_links.get(county_number) != county:
            raise ValueError("Unreviewed CEC county number to FIPS mapping or special county 00/99")
        # Normalized 1306A tables MUST have a declared aggregation grain.
        # A duplicated county/UDC/sector/month otherwise silently inflates
        # consumption. A separate original record identifier would be needed
        # to represent multiple valid filings at this same grain.
        grain = (ym, county, udc, sector)
        if grain in seen_consumption:
            raise ValueError("Duplicate county-UDC-sector-month consumption grain")
        seen_consumption.add(grain)
        try:
            val = float(row["gwh"])
        except (TypeError, ValueError) as exc:
            raise ValueError("Non-numeric observed consumption; never treat missing as zero") from exc
        if not math.isfinite(val) or val < 0:
            raise ValueError("Negative or nonfinite source consumption")
        totals[ym] += val
        assoc = members.get((ym, udc), set())
        identity = identities.get(udc)
        if not assoc:
            reason = "membership_unavailable"
        elif (ym, udc) in time_uncertain:
            reason = "membership_partial_month_unresolved"
        elif len(assoc) != 1:
            reason = "udc_multi_BA_nonexclusive"
        elif identity is None or not identity[0] or not identity[1]:
            reason = "udc_eia_identity_unreviewed"
        else:
            reason = "conditional_unique_source_association"
            ba = next(iter(assoc))
            candidate[(ym[0], ym[1], ba, county)] += val
        count[reason] += 1
    return {
        "project": "C2",
        "source_rows": {"membership": len(m), "consumption": len(c), "crosswalk": len(w)},
        "consumption_rows_by_source_association_status": dict(sorted(count.items())),
        "sum_of_source_consumption_gwh": round(sum(totals.values()), 6),
        "conditional_county_BA_month_candidates": len(candidate),
        "candidate_consumption_gwh": round(sum(candidate.values()), 6),
        "candidate_counts_are_not_observed_BA_hourly_load": True,
        "cec_county_crosswalk_checked": True,
        "unknown_county_00_99_never_allocated": True,
        "normalized_1306a_reporting_grain_requires_independent_aggregation_review": True,
        "cec_public_joint_release_verified_by_this_script": False,
        "historical_BA_footprint_approved": False,
        "load_weighted_exposure_approved": False,
        "model_training_permitted": False,
        "future_SSP_PyPSA_claims_permitted": False,
        "unresolved": [
            "Utility reporting-area association is not necessarily the operating BA area",
            "Annual/monthly delivered GWh is not hourly geolocated demand",
            "Missing or multiply associated UDC must not be fractionally split",
            "Crosswalk must receive independent external scientific approval",
            "Partial-month or unknown effective-date membership cannot assign whole-month GWh",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("membership", "consumption", "crosswalk", "county_map", "manifest", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError("Refuse to overwrite independent geographic evidence")
    result = inspect(a.membership, a.consumption, a.crosswalk, a.county_map, a.manifest)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
