# 03 · Governance: `uc-pps-035`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)

| Candidate | Search | Result |
|---|---|---|
| Edge rate (client: "edge rate", Savant 42.4%) | `edge_rate`, `edge` | **Found** (UC8, `dp_uc8_nola_vs_nationals.py`, a build script with `__main__`) → inherited by **IX-1 extraction**, segment-pinned |
| Tied-up / jam rate | `jam_rate`, `tied` | **Found** (`Baseball Functions.ipynb`, governed 2026-10-09) → IX-1 extraction, segment-pinned (`fe08ed26…`) |
| xwOBA (full PA) | `xwoba` | **Found** (UC50 XW-1 `xwoba_pa`) → imported, module-pinned |
| Barrel rate | `barrel_rate` | **Found** (`barrel_rate.py`, via K50) → imported |
| Hard-hit, LD share | `hard_hit_rate`, `bb_type_by_level` | **Found** (K44, locked) → imported |
| Release consistency | `release_consistency`, `RCI` | **Found** (UC28) → IX-1 extraction |
| Season card / pre-registration | `october_card`, `OC-1` | **Found** (UC49) → **second use**, verbatim |
| Career frame | `career_frame`, `CF-2` | **Found** (UC49) → **CF-2b** generalization (MI-1, NM-1, EN-1) |
| Outs recorded | `outs_recorded`, `OU-1` | Found (UC49) → failed DQ-18 → **OU-2** new; OU-1 kept for reproduction |
| Swing-timing buckets (centered/flail) | `flail`, `centered`, `swing_timing` | 0 hits → ST-1 (new) |
| Miss direction | `miss_side`, `clear_miss`, `waste` | 0 hits → NC-1 (new) |
| Release point by start | `release_pos`, `mechanics` | RCI found (UC28, per start SD); means per start → MX-1 (new, attaches RCI) |
| Window by reconciliation | `stretch`, `window` | 0 hits → SR-2 (new) |

## 1 · Business glossary

