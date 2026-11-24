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
FILE_KEYS = ("membership_1305", "county_consumption_1306A", "udc_eia_crosswalk")


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


def inspect(membership, consumption, crosswalk, manifest):
    """Return strictly non-admitted source identity and join diagnostics."""
    meta = json.loads(Path(manifest).read_text(encoding="utf-8"))
    if meta.get("research_only") is not True or meta.get("training_permitted") is not False:
        raise ValueError("Source manifest must explicitly prohibit model use")
    for key in FILE_KEYS:
        item = meta.get("files", {}).get(key, {})
        path = {"membership_1305": membership, "county_consumption_1306A": consumption,
                "udc_eia_crosswalk": crosswalk}[key]
        sha = item.get("sha256")
        if not isinstance(sha, str) or len(sha) != 64 or digest(path) != sha:
            raise ValueError(f"Missing or changed original input SHA256: {key}")
        if not isinstance(item.get("source_release"), str) or not item["source_release"].strip():
            raise ValueError(f"Unversioned source or crosswalk: {key}")
        if key != "udc_eia_crosswalk" and item.get("source_kind") != "official_original":
            raise ValueError("Observed source must document official-original provenance")
    m = read_table(membership, ("year", "month", "ba", "udc_id"))
    c = read_table(consumption, ("year", "month", "county_fips", "udc_id", "sector", "gwh"))
    w = read_table(crosswalk, ("udc_id", "eia_utility_id", "reviewed"))
    if not m or not c or not w:
        raise ValueError("Empty observed source or identity crosswalk")
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
        members[ym, udc].add(ba)
    count = Counter()
    totals = defaultdict(float)
    candidate = defaultdict(float)
    for row in c:
        ym = _year_month(row)
        udc = row["udc_id"].strip()
        county = row["county_fips"].strip()
        sector = row["sector"].strip()
        if len(county) != 5 or not county.isdigit() or not sector or not udc:
            raise ValueError("Bad source county FIPS, UDC or sector")
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
        ],
    }


def main():
    p = argparse.ArgumentParser()
    for name in ("membership", "consumption", "crosswalk", "manifest", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args()
    if a.output.exists():
        raise FileExistsError("Refuse to overwrite independent geographic evidence")
    result = inspect(a.membership, a.consumption, a.crosswalk, a.manifest)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
