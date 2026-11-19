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
