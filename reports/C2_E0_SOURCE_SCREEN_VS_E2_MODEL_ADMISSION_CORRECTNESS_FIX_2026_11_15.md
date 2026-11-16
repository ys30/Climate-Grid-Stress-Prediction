# C-2 E0 source screening vs formal E2 model admission — correctness correction

Date: 2026-11-15. C-1 frozen; E2 model training still blocked.

## Confirmed actual code issue and fix

Before this update, `src/c2_episode_quarantine.py` wrote `model_eligible = not bool(flag)` for each observed raw EIA-930 hour. This code conflated **passing the source anomaly screen** with **passing scientific training admission**, even though `GEO_HISTORICAL_BA_FOOTPRINT`, `GEO_LOAD_RELEVANCE` and `LOAD_QUALITY_HOLDOUT_PROTOCOL` were not cleared. An unflagged demand row therefore might falsely appear approved to downstream workflows.

Commit `0136d71bea2ca0d39acd02b6ee7649cb37664266` changed the row-level source-only classification to two separate fields:
- `source_candidate_eligible = not bool(flag)`: still evaluates the **current source-only anomaly screen**, and is NOT an approved source correction.
- `model_eligible = False`: fail-closed across all rows until all scientific admission gates are satisfied.

The CSV now contains both columns; JSON summary reports both source-screen-eligible count and zero **model-eligible** observations with explicit `historical_BA_geography_approved=false`, `load_relevance_approved=false`, `model_training_permitted=false`, `training_executed=false`, and `imputation_performed=false`.

## Regression and reproducibility

- Synthetic-data regression tests in `tests/test_c2_episode_quarantine_model_admission.py` (commit `9361be7e502534f314d1f45d128dc528a6516f6c`) verify that a clean and a flagged source hour differ in source candidate status but **both remain model-ineligible**. They also exercise the actual CSV/JSON writer under mocked source input and assert that neither output enables E2 model fitting.
- Workflow `.github/workflows/e0-source-vs-model-admission-regression.yml` (commit `3e651c9323ec8297dd6e0b2e042a1816959ce73c`) runs these tests on push or manual dispatch. A completed CI run **was not independently available** during this update. Do not claim tests passed on GitHub until a run result is retrieved.
- No historical EIA-930 data were altered or used for this synthetic test; the 2024–2025 holdout remains sealed. The change is a pipeline correctness fix, not a new scientific result or proof that historical BA geography is valid.

## Scientific next blockers

Historical EIA-930 raw ZIP-vintage verification still lacks a successfully retrieved 3-vintage source-hour comparison artifact. Candidate weather geography (HIFLD/TIGER/population) still lacks independent electricity-load relevance. 2020–2023 source diagnostics and real ERA5 proxy sensitivity are real evidence, but central E2 predictive validation, historical anthropogenic attribution and future SSP/PyPSA stress results are not yet completed. `model_training_permitted=false`.
