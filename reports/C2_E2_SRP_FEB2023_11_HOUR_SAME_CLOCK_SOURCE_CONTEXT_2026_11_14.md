# Project C-2 E2 — SRP February 2023 original 11-hour source event and same-hour references

Date: 2026-11-14 Mountain. Real original source archive SHA256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504` (GitHub Actions run 43629200989 / artifact 14127710411), inner hourly GZIP SHA256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`.

An independent Python re-ingestion extracted 11 raw SRP demand hours (20:00Z Feb 26 through 06:00Z Feb 27). For each center timestamp a descriptive reference median was calculated using the *same UTC clock hour* for up to seven days before and seven days after, excluding original missing-demand hours and original anomaly-flagged hours. No source value was altered.

| UTC interval start | Original SRP demand (MW) | Same-hour reference median (MW) | Raw/reference | Original anomaly flag |
|---|---:|---:|---:|---|
| 2023-02-26T20:00Z | 3,049 | 2,869 | 1.063 | No |
| 2023-02-26T21:00Z | 3,031 | 2,844 | 1.066 | No |
| 2023-02-26T22:00Z | 2,958 | 2,853 | 1.037 | Yes |
| 2023-02-26T23:00Z | **68,520** | 2,940 | **23.306** | Yes |
| 2023-02-27T00:00Z | **45,097** | 3,073 | **14.675** | **No (missed)** |
| 2023-02-27T01:00Z | **27,030** | 3,266.5 | **8.275** | **No (missed)** |
| 2023-02-27T02:00Z | 3,578 | 3,298 | 1.085 | Yes |
| 2023-02-27T03:00Z | 3,626 | 3,235 | 1.121 | No |
| 2023-02-27T04:00Z | 3,559 | 3,162 | 1.126 | No |
| 2023-02-27T05:00Z | 3,355 | 3,013.5 | 1.113 | No |
| 2023-02-27T06:00Z | 3,178 | 2,847 | 1.116 | No |

Three consecutive reported hours are unusually large, then return close to prior/following comparable source values. This is a **source anomaly candidate signature only**, not evidence of confirmed data error, physical load shed, or climate causation. Same-hour median is not a weather-adjusted expected demand. Original source ERA5 2018 candidate mask remains unapproved as representative load exposure. E2 model training remains BLOCKED.

## Distinct external provenance issue
Two date-separated PUDL original EIA-930 archive records are confirmed: https://zenodo.org/records/17688027 (2025-11 v53, `eia930-2023half1.zip` MD5 `122e5d253321b7baef657a4880f9a579`) and https://zenodo.org/records/22215263 (2026-09 v92, the same named ZIP MD5 `1b4acef4e1ec596cf92e7658f9be64c7`). Archive-byte differences DO NOT imply this SRP event was revised. The GitHub workflow `e2-srp-eia930-vintage-comparison.yml` has been added but no actual passed 11-hour cross-vintage comparison has been independently verified in this update.

The complete local 11-hour CSV, JSON, report and reproduction script are saved as `C2_SRP_FEB2023_11_HOUR_SOURCE_EVENT_CONTEXT_20261114.zip` in the conversation. C-1 is frozen; `model_training_permitted=false`.
