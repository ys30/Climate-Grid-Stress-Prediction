# C-2 EIA-930 observed revision windows and local-calendar-day hypothesis (2026-11-20)

## Why this was checked

The authentic old-vs-new 23-canonical-pass BA-year EIA-930 row comparison
(`reports/C2_EIA_23_BAYEAR_AUTHENTIC_ROW_REVISIONS_2026_11_20.md`)
identified 231 numeric changes and 150 explicit missing-status
changes. Newer raw hourly EIA-930 HE files were independently checked against
their converted UTC-start files for **AZPS 2025**, **BPAT 2021** and **BPAT 2023**;
all 219 changed hours in these three cohorts were present in the upstream
source, not introduced during the newer UTC conversion.

This follow-up re-read the pinned original changed-row CSV with SHA-256
`6c85c48789e55c51a7ad37e8eecbffe7f4b9cef0a7a8b354012e27d423bdd480`.
It groups **219** relevant changed UTC-hour keys into **15** contiguous
episodes, retaining the classifications and never filling source gaps.

## Three full local-calendar-day fingerprints

| Candidate BA | Exact changed UTC interval | Hypothetical local time zone | Mapped local civil day | Hours |
|---|---|---|---|---:|
| AZPS 2025 | 2025-07-26T07Z to 2025-07-27T06Z | America/Phoenix (UTC-7) | 2025-07-26 00–23 | 24 |
| BPAT 2021 | 2021-09-15T07Z to 2021-09-16T06Z | America/Los_Angeles (PDT, UTC-7) | 2021-09-15 00–23 | 24 |
| BPAT 2023 | 2023-10-24T07Z to 2023-10-25T06Z | America/Los_Angeles (PDT, UTC-7) | 2023-10-24 00–23 | 24 |

All three are complete 24h local civil days *under the selected
timezone hypotheses*. **The operator-specific EIA submission timezone
has not been independently authenticated**. Do not equate the
hypothesis with BA reporting practice or infer source revision mechanisms
solely from alignment. Note especially that an hourly EIA timestamp
representing UTC interval start can map to a different local reporting
hour-ending label.

## Relevant official EIA publication protocol

EIA Form EIA-930's official About documentation:
https://www.eia.gov/electricity/930-content/about.html

EIA collects an hourly demand submission following the operating hour
and another report at 7 a.m. on the next day for the prior day's
demand; the two values may differ, and historical corrections are
expected. EIA also documents that its **individual BA hourly source**
values are published as received, whereas higher-level aggregations
can use gap/anomaly imputation. This institutional mechanism makes
daily-batch vintage differences plausible, **but it does not confirm
that any specific AZPS/BPAT change resulted from a particular daily
submission or EIA correction**.

## Reproducibility and epistemic limits

- Source-only diagnostic code:
  `scripts/c2_eia_local_calendar_revision_probe.py`
- Synthetic regression tests:
  `tests/test_c2_eia_local_calendar_revision_probe.py`
- Independent user-facing source evidence:
  `C2_EIA_LOCAL_DAY_REVISION_HYPOTHESIS_2026-11-20.zip`,
  with CSV of all 15 episodes, JSON classifications, analysis script,
  and caveat README.
- The exact extracted episode CSV SHA-256:
  `5e516a2a386658e0e85ab6fc99799860163518cf4ebf08f0ccf477d6f04f9d01`.
- The 2024–2025 test years were checked **only for source integrity**.
  No model choice, weather-response fitting, skill evaluation,
  imputation, original-demand overwrites, or causal inference.
- C-2 historical BA operating geography remains unapproved,
  `model_training_permitted=false`; C-1 remains frozen.

## Next authentic evidence needed

1. Obtain the **actual reporting timezone**/submission offset and
   historical EIA-930 BA operator metadata for AZPS/BPAT.
2. If available, obtain authoritative BA/EIA transmission revision
   identifiers or source submission records for the particular days,
   with dated source vintage and original HE stamps.
3. Reconcile the 2025 AZPS near-zero and 0 MW values using historical
   original submissions, *not* automated replacement or thresholds
   chosen on the held-out 2024–2025 period.
4. Preserve unresolved revised hours as a documented quality-sensitivity
   risk, not as model-admitted correct observations.

## 2026-11-20 DST-aware audit refinement and EIA authority check

The earlier 24-hour/constant-UTC-offset classifier is replaced by **exact
IANA local-midnight-to-next-midnight UTC interval equality**. This is
necessary because a reporting local calendar day can contain 23 or 25
real hours on US DST transition dates. The source-independent regression
tests now exercise Pacific 2025-03-09 (23 hours), Pacific 2025-11-02
(25 hours), and Phoenix's year-round 24-hour civil days.

The SHA-pinned original 23 BA-year changed-row CSV was independently
re-audited after this correction: **219 changed hours**, **15 contiguous
episodes**, and the same **three complete local-civil-day fingerprints**
under the respective selected candidate zones. The result is unchanged
by explicit DST handling; the distinction is methodological robustness.

Authoritative references:

- EIA official Form 930 data guide:
  https://www.eia.gov/electricity/930-content/about.html .
  It explicitly says BA reports are **hour-ending**, individual BAs
  select their report-local time zones, and spring/fall DST days can
  have **23/25 hourly records**. EIA receives hourly values and a later
  daily resubmission; differences are possible.
- EIA current AZPS BA display:
  https://www.eia.gov/electricity/gridmonitor/dashboard/electric_overview/balancing_authority/AZPS
  — uses **Arizona Time** on its current display.
- EIA Northwest regional dashboard:
  https://www.eia.gov/electricity/gridmonitor/dashboard/daily_generation_mix/regional/REG-NW
  — shows BPAT daily generation using **Pacific Time** on the current
  dashboard. This evidence describes contemporary dashboard labels;
  it does NOT prove original BPAT submission-zone configuration for
  2021/2023 or give access to archived respondent-level revisions.

New source-only outputs:
`C2_EIA_DST_AWARE_REVISION_EPISODES_2026-11-20.csv` and
`C2_EIA_DST_AWARE_REVISION_QA_2026-11-20.zip` contain the independently
recomputed 15-episode table and explicit negative causal/admission flags.
The revised script is `scripts/c2_eia_local_calendar_revision_probe.py`;
test `tests/test_c2_eia_local_calendar_revision_probe.py`.

No respondent revision ledger has been obtained, no archived BA-specific
reporting-timezone proof is claimed, and **model_training_permitted=false**.
