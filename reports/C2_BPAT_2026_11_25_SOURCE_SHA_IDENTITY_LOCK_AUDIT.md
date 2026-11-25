# C-2 BPAT — immutable BPA FERC714 original-source SHA lock and unresolved acquisition (2026-11-25)

## Original-data acquisition: verified state

- [Official BPA annual FERC-714 index](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) exposes the six 2020–2025 original XLSX links, and a public URL request advertises the XLSX MIME type.
- Original official bytes **were not downloaded in this turn** from the assistant runtime (network DNS/download failure), and **no original operator-cell measurements or workbook SHA** can be reported.
- GitHub combined-status and associated commit-workflow-run queries returned empty arrays for `fedfc670b6d49d23f7c569769bc0cf50af763e88` and `89ca535bb77670121167966888f63c46d327bb72`. The workflow query is **PR-trigger-filtered**, so this does **not prove** that push-triggered Actions did or did not run. No actual BPA source artifact ID was independently identified.
- The prior 12-hour FERC714 values were transcribed from a third-party preview and remain **unverified against authentic operator workbook originals**. Their apparently close match to archived EIA930 cannot establish six-year independent validation.

## Corrected a source integrity hole

The previous BPA XLSX downloader would re-read an already-existing workbook and write its **current** SHA; a modified but structurally valid workbook would falsely appear reverified. Source hash recomputation alone cannot establish continuity against earlier source bytes.

Changes in `scripts/c2_bpa_ferc714_original_acquisition.py`:

1. On fresh download into an empty per-run output directory, save each real XLSX and SHA to the **first-acquisition** file `BPA_FERC714_SOURCE_SHA256_LOCK.json`.
2. On re-use of an existing output directory, require that the archived workbook's SHA matches its **previously frozen year-specific** value. Refuse existing unpinned XLSX and changed valid XLSX.
3. If a pinned file is absent, fail closed instead of silently replacing it with a newly downloaded publication version. Do not mutate an existing original in place.
4. Preserve a per-year failure cause and separate `existing_original_invalid` from `source_not_verified`.

Three additional synthetic-only test definitions cover (a) modified **valid** XLSX failing, (b) unpinned existing XLSX failing and (c) missing pinned XLSX failing. The existing previous-source and invalid structure tests remain. **9 total committed test methods**; no verified GitHub Actions green result in this turn.

### IMPORTANT durability limitation

GitHub-hosted Actions runners have **ephemeral local disks**. This lock protects continuity **within a persisted directory**, or within an independently recovered previous artifact, **not automatically across distinct Actions runs**. To prove cross-run identity, the prior original XLSX plus lock must be restored from immutable, independently SHA-verified artifacts, or a release-specific expected SHA must be pinned in git before another run. A fresh directory in a new Actions run creates a new first-acquisition lock for that run only. Do not interpret `first-acquisition` as a publisher-certified timestamp or authenticated archival chain.

## Existing independent source baseline

A separately authenticated **52,608 BPAT-hour EIA-930 2020–2025 source baseline** and three annual API vintage snapshots were already computed. They remain **EIA data**, not an operator independent observation, and retain unresolved 2021/2023 source-vintage differences. The next strict scientific gate is to obtain true BPA XLSX original bytes, record a pinned source snapshot and original cell/range schema, and only then compare homologous load measurements after HE/UTC conversion.

BA geography/load-weighted exposure remains not approved; 2025 already examined descriptively; no causal climate attribution, SSP projections or PyPSA adequacy simulation permitted. **C-1 frozen and untouched**.
