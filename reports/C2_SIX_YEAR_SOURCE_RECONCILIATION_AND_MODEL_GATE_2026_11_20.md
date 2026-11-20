# C-2 source completeness and scientific admission — corrected project state (2026-11-20)

## Executive finding

**Do not restart the six-year ERA5 source download.** Archived C-2 evidence
already contains a complete four-BA × 2020–2025 **source-only** hourly
ERA5/EIA panel from 72 genuine public ARCO ERA5 source-months.

The later single-point Sacramento 24h / February 696h jobs are **independent
temporal-interface diagnostics**, not the first production of six-year ERA5.

### Two separate denominators, both retained

| Audit type | Observed result | Interpretation |
|---|---:|---|
| Frozen six-year ERA5/EIA source archive | **210,432 BA-hours** | 4 BA × 52,608 UTC hours; all 24 BA-years represented |
| Original nonmissing EIA demand in frozen combined archive | **210,172** | 260 source missing hours retained blank |
| Frozen original anomaly candidate flags | **70** | Source candidates, not all proven errors; no EIA source value silently replaced |
| Newer strict per-year EIA-930 artifact+quality audit | **23/24 BA-years PASS** | AZPS 2023 fails strict canonical source gate |
| AZPS 2023 independent source diagnostic | **2 negative original hours** | Two anomalies, 2023-12-19T20Z and 2023-12-28T21Z |
| AZPS 2023 separate sensitivity derivative | **8,758 retained hours** | Source-gate fail unchanged; *noncanonical* only |
| Model-ready C-2 six-year training panel | **NOT admitted** | No approved BA weather-exposure geography/holdout anomaly protocol |

The older 70 anomaly candidates represent a **different screening definition
and source vintage** from the newer strict BA-year audit. They cannot be
subtracted or equated with the two proven AZPS negative observations without
a row-by-row source/revision reconciliation.

## Verified source evidence already present in this repository

- `reports/E1_FULL_2020_2025_REAL_ERA5_EIA930_SOURCE_DATA_FROZEN_QA.md`
  — actual all-month real-source consolidation success:
  https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989 ;
  artifact **14127710411**; immutable inner gzipped CSV
  SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.
- `reports/C2_E0_VERIFIED_210432_REAL_SOURCE_HOURLY_MODEL_ADMISSION_INTEGRITY_2026_11_15.md`
  — independent row-level original flags and all-zero science-admission checks.
- `reports/C2_E1_384_REAL_ERA5_ABC_INDEPENDENT_SPATIAL_SENSITIVITY_2026_11_14.md`
  — independent A/B/C real weather exposure differences, sampled 384 BA-hours.
- `reports/E1_REAL_BA_POLYGON_TOPOLOGY_GATE_2026_11_13.md`
  — raw 2018-vintage HIFLD candidate topology: AZPS/BPAT/CISO invalid,
  SRP valid; raw boundary year does NOT establish 2020–2025 BA operating
  area.
- `reports/E1_GEOMETRY_REPAIR_AND_EXPLORATORY_WEIGHT_GATE.md`
  — CISO topology repair changes raw invalid-geometry calculated area by
  approximately **7.0758%**. Not a measured change in true geographic area.
- `reports/C2_E1_E2_ADMISSION_DECISION_2026-11-14.md`
  — actual scientific criteria and source-vintage/holdout rule.
- `docs/E2_WAVE1_VERIFIED_STATUS.json`,
  `docs/E2_WAVE2_VERIFIED_STATUS.json`,
  `docs/E2_WAVE3_VERIFIED_STATUS.json`
  — independent newer per-year EIA source audits.

### Source-sensitive A/B/C already demonstrated

A = provisional 2018 HIFLD area-weighted geometry, B = 2024 TIGER county
membership proxy, C = Census April-2020 estimates-base county resident
population proxy. All three are *unapproved as validated BA electric load
weather exposure*. A/B/C sensitivity was measured with genuine matched
ERA5 grid data, not synthesized weather values.

From independently verified four sampled real 24-hour days (96 hours per BA):

| BA | B minus A mean °C | C minus B mean °C |
|---|---:|---:|
| AZPS | -1.921391 | +4.814620 |
| BPAT | +0.006933 | +0.595046 |
| CISO | -0.277619 | +0.390574 |
| SRP | -1.930985 | +1.964409 |

These are **source-mask sensitivity diagnostics**, not estimates of a
historical bias or load-temperature elasticity. 96 serially correlated
hourly samples are not 96 independent random days.

## Recommended research execution order (do not bypass)

**Gate G1: Historical BA geospatial identity**
Compare 2018 source control-area boundaries to independent, date-qualified
2020–2025 BA operator/service-region evidence. Independently verify spatial
intersections, crosswalk and topology. CISO topology-repair area discrepancy
and AZPS/SRP near-containment must be discussed explicitly. A county-based
source is an administrative proxy, not automatic load geography.

**Gate G2: Weather exposure estimand and source stability**
Preregister A/B/C as distinct *exposure estimands*. Clearly state whether
the target is geographic-area mean, residential-population-proxy mean or
actual load-weighted mean. Only use 'load weighted' when a validated
customer/asset/load allocation source exists. If historic geography is not
identifiable, a **sensitivity-only study** of exposure choices remains
publishable in principle, but calibrated load predictions remain blocked.

**Gate G3: EIA-930 demand anomalies and time split**
Reconcile canonical negative source hours, original frozen candidate anomaly
screens, source revision vintages and missing hours, including independent
SRP February 2023 revision review. Do not impute original demand. Preserve
train=2020–22, validation=2023, untouched test=2024–25; do not tune
geographic weights by test skill.

**Gate G4: Joint eligibility and model admission**
Once approved, produce a new **derived** 2020–25 panel from the already
verified frozen source archive, with independently documented spatial masks
and source-vintage hashes. Run temporal source, joint coverage and
holdout/leakage gates before calendar baselines/GAM/XGBoost. Any observational
temperature association is not anthropogenic ALL-vs-NAT attribution.

**Gate G5: Future SSP / PyPSA only after history**
Do not infer 2030/2040/2050 projections, grid adequacy or outages from
unapproved E2 models or synthetic climate inputs.

## Automated fail-closed reconciliation

- Script: `scripts/c2_six_year_evidence_reconciliation.py`
- Tests: `tests/test_c2_six_year_evidence_reconciliation.py`
- CI: `.github/workflows/c2-six-year-admission-reconciliation.yml`
- First new job: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44767783044
  (queued when written; do not call successful without checking)
- Machine-readable status must state `model_training_permitted=false`
  regardless of source totals.

C-1 frozen repository/results are untouched.
