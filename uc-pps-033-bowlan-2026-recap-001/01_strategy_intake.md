# 01 · Strategy & Intake: `uc-pps-033`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation

| Namespace | Ground truth checked | Claimed |
|---|---|---|
| UC ordinal | `uc_ledger_AI_PATCH_uc-pps-032…` says "Next available: UC #48"; `uc_ledger_AI.md` still says #25 (known drift) | **#48** |
| Build artifact | `ls dp_uc48*` at the MLB root, in `out/`, and in the control plane → none | **`dp_uc48`** |
| Stream id | latest control-plane `uc-pps-032`; no `uc-pps-033*` anywhere | **`uc-pps-033`** |

## 2 · Use-case validation (gap report)

| # | Gap | Blocking? | Resolution |
|---|---|---|---|
| V-1 | "xxth Percentile" names no population | Blocking | KP-1: Phillies pitcher-seasons 2015–26, regular season, ≥100 PA (the client's "Phillies pitcher-seasons" idiom from cell 114). Labelled not-MLB-wide |
| V-2 | "Elite" is used for vert, K rate, and whiff without a bar | Blocking | Four-seam: the uc-pps-032 archetype bar (≥60 on both axes). Rates: KP-1 percentile. No other superlative is used |
| V-3 | The notebook's wOBA (.269) and games (60) disagree with the log | Non-blocking | Cache-state probe (`out/dp_uc48_cache_probe.csv`): no season-end cut gives .269; no cut reaches 60 G. Reported as drift, not error |
| V-4 | "Actions people could have taken" is unfalsifiable as prose | Non-blocking | PA-1 ledger: hypothesis → declared signatures → decision rule → confirmation evidence |
| V-5 | The 9/17 injury was carried in as a "suspected oblique" | Non-blocking | Re-verified: reported as a right groin strain, no IL (Inquirer, 2026-09-18). Carry-in only |
| V-6 | "Runs created" collides with Bill James' RC | Non-blocking | Kept (approved house term, uc-pos-012), glossed, escalated E-3 |

## 3 · Source profiling

| Source | Rows for 680742 | Seasons | Game types | Note |
|---|---|---|---|---|
| `data/phillies/phils_2026.parquet`, `phillies_role=='pitching'` | 1,014 | 2026 | R 967 · **S 47** | spring excluded (DQ-18) |
| `data/phillies/phils_2025.parquet`, `phillies_role=='batting'` | 19 | 2025 | R | KC @ PHI 2025-09-13: **duplicates** of the file below (DQ-14) |
| `data/opponents/bowlan.parquet` | 851 | 2023 (56) · 2024 (68) · 2025 (727) | R | dedicated player pull; `player_name` = Bowlan on every row |
| `data/opponents/*.parquet` (other 127 files) | 0 name hits | — | — | byte search for "Bowlan" on the device; `get_nphillies_data()` adds nothing beyond `bowlan.parquet` for this subject |
| **Governed career frame (CF-1)** | **1,818** | 2023–2026 | R only | 0 duplicate keys |

**Fitness for purpose**

| CDE | Completeness (Bowlan, R) | Fit? |
|---|---|---|
| `release_speed`, `release_spin_rate`, `pfx_x`, `pfx_z` on four-seams | 100% jointly | ✅ |
| `bat_score`, `post_bat_score` (runs_created) | 100% | ✅ |
| `zone` | 99.94% (1 NULL, D-7/O-13 exposure → DQ-16 WARN) | ✅ |
| `description`, `events`, `balls`, `strikes`, `pitch_number` | 100% | ✅ |
| `estimated_woba_using_speedangle` | BIP only for `xwobacon` | ✅ (pitch-level use quarantined) |
| `delta_run_exp` | 100% | ✅ RV/100 |
| `pitcher_days_since_prev_game` | NULL on the first outing of each file season | ✅ rest (first outing excluded) |
| `on_1b/2b/3b` at first pitch | exact (after defect B-1 fix, `05` §4) | ✅ |

## 4 · Entity lock

| Subject | MLBAM | How resolved | Note |
|---|---|---|---|
| Jonathan Bowlan | **680742** | prior UCs (uc-pps-029, uc-pps-032); confirmed as the only `pitcher` id under the name in both sources | name filter used only to reproduce the client's frame |
| Jhoan Duran (staff K leader, context) | 661395 | uc-pps-018 | appears only as the staff comparison |

## 5 · Client claims inventory (the human parent)

The 14 `kpis_comments`, 4 chart subtitles, the `gy` loop state and the 2017 exclusion make **22 claims** (HP-01…HP-22). The Gemini cell adds **6 audit notes** (GM-1…GM-6). All are graded in the report §8 and `out/dp_uc48_hp_reconciliation.csv`.

## 6 · Carry-ins and external lookups (logged, never computed on)

| Item | Source | Use |
|---|---|---|
| Phillies acquired Bowlan from Kansas City for LHP Matt Strahm (offseason) | MLB.com, "Phillies deal LHP Strahm to Royals, acquire RHP Bowlan" (web search, 2026-09-24) | narrative context, chapter 1 |
| 9/17 exit vs NYM, during an at-bat with Lindor | client notebook, `September 2026.ipynb` cell 85 | narrative, chapter 6 |
| Reported as a right groin strain; no IL placement | Philadelphia Inquirer, 2026-09-18 (web search headline) | supersedes "suspected oblique"; chapter 6 and `07` T-1 |
