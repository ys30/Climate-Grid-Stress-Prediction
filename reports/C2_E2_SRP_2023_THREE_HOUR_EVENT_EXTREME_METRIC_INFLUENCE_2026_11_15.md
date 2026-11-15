# C2 E2 — Actual SRP February 2023 three-hour event influence on annual extremes

Independently recomputed **2026-11-15** directly from the verified six-year original archived BA-hour source. This is a **descriptive source QA sensitivity**, NOT an approved source correction, weather model, causal attribution or PyPSA result. C-1 remains frozen.

## Verified input source

- Original GitHub Actions run [43629200989](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43629200989), artifact `14127710411`, ZIP SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504`.
- Embedded 2020–2025 real hourly CSV.gz SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.
- Exact SRP calendar 2023 records: **8,760 valid hourly original demand observations**. The original `model_training_eligible=False` and `geometry_historically_approved=False` flags were independently checked.
- Original February 2023 three consecutive extreme candidate hours: `2023-02-26T23:00Z=68,520 MW`, `2023-02-27T00:00Z=45,097 MW` and `2023-02-27T01:00Z=27,030 MW`. The latter two were missed by the original source-neighbor screen, but independently detected by follow-up local-median screens.

## New original-data influence calculation

Compare unmodified complete 2023 SRP original source statistics with **diagnostic omission only** of those exact three extreme source hours. This is not authorization to remove or impute them.

| Annual source-demand statistic | Original all 8,760 hours | Diagnostic omitting three candidate hours (8,757 hours) | Original minus diagnostic |
|---|---:|---:|---:|
| Mean MW | 3920.391096 | 3905.673062 | 14.718034 |
| Maximum MW | 70,313 | 70,313 | 0 |
| P99 MW | 7792.46 | 7768.40 | 24.06 |
| P99.9 MW | **36009.149** | **8875.516** | **27133.633** |
| Reported hourly MW sum (MWh if hour-average MW) | 34,342,626 | 34,201,979 | 140,647 |

The diagnostic P99.9 drops **75.35% relative to the original value** despite only three omitted hours, while annual maximum remains 70,313 MW. Therefore this event profoundly affects high-tail statistics but is *not the only* extreme observation in SRP 2023. Upper-tail statistics cannot be treated as validated stress events until remaining high-demand source records are independently checked.

Percentile definition: linear interpolation at position `(n-1)*p` in sorted values. This is not an empirical claim about corrected grid load.

## Interpretation and next steps

1. Include a source-QA sensitivity table for annual mean, high percentile and peak rather than calling 68,520/45,097/27,030 MW confirmed errors.
2. Investigate remaining annual peak 70,313 MW and other original extreme hours with independently dated EIA-930 reporting versions; *do not* use a lower tail estimate as a replacement observed demand.
3. Verify the submitted pinned Zenodo-vintage comparison workflow `.github/workflows/e2-srp-eia930-vintage-comparison.yml` before claiming SRP revisions. Latest job result could not be confirmed in this turn; **no historic revision proven**.
4. Keep geographic source A/B/C as unapproved weather exposure proxies; E2 load-weather model gate and 2024–2025 sealed test remain closed.

The fully reproducible original source-only Python script, CSV, JSON evidence and report are delivered in the linked conversation archive `C2_SRP_EVENT_INFLUENCE_20261115.zip`; the raw original six-year data itself is not redistributed in that small archive.

**Status:** `model_training_permitted=false`, original sources unchanged, no forecast skill or climate-change causal claim made.
