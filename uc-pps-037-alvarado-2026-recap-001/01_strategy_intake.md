# 01 · Strategy & Intake: `uc-pps-037`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation
- Ground truth for numbering: `uc_ledger_AI_PATCH_uc-pps-036-mayza-2026-recap.md` (pending paste, wins over the ledger tail's "#52") → **UC #53, `uc-pps-037`**.
- Collision check 2026-10-18: `dp_uc53*` none (MLB root, `out/`, control plane); `uc-pps-037*` referenced only as "next".
- Prior art for this subject: `uc-pps-016` (multi-stint workload flag; stopped at scaffolding). It supplied the MLBAM id; nothing else was inheritable. Prior season recaps UC48/49/51/52 supplied the shape.

## 2 · Use-case validation (gap report)
| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Move on or a blip" has no stated test | Non-blocking | DB-1, pre-registered signature ledger (`03` §2) |
| V-2 | "Remarkably inconsistent" has no metric | Non-blocking | OD-1 outing bands + DB-1 B2 damage concentration |
| V-3 | "Tenure" not bounded | Non-blocking | Phillies regular seasons 2021–26; TB 2017–20 only in velocity/shape trends |
| V-4 | "Full-time reliever" (HP-01) undefined | Non-blocking | RP-1t: starts ≤ 20% of games over the span |
| V-5 | Client frame mixes game types (SRC-1) | Non-blocking | HP rows on the client frame, then restated regular season |
| V-6 | "Must have missed time with injury" (HP-03) | Non-blocking | Games from the log; IL as carry-in CI-5; no medical inference |
| V-7 | Whiff `hline` typed at 0.39 (DEF-1) | Non-blocking | Computed and printed |

## 3 · Source profiling
| Source | Rows for 621237 | Notes |
|---|---|---|
| `data/phillies/phils_2021…2026.parquet` (pitching) | 5,322 R (2021 1,045 · 2022 881 · 2023 742 · 2024 1,052 · 2025 457 · 2026 1,145) + 53 S (2026) + 335 postseason (2022–24) | Anchor 2026-10-01 (file); regular season ends 2026-09-27 |
| `data/phillies/phils_2018.parquet` | 9 rows with `pitcher == 621237` under `player_name` "Santana, Carlos" | **ENT-1**: TB vs PHI; batting role. Excluded by the pitching role (DQ-05) |
| `data/opponents/alvarado.parquet` (pitcher-keyed) | 2,328 | TB 2017–20 (2020 includes 47 ALCS pitches, kept out of rates) |
| 26 other `data/opponents/*.parquet` | incidental | `player_name` = the batter; dedup on the pitch key |
| 2026 automatic pitches | 16 rows (15 `automatic_ball`, 1 `automatic_strike`), no `pitch_type` | **AB-1** (found by DQ-07 in T5) |

Profiled by id column. 69 non-MLB rows were dropped by CF-2b (receipt `out/dp_uc53_career_milb_dropped.csv`).

## 4 · Entity lock
MLBAM **621237**, LHP. Every row of the frame asserts `pitcher == 621237` (DQ-02) under the pitching role. The name string is used only to reproduce the client frame (asserted to select only 621237).

## 5 · Client claims inventory (the human parent)
10 items from the notebook export, each graded in `out/dp_uc53_hp_grades.csv` and report §9: **9 confirmed** (four with frame restatements) and **1 partly** (HP-01: Adam Morgan also ranks above him as a reliever). No claim was contradicted.

## 6 · Carry-ins and external lookups (logged, never computed on)
| # | Fact | Source (outlet, date) | Used where |
|---|---|---|---|
| CI-1 | Club option exercised for 2026, $9M | CBS News / CBS Sports, Nov 2025 | §8 case, read-first box |
| CI-2 | Free agent after 2026; 31 years old | NBC Sports Philadelphia, 2026-10-02 | §8, read-first |
| CI-3 | 80-game PED suspension announced 2025-05-18; ineligible for the 2025 postseason | 6abc, 2025-05-18 | read-first; DB-1 baseline rationale |
| CI-4 | Optioned to Triple-A Lehigh Valley, May 2022 (7.62 ERA in 13 IP at the time) | Sports Illustrated (Inside the Phillies) | read-first |
| CI-5 | Reinstated from the 15-day IL, 2023-06-09 | MLB.com press release | HP-03 |
| CI-6 | Mid-2026 role reduced; 6.10 ERA vs 3.82 xERA (as of 2026-07-04) | MLB.com, 2026-07-04 | §8 blip case; G8 disclosure |
| CI-7 | 5.86 ERA, 68 G, 58⅓ IP, 70 K | NBC Sports Philadelphia, 2026-10-02 | read-first; DQ-12 reconciles G and K |
| CI-8 | "Mr. Punchie"; Caleb Cotham credited with the cutter; "the last year of the Experience" | client notebook | ch. 3, title |
