# 03 · Governance: `uc-pps-034`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)

| Candidate | Search | Result |
|---|---|---|
| Season recap table | `season_recap`, `SR-1` | **Found** (UC48) → second use, imported |
| Career frame loader | `career_frame`, `CF-1` | Found (UC48), subject hard-coded → **CF-2 generalization** (non-breaking, E-2) |
| Edge rate (client's unfinished `edge_rate`) | `edge_rate`, `edge` | **Found** (UC8, uc-pps-008) → HP-13 redirects; not rebuilt |
| Game Score | `game_score`, `gsc`, `GS-` | 0 hits → GS-1 (new) |
| Outs recorded | `outs_recorded`, `OUTS_ON` | 0 hits → OU-1 (new) |
| First-N velocity | `first_n`, `velo_by_outing` | VE-1 (UC48) buckets by pitch of outing but reports by season; VB-1 reports by outing → new, cites VE-1 |
| House percentile | `house_percentile`, `KP-1` | Found (UC48) → imported; KP-1b takes a frame (non-breaking) |
| Pitch map centroid | `pitch_map_centroid`, `PM-1` | Found (UC44) → imported |
| Pre-registered postseason card | `october`, `pre-regist` | 0 hits → OC-1 (new) |

## 1 · Business glossary

| Term | Definition | Status |
|---|---|---|
| **Runs on watch** | Runs that scored during the plate appearances a pitcher threw (house `runs_created`, `Baseball Functions.ipynb` cell 31). Includes unearned runs; excludes inherited runners he did not allow on. **Not ERA.** | Approved (uc-pos-012); display alias used here |
| **Starter workload** | A pitcher-season of ≥2,000 regular-season pitches | New, provisional (CX-1b) |
| **Game Score (GS-1)** | 40 + 2×outs + K − 2×BB − 2×H − 3×R − 6×HR, with outs from OU-1 and R = runs on watch. Tango v2 *form*, log-derived; not the published stat | New, provisional |
| **On-script (OC-1)** | A postseason outing that holds ≥3 of the 4 October-card signatures | New, provisional |
| **Chase rate** | Swings at out-of-zone pitches ÷ out-of-zone pitches (`zone > 9`) | Approved (inherited) |
| **Whiff rate** | Whiffs ÷ swings (house SWINGS/WHIFFS; whiffs include foul tips) | Approved (inherited) |
| **In-zone rate (governed)** | Pitches in zones 1–9 ÷ *tracked* pitches (zone not null). The notebook version divides by all pitches (D-7/O-13); identical here (0 NULL zones) | Approved term, denominator clarified |

## 2 · KPI specifications (`kpi-calculator`)

**CF-2 `career_frame`** · grain: pitch · population: `pitcher == id`, `game_type ∈ game_types` · precedence PHI > FILE > NPHL_ID > VS_PHI (sorted by source file within a tier) · dedup on the pitch key · receipt: rows / kept / dropped by season × source.

**NF-1 `nphl_name_frame`** · reproduces `get_nphillies_data()` exactly: sorted files, global keep-first on the pitch key, then the name filter. Returns the frame and the count lost to dedup (O-26).

**CX-1 `context_frame`** · grain: `(pitcher, game_year, p_throws)` · population: Phillies pitching log, regular season, ≥150 pitches (the client's `pitches > 149`) · whiff, chase, in-zone (tracked), BB and K rates with their counts · ranks: `method='min'`, descending · "dominated by" = count of seasons strictly higher on both chase and whiff · **CX-1b**: the same, pitches ≥2,000.

**Command fit** · per handedness, OLS of BB rate on in-zone rate over CX-1 (`numpy.polyfit`, degree 1) · residual = actual − fitted · residual percentile = share of the handedness population with a larger residual.

**KP-1 / KP-1b** · inherited formula: percentile = floor(100 × share strictly worse); rank = 1 + count strictly better; population Phillies pitcher-seasons ≥100 PA.

**OU-1 `outs_recorded`** · outs per pitch row from `events` (map in the kernel). Edge case: an out on a play with no event row is missed. Test: no game-inning credits more than 3 outs (DQ-10); Labor Day = 27 (DQ-13).

**GS-1 `game_score`** · grain: game · formula in §1 · `started` = first inning pitched is 1 · `ip_display` = outs // 3 . outs % 3.

**VB-1 `first_n_velo`** · mean four-seam velocity among the first 15 pitches of each outing (all pitch types count toward 15). NULL when no four-seam is thrown in that window (one 2026 start, 6/23).

**OC-1 `october_card`** · signatures, per outing: OC-A VB-1 (higher), OC-B chase rate (higher), OC-C whiffs per 100 pitches (higher), OC-D walks per PA (lower). Bars: his 2026 regular-season outing distribution at the 25th percentile (A–C) or 75th (D). Verdict: ON-SCRIPT if all four graded and ≥3 hold; OFF-SCRIPT if all graded and <3 hold; INCOMPLETE otherwise. Registered 2026-09-27, anchor 2026-09-26. **Changing a bar after the first postseason pitch is a breaking change.**

**BN-1 `batter_names`** · modal parsed name per batter id from PA-ending `des` (house rule: never hand-key ids).

**US-1b `appearance_log`** · UC48 US-1 verbatim except one line (ENV-1: `runs_by_game` aliases the key instead of grouping by `game_pk` twice).

**PL-1 pitch palette** · FF `#D22D49`, SI `#C77800`, ST `#3B6FD8`, CH `#16945A`, in that fixed order. Passes the six-check validator on light and dark surfaces (adjacent pairs); the all-pairs FF/CH deutan case is covered by direct labels on every pitch mark (`out/dp_uc49_palette_validation.txt`).

## 3 · Technical lineage (published numbers)

| Published number | Receipt | Built from |
|---|---|---|
| Season lines (report §1, fig 3) | `recap_governed.csv` | CF-2 → SR-1 (`season_recap`, governed) + `fpsr` + tracked in-zone |
| 2025 → 2026 tests | `rate_tests.csv` | recap counts → `two_prop_z` (K44) |
| Chase / whiff ranks, dominated-by, quadrant | `context_population.csv`, `context_starter_workloads.csv`, `context_frontier.csv` | Phillies pitching log → CX-1 / CX-1b |
| Command fit | `command_ols.csv` | CX-1 (LHP) → OLS |
| Percentiles | `house_percentiles.csv`, `house_population.csv` | log → KP-1b → KP-1 |
| Arsenal, pitch map | `arsenal_by_season.csv`, `arsenal_by_stand_2026.csv`, `pitch_map_2026.csv` | CF-2 → AR-2 (K48), PM-1 (K44) |
| Starts, halves, months, TTO | `starts_2026.csv`, `halves_2026.csv`, `monthly_2026.csv`, `tto_2026.csv` | CF-2 2026 → GS-1, US-1b, VB-1, `nresults` |
| Game Score ranks | `career_game_scores.csv` | CF-2 → GS-1 |
| Labor Day | `laborday_pitches.csv`, `_pa.csv`, `_by_inning.csv`, `_mix_by_tto.csv`, `_box_reconcile.csv` | CF-2 game 823415; batting-role rows for the run |
| Velocity by start | `velo_by_start_2026.csv` | VB-1 + US-1b |
| Postseason ledger | `postseason_ledger.csv` | CF-2 (postseason types) → GS-1 |
| October card | `october_card.csv`, `_backtest_2026.csv`, `_postseason_history.csv` | outing signatures → OC-1 |
| Client frame reconciliation | `hp_season_frames.csv`, `hp_reconciliation.csv` | NF-1 + `pps` name filter vs CF-2 |
| Every narrative number | `headlines.json` | all of the above |

## 4 · Defect exposure

| Defect | Exposed here? | Evidence |
|---|---|---|
| D-1/D-2 `whiff_rate` inner join drops zero-whiff groups | No | DQ-21: all 8 seasons survive |
| D-7/O-13 NULL zone counted in-zone | No | DQ-16: 0 NULL zones; governed denominator = tracked anyway |
| O-25 `pitch_mix` rounds `pfx_*`/location to 0.1 ft | Cosmetic | notebook pitch map vs PM-1 differ ≤0.05 ft (HP-11) |
| HP-18 leaked loop variable | Latent | correct by accident on a one-season frame (HP-12) |
| **O-26** (new) `nphl` keep-first dedup hands pitcher rows to batter-keyed files | **Yes** | 230 pitches (DQ-22 WARN, E-3) |
| **BS-1** (new) byte search as a profiling instrument | **Yes** (in uc-pps-033's method) | 2 vs 21 files; closes uc-pps-033 V-3 |
| **ENV-1** (new) US-1 groups by `game_pk` twice | **Yes** on pandas 2.3 | US-1b; E-2 |
| **E-7** (new) PM-1 docstring states + = third-base side | Text only | LHP FF pfx_x = +0.997 ft (DQ-17) |
| **HP-10** (new) `px.scatter(trendline='ols', color=…)` fits one line per color | **Yes** (client chart) | governed fit per handedness |

## 5 · Privacy, tagging, versioning

- **Privacy (`privacy-watchdog`): CLEAR.** Public MLB performance data. Carry-ins are published reporting. The shoulder is named only as reported (stiffness, inflammation, IL dates); no inference, no modeling, no language that links a data pattern to the injury (harness G).
- **Tags (`data-tagger`):** Internal · domain Phillies Pitching · subject area Season Recap · product `uc-pps-034` · no PII · player health: *reported status only*.
- **Versioning (`version-controller`):** v1.0.0, anchor 2026-09-26. **v1.1.0** = Game 162 and any postseason pitch (OC-1 graded). Changing an OC-1 bar, CX-1b's cut or GS-1's formula after publication is **breaking**.

## 6 · Ratification path

| Object | Recommendation |
|---|---|
| SR-1 `season_recap` | **Ratify** (second clean use) |
| CF-2 `career_frame` | Ratify as SR-1's loader; retire CF-1 |
| US-1b | Promote into `dp_uc48_kernel` v1.0.1 (ENV-1) |
| CX-1 / CX-1b, GS-1, OU-1, VB-1, OC-1, NF-1, BN-1, PL-1 | Provisional; second use required |
