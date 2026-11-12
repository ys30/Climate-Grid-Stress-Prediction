# C-2 E0 2023–2024 annual EIA-930 observed demand coverage — CI verified

## Verified execution
- Successful GitHub Actions annual audit: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43293578993
- Implementation commit `e3d8974201a922b82d2827abe8e3ce093a84476c` (fixed binary SHA-256 EOF sentinel).
- Archived artifacts contain four-BA annual coverage CSV, source SHA256 manifests, and temporal-gate status (individual year jobs).
- Research claims: official raw reporting coverage, **not** true demand reconstruction, climate attribution, physical adequacy, modeled EENS, or outage observations.

## Valid-hour counts
| Year | BA | valid / expected | missing timestamp keys | blank/invalid values | duplicate keys |
|---|---|---:|---:|---:|---:|
| 2023 | AZPS | 8751 / 8760 | 7 | 2 | 0 |
| 2023 | BPAT | 8752 / 8760 | 8 | 0 | 0 |
| 2023 | CISO | 8750 / 8760 | 8 | 2 | 0 |
| 2023 | SRP | 8753 / 8760 | 7 | 0 | 0 |
| 2024 | AZPS | 8777 / 8784 | 7 | 0 | 0 |
| 2024 | BPAT | 8776 / 8784 | 8 | 0 | 0 |
| 2024 | CISO | 8728 / 8784 | 8 | 48 | 0 |
| 2024 | SRP | 8729 / 8784 | 7 | 48 | 0 |

**Important:** 7/8 missing keys per BA persist despite using both official half-year files; determine whether year-boundary source slices/labels explain them before imputing or interpreting as unreported operational intervals. The 48 invalid/blank CISO/SRP values require exact date inspection. Do not silently fill these, especially for extremes.

## Admission interpretation
- 2023 and 2024 each pass a *provisional 99% BA annual coverage threshold*. This does not establish event-window completeness, source consistency, or physical validation.
- The locked 2020–2022 train / 2023 validation / 2024–2025 test split is **not fully admitted**, since 2020–2022/2025 were not yet audited at this verification point.
- The 2023 validation slice passes the provisional annual threshold. 2024 alone is not a complete sealed test admission (2025 missing).
- Next: expand 2020–2025 annual coverage, identify exact missing timestamps, and build representative ERA5 spatial exposures. Keep the scientific outcome as observed BA reported demand.
