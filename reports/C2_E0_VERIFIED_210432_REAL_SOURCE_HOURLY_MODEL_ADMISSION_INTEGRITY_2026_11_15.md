# C-2 E0: Independently audited all 210,432 real archived BA-hours for source/model admission integrity (2026-11-15)

**Actual original source archive, not synthetic regression data.** C-1 remains frozen; E2 scientific model admission remains blocked.

## Verified immutable sources
- Existing successful GitHub Actions run [43629200989](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989), artifact `14127710411`.
- Outer original ZIP SHA-256: `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Embedded six-year original hourly GZIP SHA-256: `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

Using a fresh independent Python reader directly against the archived compressed original source panel, I verified source timestamps (year/month/UTC), unique BA-hour keys, original demand-missing flags, original source anomaly flags and the per-row **model_training_eligible** and **geometry_historically_approved** assertions.

## Observed six-year results

| Measure | Verified original source data |
|---|---:|
| BA-hour records | **210,432** |
| BA-year groups | **24 / 24** (AZPS, BPAT, CISO, SRP, 2020–2025) |
| Original missing-demand hours | **260** |
| Original flagged candidate anomaly hours | **70** |
| Rows with `geometry_historically_approved=True` | **0** |
| Rows with `model_training_eligible=True` | **0** |

2020–2023 training/validation source metadata: **140,256** BA-hours, **113** original missing-demand rows, **68** original flagged anomaly candidate rows. Remaining 2024–2025 original test metadata covers **70,176** rows; it was inspected **only for source integrity and model admission assertions**, not for model fitting, threshold selection or comparative forecast evaluation. The two independently found, *originally unflagged* February 2023 SRP observations are NOT part of the frozen original 70 flags; preserving the original source flags is deliberate.

## Reproducible output
`C2_REAL_210432_HOUR_ADMISSION_INTEGRITY_AUDIT_20261115.zip` attached to this project conversation contains the independent source-reader script, verified 24-BA-year row/flag/missing counts JSON, and README, with archive-specific pinned source SHA-256 and fail-closed eligibility checks. ZIP SHA-256: `176570f007a3cfc885061b5cf0255eb8c3b2614dabe7ccfe5b27c6aadf6395a5`.

## Interpretation and blockers
A successful source eligibility audit **does not** approve historical load-weighted BA weather exposure or prove any questionable EIA-930 original observation is an error. It also does not establish GitHub's latest newly added CI workflows completed. The three pinned original EIA-930 Zenodo version comparison program has been submitted, but as of this check **no independently verified real three-vintage comparison result** was accessible through the available connector. Direct public ZIP download was blocked in this environment.

Source-only classification and model admission are separately protected in commits `0136d71bea2ca0d39acd02b6ee7649cb37664266`, `6e8714655bbcd07d0459cee7b48db73cda3cc440`, `defa854dce0332fb12ff26a2c62981008b3d8b74`.

**Decision:** `model_training_permitted=false`, `GEO_HISTORICAL_BA_FOOTPRINT=BLOCKED`, `GEO_LOAD_RELEVANCE=BLOCKED`, `LOAD_QUALITY_HOLDOUT_PROTOCOL=BLOCKED`. No GAM/XGBoost prediction skill, historical ALL/NAT attribution or SSP/PyPSA stress inference can be claimed.
