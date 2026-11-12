# E0 verified source intake milestone — 2026-11-12

## Independent observed success
- **GitHub Actions run:** https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43280016458
- **Code commit:** `a36f2aa8a9588673025aa7a28cdb7734c961dbfd`
- **Scope:** UTC start intervals July 1, 2024 00:00–23:00, four EIA-930 BAs AZPS/BPAT/CISO/SRP, **96 expected and 96 valid** demand BA-hours; 0 missing, duplicate, blank/invalid records.
- **Official Jan–Jun 2024 balance CSV hash:** `26768c495c3ba987e29d79df2e40d4e741f9dbcff086f53c12ff774465756a10`.
- **Official Jul–Dec 2024 balance CSV hash:** `a602a8e577cfdd2fa3083413eaa4dd8ba7f0d2b26a2986f8f6d22917465ea49f`.
- **Scientific interpretation:** observational demand source-access and 24-hour reporting coverage ONLY. No ERA5 alignment, 2020–2025 complete-year validation, climate attribution, held-out forecast skill, or physical blackout inference.

## Recovery of earlier failures
- Official API call without a key returned HTTP 403: https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43275075481
- First H2-only CSV attempt yielded 68/96 BA-hours, missing 28 boundary BA-hours; both halves are required.
- EIA 2024 Jan–Jun and Jul–Dec fuel/category columns differ. The intake explicitly harmonizes only three stable original demand columns; no automatic fusion of fuel categories.

## Full-year audit status
The original combined 2023/2024 annual audit exceeded its 25-minute job limit and was cancelled (https://github.com/ys30/Climate-Grid-Stress-Prediction/actions/runs/43280524210). This is a **workflow execution failure, not observed annual missingness**.

A revised parallel per-year workflow imposes bounded download deadlines and independently stores source SHA256, 4-BA annual completeness, and a preregistered chronological split gate. Results are not claimed until independent successful runs and artifacts are inspected.

## Next gate
1. Verify 2023/2024 annual candidate admission.
2. Broaden to 2020–2025 only after source requests are bounded and year audits have stable runtime. A 99% coverage threshold alone is not equivalent to complete hourly event data; contiguous heat-event windows require separate event-specific complete-case admission.
3. Obtain geographically representative ERA5 gridded exposure and record a spatial weights/version/clock manifest.
4. Compare calendar baselines with GAM and boosted-tree models using 2020–2022 train / 2023 validation / 2024–2025 sealed holdout, only if cohort coverage permits.
