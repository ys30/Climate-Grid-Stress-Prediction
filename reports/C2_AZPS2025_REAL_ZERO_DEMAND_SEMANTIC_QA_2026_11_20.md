# C-2 EIA AZPS 2025 — source coverage is NOT semantic content quality

Date: 2026-11-20. **Real original-source QA, no modeling.**

## Evidence

Actual EIA-930 API AZPS 2025 source archived as GitHub Actions artifact
**14497859928**. Reopened and independently checked two original
source hashes:
- original raw HE CSV SHA-256:
  `a4c1b381ff9ab3efe573fbc5a19643329ea572ab4c045eb1441f047dc659ee16`
- original UTC-start converted CSV SHA-256:
  `f889acd93499bf9336b0447b0e7de650361f4730ae64c5cce7e023650da02110`

The original annual source completeness audit reports 8,760 distinct
hourly source keys, no missing hours/nulls, and `pass=true`. This
**does not mean all numerical demand readings are physically plausible**.

Independently read all 8,760 rows; actual source values from the raw
hour-ending file agree exactly with corresponding UTC-start values:

| Original UTC-start time | Actual reported demand | Adjacent observed demand | Classification |
|---|---:|---|---|
| 2025-07-31T19:00Z | **0 MW** | previous 7,143; next 7,122 MW | EIA-documented anomalous zero |
| 2025-07-31T21:00Z | **273 MW** | previous 7,122; next 485 MW | exploratory positive-low review |
| 2025-07-31T22:00Z | **485 MW** | previous 273; next 2,004 MW | exploratory positive-low review |

The `<1000 MW` review threshold is **not an official EIA criterion**
and **not an approved quality-correction rule**. It merely places
unusual positive values in a source QA queue.

U.S. EIA official EIA-930 methodology:
https://www.eia.gov/electricity/930-content/about.html
- Individual BA hourly data are published as received;
- EIA imputation for **aggregations** considers blank, negative and
  zero demand anomalous;
- Hourly and next-day submissions can differ, but such possible
  revision practices are not proof of the origin of these AZPS changes.

For this particular date, absence of a model-derived forecast error
does not make the zero valid or invalid by inference from neighboring
readings. Source-year coverage and content-based semantic validation
must remain **independent**.

## Machine-readable implementation

- `scripts/c2_azps2025_source_semantic_gate.py` verifies the raw ZIP,
  pins both CSV hashes, checks every UTC HE→start mapping and flags
  the zero / low-positive original values without changing anything.
- `tests/test_c2_azps2025_source_semantic_gate.py` guards zero, low
  positive and negative/nonfinite behavior on explicitly synthetic data.
- Real-source GitHub CI:
  https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44860248096
  **queued when this report was prepared; do not call it successful
  until completed and its artifact independently inspected**.
- Independent user-facing JSON:
  `C2_AZPS2025_Real_EIA_Source_Semantic_QA_2026-11-20.json`,
  generated from the authenticated Actions source ZIP.

## Scientific admission consequences

- AZPS 2025 has passed **source-hour completeness**, but independently
  **fails a content-based zero-demand semantic QA gate**.
- This content QA does **not** retroactively alter the 23/24 annual
  source-completeness/invalid-negative gate pass statistic; it is
  a **separate quality dimension**, not a replacement denominator.
- Treat 2024–2025 as untouched model holdout; source-only anomalies
  can be recorded without analyzing model performance or choosing
  a model based on those years.
- **No interpolation, replacement, winsorization or model fitting**;
  `model_training_permitted=false`.
- Original source revisions / actual archival BA operator submissions
  need separate provenance verification; no causal claim that EIA
  daily reporting or DST caused this zero.
- Project C-1 remains frozen.
