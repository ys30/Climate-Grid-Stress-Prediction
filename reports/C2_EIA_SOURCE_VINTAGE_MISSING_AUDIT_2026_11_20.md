# C-2 EIA source-vintage audit: the 260 vs 210 missing-hour discrepancy

Status 2026-11-20: **accounting comparison implemented; individual source
hour revisions NOT independently established**. C-1 frozen.

## Sources and denominators

The original 2020–2025 four-BA ARCO ERA5 × EIA-930 archive has **210,432**
BA-hour rows, **260** original EIA demand blanks, and **70** candidate
source anomalies (not all proven errors). It has all **24 BA-year groups**
present but uses a geographically **unapproved** ERA5 exposure candidate.
Source ZIP artifact 14127710411, workflow:
https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989 .
The original inner gzip SHA-256 is
`88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

Newer EIA-930 API strict annual source evidence is archived in:
`docs/E2_WAVE1_VERIFIED_STATUS.json`,
`docs/E2_WAVE2_VERIFIED_STATUS.json`, and
`docs/E2_WAVE3_VERIFIED_STATUS.json`. Those files independently
authenticate **22** passing cohorts in the three waves, plus **CISO 2024**
from separate source pilot evidence = **23 passing BA-years**.
**AZPS 2023 fails** canonical annual QA because two authentic original
negative values were found; its noncanonical derivative does not
count as annual source QA pass.

## Comparison — NOT a repair rate

| BA | Original archive 6-year missing | Newest passing annual cohorts missing |
|---|---:|---:|
| AZPS | 26 | 25 (**AZPS 2023 excluded**) |
| BPAT | 0 | 49 |
| CISO | 109 | 13 |
| SRP | 125 | 123 |
| **Total** | **260** | **210** |

**Do not claim that the 50-unit difference equals 50 corrected hours.**
These are different source-release/vintage definitions AND different
BA-year denominators. The counts alone establish neither the direction
of changes to individual values nor whether the old/new original data
are comparable on every hour. The increased BPAT missingness and
decreased CISO missingness in the newer API run require a direct
row-keyed vintage audit. Never infer either source is more correct
solely because its missingness count is smaller.

The genuine AZPS2023 diagnostic:
`docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json`
shows **8,760 original time keys**, **zero null demand rows**, and
**two invalid negative source values**:
- 2023-12-19T20:00:00Z, -21897 MW
- 2023-12-28T21:00:00Z, -10944 MW

These two source anomalies are numeric negatives, **not missing nulls**,
and must not be silently added to the 260/210 source missing totals.

## Work completed

- `scripts/c2_eia_cross_vintage_missing_accounting.py` reads all
  3 audited waves plus the separately authenticated AZPS source diagnostic.
- `tests/test_c2_eia_cross_vintage_missing_accounting.py` asserts both
  incompatible totals, per-BA counts, duplicate BA-year rejection, and
  rejection of mislabeled AZPS negative-as-missing rows.
- `.github/workflows/c2-eia-cross-vintage-gaps.yml` runs regression
  tests and emits the research-quality fail-closed JSON ledger.
- Initial run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44770480518
  (queued at initial authoring; job/artifact success not yet verified).

## Next scientific audit: actual source revisions

1. Re-download immutable old original full six-year artifact and the
   authentic newer annual EIA sources under separate versioned filenames.
2. Pin file hashes, retrieval dates, official EIA source vintage details,
   EIA HE→UTC-start conversions and hourly schema.
3. Build per-BA-year, per-UTC-hour comparisons distinguishing:
   missing→nonmissing, nonmissing→missing, positive value→different
   positive value, negatives, exact agreement, and conflicting source
   timestamps. Preserve both original values; never impute or overwrite.
4. Report changes on an explicitly matched BA-year denominator, not a
   24-group vs 23-passing-group denominator.
5. Do not unseal 2024–25 test years for model selection or tune geographic
   masks using any test-period values; revision QA may verify source
   integrity without examining model performance.
6. Keep `model_training_permitted=false` until geographic load relevance,
   historical BA identity, and abnormal-source/holdout gates are cleared.

This accounting check adds **no** new model predictions, causal climate
attribution or SSP PyPSA forecasts.