| Term | Definition | Status |
|---|---|---|
| **Tied-up rate** | Share of tracked swings (house swing list less bunts) whose ball–batter intercept is < 32.5 in (JR-1). Public-data proxy for Savant's "tied-up" swing-timing bucket. The client's preferred name over "jam rate" | Approved name (client); formula inherited |
| **Centered / flail (ST-1)** | Centered: intercept 32.5–41.0 in. Flail: > 41.0 in (the client's second histogram line) | New, provisional (E-7) |
| **Clear miss (NC-1)** | A pitch whose centre is more than two baseball widths (0.49 ft) outside the rulebook zone (ER-1 geometry). Side = axis of larger exceedance: arm / glove (catcher view; RHP arm side = −x), high / low | New, provisional |
| **The slide (SR-2)** | The unique run of six consecutive post-break starts whose runs on watch per 27 outs reconcile to the reported 8.51 ERA: 2026-07-27 → 2026-08-24 | New, provisional; carry-in-anchored |
| **Edge rate (ER-1)** | Share of located pitches whose centre is within one baseball (0.245 ft) of the rulebook zone line, inside or out | Approved (UC8); **not Savant's Edge%** |
| **xwOBA (XW-1)** | PA-denominated: Statcast contact expectation on batted balls, actual `woba_value` elsewhere, over `woba_denom` | Approved (UC50) |
| **Runs on watch** | Runs scored during the PAs he threw (house `runs_created`). Includes unearned runs. Not ERA | Approved (inherited) |
| **Outs (OU-2)** | Outs made during each PA, from the `outs_when_up` sequence of the full defensive log; 3 at an inning's end; last PA of a game capped by its out-event | New, provisional |
| **On-script (OC-1)** | A start holding ≥3 of the 4 card signatures | Approved (UC49), second use |

## 2 · KPI specifications (`kpi-calculator`)

**CF-2b `career_frame_mlb`** · grain: pitch · K49 `career_frame` unchanged, then: keep rows where `home_team` and `away_team` both appear in a Phillies regular-season game 2015–26 (MI-1); `player_name` := subject name (NM-1); left-join `ENRICH_COLS` from the house log on `(pitcher, PITCH_KEY)`, dedup'd first (EN-1). Receipts: `source_receipt.csv`, `milb_rows_excluded.csv`.

**IX-1 `extract(file, functions, constants)`** · parse the host file (or every parseable code cell of a notebook), take the named top-level `def`/assignment source segments, sha256 each, assert against `IX_PIN_EXPECTED`, `exec` into a fresh namespace with `np`/`pd`. The host is never imported or run. Receipt: `lineage_pins.csv`.

**OU-2 `outs_by_pa(def_log)`** · grain: (game_pk, at_bat_number) · first pitch of each PA; `outs_on_pa = next PA's outs_when_up in the same game-inning − this PA's`, 3 when none follows; last PA of the game = `min(3 − outs_when_up, OU-1(event))`. Edge: a mid-PA pitching change credits the PA to the pitcher of its first pitch. Test: 486 = 162.0 IP (DQ-18).

**GS-1b `game_score_b`** · GS-1 (Tango v2 form) with `outs` from OU-2; `game_score += 2 × (OU-2 − OU-1)`; OU-1 kept as `outs_ou1`.

**ST-1 `swing_timing(level, df)`** · population: JR-1 swing list, intercept not null · buckets as in §1 · rates over tracked swings.

**NC-1 `clear_miss(df, throws, balls=2)`** · located pitches · flag + side as in §1.

**MX-1 `mechanics_by_start(df)`** · grain: start · four-seam means of `release_pos_x`, `release_pos_z`, `arm_angle` (with its count), `release_extension`, velocity, movement · RCI (UC28) attached by date. Tests: Welch t on start means, slide vs other starts.

**SR-2 `stretch_windows` / `stretch_label`** · enumerate every run of 6 consecutive starts on/after the break; `r27 = 27 × runs / OU-2 outs`; the window with `|r27 − 8.51| < 0.005` must be unique (DQ-30) and is labelled `stretch`; earlier post-break starts `opener`; later `finish`; pre-break `first_half`.

**Still-Wheeler card (OC-1, second use)** · `october_card(outing_signatures(2026 regular-season starts))` verbatim · bars at the 25th percentile (75th for walks) · `grade_outing` verbatim · also computed on 2021–25 starts for comparison (`bar_2021_25`). Registered 2026-10-12. **Changing a bar after the first 2027 pitch is breaking.**

**Tests** · rates: pooled two-proportion z (K44 `two_prop_z`); start-level measures: Welch t (scipy).

## 3 · Technical lineage (published numbers)

| Published number | Receipt | Built from |
|---|---|---|
| Season lines (report §1, fig 2) | `recap_governed.csv` | CF-2b → K44 `nresults` + HH/barrel/LD/JR-1 + K44 whiff/chase + XW-1 + ER-1 + `runs_created` |
| Client's table | `recap_notebook.csv`, `hp_season_frames.csv` | `pps` name filter (postseason kept) → same chain |
| 2026 vs 2025 / 2021–25 tests | `rate_tests.csv` | recap counts → `two_prop_z` |
| House percentiles, staff ranks | `house_percentiles.csv`, `house_population.csv` | Phillies log → KP-1b + XW-1 → KP-1 |
| Starter board | `context_starter_workloads.csv` | Phillies log → CX-1 + XW-1 + ER-1, ≥2,000 pitches |
| Starts, periods, months, halves | `starts_2026.csv`, `periods_2026.csv`, `monthly_2026.csv`, `halves_2026.csv` | CF-2b 2026 → GS-1b (OU-2), US-1b, VB-1, ER-1, XW-1, NC-1, MX-1, SR-2 |
| The slide | `stretch_windows.csv`, `stretch_tests.csv` | starts → SR-2; tests |
| Outs | `outs_by_pa.csv` | defensive log → OU-2 |
| Swing timing | `swing_timing_by_season.csv`, `_by_pitch_stand_2026.csv`, `tied_up_population.csv`, `tied_up_population_client.csv` | JR-1 / ST-1 |
| Platoon | `platoon_by_season.csv`, `platoon_tests.csv`, `platoon_notebook.csv` | CF-2b by stand |
| Arsenal, pitch map, plot | `arsenal_by_season.csv`, `arsenal_by_stand_2026.csv`, `pitch_map_2026.csv`, `wheeler_pitches_2026.csv` | AR-2, PM-1 |
| Velocity | `ff_velo_by_month.csv` | CF-2b four-seams |
| Parent reproduction | `parent_reproduction.csv` | CF-2b first half → uc-pps-020's six figures |
| Postseason, WC G3 | `postseason_ledger.csv`, `wc_g3_plate_appearances.csv` | CF-2b postseason → GS-1b, BN-1 |
| Card | `still_wheeler_card.csv`, `still_wheeler_backtest_2026.csv` | OC-1 |
| Client grading | `hp_reconciliation.csv` | `headlines.json` |
| Every narrative number | `headlines.json` | all of the above |

## 4 · Defect exposure

| Defect | Exposed here? | Evidence |
|---|---|---|
| **MI-1** (new) CF-2 admits AAA games via pitcher-keyed MiLB pulls | **Yes** | 148 rows / 3 games (DQ-06, DQ-28) |
| **NM-1** (new) CF-2 stamps UC49's subject name | **Yes** | CF-2 frame for 554430 labelled "Luzardo, Jesús" (`headlines.json: cf2_exposure`) |
| **OU1-1** (new) OU-1 misses base-running outs | **Yes** | 480 vs 486 (DQ-18) |
| **SJ-1** (new, build-caught) sinker tied-up count used all rows with an intercept, including a foul bunt | Fixed | harness E caught 125 vs 124; build now uses JR-1's swing list |
| O-26 `nphl` keep-first dedup | Yes (client frame) | 283 Mets-era pitches (DQ-29) |
| HP-13 role-mixed `player_name` population | Yes (client chart) | 33 of 186 points are batter-seasons |
| HP-18 leaked loop variable | Latent | correct by accident on a one-season frame (HP-15) |
| D-7/O-13 NULL zone | No | 0 NULL zones (DQ-22) |
| E-7 PM-1 `plate_x` docstring sign | Text only | axis labels say + = first-base side; DQ-14 RHP arm-side pfx_x < 0 |

## 5 · Privacy, tagging, versioning

- **Privacy (`privacy-watchdog`): CLEAR.** Public MLB performance data. The 2025 blood clot and surgery are named only as reported, once, as context; nothing is modeled and no data pattern is linked to them (harness G). The reported mechanical cause is a carry-in; the log is described, not interpreted.
- **Tags (`data-tagger`):** Internal · domain Phillies Pitching · subject area Season Recap · product `uc-pps-035` · no PII · player health: *reported status only*.
- **Versioning (`version-controller`):** v1.0.0, anchor 2026-09-27 (+ WC rows through 10/1). **v1.1.0** = any 2027 pitch (card graded). Changing a card bar, SR-2's tolerance, ST-1's boundaries or OU-2 after publication is **breaking**.

## 6 · Ratification path

| Object | Recommendation |
|---|---|
| OC-1 `october_card` | **Ratify** (second clean use); rename "season card", add `reference_window` |
| CF-2b | Promote into `dp_uc49_kernel` v1.0.1 (MI-1, NM-1); retire CF-2 |
| OU-2 / GS-1b | Promote; retire OU-1 for innings (E-3) |
| IX-1 | Adopt as the house mechanism for inheriting from scripts and notebooks; move ER-1, JR-1, RCI into a kernel (E-4) |
| ST-1, NC-1, MX-1, SR-2 | Provisional; second use required |
