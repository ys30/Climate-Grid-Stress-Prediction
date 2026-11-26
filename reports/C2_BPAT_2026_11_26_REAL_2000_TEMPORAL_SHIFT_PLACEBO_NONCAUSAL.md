# C-2 BPAT — real 2020–2025 cold-load temporal-shift placebo (2026-11-26)

## Direct observed-source result
Reanalyzed genuine archived 52,608 BPAT EIA930 UTC-start demand hours and linked candidate-area ERA5 two-meter temperature. Independently asserted ZIP SHA-256 `bc226839dbd4ababedfe2b4079cb79f06c3b0dd9d9971f3c98b3d27256eaa504` and source gzip SHA-256 `88551b144acfaafb1be1e1a4691cd263101241a3b6def4429c3f099a006419ac`. This is a **source-backed** exploratory relation with **unapproved weather area geometry**, not a causal attribution.

Outcome: demand above the within-year-month 95th percentile; exposure: candidate ERA5 temperature ≤ -5 C relative to the same year-month UTC-hour mean; odds ratio pooled by Mantel–Haenszel over 72 year-month strata. Observed stratified MH OR **6.047548**.

## New temporally shifted negative control
Hold real demand/hourly target fixed. Independently for each year-month circularly shift *all cold exposure hours as a block* by one randomly selected whole-day lag in [7, days in month − 7] days. Recompute stratified MH OR on exactly the same observations. Seed 20261126, **2,000 draws**; tested against the true archived source, not mock rows.

| Result | Actual |
|---|---:|
| Observed MH OR | 6.047548 |
| Shift-placebo median OR | 0.823020 |
| Placebo 2.5% quantile | 0.522233 |
| Placebo 97.5% quantile | 1.219882 |
| Maximum placebo OR | 1.651850 |
| Placebo draws reaching observed OR | **0 / 2,000** |
| Continuity-adjusted empirical exceedance fraction | 1/2001 = 0.00049975 |

This is **NOT a preregistered confirmatory p-value**. The randomized shift is an observational negative control, does not imply randomized weather, can split true multiday cold spells at year-month borders, and does not account for geography misclassification, load structural changes, unobserved confounding, multiple explored hypotheses or historical EIA vintages. It is not an independently validated test of future prediction performance.

## Relation to earlier persistence checks
Earlier within-month day-block OR 95% percentile interval **[4.90,7.47]** and nonoverlapping within-month seven-day-block interval **[4.22,7.56]** varied the *sampling* of contiguous segments. This new analysis instead shifts temperature relative to demand by ≥7 days within the same calendar month to test contemporaneous specificity. It provides a **different diagnostic** rather than another confidence interval; zero-shift association is much larger than the shifted placebo distribution but remains noncausal.

## Files and provenance
- Independently executable repository script `scripts/c2_bpat_era5_monthyear_shift_placebo.py`.
- Downloadable executed reproduction bundle `C2_BPAT_2026_11_26_Temporal_Shift_Placebo_2000_Reproducible.zip` containing actual executed local script, full 2,000-row draw CSV, JSON evidence summary and SHA manifest; archive SHA-256 `821db66f5ec42240db244017be0a02549a97be5c0322f44d188e2c7a8c733d73`, ZIP CRC checked.
- The local executed script and repository script implement the same methodological design but are separately authored; a fresh CI run on GitHub source is not yet verified.

## Next scientific steps
Prioritize corrected historical BA territory/temperature sampling, event-level weather comparison spanning month boundaries and source vintage checks. Run source-verified actual FERC714 respondent 21 hourly comparison only after original core data arrives. No SSP/CMIP6 climate effects or PyPSA outcomes inferred. **C-1 remains frozen.**
