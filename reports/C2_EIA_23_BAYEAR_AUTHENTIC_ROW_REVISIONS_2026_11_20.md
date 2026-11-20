# C-2 EIA-930: complete row-level vintage audit for all 23 canonical-pass BA-years

**Evidence date: 2026-11-20. Source integrity only; model training BLOCKED.**

## What was actually compared

The old six-year source artifact, GitHub Actions run
[43629200989](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989),
artifact **14127710411**, was reopened in read-only mode and independently
verified against its original outer ZIP SHA256
`bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`
and inner data GZIP SHA256
`88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

Twenty-three independently authenticated newer yearly EIA-930 Actions ZIP
artifacts were downloaded using IDs in `docs/E2_WAVE1_VERIFIED_STATUS.json`,
`docs/E2_WAVE2_VERIFIED_STATUS.json`, `docs/E2_WAVE3_VERIFIED_STATUS.json`,
plus the separate CISO-2024 verified pilot. Every joined newer CSV
recomputed its original `sha256_csv` manifest and verified its annual
`audit/eia930_*_coverage.json` `pass=true` plus source SHA. Hourly
identity was **(BA, year, timestamp_utc_start)**; old/new original
reported demand values retained without interpolation.

**AZPS 2023 is not among 23 canonical-pass comparisons**: two negative
published EIA values fail its source gate; it has a separate SHA-pinned
noncanonical sensitivity dataset. All original 24 BA-years remain present
in the old source archive, but this strict-version audit intentionally
uses the identical 23-year sample for both vintages.

## Actual matched-denominator source revisions

| Actual row-level classification | UTC hours |
|---|---:|
| Same numeric demand | **201,131** |
| Both versions explicitly null | **159** |
| Old null → new numeric | **99** |
| Old numeric → new null | **51** |
| Two numeric reported demand values differ | **231** |
| Newer source has no hourly timestamp at all | **1** |
| **Expected UTC hour slots, 23 BA-years** | **201,672** |

The 23 matching old BA-year groups have **258** null demand hours;
newer archives have **210** explicit null rows **plus one absent UTC
timestamp**. These are **matched-group vintage differences**, not
evidence that one version is a correct replacement for another. In
particular 99 old-null→new-numeric and 51 reverse changes are
separately identifiable. The omitted newer time key is **CISO
2021-11-07T05:00:00Z**, old published demand **22,672 MW**.
The earlier apparent 260 vs 210 comparison conflated both different
vintages and the AZPS 2023 excluded BA-year; the row-level audit
corrects this denominator ambiguity.

## High-priority differences

- **AZPS 2025**: **169 changed numeric hours**. Changes are clustered
  in selected April, July, August, September and October 2025 periods.
  Largest observed: **2025-07-31T21Z**, old **6,934 MW**, new **273 MW**
  (−6,661 MW); 2025-07-31T19Z old **6,569 MW**, new **0 MW**.
  These authentic source values require high-impact revision/quality
  review. Numeric 0 does not automatically indicate a plausible
  operational BA demand; don't turn coverage pass into eligibility.
- **BPAT 2024**: 56 changed numeric hours (mostly small integer changes).
- **BPAT 2021**: 25 old-numeric→new-null hours, plus one changed
  numeric hour; **BPAT 2023**: 24 old-numeric→new-null hours.
- **CISO 2024 and 2025**: 48 old-null→new-numeric hours in each year.
- **SRP 2025**: three old-null→new-numeric hours and three changed
  numeric hours; **SRP 2024** one numeric change.
- **AZPS 2021**: one old-numeric→new-null plus one changed numeric;
  **SRP 2021** one old-numeric→new-null.
- Other compared yearly sources either match exactly or preserve
  identical explicit nulls.

## Reproducible user-facing evidence

- `C2_EIA_23_PASSING_BAYEAR_ROW_CHANGE_AUDIT_2026-11-20.zip` includes
  the original source-only Python audit, full changed-row CSV and JSON
  cohort-by-cohort source SHA manifest.
- Extracted changed-row CSV SHA256:
  `6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480`.
- Cohort result JSON SHA256:
  `aadbcc629277eecbac38848f1698025313e9edd99c223cc56b77ebda6024c0aa`.
- Output ZIP SHA256:
  `a9cfb041cdb8235903f0b4662619ca9398a9dc2aca43e83f1734bc9b631a20e5`.

## High-impact source-review queue (not a modeling filter)

Among the **231** genuine old/new numeric revisions, **38** have
absolute change **>= 1,000 MW**: **36 in AZPS 2025**,
one in **AZPS 2021** and one in **BPAT 2021**.
Of the AZPS 2025 revisions, **169** are numeric changes and **one**
changes from old positive demand to new **0 MW** (2025-07-31T19Z).
These are investigative source-review flags, NOT automatic source
error classifications or an approved clipping/imputation rule.

The new source-only priority program
`scripts/c2_eia_revision_priority_review.py` requires the SHA-pinned
changed-row CSV and separates "large revision" and "new 0 demand"
review status from `model_training_permitted=false`. Synthetic
regression tests: `tests/test_c2_eia_revision_priority_review.py`.
No 2024–2025 model fitting or test metric was computed.

## Scientific decision

1. This is a **source-vintage QA comparison**, not an error-correction
   claim and not a reason to overwrite the frozen E1 six-year archive.
2. Investigation of changed source values, EIA reporting time/clock
   conventions, revisions and zero demands is required. Preserve both
   originals. Do not infer DST as cause merely because some changes
   cluster in nearby dates.
3. 2024–2025 values were examined **only for input integrity**,
   not for weather-response prediction skill, threshold choice,
   geography selection or model tuning. Train=2020–2022,
   validate=2023, test=2024–2025 stays frozen.
4. 2018 HIFLD control-area, 2024 TIGER county and Census population
   proxy weather exposures are not independently approved as historical
   2020–2025 electricity-load geographies. All 210,432 old real
   BA-hours remain source evidence, not a model-admitted weather panel.
5. `model_training_permitted=false`;
   `anthropogenic_attribution_permitted=false`;
   `future_SSP_PyPSA_stress_claims_permitted=false`.
   C-1 frozen study is unchanged.
