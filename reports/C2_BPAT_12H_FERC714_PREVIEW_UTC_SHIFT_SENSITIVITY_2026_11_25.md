# C-2 BPAT — 12-h public preview clock-offset sensitivity, authentic archived EIA-930 (2026-11-25)

## Execution and source status

Used the previously delivered archived `C2_BPAT_FERC714_2025_12h_Public_Preview_EIA930_Compare_2026_11_25.zip` and its original 72-month EIA-930 BPAT source (inside the BPAT 6-year baseline ZIP). The archived original EIA gzip SHA-256 was independently rechecked against the inner actual source manifest: `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

The 12 third-party **AskTheGrid preview values** are copied directly from the previous audit. They are **not verified against the underlying BPA workbook** and are *not* a verified original operator source. The original BPA 2025 XLSX direct download URL was retried in the container and download helper: the former failed DNS resolution; latter returned failure. GitHub workflow run/artifact status still cannot be confirmed; therefore do not claim its original BPA files were downloaded.

## Actual alternative time-alignment calculation

Take 2025-12-31 12:00–23:00 UTC third-party preview `event_time` strings; compare the same values against EIA-930 BPAT archived UTC *interval-start* demand with experimental integer offsets −12 through +12 h. Preserve common-hour counts, never fill missing or manufacture 2026 EIA data.

| Preview UTC time shift | Source-matched hours | Mean absolute difference MW |
|---|---:|---:|
| −8 hours | 12 | 963.166667 |
| −1 hour | 12 | 251.416667 |
| **0 hours** | **12** | **6.750000** |
| +1 hour | 11 | 254.363636 |
| +8 hours | 4 | 689.000000 |
| +12 hours | 0 | not computed |

**0 h is the smallest MAE of the shifts that allow all 12 hours to be paired**, and matches the previous signed mean preview-minus-EIA difference of −6.75 MW. The 25-shift CSV reports each shift; shifts with fewer than 12 pairs must not be ranked directly against complete-pair candidates. This supports the plausibility of the **third-party rendered UTC labels**, not the truth of original BPA hour-ending, reporting timezone/DST, load series semantics, or six-year load equivalence.

## Verified artifact

User package `C2_BPAT_12h_Preview_UTC_Clock_Sensitivity_2026_11_25.zip` SHA-256 `9ce8ed8d6b083b1ce25a82b4fd765ee950e38d04a0d926149bcee767ec47674d` (2,638,051 bytes), contains complete previous archived preview and EIA source ZIP, source-hashed 25-offset CSV, result JSON, Python reproducer, six **actually passed local Python tests**, and README. ZIP was reopened and CRC validated.

## Scientific interpretation and next source gate

BPA officially lists its 2020–25 original FERC-714 annual XLSX: https://transmission.bpa.gov/business/operations/ferc714/default.aspx . The FERC-714 reported series may include area load, system load and BPA BA area load; exact clock and measurement definitions must be read in the **original** workbook before comparing them with EIA-930. A third-party preview can be used as a lead only. The next measurement task is to recover the source XLSX in GitHub Actions, pin its SHA and original cells, then recompute multiple full days including DST and exact series selection before expanding to full six years.

Historical BA geography and load-weighted hourly exposure still unapproved; demand-vintage and holdout restrictions persist; no forecasting, climate attribution, CMIP6 SSP or PyPSA adequacy simulation results are claimed. **C-1 frozen and untouched.**