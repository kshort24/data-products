# 02 · Engineering Design
**data-architect · eda-agent · metadata-mapper · dashboard-specifier**

## 1 · Data model
- **Grain:** pitch (`game_pk, at_bat_number, pitch_number`), with derived PA rows (K40 `pa_rows`) and BIP rows.
- **Frames:**
  - `S`: subject, regular season, batting role.
  - `pos_r` / `pps_r`: house batting and pitching, regular season, 2015–26.
  - `a`: AAA tier.
  - `jc`: the client's frame, HP only.
- **Populations:**
  - House hitter-seasons (≥50 PA, n=220).
  - CX-1 CF seasons (n=9; CF games only).
  - CC-1 reference (house batting 2023–26 out-of-zone takes by count).
  - XO-2 comparison pool: CF-sector air balls in every Phillies game 2015–26 not fielded by him, n=15,240.
- **Joins:** none fan out. The CX-1 merge is on (`game_year, game_pk, batter, player_name`), inherited; the CM-1 endpoint reconcile proves 1:1 on every series. The XO-2 pool is de-duplicated on the pitch key after concatenating both roles.

## 2 · EDA findings (to file: MLB `eda/dp_uc54/subject_2026.md`, `aaa_2025.md`, `xo2_opportunities.md`)
- Subject 2026: no null zone or pitch type (AB-1 exposure 0); 4 untracked BIP (O-8); bat tracking on 876 swings.
- AAA 2025: `woba_denom` null on most rows (AAA pulls lack it). AAA wOBA is computed from events with K40 weights, never from `woba_value`. EV missing on 25 BIP.
- XO-2 opportunities: distance 150–430 ft, spray ±15°. The first neighbourhood (v1) scored only 45%, which triggered the selection rule (`03` §2).

## 3 · Metadata map (metadata-mapper)
All CDEs map exact to the live schema:
- `events`, `description`, `zone`, `type`, `bb_type`
- `launch_speed`, `launch_angle`, `hit_distance_sc`, `hc_x`, `hc_y`
- `plate_x`, `plate_z`, `sz_top`, `sz_bot`, `p_throws`, `stand`
- `estimated_woba_using_speedangle`, `woba_value`, `woba_denom`, `delta_run_exp`
- `fielder_8`, `hit_location`, `attack_angle`, `bat_speed`, `on_2b`, `on_3b`

Negative confirmations: `loc_x`/`loc_y` are absent (derived by PA-L1). `phillies_role` is absent from AAA files (the AAA tier is batter-keyed by id).

## 4 · Dashboard specification (dashboard-specifier)
| Ch | Client Q | Title | Figures | Interaction |
|---|---|---|---|---|
| 1 | Q1 | The rookie line | F1 cumulative BA/OPS/wOBA vs CX-1 | hover per season line |
| 2 | Q2 | The June turn | F2 rolling + breakpoint scan · F3 TR-1 ledger | hover PA counts per split |
| 3 | Q3 | The approach | F4 percentile profile · F5 attack regions | hover pool n |
| 4 | Q6 | Ground balls | F6 cumulative GB% / HH% vs CX-1 | hover |
| 5 | Q4 | Where the walks went | F7 chase map vs RHP | hover pitch + count |
| 6 | Q4 | Righty spin | F8 EV + hit maps AAA vs MLB · F9 spray on drawn field | hover pitch, outcome, EV |
| 7 | Q5 | Centre field | F10 opportunity map + running OAE | hover xOut, EV, LA |
| App. | — | Your notebook, graded · Five ways to tell this story | HP table, product cards | — |

**Shell:** house `dashboard_shell.md` tokens (Phillies red/navy, light and dark), Barlow Condensed display with Source Sans 3 body, plotly via `plotly_script_tag()` (jsDelivr pin 3.0.1), and theme choice persisted under `uc54-theme`. Figures are re-themed in-page; navy and the fixed inks remap to tokens in dark mode. Wide figures sit in their own horizontal scroller at phone width (page body never scrolls sideways; QA at 390 px).
