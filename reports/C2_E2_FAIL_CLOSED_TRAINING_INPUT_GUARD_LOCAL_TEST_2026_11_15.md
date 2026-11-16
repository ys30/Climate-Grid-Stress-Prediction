# C2 E2 source-to-model input admission: verified fail-closed guard

Date: 2026-11-15. C-1 remains frozen; `model_training_permitted=false`.

## Why a downstream guard was necessary
The source-only E0 `c2_episode_quarantine.py` exporter was corrected previously to distinguish `source_candidate_eligible` from `model_eligible`. However, an individual downstream consumer could still misinterpret a clean source flag or forged CSV `model_eligible=True` as permission for weather-demand training. This new read-side preflight independently rejects such cases. It does **not** unlock model training.

## Implemented and committed
- `src/c2_e2_training_input_guard.py`: reads an E0 observed-hour CSV and E0 source QA JSON, requires both distinct eligibility columns, requires five *explicit* denial flags (`model_training_permitted`, `historical_BA_geography_approved`, `load_relevance_approved`, `training_executed`, `imputation_performed`), rejects any `model_eligible != 'False'`, incompatible candidate/quarantine flags, duplicate BA-hours, and CSV-vs-manifest observed/candidate/quarantine count differences. Produces source QA only and exits nonzero on all CLI outcomes, **including source QA success**.
- `tests/test_c2_e2_training_input_guard.py`: six synthetic regressions for valid source-only QA, forged training approval, omitted manifest denial, duplicate keys, contradictory flags and QA-count mismatch.
- `.github/workflows/e2-training-input-guard-tests.yml`: new on-push/manual CI test workflow. **Not yet verified successful from Actions**.

## Actual verification (local)
A standalone equivalent copy of the source guard and tests was executed with Python unittest in this conversation container; six tests ran and **all six passed**. Packaged as `C2_E2_FAILCLOSED_TRAINING_INPUT_GUARD_20261115.zip` (SHA256 `dffe4090c27cc1d8b1d5dd4f22624c9640f5d71082e6171a8a811f7c4075b7c5`). These are **synthetic logic tests**, not validation on all 210,432 archived source rows; the original 2024–2025 demand holdout was not accessed.

## Research progress and limitations
This closes a *software safety/semantic* gap, not the geography or historic data-revision scientific gate. Original source panel and existing 27 candidate events remain unchanged. E2 historical load-weather training, ALL/NAT attribution, SSP scenario weather and PyPSA future stress remain pending independent operational geography/load exposure and source QA validation. A passing local guard test does not imply approved model fit or climate inference.

Commits: `6e8714655bbcd07d0459cee7b48db73cda3cc440` (guard); `defa854dce0332fb12ff26a2c62981008b3d8b74` (tests); `72b5365b3192523d59a68ec9c402cfa2e2c8d693` (workflow).
