# C-2 EIA upstream RAW HE provenance and contiguous episode audit (2026-11-20)

**Source-only forensic finding, not a model accuracy claim.**

The earlier full 23 canonical-passing BA-year vintage comparison yielded 201,672
expected UTC hours and 231 numeric differences, in addition to missing-state
changes. The original changed-row CSV was SHA-pinned as
`6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480`.

This follow-up independently reopened authenticated newer EIA-930 ZIP
artifacts for **AZPS 2025**, **BPAT 2021** and **BPAT 2023**, and compared
each changed hour's newer `raw/eia930_*_he.csv` source with the
`utc_start/eia930_*_start.csv` conversion. Both files' SHA-256
matched their own original manifests. The UTC-start label was verified
against the original hour-ending label, **exactly -1 hour**.

| Source cohort | Old/new different or missing-state hours inspected | Original HE/new UTC-start agree |
|---|---:|---:|
| AZPS 2025 | 169 | 169 |
| BPAT 2021 | 26 | 26 |
| BPAT 2023 | 24 | 24 |
| **Total** | **219** | **219** |

This establishes that the *newer* hour-ending source file already
contains the differing values or nulls; the newer UTC conversion did not
create the observed changes at those hours. It **does not independently
prove the upstream reason for original EIA version revisions**. A
limited ±1/±2-hour neighbor check found no exact match explaining the
changed numeric values as a simple shift; that is NOT proof all
timestamp-related causes are ruled out.

## Contiguous UTC episode evidence

- AZPS 2025: 24-hour source revision sequence
  `2025-07-26T07Z` to `2025-07-27T06Z`.
  Other source revision runs include 22 hours
  `2025-04-30T07Z` to `2025-05-01T04Z`,
  and 20 hours `2025-09-17T07Z` to
  `2025-09-18T02Z`. Its independently source-authenticated
  `2025-07-31T19Z` revision changes old **6569 MW**
  to newer **0 MW**, and `2025-07-31T21Z`
  changes old **6934 MW** to newer **273 MW**.
- BPAT 2021: 24 contiguous new null hours
  `2021-09-15T07Z` to `2021-09-16T06Z`.
  Two other changed hours fall near 2021-11-07 UTC.
- BPAT 2023: 24 contiguous new null hours
  `2023-10-24T07Z` to `2023-10-25T06Z`.

These are genuine source-vintage differences, not a reason to
choose which vintage is correct, delete zero values or impute gaps.

## Reproducibility

- `scripts/c2_eia_raw_he_revision_episode_audit.py` performs SHA-pinned
  actual raw-to-shifted original-data checks.
- `tests/test_c2_eia_raw_he_revision_episode_audit.py` exercises
  clock semantics, source discrepancies and contiguous episode
  construction with explicitly synthetic fixtures.
- A detailed JSON `C2_EIA_AZPS_BPAT_RAW_HE_EPISODE_QA_2026-11-20.json`
  was generated from the downloaded authentic source artifacts and
  supplied separately.

**Further upstream data provenance:** inspect EIA reporting revisions
and 2025 AZPS utility/operator notes; seek exact retrieval-vintage
history or independent published original values to infer why
newer reported demand differs. Source change ≠ confirmed source error.

The frozen source panel of 210,432 ERA5×EIA BA-hours remains unchanged.
The independently audited newer annual canonical gate remains 23/24
with AZPS 2023 failing. BA operating geography and weather/load
relevance remain unapproved; `model_training_permitted=false`.
Train 2020–2022, validation 2023, 2024–25 test sealed for modeling.
C-1 remains frozen.
