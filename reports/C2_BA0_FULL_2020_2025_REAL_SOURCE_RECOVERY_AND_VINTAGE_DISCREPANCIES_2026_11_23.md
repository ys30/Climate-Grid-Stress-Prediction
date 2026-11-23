# C-2 BA-0 — six-year original panel recovered and independently enumerated (2026-11-23)

This is an **executed original-data recovery and read-only QA**, not another proposed experiment.

## Verified recovery

Original [GitHub Actions run 43629200989](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989), artifact `14127710411`, was downloaded. ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504` matched prior frozen source evidence. Inner original six-year gzip CSV SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac` matched the original manifest.

Independent extraction and complete UTC-key enumeration checked all **210,432** hourly BA source records, across **288 BA×calendar months** and **24 BA×years** (AZPS, BPAT, CISO and SRP; 2020–2025 inclusive). Every expected BA×UTC hourly key was present once; **210,172** rows have nonblank EIA reported demand, **260** source demand gaps remain blank, **70** events are unconfirmed anomaly *candidates*. No imputation, no model training. ERA5 temperature is reanalysis and uses **unapproved HIFLD-derived 2018 BA candidate masks**, not a certified historical or load-weighted BA exposure.

**Correction to recent progress narrative:** Full-year real ERA5 source collection had **already succeeded on November 14** and should not have been presented as a still-uncompleted download task. Subsequent four-month source matching/robustness remains useful for A/B geographic-proxy sensitivity, but is **not the limit of available historical source data**.

## Important new old-panel-vs-new-EIA annual QA discrepancies

A count comparison with later standalone strict EIA-930 annual audits shows **8 of 24 BA×years have differing numbers of nonblank old-archive demand hours versus valid newer annual-audit hours**:

| BA | Year | Older archived nonblank | Later source-audited valid | Delta (new − old) |
|---|---:|---:|---:|---:|
| AZPS | 2021 | 8760 | 8759 | -1 |
| BPAT | 2021 | 8760 | 8735 | -25 |
| BPAT | 2023 | 8760 | 8736 | -24 |
| CISO | 2021 | 8755 | 8754 | -1 |
| CISO | 2024 | 8736 | 8784 | +48 |
| CISO | 2025 | 8712 | 8760 | +48 |
| SRP | 2021 | 8735 | 8734 | -1 |
| SRP | 2025 | 8757 | 8760 | +3 |

**Not an established revision finding:** Old 'nonblank' and later 'valid nonnegative' filters are different. Differences could also arise from version/vintage, extract clock semantics, and QA. It would be scientifically invalid to silently overwrite the old six-year UTC rows with newer annual numbers. **Exact row-level, identical UTC-key, source-vintage comparison is the next priority.** The later strict QA has 23/24 BA×years passing; AZPS2023 still fails for two original negative demand values.

## Downloadable evidence

A verified self-contained user archive `C2_Complete_2020_2025_Source_Recovery_Vintage_Audit_2026_11_23.zip` (SHA256 `d68e6c5fa0e710f26ac83d841aca32d13f78de296a457ea26206f8f05c376808`) contains the **original GitHub artifact ZIP**, independent source-reading script, exact 288-BA-month coverage CSV, 24-BA-year comparison, SHA manifest, JSON audit summary and reproducibility report. Original data are **not copied into this public repository**.

## Hard scientific gates

- 2018 HIFLD candidate BA polygon source is **not** a 2020–2025 verified load-relevant BA operating geography. Two sampled alternatives (HIFLD vs TIGER) show spatial support sensitivity, but neither is approved.
- 2025 has already undergone exploratory description in this project; it cannot be represented as wholly unseen data.
- Candidate demand anomalies are not automatically source errors. EIA missing must not be coerced to zeros.
- No fitted forecast accuracy, weather attribution to anthropogenic forcing, SSP forecast or PyPSA stress output exists from this verification.
- C-1 frozen results remain unchanged.

**Recommended sequencing:** resolve exact old/new BA-year demand-hour value and missingness disagreements, independently audit dated BA operating footprints and geography-vintage sensitivity, then predeclare a leakage-resistant multiyear historical analysis.
