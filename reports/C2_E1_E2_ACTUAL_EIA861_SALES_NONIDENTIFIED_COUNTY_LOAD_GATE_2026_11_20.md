# C-2 E1/E2 scientific admission correction: actual EIA861 retail sales already verified

Updated 2026-11-20. C-1 frozen; C-2 E2 scientific model training remains blocked.

## Why this correction matters

The prior joint scientific-admission report highlighted 1,418 utility–BA–state
associations and 979 county source matches but did not reflect **already completed
original PUDL v2026.10.0 sales acquisition and county-identifiability experiments
from 2026-11-17**. It would be inaccurate to describe EIA861 sales MWh as
not yet acquired or to suggest that 2020–23 observed MWh county identifiability
is wholly unexamined.

### Authenticated annual retail sales source

PUDL v2026.10.0 original `core_eia861__yearly_sales.parquet` has actual SHA256
`996d6ac640ab664272187711a45b5944cf3116cab882ca05749f93d4a74ae9fe`,
and passed independent real-source acquisition runs
[44032717255](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44032717255),
[44031912206](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44031912206)
and SHA-pinned [44037370237](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44037370237).
Frozen 24-row annual MWh summary SHA256:
`2b437b6288e1d8221aa555c63aadfbf16d033406b4ac5ee6c70bff0d497987c0`.

The source has **24/24 BA-year** selected nonempty bundled retail sales
observations, 2,224 retained source records with observed MWh, across
2020–2025; this is a different denominator from the 23/24 strict annual
EIA930 demand-content source QA.

## Actual 2020–2023 retail MWh support: not meter location

Verified source-run [44244205677](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44244205677)
(artifact **14400293606**) and its independent MWh reconciliations give:

| BA | Total selected retail MWh | One-county conditional MWh | Multi-county ambiguous MWh | Unlocated-source MWh |
|---|---:|---:|---:|---:|
| AZPS | 129,057,618 | 4,840,693 | 120,464,912 | 3,752,013 |
| BPAT | 207,663,786 | 83,728,317 | 123,932,777 | 2,692 |
| CISO | 463,195,807 | 57,723,274 | 389,552,906 | 15,919,627 |
| SRP | 124,284,031 | 0 | 123,741,352 | 542,679 |
| **Total** | **924,201,242** | **146,292,284** | **757,691,947** | **20,217,011** |

The ~**82.0%** multi-county ambiguous share of all selected MWh
(757,691,947 / 924,201,242) has **no uniquely identified county
allocation** from utility–BA–state service county membership alone.
The ~15.8% single-county portion is only *conditional* on a complete,
accurate service-county list and the selected retail MWh being distributed
exclusively to those counties; it is **not observed county-level electricity**.
The remaining ~2.2% has no source county link under the frozen rules.
These denominators are observed *retail sales*, not hourly BA reported demand.

The initial 810 null original 2020–23 sales class cells have separately
authenticated exact source lineage: **468** 'other' slots have no original
form column; **342** originate as literal `.` in original Excel, a
missing symbol, not an automatically estimated 0. See
`reports/C2_E1_EXACT_810_ORIGINAL_EIA861_MWH_NULL_SECTOR_CELL_LINEAGE_2026_11_17.md`,
run [44217883298](https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44217883298).

## Research implication

**EIA861 original annual sales source availability = YES.**

**Identified actual county MWh and 0.25-degree hourly load-weighted ERA5
exposure = NO.**

This distinction is now encoded in the existing unified scientific
admission program
`scripts/c2_real_source_scientific_admission_decision.py`, with regressions
in `tests/test_c2_real_source_scientific_admission_decision.py`.

Historical operating BA geography, physical load-to-weather spatial
support and EIA demand quality/holdout all remain CLOSED, so
`model_training_permitted=false`. The frozen C-1, historical ERA5
source archive and 2024–25 EIA demand test holdout are unchanged.

Next useful action is not re-downloading sales: obtain **independent actual
county allocation of customer meters or retail MWh** for major ambiguous
source entities (AZPS utility ID 803, SRP 16572, CISO 17609/14328/16609),
carefully checking source coverage, vintage and eligibility. If unavailable,
formally bound the inference to weather geography sensitivity and conditional
MWh source-support results rather than claiming validated BA load exposure.
