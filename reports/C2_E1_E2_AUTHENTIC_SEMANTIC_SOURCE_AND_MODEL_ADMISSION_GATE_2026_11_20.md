# C-2 E1→E2 actual-source model admission decision — 2026-11-20

**Decision: SOURCE PROVENANCE VERIFIED; SCIENTIFIC MODEL ADMISSION BLOCKED.**
C-1 research stays frozen. No model fitting, anthropogenic attribution,
future SSP/PyPSA forecast, raw EIA values change or test-set tuning.

## Newly independently confirmed real-source CI evidence

Two previously queued authentic-source workflows are now **SUCCESS**:

1. [23 canonical-pass BA-years real semantic source QA, run 44861789787](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44861789787), source evidence artifact **14692623744**, extracted original JSON SHA-256 `b4abc2ac79ebf9e04c0f2b677b136f0d91d7aed5be4bb676c9dc99f54471fc61`.
2. [Actual AZPS 2025 raw EIA HE semantic source QA, run 44860248096](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44860248096), source evidence artifact **14691111231**.

The original CI-produced JSONs were *downloaded and separately inspected*
rather than inferring success from a committed workflow file.

| Independently authenticated source field | Actual value |
|---|---:|
| Annual EIA source groups with strict original completeness pass | **23/24** |
| Expected UTC-hour slots in 23 annual pass groups | **201,672** |
| Actual UTC timestamps present | **201,671** |
| Missing whole UTC timestamp keys | **1** |
| Explicit missing reported demand values | **210** |
| Actual zero reported demand values | **1** (AZPS 2025) |
| Positive reported demand values 0–1,000 MW | **2** (AZPS 2025; nonofficial review rule) |
| Excluded BA-year failing source numeric validity | **AZPS 2023** (2 genuine negatives) |

The AZPS 2025 original source reports 0 MW at
`2025-07-31T19:00:00Z`, 273 MW at
`2025-07-31T21:00:00Z`, and 485 MW at
`2025-07-31T22:00:00Z`. The threshold 1,000 MW is a
**preliminary investigation filter only**, not an official EIA error
definition or a justification for replacing, deleting or interpolating
demand.

Older frozen 72-month source archive
[run 43629200989](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989)
contains **210,432 true public ARCO ERA5 / EIA BA-hour *source-only* rows**
across all four BAs × 2020–2025. Its denominator, revised EIA API annual
source quality (23 passing groups), and model-admitted rows are distinct.
The original frozen archive remains unchanged.

## Three scientific gates, all currently BLOCKED

| Mandatory gate | Original-source evidence preventing approval | What would clear it |
|---|---|---|
| `GEO_HISTORICAL_BA_FOOTPRINT` | 2018 HIFLD geography is not certified as 2020–25 hourly electricity BA operating support; CISO raw polygon invalid and make-valid area diagnostic differs ~7.08%; AZPS/SRP candidate masks overlap ~96.66% of SRP polygon area | Independent date-qualified BA geography/crosswalk interpretation and explicit source-license/topology/overlap review |
| `GEO_LOAD_RELEVANCE` | 1,418 historical utility–BA–state associations had 979 county matches; neither source association coverage nor Census resident population establishes observed BA hourly demand locations | Original EIA861 sales/customers or other load-location data with careful utility-state/BA mapping and geographic uncertainty, not mere source association counts |
| `LOAD_QUALITY_HOLDOUT_PROTOCOL` | AZPS 2023 negative values; AZPS 2025 authentic zero/low values; 23-BA-year old/new EIA vintage mismatch and exact missing timestamps; 2024–25 remains held out | Source-vintage investigation, frozen anomaly treatment criteria based on train/validation only, immutable 2024–25 holdout rules; do not tune on test years |

PUDL tagged release v2026.10.0 provenance was already verified; this
does **not** waive missing load geography. The preliminary 2018 HIFLD A,
2024 county B and Census estimates-base population proxy C have **real
ERA5 sensitivity results**, but none is an approved electricity-load
exposure. This memo does not claim a validated weather-demand association.

## Machine-checkable integration with real data

- `scripts/c2_real_source_scientific_admission_decision.py` accepts
  only the published original run **44861789787** semantic evidence JSON
  whose exact SHA-256 is pinned, then checks frozen geography/source
  reference reports. It does not grant geography approval.
- `tests/test_c2_real_source_scientific_admission_decision.py` checks
  SHA tampering, unauthorized zero-to-positive demand changes and
  failure to admit a model despite source success.
- `.github/workflows/c2-real-source-scientific-admission.yml` retrieves
  authentic original Actions artifact **14692623744**, verifies all
  mandatory blockers, and publishes JSON-only decision evidence.

**No provenance or model result is inferred solely from a queued job.**
Current real model admission CI:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44870740392

## Required next scientific work

Prioritize independently dated BA operator identity and actual utility
customers/sales source coverage before trying another weather-demand
model. Independently reconcile EIA vintage-specific anomalous values,
including zero-load reporting and AZPS2023 negative values. Predeclare
the exposure estimand and a chronology-safe 2020–22 / 2023 /
2024–25 train/validation/held-out split before any E2 calibration. If
historical BA load geography remains unidentifiable, present the
already-verified A/B/C reanalysis as a **geographic exposure sensitivity
study**, not climate-attributable electric demand or calibrated future
stress prediction.

C-1 source, results, and submission package remain untouched.
