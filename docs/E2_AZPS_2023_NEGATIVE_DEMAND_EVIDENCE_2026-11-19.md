# C-2 E2 AZPS 2023: authenticated negative-demand anomaly

## Provenance (verified 2026-11-19 UTC)

- Diagnostic run: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/44463391069
- Diagnostic artifact ID: `14503830832`
- Signed evidence status: `docs/E2_AZPS2023_DIAGNOSTIC_STATUS.json`
- Original EIA HE CSV SHA-256: `3f56ed359e8eea0298e611f85f00f3b0b20f6b104d0a43064db8ebfc9a80a6eb`
- Derived UTC-start CSV SHA-256: `fdbb0f8692dc201e0e2f36ee72c7a831255fa86d01800ba639adb61e6dd0054f`

The complete SHA chain (original CSV, source manifest, derived CSV,
conversion manifest, annual report) is independently authenticated.
The UTC year includes 8760/8760 distinct timestamps, no source nulls,
no missing timestamp hours, and **two invalid negative demand values**.

| UTC interval start | EIA reported demand | Classification |
|---|---:|---|
| 2023-12-19T20:00:00Z | -21897 MW | invalid negative demand |
| 2023-12-28T21:00:00Z | -10944 MW | invalid negative demand |

The effective measured-demand coverage excluding the anomalies is
8758/8760 = **99.977169%**. The annual source audit's `pass` remains
**FALSE**, because any negative nonblank demand is disallowed under the
current canonical source-quality rule, irrespective of aggregate coverage.

## Required research handling

1. Never replace the two reported values with zero, local mean, or a
   fabricated interpolated value. Keep raw source and SHA unmodified.
2. Treat AZPS 2023 as **source-gate failed** in the canonical 24 BA-year
   inventory; verified inventory remains **23/24**.
3. A separately derived, explicitly flagged *sensitivity* panel may
   exclude those hours from model scoring, recording exact timestamps,
   original values, and all provenance hashes. It is not an alternate
   `pass` result for the canonical source gate.
4. Recheck the official EIA demand semantics / subsequent data revisions
   before publication and record whether these hours reflect errors,
   corrections, or special data conventions.
5. Report all estimates with and without AZPS 2023, using matched
   evaluation samples and no invented load or weather values.

The 2020–2025 four-BA EIA source validation is **23/24**, not 24/24.
No ERA5 joint-hour eligibility or climate attribution follows from this audit.
The frozen C-1 repository is unchanged.
