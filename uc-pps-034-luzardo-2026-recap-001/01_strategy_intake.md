# 01 · Strategy & Intake: `uc-pps-034`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation

- Ground truth for numbering: `uc_ledger_AI_PATCH_uc-pps-033-bowlan-2026-recap.md` → **next UC #49, `uc-pps-034`**. `uc_ledger_AI.md` still reads "next #25" (drift carried as E-6). The skill-bundled ledger reads "next #12" (stale).
- Collision check 2026-09-27: `dp_uc49*` none (MLB root, `out/`, control plane); `uc-pps-034*` referenced only as "next" in the uc-pps-033 patch.
- Prior art for this subject: `uc-pps-017` (first half / All-Star, UC #19), `uc-pps-028` (consistency audit vs AZ, UC #39), plus the pre-ledger `dp_uc3`, `dp_uc6`, `dp_uc8_luzardo_vs_mets`, `dp_uc13`. **Inherited:** 017's first-half figures (reproduced 4/4) and its sweeper-first finding; 028's workload-band finding (restated from this build, 86–110 pitches).

## 2 · Use-case validation (gap report)

| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Better than most pitchers in my dataset" names a population (Phillies pitcher-seasons ≥150 pitches) but no rank | Blocking | CX-1: rank with n printed; CX-1b adds the starter-workload cut (≥2,000 pitches) with sensitivity at 1,500 / 2,500 |
| V-2 | "Best shift of his Major League career" has no metric | Blocking | GS-1 (Game Score, Tango v2 form, log-derived) over all 150 career starts; also tested against strikeouts (not his high) |
| V-3 | "Done for the regular season": the log's last pitch is 9/7 while the Phillies played through 9/26 | Non-blocking | Carry-ins: scratched 9/12, IL 9/15 (shoulder inflammation), activated for Game 162 as a reliever. Premise superseded (HP-07) |
| V-4 | "A defining postseason" is unfalsifiable as prose | Non-blocking | OC-1 October card: 4 signatures, bars from his own 2026 range, decision rule, published backtest |
| V-5 | "One of the best acquisitions" needs "acquired by" data | Non-blocking | Not graded; no transaction table in either repo (P8 declined, E-8) |
| V-6 | The client frame concatenates `pps` and `nphl` by name | Non-blocking | NF-1 reproduces `nphl` exactly; O-26 found (230 pitches lost); postseason rows inside season rows (380). Governed frame is CF-2 |
| V-7 | ERA is quoted in reporting but not computable from Statcast | Non-blocking | Carry-in only; "runs on watch" defined for the log |

## 3 · Source profiling

| Source | Rows for 666200 | Notes |
|---|---|---|
| `data/phillies/phils_2025.parquet`, `phils_2026.parquet` (pitching role) | 3,013 R + 112 D (2025); 2,860 R + 165 S (2026) | Anchor 2026-09-26; last Luzardo pitch 2026-09-07 |
| `phils_2021…2024` (batting role: he pitched *against* the Phillies) | 177 / 92 / 181 R + 90 F / 79 | All duplicates of the dedicated file |
| `data/opponents/luzardo.parquet` (pitcher-keyed) | 8,553 R + 195 F + 73 D, 2019–2024 | 2024 ends 2024-06-16 (season ended in June) |
| 20 other `data/opponents/*.parquet` (batter-keyed) | 659 regular-season rows | `player_name` = the **batter**; every row duplicates PHI or FILE; 0 pitches added |

**BS-1 (instrument defect).** `uc-pps-033` profiled `nphl` with a byte search of the parquet files. For Luzardo that finds 2 files (`bdodgers`, `luzardo`); the id column finds **21**. Compressed pages hide strings, and batter-keyed pulls carry the batter's name. The id scan (`opponent_id_scan`) replaces it.

**O-26 (loader defect).** `get_nphillies_data()` concatenates the opponent files in sorted order and drops duplicate pitch keys `keep='first'`. When a Luzardo pitch also sits in an alphabetically earlier batter-keyed file (`adolis`, `arraez`, `bader`, `castellanos` …), the surviving row carries the batter's name, and `nphl[nphl.player_name == 'Luzardo, Jesús']` loses it: **230** regular-season pitches, 2019–2024.

**Back-check of uc-pps-033 (V-3 closed).** The same id scan for Bowlan finds 3 files, including `lhvp26.parquet` (Lehigh Valley, pitcher-keyed, 16 pitches on 2026-04-26). Through `nphl`, that AAA outing enters the client's Bowlan frame: 60 games and a .269 wOBA, exactly the notebook numbers uc-pps-033 could not reproduce with a cache-state probe (`out/dp_uc49_bs1_bowlan_v3_resolution.csv`).

## 4 · Entity lock

MLBAM **666200**, LHP. Every row of CF-2 asserts `pitcher == 666200` (DQ-02) and `p_throws == 'L'` (DQ-05). The accented name `'Luzardo, Jesús'` is used only to reproduce the client frame.

## 5 · Client claims inventory (the human parent)

13 items from cells 51 and 118, each graded in `out/dp_uc49_hp_reconciliation.csv` and report §9: 3 supported (HP-01 zone, HP-02 better than most, HP-03 best shift), 2 carry-ins verified (All-Star, extension), 1 not graded (acquisitions), 1 superseded (season "done"), 2 reproduced (scatter, pitch map), 1 differs-explained (frame), 1 chart defect (per-color OLS), 1 correct-by-accident (leaked `gy`), 1 Rule-1 redirect (`edge_rate` exists in UC8).

## 6 · Carry-ins and external lookups (logged, never computed on)

| Fact | Source | Used where |
|---|---|---|
| Acquired from MIA, Dec 2024, for Starlyn Caba and Emaarion Boyd | MLB.com (extension story, 3/10/2026) | ch. 1 |
| 5 years / $135M, 2027–2031, 2032 club option | MLB.com, 3/10/2026 | ch. 2, HP-05 |
| First All-Star selection, named 7/7 as a replacement; ASG 7/14 at Citizens Bank Park | MLB.com, 7/7/2026 | ch. 5, HP-04 |
| Labor Day: 1:51 game time, Schwarber HR off Didier Fuentes, Braves led the NL East by 4; NL Pitcher of the Month (August) | MLB.com, 9/7/2026 | ch. 5–6 (the box itself reconciles to the log, DQ-14) |
| Scratched 9/12 (shoulder stiffness); 15-day IL 9/15 (shoulder inflammation); 30-pitch bullpen 9/25; 2.87 ERA in 29 starts, 1.84 after the break | Phillies Nation, 9/24/2026 | ch. 7, HP-07; "29 starts" reconciles (DQ-07) |
| Activated for Game 162, available out of the bullpen | SI, 9/27/2026 | ch. 7–8 |
| "Two game plans" on Labor Day | Metro Philadelphia (headline) | fig 6 framing; the log is consistent with it |
