# 05 · Quality & Certification: `uc-pps-034`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed; `out/dp_uc49_dq_scorecard.csv`) — **21 PASS / 2 WARN / 0 FAIL**

| Rule | Dimension | Rule (grain) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate pitch key in CF-2 (pitch) | PASS | 0 |
| DQ-02 | consistency | entity lock: every row pitcher == 666200 (pitch) | PASS | [666200] |
| DQ-03 | validity | regular season only in the rate frame (pitch) | PASS | R |
| DQ-04 | timeliness | Phillies log current through the pinned anchor (file) | PASS | 2026-09-26 |
| DQ-05 | validity | p_throws == L (pitch) | PASS | L |
| DQ-06 | timeliness | no 2026 appearance after Labor Day (carry-in: IL 9/15) | PASS | 2026-09-07 |
| DQ-07 | consistency | 29 appearances == carry-in "29 starts" (season) | PASS | 29 |
| DQ-08 | completeness | id scan finds every file the name filter finds (file) | PASS | 21 ⊇ {luzardo} |
| DQ-09 | consistency | client frame (R) + O-26 losses == CF-2 (pitch) | PASS | 14,196 + 230 = 14,426 |
| DQ-10 | validity | OU-1: no inning credits > 3 outs (game-inning) | PASS | — |
| DQ-11 | consistency | every 2026 appearance is a start (game) | PASS | 29 |
| DQ-12 | consistency | uc-pps-017 first-half figures reproduced (season) | PASS | 4/4 |
| DQ-13 | consistency | Labor Day OU-1 outs == 27 (game) | PASS | 27 |
| DQ-14 | consistency | Labor Day log == published box on 8 items (game) | PASS | 109 / 2 / 1 / 12 / 23 / 1–0 / 8th |
| DQ-15 | completeness | FF velo/spin/pfx jointly non-null ≥ 99% (pitch) | PASS | 1.0 |
| DQ-16 | completeness | NULL zone share (pitch) | PASS | 0.0 |
| DQ-17 | validity | LHP arm-side FF pfx_x > 0, catcher view (pitch) | PASS | +0.997 ft |
| DQ-18 | comparability | CX-1 / KP-1 are Phillies-only (**permanent**) | **WARN** | 259 / 198 pitcher-seasons |
| DQ-19 | validity | spring and exhibition rows excluded (pitch) | PASS | 165 |
| DQ-20 | consistency | parent kernels sha256 pinned (file) | PASS | 0f63857a1032 / a2c119096db2 |
| DQ-21 | validity | D-1: no whiff subset drops a season (pitcher-season) | PASS | 8/8 |
| DQ-22 | consistency | O-26 exposure in the client frame (pitch) | **WARN** | 230 |
| DQ-23 | validity | postseason never enters a rate (pitch) | PASS | 380 pitches, 6 games |

## 2 · Brand and palette compliance

- **9 / 9 figures pass** the in-process brand checks (Arial, title, subtitle, axis titles on every visible axis, palette ⊂ house set): `out/dp_uc49_brand_compliance.csv`. The brand center MCP was not attached to this host; the checks are the same rules run locally.
- **PL-1 pitch palette** passes all six dataviz checks on the light surface and on the dark surface (`out/dp_uc49_palette_validation.txt`). The house Statcast pitch colors **fail** the validator for this arsenal (sinker vs sweeper ΔE 6.7 at normal vision; changeup vs sweeper ΔE 1.9 protan), so PL-1 keeps the four-seam red and re-steps the other three. Recommended as the house default for four-pitch arsenals (E-5 family).
- The first render failed the axis-title check on the shared x-axis of fig 4; the rule was refined to ignore axes whose tick labels are hidden by `shared_xaxes`.

## 3 · Verification harness: **226 / 226 PASS** (`dp_uc49_verification.py`, `out/dp_uc49_verification_log.csv`)

The harness imports no build kernel for computation. It re-reads the parquet files with pyarrow, rebuilds the frame with its own dedup and recomputes.

| Family | What it recomputes | Checks |
|---|---|---|
| A · lineage | kernel hashes, anchor, DQ 0 FAIL | 5 |
| B · career frame | the 21-file id scan, 14,426 pitches, 1,188 duplicates, 380 postseason pitches; 8 seasons × 6 rates vs the recap receipt; the tests' p-values; O-26 (230); the uc-pps-033 V-3 resolution | 65 |
| C · context | n = 259; ranks #28 / #31; dominated by 10 (none ≥2,000 pitches); quadrant 76; starters n = 41, whiff #1, chase #8; **cut sensitivity at 1,500 (n = 51) and 2,500 (n = 26): still #1**; percentiles; the command fit | 17 |
| D · Labor Day | the box, 30 batters, 23 whiffs = 22 + 1 foul tip, 28/61 chases, 42 CSW, velocities, 8–17 pitch innings, the run, the changeup counts by time through | 13 |
| E · arc | 150 starts / 166 games, GS 100 #1, next 86, only 27-out game, K high 13, halves, August, pitch-count band, 8/26, first-15 velocity, postseason ledger, OC-1 bars / backtest / history, uc-pps-017 reproduction | 21 |
| F · published numbers | 79 report strings and 15 dashboard strings, each formatted from a harness-recomputed value; bans "lowest of his career" and any MLB-wide claim | 96 |
| G · carry-in discipline | 6 carry-ins in the manifest; ERA only as carry-in; no causal injury language | 9 |

## 4 · What the build and the harness caught

| # | Caught | By | Fix |
|---|---|---|---|
| 1 | "Lowest in-zone rate of his career" (2021 was lower) | review of the recap receipt, then harness B/F | "lowest since 2021"; F bans the phrase |
| 2 | "Made hitters chase better than almost any Phillies pitcher" (#28) | certification argument | dek rests on whiff among starters (#1) |
| 3 | "The 10 that beat him are relief workloads" (unproven for 1,500–1,999 pitches) | harness C | "none carried a starter's workload" (max 1,126) |
| 4 | Labor Day "23 swings and misses" compared to swinging strikes (22) | DQ-14 WARN on first run | house whiffs include the foul tip → 23 = 23 |
| 5 | US-1 crash on pandas 2.3 (ENV-1) | first device run | US-1b |
| 6 | Older Phillies seasons lack `n_thruorder_pitcher` | first device run | schema-aware projection (`_cols_in`) |
| 7 | pitch-map axis label copied the PM-1 docstring (+ = 3B side) | figure review against DQ-17 | "+ = 1B side"; E-7 |
| 8 | NaN in the dashboard payload broke `JSON.parse` | headless render | NaN → null |
| 9 | Fixed plot heights overlapped the PA stepper; dark-mode labels invisible | headless render (1280 light/dark, 390 phone) | autosize to container; ink remapped in dark |

## 5 · Certification

**READY-CONDITIONAL** (conditions C1–C6 in `00` §8). Lineage complete (`03` §3), glossary entries recorded (`03` §1), KPI specs precede code (`03` §2), DQ 0 FAIL, harness 226/226, brand 9/9, privacy CLEAR, anchor pinned. The two WARNs are designed and disclosed.
