# C2 four-BA full original EIA-930 source anomaly family screen — 2026-11-26

## Actually executed

Re-read full original four-BA dual-vintage quarantine archive (210,432 hour rows) from local immutable `C2_C2_EIA930_Dual_Vintage_210432h_Quarantine_2026_11_23.zip`, ZIP SHA-256 `2e61b850272495e9e1644f23d06a3bb1c3aa93229229974a0ac7aa00432eec4c`, inside gzip SHA-256 `5a7fc7bf030cdac33131c480ca0c145db0b942db050e09bf1c5d1396994dbee1`. Source hash checks are hard gates; all four BA-hour identifiers unique.

For every original BA hour, compare the observed original bulk MW against the median of up to 20 other observed reference hours at offsets [-12,-3] and [+3,+12]. Only screen if at least 14 valid reference hours exist, current demand >=10,000 MW and demand >=3× reference. **This threshold is an exploratory high-precision candidate screen, not an automatic error detector or approved cleaning rule.** It will miss non-spike problems (including some physical anomalies) and may flag rare real peaks.

| BA | Original source-anomaly flags (all hours) | Newly screened extremes | Screened but NOT source-flagged | Screened with API numerically available |
|---|---:|---:|---:|---:|
| AZPS | 12 | 3 | 1 | 0 |
| BPAT | 0 | 0 | 0 | 0 |
| CISO | 1 | 0 | 0 | 0 |
| SRP | 57 | 20 | 2 | 11 |
| **Total** | **70** | **23** | **3** | **11** |

### Three previously unflagged review candidates

1. **AZPS 2024-01-23 18:00 UTC:** 11,308 MW, 3.365× nearby 3,360.5 MW median, originally unflagged; API year **not fetched**. No claim it is an erroneous value.
2. **SRP 2023-02-27 00:00 UTC:** 45,097 MW, 14.233× nearby 3,168.5 MW median; source unflagged but adjacent to flagged hour. Old bulk / later API numeric match where checked.
3. **SRP 2023-02-27 01:00 UTC:** 27,030 MW, 8.531× nearby 3,168.5 MW median; also unflagged, API numeric matching as checked.

Importantly, BPAT 2020-11-25 23:00 UTC (11,742 MW) does not cross the strict 3× contextual filter, **which does not certify the value**; see prior five-event audit. Existing flags + this screen must be reported separately, without silently modifying original loads.

### Actual reproducibility

- Executed exact local source script `c2_four_ba_spike_family_screen.py` with pinned ZIP and gzip hashes.
- Actually ran seven local original-source regression tests, **7/7 passed**: source hashes, complete cohort, source flags insufficient, three exact previously unflagged hours, model gate closed, API-not-checked semantics, unpinned file rejection.
- Outputs full 23-row event ledger, 4-row BA summary, a provenance JSON with derived file SHA, tests and logs.
- Downloadable self-contained archive `C2_Four_BA_20261126_Full_Cohort_Anomaly_Family_Audit.zip` contains the actual 210,432-row **original dual-vintage ZIP** plus script, 7 tests, all actual output, and README. ZIP SHA-256 `a262fdf92b5eba6aa1bbaacaf27ea84f4237dfca7a340e73a2254924d7269862`, CRC checked.
- GitHub `scripts/c2_four_ba_eia930_spike_family_source_audit.py` is a separately authored equivalent implementation; do **not** claim it was byte-identically executed or that CI passed.
- Full review-candidate data stays in downloadable reproducible archive, not just this four-row Github table.

### Scientific decision

**No source value altered or removed.** The new anomaly family screen improves source review coverage, but does not solve cross-vintage API gaps (including AZPS/BPAT 2020), establish SRP/APS operator certified load, FERC714 respondent 21 hourly validation, ERA5 historic BA geography, or a scientifically admitted weather model. It cannot be interpreted as new causal climate evidence.

EIA's official API route is `/v2/electricity/rto/region-data/data/`; official portal confirms Form EIA-930 hourly BA electricity data at https://www.eia.gov/opendata/browser/electricity/rto/region-data . The still-missing 2020 API hours should be acquired with source query/time-convention and response hashes before making a vintage claim.

**C-1 remains frozen; C-2 full model and future SSP/PyPSA gates remain closed.**
