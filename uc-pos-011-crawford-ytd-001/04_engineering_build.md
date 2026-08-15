# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## Artifacts

| File | Purpose |
|---|---|
| `dp_uc34_kernel.py` | loader + governed KPI kernel + CR-1/CR-2/CX-1/PL-1 |
| `dp_uc34_crawford_ytd.py` | build script — every receipt and figure |
| `dp_uc34_verification.py` | independent verification, **no kernel import** |
| `dp_uc34_build_pdf.py` / `dp_uc34_build_dashboard.py` | renderers |
| `dp_uc34_monthly_master.csv` | curated `z`, 44 columns × 6 months |
| `dp_uc34_monthly_panel.csv` | presentation projection, rounded to 3 |
| `dp_uc34_window_split.csv` | the pre/post 15 Jun contrast, all KPI families |
| `dp_uc34_breakpoint_scan.csv` | 9 candidate breakpoints — **the sensitivity evidence** |
| `dp_uc34_rolling_line.csv` | Crawford cumulative BA/OBP/wOBA by PA |
| `dp_uc34_cf_context_pool.csv` / `_rolling.csv` / `_matched_pa_snapshot.csv` | CX-1 / CX-2 |
| `dp_uc34_population_pool.csv` | 217 Phillies hitter-seasons ≥50 PA |
| `dp_uc34_profile_percentiles.csv` / `_archetype_cohort.csv` | profile benchmark |
| `dp_uc34_platoon_exposure.csv` / `_splits.csv` / `_counterfactual.csv` | PL-1 |
| `dp_uc34_pitch_group_window.csv` / `_pitch_type_season.csv` / `_count_state.csv` / `_groundball_quality.csv` | arsenal + leverage |
| `dp_uc34_headlines.json` | every scalar quoted in the report |
| `dp_uc34_fig1..6_*.png` | report figures |
| `_chartjs_4.4.1.umd.js` | vendored charting library (MIT) — see below |

## Pipeline

`phils_{2015..2026}.parquet` → role tag (`home/away × inning_topbot`) → drop `game_type` S/E →
`month = game_date.dt.month`, `pitch_group = pitch_type.map(PITCH_GROUP)` → subject filter on
`batter == 702222` → per-layer aggregation → left-merge on `level` → **named count columns filled to
0; rates left NULL** → `round(3)` applied **once**, in the presentation projection only.

`z` is unrounded. This is what makes ISO, BABIP and every derived ratio exact rather than
inheriting D4's 3dp truncation.

## Dashboard: charting library vendored, not CDN-loaded

The house pattern loads Chart.js from cdnjs. **Building this one surfaced a robustness defect in that
pattern:** when the CDN is unreachable, `Chart is not defined` throws at the first configuration
statement and halts the entire script — taking the tables, the tab navigation and the governance
panel down with it. A staff laptop behind a proxy would see a header and nothing else.

Two changes, both worth propagating:

1. **Chart.js 4.4.1 UMD is inlined** into the HTML (`_chartjs_4.4.1.umd.js`, MIT). The dashboard is
   now genuinely self-contained — it renders with no network at all and survives being emailed as a
   single attachment.
2. **Every chart call is wrapped** in a `chart(id, cfg)` helper that degrades to a visible placeholder
   reading *"chart library unavailable — the tables on this page carry the same numbers"*. Tables and
   navigation are never taken down by a charting failure.

File size rises from 242 KB to 443 KB. For an artifact whose whole purpose is to open reliably on
someone else's machine, that is the correct trade.

## Column-level lineage (extract)

| KPI | Source columns | Transformation |
|---|---|---|
| wOBA | `events`, wOBA constants CSV | per-row seasonal weight; den = AB + uBB + SF + HBP; **IBB excluded** |
| BABIP | `events` | `(H − HR) / (AB − K − HR + SF)` |
| ISO | `events` | SLG − BA, both from counts |
| `swing_rate` | `description` | `isin(SWINGS)` ÷ row count |
| `chase_rate` | `description`, `zone` | `(zone>9 & SWINGS)` ÷ `(zone>9)` |
| `whiff_rate` | `description` | `isin(WHIFFS)` ÷ `isin(SWINGS)` — **left-merge, D1-corrected** |
| `fpsr` | `type`, `pitch_number` | `(n − n[type=='B'])` ÷ n over `pitch_number==1` — **D3-corrected** |
| `gb_rate`, `fb_rate`, `ld_rate`, `pu_rate` | `bb_type`, `type` | share of `type=='X'` — **all BIP**, classifier is complete |
| `mean_la`, `median_la`, `mean_ev` | `launch_angle`, `launch_speed`, `type` | over `type=='X'` **and both sensor fields non-null**; NULL below 50 tracked BIP |
| `hard_hit_rate` | `launch_speed`, `type` | `(≥95)` ÷ **all BIP** — governed denominator retained; divergence reported as **O-8** |
| `barrel_rate` | `launch_speed_angle`, `type` | `(lsa==6)` ÷ BIP |
| `xwobacon_bip` | `estimated_woba_using_speedangle`, `type` | mean over BIP; NULL below 50 |
| `cum_ba` / `cum_obp` / `cum_woba` | `events`, constants | cumulative num ÷ den within `season_key`, ordered `game_date` → `game_pk` → `at_bat_number` |
| CX-1 pool | `fielder_8` (pps), `game_pk`, `batter` (pos) | CF games per season > 80 → per-game CF pitches > 10 → inner-join batting rows |
| PL-1 `mix_effect` | `p_throws`, `plate_apps`, target metric | `Σ(rate_target × w_target) − Σ(rate_target × w_reference)` |
