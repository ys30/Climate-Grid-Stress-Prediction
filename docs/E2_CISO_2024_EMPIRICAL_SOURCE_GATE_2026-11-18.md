# E2 empirical source pilot — CISO 2024 (verified 2026-11-18 UTC)

## Execution record

- GitHub Actions run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44427373589
- Successful rerun job ID: `135244337622`; conclusion: **success**
- Artifact ID: `14486655626`, name `c2-eia930-CISO-2024-44427373589`
- API credential: stored as Actions secret; **never** include key in code or this report
- API response: `8785` original HE-labeled rows (includes preceding boundary hour)
- UTC interval-start CISO 2024: **8784 unique hours**
- Expected: **8784 hours**, coverage: **100%**
- Missing: **0**; duplicates: **0**; invalid: **0**
- Wrong BA: **0**; out-of-period: **0**; source HE mismatch: **0**
- Standalone annual coverage gate: **PASS**

## Cryptographic source provenance

- Raw HE CSV SHA-256: `04b927f1b890e0eb91df89b0db77f59010e0e37c4a63509b2ad34e61e0a8293d`
- Converted UTC interval-start CSV SHA-256: `375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c`
- Source trace: original HE `2024-01-01T01` -> start `2024-01-01T00:00:00Z`
- Final boundary: original HE `2025-01-01T00` -> start `2024-12-31T23:00:00Z`

## Demand descriptive checks (derived solely from artifact CSV)

- Mean: **25,504.36 MW**; median **24,524 MW**
- Min/max: **14,794 / 47,571 MW**
- Annual sum of hourly mean demand (MWh equivalent): **224,030,258 MWh**
- Zero/negative readings: **0**
- These are EIA's reported `D` demand for respondent CISO; do not confuse with sales, individual counties, outages, or system-wide physical load certainty.

## Research eligibility

The **EIA-only 2024 annual source gate passes** for CISO. This does **not** qualify the BA for the predeclared historical six-year train/validation/test protocol; 2020–2023 and 2025 remain unverified, as does its independent ERA5 weather exposure and provenance. No model skill, weather attribution or future SSP forecast has been established. The C-1 frozen repository is unchanged.

## Next empirical gates

1. Acquire CISO other years and AZPS, BPAT, SRP (strict source manifest for each).
2. Independently validate ERA5 BA weather geometry, UTC interval-start, and no claims of measured county load weighting.
3. Match sources hour by hour; use joint coverage gate before any held-out experiment.
4. Fit preregistered calendar and weather baselines; evaluate 2024–2025 only when full split eligibility is demonstrated.

## Independent artifact-byte verification and demand-only EDA

The downloaded GitHub artifact ZIP was reopened and both enclosed CSVs were
SHA-256 checked against their own manifests (both **match**). The original
and converted hour counts are 8785 and 8784, respectively. All 366 UTC
calendar days contain exactly 24 observations.

| 2024 UTC month | Mean demand (MW) | Peak demand (MW) |
|---|---:|---:|
| Jan | 23,501.4 | 28,795 |
| Feb | 22,891.6 | 28,462 |
| Mar | 21,655.7 | 26,950 |
| Apr | 21,511.9 | 26,625 |
| May | 22,823.2 | 30,332 |
| Jun | 26,887.1 | 38,678 |
| Jul | 32,014.5 | 44,727 |
| Aug | 30,779.4 | 43,106 |
| Sep | 28,822.8 | 47,571 |
| Oct | 26,419.9 | 41,205 |
| Nov | 24,005.7 | 28,425 |
| Dec | 24,545.1 | 29,961 |

Maximum single hourly demand: **47,571 MW**, UTC interval start
`2024-09-06T01:00:00Z` (original HE `2024-09-06T02`). Minimum:
**14,794 MW**, start `2024-05-05T23:00:00Z`. These are demand-only
seasonal descriptions; no ERA5 weather response or climate causality has
been estimated.

## Expansion wave submitted

The bounded eight-BA-year follow-up workflow is committed at
`.github/workflows/c2-eia-expansion-wave1.yml` (commit `7820e74510cc968a68cf0935d7a5754a2b381cb0`).
It covers the five missing CISO years (2020–23, 2025) plus AZPS/BPAT/SRP
for 2024. **Do not count these as validated** until each real artifact
and standalone annual audit are verified. The remaining 15 BA-years
will require their own evidence runs.
