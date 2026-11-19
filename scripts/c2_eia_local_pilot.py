"""Run first C-2 EIA-930 year locally from a key file without recording credentials.

Usage:
  python -m scripts.c2_eia_local_pilot --key-file /secure/path/API.txt \
      --ba CISO --year 2024 --outdir data/eia930_pilot_2024

The key is read into this process's memory and passed to child Python calls in
an environment variable. It is never placed on a shell command line, manifest,
URL printed by this runner, or GitHub source control.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def run(key_file: Path, ba: str, year: int, outdir: Path) -> dict:
    if ba not in {"CISO", "AZPS", "BPAT", "SRP"}:
        raise ValueError("Unexpected balancing authority")
    if year not in range(2020, 2026):
        raise ValueError("Year must be 2020–2025")
    key = key_file.read_text(encoding="utf-8-sig").strip()
    if not key or len(key.split()) != 1:
        raise ValueError("Key file must contain exactly one nonblank API key")
    raw = outdir / "raw" / f"eia930_{ba}_{year}_he.csv"
    clocked = outdir / "utc_start" / f"eia930_{ba}_{year}_start.csv"
    report = outdir / "audit" / f"eia930_{ba}_{year}_coverage.json"
    for path in (raw, clocked, report):
        if path.exists() or path.with_suffix(".manifest.json").exists():
            raise FileExistsError(f"Output exists; use a new vintage directory: {path}")
    raw.parent.mkdir(parents=True, exist_ok=True)
    clocked.parent.mkdir(parents=True, exist_ok=True)
    report.parent.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, EIA_API_KEY=key)
    commands = [
        [sys.executable, "-m", "scripts.c2_eia930_raw_api_intake",
         "--ba", ba, "--year", str(year), "--output", str(raw)],
        [sys.executable, "-m", "scripts.c2_eia930_he_to_utc_start",
         str(raw), str(clocked), "--year", str(year)],
        [sys.executable, "-m", "scripts.c2_eia930_year_coverage_gate",
         str(clocked), "--ba", ba, "--year", str(year), "--output", str(report)]
    ]
    # No shell, no key in argv, and no key in stdout.
    for command in commands:
        subprocess.run(command, env=env, check=True)
    audit = json.loads(report.read_text(encoding="utf-8"))
    return {"status": "annual_EIA_source_audit_only",
            "ba": ba, "year": year,
            "coverage_gate_pass": audit["pass"],
            "coverage": audit["coverage"],
            "annual_report": str(report),
            "no_weather_join_or_model_skill_claim": True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--key-file", type=Path, required=True)
    p.add_argument("--ba", choices=["CISO", "AZPS", "BPAT", "SRP"], default="CISO")
    p.add_argument("--year", choices=list(range(2020, 2026)), type=int, default=2024)
    p.add_argument("--outdir", type=Path, required=True)
    args = p.parse_args()
    result = run(args.key_file, args.ba, args.year, args.outdir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
