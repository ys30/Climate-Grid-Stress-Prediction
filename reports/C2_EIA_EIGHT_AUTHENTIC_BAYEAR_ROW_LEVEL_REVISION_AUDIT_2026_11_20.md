# C-2 EIA old vs new authentic source: first independent row-level reconciliation (2026-11-20)

This is **real-source QA** only. It is not E2 predictive evaluation or a
change to the frozen six-year original source. C-1 remains frozen.

## Authenticated source provenance

Frozen six-year 2020–2025 archive:
- GitHub run https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989
- Original artifact ID **14127710411**
- Actual outer ZIP SHA256:
  `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`
- Embedded original CSV.gz SHA256:
  `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`
- All 210,432 original BA×UTC-hour source records individually enumerated.

Compared against **eight actually accessible, original, newer API annual ZIP
artifacts**: CISO 2020, 2021, 2022, 2023, 2024, 2025; AZPS 2024; BPAT
2024. Each newer CSV passed its source manifest SHA256 and its original
Actions annual QA. This is **eight** verified annual samples, not all 24.

Each matching key uses `(BA, year, timestamp_utc_start)` with exact source
EIA hour-ending conversion preserved. Original values and source ZIPs were
read-only throughout the comparison. Neither source EIA demand nor ERA5
temperature was interpolated or overwritten.

## Actual verified classifications

| Comparison classification | Count |
|---|---:|
| Exact equal numeric EIA demand | **70,010** |
| Both old and new have explicit blank EIA demand | **13** |
| Frozen old EIA demand blank; newer API has numeric demand | **96** |
| Frozen old numeric; newer API explicitly blank | **0** |
| Both numeric but EIA demand differs | **56** |
| Newer API hourly timestamp absent altogether | **1** |
| **Total UTC hour slots across 8 BA-years** | **70,176** |

The single newer missing time key is **CISO 2021-11-07T05:00:00Z**.
The older six-year original archive contains an EIA demand of
**22,672 MW** at that exact UTC time. The new 2021 annual source QA
reports 8,759 unique in-year timestamps and 1 absent hour, yet still
passes the predeclared >=98% annual coverage gate. Thus the previous
short-form description of this annual ZIP as “8,760 recorded hours”
was imprecise; it has **8,759 rows**, not 8,760.

### Changes by verified cohort

| BA/year | Old blank | New explicit blank | Old blank → new value | Changed numeric | Missing new timestamp |
|---|---:|---:|---:|---:|---:|
| AZPS 2024 | 0 | 0 | 0 | 0 | 0 |
| BPAT 2024 | 0 | 0 | 0 | **56** | 0 |
| CISO 2020 | 3 | 3 | 0 | 0 | 0 |
| CISO 2021 | 5 | 5 | 0 | 0 | **1** |
| CISO 2022 | 3 | 3 | 0 | 0 | 0 |
| CISO 2023 | 2 | 2 | 0 | 0 | 0 |
| CISO 2024 | 48 | 0 | **48** | 0 | 0 |
| CISO 2025 | 48 | 0 | **48** | 0 | 0 |

### Observed temporal clustering — source mechanism NOT established

- CISO 2024 missing→numeric: exactly 48 hours, from
  **2024-11-01T07:00:00Z** through **2024-11-03T06:00:00Z**.
- CISO 2025 missing→numeric: 48 hours grouped around March 8–9 and
  November 1–2, 2025.
- BPAT 2024: 56 changed numeric hourly demand values, mostly small
  integer differences observed in August–October; the first changed
  source hour is 2024-08-06T15:00:00Z with old **6,629 MW**, new
  **6,630 MW**.
- CISO 2021 source time missing at 2021-11-07T05:00:00Z, while old
  frozen source reported 22,672 MW.
- Several clusters coincide with US daylight-saving transition
  windows. **This is only a temporal observation, not evidence that
  DST caused the source differences**. Verify the exact EIA-930
  original source/revision vintage and timestamp semantics before
  assigning a mechanism.

## Local independently generated reproducibility package

The user-facing evidence package
`C2_EIA_OLD_vs_NEW_AUTHENTIC_ROW_CHANGE_AUDIT_2026-11-20.zip`
contains:
- `C2_EIA_OLD_vs_NEW_AUTHENTIC_ROW_CHANGE_AUDIT_2026-11-20.csv`
  with all old/new disagreements and exact original values
- matching JSON report with eight BA-year SHA256 and annual QA;
- Python source used to regenerate the comparison from the original
  archived ZIPs without imputation or model use.

The package was produced outside GitHub Actions by directly reading the
authentic archived source ZIPs. The frozen six-year source was SHA-pinned.
It is a subset-source audit, not a revised 24-BA-year annual gate.

## Priorities to unblock science

1. Perform matching source-vintage comparisons on the **remaining 16**
   BA-years, especially **BPAT 2021/2023** and **SRP**; treat AZPS 2023's
   two negative original API values as invalid canonical observations,
   and keep its noncanonical sensitivity separately.
2. Investigate the source revision/extraction clock of CISO 2021 and
   DST-adjacent 2024/2025 changes, not assuming which source is correct.
3. Retain train 2020–22, validation 2023, test 2024–25; all test-year
   inspection here is **source integrity only**, not hyperparameter
   selection or model evaluation.
4. Geography/load-relevance and anomaly/holdout admission remain
   BLOCKED: `model_training_permitted=false`. The full
   210,432-source-hour archival provenance does **not** certify
   operational BA climate exposure.

No new supervised modeling, anthropogenic attribution, forecast skill or
future SSP–PyPSA outcome is claimed in this report.
