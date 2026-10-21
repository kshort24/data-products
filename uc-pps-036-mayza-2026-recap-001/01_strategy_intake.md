# 01 · Strategy & Intake: `uc-pps-036`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation
- Ground truth: the `uc_ledger_AI.md` tail reads "Next available: **UC #52 / dp_uc52** (pps next `uc-pps-036`)", as of 2026-10-12. No root patch claims higher (the newest is UC51's).
- Collision check 2026-10-14: `dp_uc52*` none (MLB root, `out/`, control plane). `uc-pps-036*` appears only as "next" in the ledger and in UC51's patch and `07`.
- Prior art for this subject: none (first Mayza UC). Pattern prior art: the season recaps UC48 (Bowlan, reliever), UC49 and UC51, inherited by import.

## 2 · Use-case validation (gap report)
| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Phillies LHP relievers historically" has no role definition | Non-blocking | RP-1: starts ≤ 20% of games; population n=32 (100+ PA) |
| V-2 | "Most similar Phillies LHP" has no metric | Non-blocking | DS-1 (6 z-scored delivery/stuff features) |
| V-3 | "Bullet slider" has no threshold | Non-blocking | BS-1 (|HB| and |IVB| ≤ 4 in), written before results |
| V-4 | `tm_success_rate` code ≠ stated definition (pre-pitch `strikes`) | Non-blocking | QA-1 implements the definition; client method kept as HP-13 |
| V-5 | Client frames carry postseason rows (no `game_type` filter) | Non-blocking | Regular season for rates; postseason ledger (6 pitches) |
| V-6 | "Should he be back" assumes free agency | Non-blocking | Carry-in CI-3, unverified; no roster recommendation |

## 3 · Source profiling
| Source | Rows for 641835 | Notes |
|---|---|---|
| `data/phillies/phils_2026.parquet` (pitching) | 1,093 R + 66 S + 6 F | Anchor 2026-10-01; RS 2026-03-28 → 2026-09-25 |
| `data/phillies/phils_2025.parquet` (pitching) | 139 R | September 2025 after the waiver claim |
| `data/opponents/mayza.parquet` (pitcher-keyed) | 5,221 (RS 2017–19, 2021–25; postseason 2022–24) | No 2020 rows |
| 21 other `data/opponents/*.parquet` (batter-keyed) | 1–132 each | `player_name` = the batter; dedup on the pitch key |
| `pp26.csv` (MLB root) | 134 (through 2026-04-14) | **Stale**; not used; the client's live `pp26` matches the parquet |

Profiled by id column, never by name. Career frame after dedup: 6,376 regular-season pitches over 9 seasons.

## 4 · Entity lock
MLBAM **641835**, LHP. Every frame asserts `pitcher == 641835` and `game_type == 'R'`. The name string `Mayza, Tim` is used only to reproduce the client frames (HP family).

## 5 · Client claims inventory (the human parent)
14 items from the attached notebook export and `July 2026.ipynb` cell 137, graded in `out/dp_uc52_hp_grades.csv` and report §9: **10 Confirmed · 3 Partly · 1 Not confirmed** (HP-05 release point "bang average").

## 6 · Carry-ins and external lookups (logged, never computed on)
| Fact | Source (outlet, date) | Used where |
|---|---|---|
| CI-1 Claimed off waivers from PIT, on the 60-day IL | MLB Trade Rumors, 2025-08-31 | Read-first box |
| CI-2 Re-signed to a major-league deal | MLBTR headline "Phillies Re-Sign Tim Mayza To MLB Deal" (date not verified) | Read-first box |
| CI-3 2027 status | not verified | Read-first box; caveats |
| CI-4 Pattison interview: "two strikes or a grounder within 3 pitches" | client notebook paraphrase (July 2026 cell 137); primary not fetched | QA-1 definition source |
| CI-5 "#37, The Sheriff" | client | Title (DPO instruction) |
