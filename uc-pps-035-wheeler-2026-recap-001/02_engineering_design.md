# 02 · Engineering Design: `uc-pps-035`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dq-rule-definer` · `dashboard-specifier`

## 1 · Data model

**One pitch-grain frame, one defensive log, many groupbys.**

- **CF-2b** (`career_frame_mlb`): CF-2's four-source precedence (PHI > FILE > NPHL_ID > VS_PHI, dedup on the pitch key), then MLB games only, the subject's name, and an enrichment left-join of 15 columns (bat-tracking intercept, `woba_value`/`woba_denom`, release point, arm angle, `launch_speed_angle`) from the house log on `(pitcher, game_pk, at_bat_number, pitch_number)`. A second call with postseason game types builds the ledger frame; postseason never enters a rate.
- **Defensive log** (OU-2): every Phillies pitching row in Wheeler's games (all pitchers), one row per PA, outs from the `outs_when_up` sequence.
- **Populations:** CX-1b (Phillies pitcher-seasons ≥2,000 pitches), KP-1 (≥100 PA), the tied-up board (Phillies pitcher-seasons 2025–26 ≥50 tracked swings). All keyed by MLBAM id.

Every table (season, half, period, month, start, batter side, pitch type × side) is a groupby of these frames. There are no cross-grain joins.

**Environment decision (carried from UC49/50).** Build and harness run on the laptop VM where the parquet lives (pyarrow + scipy reinstalled into `/tmp/pyl`; `/sessions` still 100% full). Render runs in the cloud on 39 staged receipts (748 KB). 0 data files staged.

## 2 · EDA findings that changed the build

| # | Finding | Consequence |
|---|---|---|
| E-1 | xwOBA (XW-1) = .263 exactly, #6 of 41 starter seasons; 6 of the top 10 are his | The thesis; ch. 2, fig 1 |
| E-2 | The first-six-after-the-break window gives 5.60 runs per 27 outs, not 8.51; 7/27–8/24 gives 8.51 exactly | SR-2 defined by reconciliation; DQ-30 |
| E-3 | Slide BB 13.4% vs 5.9% (p = .004); K, chase, in-zone, edge, velocity not different | "Command event", ch. 4 |
| E-4 | Clear misses arm side 25.5% vs 17.8% (p = .033), 12% in the finish; release x/z/extension/RCI flat | Fig 5; descriptive only (G12) |
| E-5 | In-zone 42.1% vs 50.2% (p < .001); chase 36.2% vs 32.1% (p = .002); ER-1 flat | Zone expansion is the year's biggest change; HP-06/07 |
| E-6 | OU-1 = 480 outs vs published 486 | OU-2 + GS-1b (DQ-18) |
| E-7 | Hard-hit vs LHB 41.9% vs 25.7% (p = .001) | Platoon chapter |
| E-8 | Arm angle published for only 56% of 2026 four-seams (1 of 6 slide starts) | MX-1 does not test it (DQ-23 WARN) |
| E-9 | Still-Wheeler card backtest: on-script 2.16 vs off-script 4.96 runs per 27 outs | Unlike UC49's card, this one discriminates; published with the backtest |

## 3 · Metadata map (physical → CDE)

| Physical column | CDE / term | Status |
|---|---|---|
| `pitcher` | Pitcher (entity key) | exact |
| `player_name` | Pitcher name (pitching role) / **batter name** (`pos`, batter-keyed pulls) | **AMBIGUOUS** (HP-13); display only |
| `game_type` | Season phase | exact; **does not separate MLB from AAA** in pitcher-keyed MiLB pulls (MI-1) |
| `home_team`, `away_team` | Club | exact; MLB club list derived from the Phillies log |
| `intercept_ball_minus_batter_pos_x_inches` | Swing-contact point → tied-up / centered / flail | exact on tracked swings (2025+); JR-1 boundary 32.5 in |
| `outs_when_up` | Outs before the PA → OU-2 | exact |
| `woba_value`, `woba_denom`, `estimated_woba_using_speedangle` | XW-1 numerator/denominator | exact (EN-1 join); DQ-10 coverage ≥ 99% |
| `release_pos_x`, `release_pos_z`, `release_extension`, `arm_angle` | Release point (MX-1) | exact; arm angle 56% coverage |
| `plate_x`, `plate_z`, `sz_top`, `sz_bot` | Location vs zone → ER-1, NC-1 | exact; + `plate_x` = first-base side (catcher view); RHP arm side = − |
| `zone` | Zone cell | exact; NULL share 0.0 |
| `launch_speed_angle` | Barrel (== 6) | exact |

## 4 · DQ rule design (handed to `05`)

30 rules: uniqueness (01), consistency (02, 07, 09, 11, 13, 15–20, 26, 28–30), validity (03, 05, 06, 12, 14, 25, 27), timeliness (04, 08), completeness (10, 21–23), comparability (24). Designed WARNs: DQ-23 (arm angle coverage), DQ-24 (Phillies-only populations, permanent), DQ-28 (MI-1 exposure in the client frame), DQ-29 (O-26 exposure).

## 5 · Dashboard specification

- **Structure:** hero (title, dek, 4 tiles, data-window box) → sticky chapter nav → 8 chapters → appendix (notebook graded, product forms) → footer with lineage.
- **Chapters:** 1 Return (season table) · 2 Still Wheeler (F1, F2) · 3 The zone (F3) · 4 The slide (F4 + start drill + period table + F5) · 5 Contact (F6, F7, F8) · 6 Platoon (F9) · 7 Arsenal (F10, F11) · 8 October & 2027 (F12, card table, WC G3 PA list, postseason ledger).
- **Interactions:** hover on every mark; a start selector (28 starts) with a 9-tile panel (BB%, xwOBA, Game Score, in-zone, edge, chase, first-15 velocity, arm-side misses, release point); clicking a bar in F4 selects that start; lazy chart draws.
- **Theme:** CSS tokens light/dark under `prefers-color-scheme` + toggle (Match my system / Brand light / Notebook dark); ink, navy and grid colours remapped in dark.
- **Offline:** plotly.js inlined; Artifact body variant written alongside.
- **Mobile:** single column below 820 px; no horizontal scroll at 390 px (checked).
