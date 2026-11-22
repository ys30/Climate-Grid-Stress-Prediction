# C-2 BA-0 — historical EIA-930 provenance reconciliation (2026-11-22)

## Corrected source-only cohort count

The Wave 1–3 index alone includes 22 of 24 source-verified BA-years. It **omits** the separately authenticated CISO 2024 pilot; this was not a missing observation. The independent source-and-artifact recheck is documented at `docs/E2_CISO_2024_EMPIRICAL_SOURCE_GATE_2026-11-18.md`, with raw HE SHA256 `04b927f1b890e0eb91df89b0db77f59010e0e37c4a63509b2ad34e61e0a8293d` and UTC-start SHA256 `375403e3fd278280bf8eb4140661f6dc7ab9102fa7111f2489a05c44f3051d9c`. 8784/8784 unique 2024 UTC hours and zero invalid values were independently checked. Run `44427373589`, successful job `135244337622`, artifact `14486655626`.

**Result: 23/24 canonical strict EIA-930 annual source gates have existing evidence.**

## Unresolved AZPS 2023 is a data anomaly, not just an expired artifact

The independent diagnostic `docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json` authenticates all 8760 UTC source timestamps and 2 negative demand values:

| UTC interval start | Source value MW |
|---|---:|
| 2023-12-19T20:00:00Z | -21897 |
| 2023-12-28T21:00:00Z | -10944 |

Remaining 8758 values pass the nonnegative numeric validity check; strict annual gate still FAILS. Do **not** replace these two original rows with zero, forward-fill them, assume demand is negative, or waive the canonical gate merely because overall coverage is 99.977169%.

An independently checked **noncanonical exclusion sensitivity** exists (`docs/E2_AZPS2023_SENSITIVITY_STATUS.json`), but its status explicitly states `canonical_source_gate_pass=false`. Any optional supplemental analysis must prominently disclose the two excluded observations and never misrepresent the sensitivity as canonical eligibility. A source correction or documented official revision is preferable.

## Machine-readable execution

```bash
python scripts/c2_eia930_wave_status_matrix.py \
  docs/E2_WAVE1_VERIFIED_STATUS.json \
  docs/E2_WAVE2_VERIFIED_STATUS.json \
  docs/E2_WAVE3_VERIFIED_STATUS.json \
  --standalone docs/E2_CISO2024_STANDALONE_SOURCE_STATUS.json \
  --diagnostic docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json \
  --output reports/generated/c2_eia_annual_provenance_matrix.csv
```

The version-controlled `c2-ba0-coverage-contracts.yml` asserts 24 cohort records, 23 source-verified, one strictly blocked and 0 model-training permissions. Test/CI green status must be independently confirmed from a real run before reporting a passed build.

## Next empirical priority

**Do not re-download CISO 2024 or repeatedly rebuild all 24 EIA years.** First recover authenticated data **bytes** from existing SHA-identified artifacts and create a durable, reproducible EIA hourly dataset inventory without exposing API credentials. Independently obtain and document fixed-site / explicitly characterized ERA5 hourly proxy data, UTC/time conventions, available variables and source hashes. Only thereafter run `scripts/c2_ba_hourly_join_audit.py` and report a real paired 2020–2025 BA-year coverage matrix.

Keep CISO/AZPS/BPAT/SRP geographic footprint proxies, NOT load-weighted counties, unless separate GEO-1 evidence is passed. Holdout years (2024–25) are not to be used to choose predictor selection, imputation or tuning. Full BA-0, geographic and future/CMIP6 gates are still blocked; no empirical forecast scores or anthropogenic climate attribution are established. C-1 is frozen.
