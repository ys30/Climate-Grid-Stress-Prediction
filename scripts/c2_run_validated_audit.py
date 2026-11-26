#!/usr/bin/env python3
"""Validated C2 retrospective event audit: do not bypass integrity checks.

Input includes precomputed predictions and predeclared episodes, not raw hourly
EIA-930 and not issue-time weather forecasts. This is *not* blind validation.
"""
import argparse
import json
import tempfile
from pathlib import Path

try:
    from scripts.c2_cross_model_integrity import validate
    from scripts.c2_episode_tail_audit import audit
except ModuleNotFoundError:
    from c2_cross_model_integrity import validate
    from c2_episode_tail_audit import audit


def run(input_csv, output_dir, bootstrap=1200, seed=20261126):
    """Validate an immutable input snapshot, publish completed output atomically."""
    input_csv = Path(input_csv)
    output_dir = Path(output_dir)
    if output_dir.exists():
        raise ValueError('C2 OUTPUT EXISTS: choose a new output directory to prevent stale result reuse')
    if bootstrap < 0:
        raise ValueError('bootstrap must not be negative')
    # Copy exactly once: validation and metrics operate on identical source bytes.
    frozen_bytes = input_csv.read_bytes()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='c2_audit_', dir=output_dir.parent) as scratch:
        scratch = Path(scratch)
        snapshot = scratch / 'frozen_input.csv'
        snapshot.write_bytes(frozen_bytes)
        integrity = validate(snapshot)
        if not integrity["passed"]:
            summary = "; ".join(x["issue"] for x in integrity["issues"][:8])
            raise ValueError("C2 INPUT INTEGRITY FAILED: " + summary)
        stage = scratch / 'completed'
        result = audit(snapshot, stage, bootstrap=bootstrap, seed=seed)
        result["input_csv"] = str(input_csv)
        result["input_sha256"] = integrity["input_sha256"]
        result["integrity_passed"] = True
        result["required_estimators"] = ["Huber", "Ridge"]
        result["evidence_level"] = "retrospective_nonblind_observed_weather"
        (stage / "audit_manifest.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8")
        (stage / "input_integrity.json").write_text(
            json.dumps(integrity, indent=2) + "\n", encoding="utf-8")
        # A completed audit appears only after all outputs have been written.
        if output_dir.exists():
            raise ValueError('C2 OUTPUT EXISTS: directory appeared during this run')
        stage.rename(output_dir)
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--bootstrap", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=20261126)
    args = parser.parse_args()
    if args.bootstrap < 0:
        parser.error("bootstrap must not be negative")
    try:
        result = run(args.input_csv, args.output_dir, args.bootstrap, args.seed)
    except ValueError as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
