# 01 — Use-Case Validation & Gap Report · uc-pos-004 (dp_uc20)

**Agent role:** use-case-validator · **Verdict: GO** (0 blocking, 3 non-blocking gaps, all resolved at intake)

## Use case as received (DPO prompt, 2026-07-14)
First-half 2026 analysis of Kyle Schwarber (All-Star, HR Derby runner-up). Narrative to open with high-level measurables, then KPI results — user-specified list (home runs, run creation, wOBA, SLG, OPS, OBP, batting average, hard-hit rate, barrel rate, pitches_per_plate_app) plus standard scouting KPIs — then describe, quantify, and measure the 2026 approach as potential leading indicator of the KPI outcomes. Follow org discipline + MLB repo standards. Additional scope: token-economist agent next-step (def + pilot telemetry) and a formatting-improvement backlog note.

## Completeness check
| Element | Present? | Note |
|---|---|---|
| Business question | YES | "What approach is driving the KPI outcomes?" — well-formed, falsifiable |
| Entity | YES | Kyle Schwarber → locked to MLBAM 656941 (never name-filter) |
| Window | IMPLIED | "first half 2026" → 2026-03-26..2026-07-12 (cache-complete); career context needed for "career-high" claims |
| KPI list | YES | 10 user KPIs; 8 map to locked kernel, 2 are NEW (gaps 1–2) |
| Personas | IMPLIED | Inherited from Marsh/ASG shape: Manager, Hitting Dept, Player, DPO |
| Acceptance criteria | IMPLIED | Marsh-report shape (uc-pos-marsh-breakout-001) accepted as the standard |

## Gaps (all non-blocking)
1. **"Run creation" is not a locked KPI.** No wRC in the kernel or glossary. *Resolution:* kpi-calculator spec SC-1 (03); constants available in `wOBA and FIP Constants.csv` (wOBAScale, R/PA present — verified). Provisional pending glossary approval.
2. **"pitches_per_plate_app" is not a locked KPI.** Trivial derivation but still requires a spec per governance rule 1. *Resolution:* SC-2 (03).
3. **All-Star / Derby facts not in the data plane.** *Resolution:* DPO-provided manual carry-ins, labeled in report header and freshness notes (Duran-saves precedent).

## Feasibility
Source coverage verified before GO: `data/opponents/schwarber.parquet` (2015–2021, 11,449 pitches) + `phils_{2022..2026}.parquet` (batter 656941 present; 2026 fresh through 07-12). Bat-tracking fields present 2024+ (42.6% of 2026 pitches ≈ swing rate — expected, tracked-on-swing only). League-wide benchmark plane absent → career-self benchmarking, stated in report.
