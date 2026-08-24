# 04 · Engineering Build
**technical-lineage-builder · data-engineer**

## Column-level lineage (source → KPI)

All paths begin at `data/phillies/phils_{2015..2026}.parquet` → PHI-batting mask
(`home_team=='PHI' & inning_topbot=='Bot'` | `away_team=='PHI' & inning_topbot=='Top'`) →
`~game_type.isin(['S','E'])` → `batter == 664761` (entity lock) → `game_year == 2026`
(windows/monthly) or all years (career, pool, ghost lines).

| Published KPI | Hop 1 (population) | Hop 2 (numerator/denominator) | Function |
|---|---|---|---|
| ba / obp / slg / iso / ops / babip / woba / krate / bbrate | terminal-event rows (`events` ∉ NON_PA) | event-class counts → ratios from COUNTS (no 3dp round); wOBA via seasonal constants CSV, IBB excluded both sides | `nresults_unrounded` |
| ba_risp family | + `on_2b.notna() \| on_3b.notna()` (terminal-pitch RISP) | as above | `nresults_unrounded` ∘ `risp_rows` |
| runs_created / rc_per_pa | PA grain (`game_pk`,`at_bat_number`) | max `post_bat_score` − min `bat_score`, summed; ÷ PA | `runs_created` (governed) / `rc_rate` |
| whiff / swing / chase / ooz-whiff | `description` vs 8-value SWINGS, 5-value WHIFFS; `zone > 9` for OOZ | left-merged counts | `whiff_rate_fix`, `swing_rate`, `chase_rate_g`, `ooz_whiff_rate` |
| swing_rate_in_zone / whiff_rate_in_zone | `zone < 10` | as above on the in-zone frame | `zone_swing_whiff` |
| hard_hit / barrel | `type=='X'` | `launch_speed>=95` / `launch_speed_angle==6` ÷ all BIP | `hard_hit_rate_fix`, `barrel_rate_g` |
| gb/fb/ld/pu shares; mean EV/LA | `type=='X'`; tracked = `launch_speed & launch_angle` non-null | shares over ALL BIP (bb_type complete); central tendency over TRACKED, NULL < 50 tracked | `battedball_profile` |
| xwobacon_bip / xba_bip | `type=='X'` | mean of Statcast estimates, NULL < 50 tracked | `xcontact` |
| pull_air_rate / pull_rate | `type=='X'` → PA-L1 loc derivation from `hc_x`/`hc_y` | cell-24 ±4.7-slope classification verbatim; pulled-air ÷ all BIP | `pull_air_rate_fix` |
| ev_mu/la_mu (all-rows, reconciliation only) | every pitch row | skipna means (foul-contaminated, O-3) | `inds_unrounded` |
| fpsr / in_zone_rate (opponent panel) | `pitch_number==1` / all pitches | (FP − FP balls) ÷ FP; (pitches − OOZ) ÷ pitches | `fpsr_fix`, `chase_rate_g` |
| cum_ba/obp/slg/woba by PA | PA rows ordered `game_date → game_pk → at_bat_number` | per-event weights cumsum within `game_year` | `running_line_pa` |
| PL-1 counterfactual | `window × p_throws` masters | post rates re-weighted to pre PA shares | `platoon_counterfactual` |
| pool percentiles | `pos` all hitters, seasons ≥ 50 PA | strict-less share, self-inclusive | `pool_percentile` |

## Build artifacts

| File | Role |
|---|---|
| `dp_uc37_kernel.py` | loader + governed KPI kernel (inherited `_fix` lineage + this UC's additions) |
| `dp_uc37_bohm_turnaround.py` | build script — writes every receipt and figure |
| `dp_uc37_verification.py` | independent path (no kernel import) — **227/227 PASS** |
| `dp_uc37_build_pdf.py` / `dp_uc37_build_dashboard.py` | consumables (house weasyprint CSS; vendored Chart.js) |
| 14 × `dp_uc37_*.csv` + `dp_uc37_headlines.json` | receipts — every reported number traces to one |
| `dp_uc37_fig1..6_*.png` | figures — each renders only receipt-backed values |

## Portability & reproducibility

Data root resolves `DP_UC37_DATA` env var → default MLB repo Windows path, so every script runs
unmodified on the DPO's machine and in the build sandbox. Deterministic end-to-end: no sampling, no
random seeds, no network. Rebuild order: build → dashboard → pdf → verification. New files only —
no prior-UC artifact is overwritten (checked against the `data-products/` inventory at delivery).

## Deviations from spec encountered and resolved

1. Headline window values initially stored at 4dp caused a 0.1-pt display divergence between report
   (full-precision) and dashboard (tile rounding) on K% — fixed by storing headlines at 6dp so every
   surface rounds identically from the stored value. (Screenshot QA catch, uc-pps-026 precedent.)
2. `json.dumps(allow_nan=False)` rejected NaN cells present in legitimately-NULL receipt fields
   (below-floor rates, the `other` pitch-group row) — resolved with an explicit NaN→null sanitizer in
   the dashboard builder, preserving the sensor-boundary NULL standard in the payload (`null`, never 0).
