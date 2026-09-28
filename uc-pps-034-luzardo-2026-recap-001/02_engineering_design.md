# 02 · Engineering Design: `uc-pps-034`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dq-rule-definer` · `dashboard-specifier`

## 1 · Data model

**One pitch-grain frame, many groupbys.** CF-2 builds every regular-season pitch thrown by 666200 from four sources in precedence order and de-duplicates on `(game_pk, at_bat_number, pitch_number)`:

| Precedence | Source | Why it ranks here |
|---|---|---|
| 1 PHI | `phils_*`, `phillies_role == 'pitching'` | the house log, freshest |
| 2 FILE | `data/opponents/luzardo.parquet` | pitcher-keyed dedicated pull |
| 3 NPHL_ID | the 20 other opponent files, rows with `pitcher == 666200` | batter-keyed; completeness only |
| 4 VS_PHI | `phils_*`, `phillies_role == 'batting'` | he pitched against Philadelphia |

A second call with `game_types = (F, D, L, W)` builds the postseason ledger frame; postseason never enters a rate. Every published table is a groupby of these two frames (season, month, half, start, time-through-order, inning, batter side, pitch type). The context population (CX-1) is a groupby of the Phillies pitching log by `(pitcher, game_year, p_throws)`. There are **no cross-grain joins**.

**Environment decision.** The data build and the harness run on the laptop VM, where the data lives (pyarrow, scipy and plotly installed to `/tmp` because `/sessions` is full). LP-1 projects 50 of 119 columns to fit 3 GB of RAM. Only rendering (Chromium for PNG, pango for PDF) runs in the cloud, on the 40 receipts.

## 2 · EDA findings that changed the build

| # | Finding | Consequence |
|---|---|---|
| E-1 | 2025 → 2026: in-zone −4.0 pts (p = 0.002), chase +3.3 (p = 0.057), BB flat | The spine: "letting go of the zone" (ch. 4) |
| E-2 | 2026 whiff is #31 of 259 overall but **#1 of 41** starter workloads | CX-1b declared, with sensitivity at 1,500 / 2,500 pitches (harness C) |
| E-3 | Second half 1.87 runs on watch per 27 outs vs 3.82 | ch. 5; half split at the 2026-07-13 break, matching uc-pps-017's 19-start cut |
| E-4 | Labor Day chase 45.9% vs 33.7% season; FF 97.4 in the 9th | ch. 6 bullets; F5 subtitle |
| E-5 | RHB changeups 2 → 8 → 2 by time through the order on Labor Day | F6 "two game plans", descriptive only |
| E-6 | 8/26 FF 95.4 mph, below his per-start IQR (96.5–97.3) | ch. 7 states it; no inference |
| E-7 | OC-1 backtest: off-script starts allowed fewer runs | OC-1 reframed as a sameness card (G8) |
| E-8 | 2021 in-zone (45.5%) is lower than 2026 (46.5%) | "Lowest since 2021", enforced by harness F |

## 3 · Metadata map (physical → CDE)

| Physical column | CDE / term | Status |
|---|---|---|
| `pitcher` | Pitcher (entity key) | exact |
| `player_name` | Pitcher name | **AMBIGUOUS**: batter's name in batter-keyed pulls (BS-1, O-26). Display only |
| `zone` | Strike-zone cell (1–9 in, 11–14 out) | exact; NULL share 0.0 for this subject (DQ-16) |
| `description` | Pitch result → Swing, Whiff (house SWINGS/WHIFFS) | exact, inherited |
| `events` | PA outcome → K, BB, H, HR, outs (OU-1) | exact; OU-1 map new |
| `bat_score`, `post_bat_score` | Runs on watch (`runs_created`) | exact, inherited |
| `n_thruorder_pitcher` | Time through the order | exact; absent in some older schemas (projected by `_cols_in`) |
| `release_speed` | Velocity (mph) | exact |
| `plate_x`, `plate_z` | Location, catcher's view (**+x = first-base side**) | exact; K44 PM-1 docstring wrong (E-7) |
| `pfx_x`, `pfx_z` | Movement (ft) | exact; LHP arm-side FF pfx_x > 0 (DQ-17) |
| `game_type` | Season phase (R / F / D / L / W / S / E) | exact |

## 4 · DQ rule design (handed to `05`)

23 rules across uniqueness (DQ-01), consistency (02, 07, 09, 12–14, 20, 22), validity (03, 05, 10, 11, 17, 19, 21, 23), timeliness (04, 06), completeness (08, 15, 16) and comparability (18). Two are designed WARNs: DQ-18 (the populations are Phillies-only, permanently) and DQ-22 (O-26 exposure, 230 pitches, reported not fixed).

## 5 · Dashboard specification

- **Structure:** hero (title, dek, 4 stat tiles, data-window box) → sticky chapter nav → 8 chapters → appendix (notebook graded, product forms) → footer with lineage.
- **Chapters:** 1 Arrival (F3) · 2 The bet (F7) · 3 The chase (F1 + drill-through panel) · 4 The zone (F2) · 5 Summer (F4) · 6 Labor Day (F5 + PA stepper + F6 + F8) · 7 Silence (prose only, by design) · 8 October (OC-1 table, backtest callout, postseason ledger).
- **Interactions:** hover on every mark; click-to-drill on F1; a 30-step PA stepper that highlights the PA's pitches on F5 and lists them as chips (count, pitch, velocity, result); chart draws are lazy (IntersectionObserver).
- **Theme:** CSS tokens with light and dark under `prefers-color-scheme` and an explicit toggle (Match my system / Brand light / Notebook dark); plotly templates swap with the theme; fixed ink colors are remapped in dark.
- **Offline:** plotly.js inlined; no network. Artifact body variant written alongside.
- **Mobile:** single column below 820 px, no horizontal scroll (checked at 390 px).
