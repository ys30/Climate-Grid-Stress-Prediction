# C-2 BA-0 — five-half-year original EIA source-byte acquisition gate (2026-11-23)

## Executed work (not a planned proposal)

Read two immutable previous authenticated user archives: `C2_2020_2025_72_Month_Original_Source_Archive.zip` (original 210,432 BA×hour 2020–2025 EIA/ERA5 source) and `C2_C2_EIA930_Dual_Vintage_210432h_Quarantine_2026_11_23.zip` (12 later API BA-year snapshots, 325 real old-vs-new disagreements). Validated old archive SHA, the old ZIP SHA embedded in the quarantine provenance manifest, and the quarantine's **actual conflict CSV SHA-256**. Reconstructed the true EIA original **hour-ending** time for all 325 conflicts and traced their old raw six-month source SHA-256 plus newer API raw-source SHA-256.

All 325 conflicts map into **exactly five source bulk half-years**:

| Original EIA bulk half | All 325 conflict hours | Changed numeric values | Blank/key differences |
|---|---:|---:|---:|
| `2025_Jul_Dec.csv` | 175 | 149 | 26 |
| `2024_Jul_Dec.csv` | 48 | 0 | 48 |
| `2025_Jan_Jun.csv` | 48 | 23 | 25 |
| `2021_Jul_Dec.csv` | 30 | 2 | 28 |
| `2023_Jul_Dec.csv` | 24 | 0 | 24 |
| **Total** | **325** | **174** | **151** |

Each individual conflict now has an explicit acquisition target for EIA's official bulk CSV and the historically frozen SHA. The output CSV distinguishes *current official file* from *historically identical original source bytes*. A source-byte inspection helper can compare future downloaded bulk CSVs and report whether the **whole file** equals the 2026-11-14 historically archived SHA; when SHA differs, it cannot certify what EIA revised or which source was correct at publication.

## Retrieval limitation, strictly recorded

The EIA official documentation lists 6-month bulk CSV and API distribution; direct retrieval of current official EIA original bulk bytes was attempted but **failed in this execution environment**. Thus these historical file bytes were not retrieved or proven equivalent to the stored original SHA values. The 325 individual conflicts remain **root-cause-unresolved**, and no demand value is silently replaced or imputed. The source-download URLs in the queue are targets, *not* verified downloads. Five files represent all **currently known** discrepancies among twelve compared BA-year API snapshots, not a guarantee that un-compared BA-years are conflict-free.

## Reproducible local package and tests

Delivered the complete independently tested user bundle `C2_EIA930_Five_Bulk_SourceByte_Investigation_2026_11_23.zip` SHA-256 `22fea7c62afc46e26526c505a0255b1bd3c399b3b1dcae61ffaa14df87c9333c`, containing the frozen source ZIPs, 325-row byte-acquisition queue, prioritized five-half-year CSV, strict no-overwrite `c2_eia_bulk_api_provenance_gate.py`, README, source SHA manifest, and **4 locally passing contract tests**. Internal ZIP contents were reopened and SHA-verified.

**Scientific gate stays closed:** old 2018 candidate BA mask not certified historical operational or load-weighted BA geography, 2025 already descriptively inspected, AZPS2023 strict annual source gate fails. No source-vintage correction, model fitting, causal climate attribution, CMIP6 forecast or PyPSA output claimed. C-1 unchanged/frozen.

**Next execution priority:** secure the complete original EIA `EIA930_BALANCE_2025_Jul_Dec.csv` and `EIA930_BALANCE_2025_Jan_Jun.csv` source bytes; compare their SHA to frozen originals, then inspect raw hour-ending rows. Without matched historical bytes or release snapshots, describe evidence as source-vintage discordance rather than confirmed official corrections.
