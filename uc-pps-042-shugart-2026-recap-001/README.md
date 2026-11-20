# A Solid Middle Reliever Who Rebuilt His Plan Against Lefties — Chase Shugart 2026 Recap

**UC #66 · `uc-pps-042` · `dp_uc66` · v1.0.0 · delivered 2026-11-20 · READY-CONDITIONAL (C1–C4) · harness 34/34 · DQ 12/5/0 · V1–V7 11/11 · HP 8/3/1**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here
| If you want | Open |
|---|---|
| the story on paper | `dp_uc66_shugart_2026_recap_report.pdf` (11 pages) |
| the story, clickable, with the Pitch × Hand Explorer | `dp_uc66_shugart_2026_dashboard.html` |
| the graphs | `figures/` (11 PNGs) |
| the bid and the award | `BID_2026-11-20_uc-pps-042-shugart-2026-recap.md` |
| the client's prompt and scratch work | `intake/` |
| what the org decided and why | `00_dpo_orchestration_record.md` |

## The answer in eight lines
1. .312 wOBA (56th pct of 114 Phillies RHP relief seasons) on .300 xwOBA (65th); K 26.5% (71st); barrels 10.0% (18th) and chase 25.7% (21st) are the leaks.
2. Platoon even with a hair of reverse (.309 vs LHB / .315 vs RHB) where the typical righty reliever runs .028 worse vs lefties — 6/6 legs of the client's read hold.
3. Cutter: .289 wOBA vs LHB, .439 vs RHB (lives middle-away to righties; 12% on their inner third). 42% of cutters to lefties go inner third or in.
4. Sinker: 51% of all strikeouts; .039 wOBA vs LHB on 18 PA (top of 32 RHP relief sinker-vs-lefty seasons) — atypical, and due to regress (xwOBA .217).
5. The mix change was against lefties: sweeper 25% (Apr) → 4% (Aug–Sep), changeup and cutter up; vs righties the sweeper stayed ~22–30%.
6. June (.441 wOBA) was contact — 17% barrels — not walks; zone rate tied September for his best.
7. After the July recall: first-pitch strikes 54% → 64%, wOBA .352 → .262, BB% unchanged.
8. Role: middle relief — 6 of 46 outings late & close (rank 10 of 13), entered behind 30 times.

## Package
```
BID_…md · 00–07 · README · contract (copy) · ledger patch (copy) · intake/ (prompt + scratch)
dp_uc66_shugart_2026_recap_report.md/.pdf · dp_uc66_shugart_2026_dashboard.html
data/     key receipts (headlines, overall, by_stand, stand_pitch, context, platoon, cs_c ranks, months, usage, CU-1, CW-1, role, stints, HP, DQ, verification)
figures/  11 PNGs (F1, F2, F3, F4a, F4b, F5, F6, F7, F8, F9, S1)
```
Code and all 64 receipts live at the MLB root (`dp_uc66_*.py`, `out/dp_uc66_*`, `eda/dp_uc66/`). Re-run: `04` §2.

## Governed objects
Inherited (pinned import via K64): K44 KPI functions, K48 rv100 / KP-1, K49 CX-1, K50 XW-1, K51 BR-1, K52 RP-1, K63 outing ledger + FN-1, recap_viz, cumulative_metric.
New, provisional: FR-1, CS-A (`phi_rhp_relief_seasons`, DRAFT), CS-B, CS-C, IN-1, LC-1 (= FN-1), CU-1, CW-1, S-1, VZ-1…VZ-6.
