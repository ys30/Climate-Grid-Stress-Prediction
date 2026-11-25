# C-2 BPAT — actual 12-UTC-hour public FERC714 PREVIEW vs archived EIA930 (2026-11-25)

## What was actually computed

The independent external [AskTheGrid BPA FERC714 hourly load preview](https://askthegrid.com/catalog/bpa_ferc714_hourly_load) publicly displays 2025-12-31 operator-labeled `BPA BALANCING AUTHORITY AREA LOAD`, `hour_ending`, UTC `event_time`, numerical MW and `source_file=FERC714_2025_Masterx.xlsx`. I transcribed the **12 visible rows with UTC event_time from 2025-12-31T12:00 through 23:00**, preserving displayed timestamps and values as third-party *preview*, not verified workbook originals. I independently reopened the archived original six-year EIA930 source ZIP, verified gzip SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`, and paired 12 BPAT reported-demand hours on the same UTC interval-start keys, without fill or source version substitution.

| UTC interval start | Third-party FERC714 preview MW | Archived original EIA930 BPAT MW | Preview minus EIA MW |
|---|---:|---:|---:|
| 2025-12-31 12:00 | 8285 | 8291 | -6 |
| 2025-12-31 13:00 | 8734 | 8741 | -7 |
| 2025-12-31 14:00 | 9225 | 9232 | -7 |
| 2025-12-31 15:00 | 9563 | 9570 | -7 |
| 2025-12-31 16:00 | 9702 | 9709 | -7 |
| 2025-12-31 17:00 | 9650 | 9658 | -8 |
| 2025-12-31 18:00 | 9380 | 9387 | -7 |
| 2025-12-31 19:00 | 9038 | 9044 | -6 |
| 2025-12-31 20:00 | 8691 | 8698 | -7 |
| 2025-12-31 21:00 | 8439 | 8440 | -1 |
| 2025-12-31 22:00 | 8345 | 8357 | -12 |
| 2025-12-31 23:00 | 8376 | 8382 | -6 |

**12 preview pairs; signed mean difference −6.75 MW, MAE 6.75 MW, maximum absolute difference 12 MW, all 12 differences nonzero.** These are actual published preview observations against frozen actual EIA, not modeled predictions, but original operator source bytes **have NOT been downloaded and SHA authenticated**, the displayed third-party data has **not** been separately verified, and exact original BPA reporting clock/measurement scope is **not** proven. The observation is a *time alignment/provenance lead*, not formally independent certified BA-year validation.

## Executed tests and user package

Archive `C2_BPAT_FERC714_2025_12h_Public_Preview_EIA930_Compare_2026_11_25.zip` (SHA256 `187b40e41eefbd2598696ba2fb4b17f5826498fb33e045eaf421663c18453bf0`) contains the complete original **2.63-MB** previously authenticated BPAT EIA source pack, frozen preview literal values with source citation in `reproduce.py`, 12-hour output CSV, audit JSON, README, and **4/4 actually passed** local Python unittest checks. Unpacked source ZIP's original archived gzip hash was compared to original manifest; user can reproduce offline using only Python standard library.

## Additional source-download status

Original BPA [2020–2025 FERC714 XLSX index](https://transmission.bpa.gov/business/operations/ferc714/default.aspx) and direct report URLs are official and verified. The local environment still cannot resolve `transmission.bpa.gov` for direct binary downloads, so no official XLSX original workbook has been archived here. GitHub Actions downloader is committed, but its completed execution and artifacts have not been verified. It would be incorrect to call these 12 preview comparisons an authenticated FERC714 original analysis.

**Next operator-source gate:** acquire BPA 2025 original XLSX, hash, verify `BPA BALANCING AUTHORITY AREA LOAD` raw hourly source and define original UTC conversion. Repeat the 12-hour comparison from original cells and then full 2020–25 source. Keep all EIA vintages isolated. Spatial BA control boundary/load weights and scientific modeling admission remain BLOCKED. C-1 unchanged/frozen.