```yml
# Identity
name: Andrew Painter Return Read 20260731 BAL (Away)
id: uc-pps-023-Andrew Painter BAL 20260731
description: >
  Return-to-MLB read on Andrew Painter, starting at Oriole Park at Camden Yards
  on 2026-07-31 after five Triple-A starts following a mid-June option. Deep-dive
  angles: cross-level stuff comparison (velocity, spin, movement), location /
  chase / whiff, and release point / extension / arm angle. Opponent dimension
  formally descoped — no Orioles data exists in the repo. First self-scout
  variant of the uc-pps pattern.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — Ready for DPO Sign-off
priority: High
classification: Internal — Restricted (external publish blocked)

# People
personas: Pitcher, Catcher, Pitching Coach, Manager
owner: Kellen Short

# Relationships
parent_use_case: UC#3 -> UC#8 -> UC#11 -> UC#29 (this)
supersedes: _scratch_painter_lhv_scouting_20260709.md (dev scratch, never certified)
sub_use_cases: []

# Metadata
ledger_uc: 29
created: 2026-07-31
last_updated: 2026-07-31
build_artifact: dp_uc28_painter_vs_orioles.py
report: dp_uc28_painter_vs_orioles_report.md / .pdf
dashboard: dp_uc28_painter_vs_orioles_dashboard.html
verification: dp_uc28_verification.py — 76/76 passed
governance_trail: >
  Agents for Data Products/data-products/uc-pps-painter-return-001/ (00-07)

# Data References
entity_lock: pitcher == 691725 (MLBAM)
kpis:
  - whiff_rate            # LOCKED — verbatim from dp_uc11
  - chase_rate            # LOCKED
  - putaway_rate          # LOCKED
  - first_pitch_strike_rate  # LOCKED
  - hard_hit_rate         # LOCKED
  - nresults              # LOCKED
  - csw_rate              # mechanical helper
  - strike_rate           # mechanical helper
  - release_consistency_index    # NEW
  - fastball_upper_third_rate    # NEW
  - cross_level_stuff_delta      # NEW
  - arm_spread_deg               # NEW — PROVISIONAL, correlational
data_domains:
  - Pitch Profile
  - Pitch Outcomes
  - Strike Zone
  - At-Bat Outcomes
  - Batted Ball Profile (directional only)
  - Release Mechanics
```

# Andrew Painter — Return Read vs BAL, 2026-07-31

> **Document status:** the full contract, business context, and answered business
> questions live in the governance trail at
> `Agents for Data Products/data-products/uc-pps-painter-return-001/USE_CASE_uc-pps-painter-return-001.md`.
> This file is the repo-side registry entry so the `uc-pps-NNN` naming convention stays intact.

## Sources

| Tier | File | Filter | Rows | Window | Starts |
|---|---|---|---|---|---|
| MLB | `data/phillies/phils_2026.parquet` | `phillies_role=='pitching' & pitcher==691725 & game_type=='R'` | 1,141 | 2026-03-31 → 06-17 | 14 |
| AAA (supporting) | `data/opponents/lhvp26.parquet` | `pitcher==691725` | 396 | 2026-06-28 → 07-26 | 5 |
| Benchmark | `data/phillies/phils_2026.parquet`, both roles | `game_type=='R' & p_throws=='R'`, ≥150 four-seams | 31 pitchers | 2026 | — |
| Opponent (BAL) | — | — | **0** | — | — |

52 spring-training pitches excluded. AAA cache fresh through 2026-07-30 (T-1).

## Findings in one table

| # | Finding | Key numbers |
|---|---|---|
| 1 | The four-seam is the anomaly, not the secondaries | velo 55th pctile, ride 52nd, ext 52nd, FUTR 48th — **whiff 26th (.106 vs .200), upper-third whiff 23rd (.101 vs .250)** |
| 2 | Arm slot varies by pitch more than almost anyone's | **13.8°** spread vs pool median **4.25°**, p90 9.93° → **96th pctile** (n=23). AAA widened to 15.0° |
| 3 | Triple-A changed sequencing, not stuff | FF **33.1% → 49.2%**, SL −13.1, SW +8.3, SP −7.6; four-seam Δvelo +0.64, Δride −0.25 |
| 4 | The delivery is still moving | release-x jumped ~5 in for two starts then returned; **same-park control 6/28 vs 7/10 = 5.6 in**; extension fell every AAA start 6.451 → 6.293 while velo rose 96.6 → 97.8 |
| 5 | The lefty weapon was shelved | splitter vs LHH **.395 whiff / 76 sw**, usage **21.4% → 10.6%**; sweeper 4.4% → 17.6%; AAA whiff vs LHH **.150 (65 PA)** |

## Certification

21 PASS · 3 WARN · 1 FAIL (opponent coverage — reclassified non-blocking by formal descope).
Verification: **76/76** (`out/dp_uc28_verification_log.txt`).
Publish surface: **internal only**, need-to-know distribution.

## Closure

Post-game backtest — 8 checks at `07_platform_marketing.md` §7.4. Item 6 is the tipping hypothesis; a single start records evidence, not a verdict.
