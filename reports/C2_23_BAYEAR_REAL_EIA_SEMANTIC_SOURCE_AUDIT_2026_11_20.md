# C-2 EIA-930: Independent real 23-BA-year demand semantic source audit — 2026-11-20

## Exact provenance and results

Read original independently downloaded GitHub Actions source ZIPs from **all
23 strictly canonical-source-passing BA-years**: AZPS 2020–22/2024–25,
BPAT 2020–25, CISO 2020–25 and SRP 2020–25. AZPS 2023 remains excluded
from this particular canonical-pass group because its *two original
negative reported demand records* fail annual gate; they remain separately
preserved, not zero/null imputed.

Each of 23 original archive ZIPs was opened, and **both** raw original EIA
hour-ending CSV SHA-256 and converted UTC-start CSV SHA-256 were recomputed
against the original embedded manifests. For all observed yearly records,
the preserved original HE report value matched the converted UTC-start
record exactly under the `HE - 1 hour` convention. The original annual
coverage audit for each cohort also reported `pass: true`.

| EIA source quantity | Authenticated count |
|---|---:|
| Canonical-pass BA-year datasets | **23** |
| Expected UTC hour slots | **201,672** |
| Original source UTC hourly keys present | **201,671** |
| Missing UTC *timestamp keys* | **1** |
| Observed rows with explicit null demand | **210** |
| Original demand values exactly equal to zero | **1** |
| Original positive values below a provisional 1000 MW flag | **2** |

The single missing *timestamp* is CISO 2021-11-07T05:00:00Z,
not one of the 210 explicit null EIA demand rows. Both must remain
separate. No gap was interpolated or filled.

The three content-review observations are all **AZPS 2025**,
the authentic EIA reported values from raw HE source:
- 2025-07-31T19:00:00Z — **0 MW**, original HE
  2025-07-31T20.
- 2025-07-31T21:00:00Z — **273 MW**, original HE
  2025-07-31T22.
- 2025-07-31T22:00:00Z — **485 MW**, original HE
  2025-07-31T23.

EIA's zero demand category warrants formal content-quality review.
The *strictly positive below 1000 MW* criterion is **an exploratory
review cutoff chosen only for source forensics**, not an EIA-sanctioned
rejection rule or proof that these values are erroneous. Other 22 BA-year
sources did not contain values in these two categories.

## Source version integrity is not prediction readiness

Prior source-vintage reconciliation already identified 231 revised
numeric hours across the 23 BA-years, plus source missing-state changes;
those source versions are not silently replaced by this scan. A passing
calendar-year *source completeness* audit does not certify physical
content plausibility, historical geographical relevance or suitability
of archived 2018 HIFLD BA masks.

The entire old four-BA 2020–25 ERA5/EIA original source archive remains
210,432 BA-hours; it is untouched. Its weather exposure was an
**unapproved 2018-vintage geography candidate**, not a qualified
electric-load-weighted BA temperature. Model training and
weather-based prediction/causal attribution/future SSP PyPSA inference
stay blocked.

2024–25 years examined strictly for source integrity, without
optimizing any model, thresholds or spatial masks using held-out
prediction outcomes.

## Reproduction and evidence

- Reproducible source-scanning program:
  `scripts/c2_eia_23_year_semantic_source_audit.py`.
- Scope regression:
  `tests/test_c2_eia_23_year_semantic_source_audit.py`.
- Authentic-source GitHub Actions workflow:
  `.github/workflows/c2-eia-23-year-semantic-source-qa.yml`
  https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44861789787
  (QUEUED when documented; **not a verified successful workflow**).
- Independently verified local file pair:
  `C2_EIA_23_BAYEAR_REAL_SEMANTIC_QA_2026-11-20.csv`
  and `C2_EIA_23_BAYEAR_REAL_SEMANTIC_QA_2026-11-20.json`.
  Both list original artifact ZIP filenames and 23 per-year raw/UTC
  SHA-256 fingerprints. Included in user-facing ZIP
  `C2_EIA_23_BAYEAR_REAL_SEMANTIC_QA_2026-11-20.zip`.

## Outstanding blockers

1. Determine whether specific AZPS 2025 original 0/273/485 MW readings
   were revised or corrected by EIA/BA using *dated upstream source
   submissions*, not automatically assuming which published vintage is
   right.
2. Keep the 1 missing UTC key and 210 explicit null rows distinct in
   coverage and sensitivity checks. Keep AZPS 2023 two invalid negatives
   outside canonical-pass cohorts.
3. Verify true 2020–25 BA operating-area weather-exposure geography,
   electric load/customer locational relevance, and locked
   training=2020–22 / validation=2023 / test=2024–25 protocol.
4. No model training/admission, reconstructed source "fix", historical
   climate attribution or future grid-stress inference at this step.

C-1 remains frozen.
