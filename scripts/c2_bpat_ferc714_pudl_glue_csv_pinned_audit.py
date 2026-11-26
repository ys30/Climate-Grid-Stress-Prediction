"""Validate PUDL's cross-format FERC714 respondent glue CSV at a pinned Git commit.

This is a real published source mapping, but it contains NO utility/BA names,
EIA codes, hourly readings or geographic data. Never infer BPAT ID from it.
"""
import csv
import hashlib
import io
import json
from collections import Counter

COMMIT = "97874c209147452055842c1d9a5f2614d934be6b"
BLOB = "3eb0291e51502df9a5fca38e9f3ac4ebf3526ad7"
URL = (f"https://raw.githubusercontent.com/catalyst-cooperative/pudl/{COMMIT}/"
       "src/pudl/package_data/glue/respondent_id_ferc714.csv")
FIELDS = ["respondent_id_ferc714", "respondent_id_ferc714_xbrl",
          "respondent_id_ferc714_csv", "Source", "Notes"]


def git_blob_sha1(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\\0" + raw).hexdigest()


def inspect(raw):
    if git_blob_sha1(raw) != BLOB:
        raise ValueError("Pinned Git blob source identity mismatch")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames != FIELDS:
        raise ValueError("Unexpected source mapping fields")
    rows = list(reader)
    if len(rows) != 219:
        raise ValueError("Unexpected original source row count")
    ids = [r["respondent_id_ferc714"] for r in rows]
    if any(not i.isdigit() for i in ids) or len(ids) != len(set(ids)):
        raise ValueError("Invalid or duplicate published respondent ID")
    counts = Counter("xbrl_present" if r["respondent_id_ferc714_xbrl"].strip()
                     else "xbrl_missing" for r in rows)
    if counts != {"xbrl_present": 119, "xbrl_missing": 100}:
        raise ValueError("Published source ID coverage changed")
    return {
        "pudl_source_commit": COMMIT, "git_blob_sha1": BLOB,
        "raw_source_sha256": hashlib.sha256(raw).hexdigest(),
        "respondent_mapping_rows": len(rows),
        "with_xbrl_mapping": counts["xbrl_present"],
        "without_xbrl_mapping": counts["xbrl_missing"],
        "contains_BPA_identity": False,
        "operator_identity_certified": False,
        "model_training_permitted": False,
        "source_url": URL,
    }


def main():
    import argparse
    from pathlib import Path
    from urllib.request import urlopen
    p = argparse.ArgumentParser()
    p.add_argument("--csv", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    if args.out.exists():
        raise FileExistsError("Refuse overwrite of source audit")
    raw = args.csv.read_bytes() if args.csv else urlopen(URL, timeout=30).read()
    result = inspect(raw)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
