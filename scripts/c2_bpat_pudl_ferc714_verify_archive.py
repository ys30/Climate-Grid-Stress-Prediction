#!/usr/bin/env python3
"""Read-only verification of previously downloaded PUDL FERC-714 source archives.

Does NOT download, overwrite, silently select respondents, or certify BPA original XLSX.
"""
import argparse
import json
from pathlib import Path

from scripts.c2_bpat_pudl_ferc714_fixed_release import (
    RELEASE, TABLES, audit, digest,
)


def verify_archive(source_dir, reviewed_respondent_id=None):
    source_dir = Path(source_dir)
    manifest_path = source_dir / "PUDL_FERC714_BPAT_SOURCE_AUDIT_MANIFEST.json"
    if not manifest_path.is_file():
        raise ValueError("Original download manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("release") != RELEASE:
        raise ValueError("Source release does not match pinned PUDL version")
    entries = manifest.get("source_originals")
    if not isinstance(entries, list) or len(entries) != len(TABLES):
        raise ValueError("Incomplete original source inventory")
    verified = {}
    for name in TABLES:
        expected_name = name + ".parquet"
        matches = [x for x in entries if x.get("name") == expected_name]
        if len(matches) != 1:
            raise ValueError("Missing or duplicate archived source entry: " + name)
        entry = matches[0]
        path = source_dir / expected_name
        if not path.is_file() or path.is_symlink():
            raise ValueError("Archived original missing or symlinked: " + name)
        expected = entry.get("sha256")
        if not isinstance(expected, str) or len(expected) != 64:
            raise ValueError("Unpinned original SHA for " + name)
        actual = digest(path)
        if actual != expected:
            raise ValueError("Archived source SHA mismatch: " + name)
        if path.stat().st_size != entry.get("bytes"):
            raise ValueError("Archived source size mismatch: " + name)
        verified[name] = {"sha256": actual, "bytes": path.stat().st_size}
    evidence = audit(source_dir / (TABLES[0] + ".parquet"),
                     source_dir / (TABLES[1] + ".parquet"), reviewed_respondent_id)
    return {
        "release": RELEASE,
        "source_hashes_verified": verified,
        "reviewed_respondent_id_supplied": reviewed_respondent_id is not None,
        "respondent_audit": evidence,
        "bpa_operator_original_xlsx_verified": False,
        "model_training_permitted": False,
        "EIA930_full_hourly_comparison_completed": False,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-dir", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--reviewed-respondent-id", type=int, default=None)
    args = ap.parse_args()
    if args.out.exists():
        raise FileExistsError("Refuse to overwrite source review output")
    result = verify_archive(args.source_dir, args.reviewed_respondent_id)
    args.out.mkdir(parents=True)
    (args.out / "PUDL_FERC714_BPAT_ARCHIVE_REVIEW.json").write_text(
        json.dumps(result, indent=2, default=str) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["respondent_audit"]["status"],
                      "model_training_permitted": False}))


if __name__ == "__main__":
    main()
