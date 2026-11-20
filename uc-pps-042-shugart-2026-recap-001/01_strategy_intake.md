# 01 · Strategy & Intake
Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent` · `token-economist`

## 1 · ID reservation
UC #66 · `uc-pps-042` · `dp_uc66` · folder `uc-pps-042-shugart-2026-recap-001`. Collision check in the BID (UC65 patch reserved #66; no `dp_uc66*`).

## 2 · Use-case validation: GO (0 blocking, 4 non-blocking)
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | Comparison set unspecified ("righty relievers? middle relievers? all RHP? own history?") — delegated to the org | non-blocking | CS-A / CS-B / CS-C chosen and defended in the BID; own history NOT OBSERVABLE |
| G2 | Client `pps` (house projection) carries 73 spring-training pitches | non-blocking | FR-1: governed frame = regular season; client's printed numbers reconcile to it |
| G3 | "Better visualization" has no acceptance criterion | non-blocking | VZ-1…VZ-6 filed in the BID; V1–V7 machine audit; two eyeball-QA rounds |
| G4 | "Middle reliever / higher leverage" — no leverage index in Statcast | non-blocking | LC-1 late-close entry share (K63 FN-1 definition reused) vs the 2026 bullpen |

## 3 · Source profile (`source-system-profiler`)
| Source | Rows for subject | Use |
|---|---|---|
| `data/phillies/phils_2026.parquet`, pitching role | 944 (871 R + 73 S), 46 regular-season outings, 2026-04-14 → 09-26 | evidence (regular season) |
| `phils_2015..2025` + opponent files | 77 MLB pitches (2025, fragments) + 22 A-ball (2025) | not used (NOT OBSERVABLE) |
| `data/opponents/lhvp26.parquet` | 115 AAA pitches, 7 outings (03-28 → 07-08) | supporting tier, never blended |
| `wOBA and FIP Constants.csv` | Season 2026 row | house wOBA weights |
Anchor: house max `game_date` 2026-10-01 (no postseason rows for Shugart). EDA → `eda/dp_uc66/governed_frame.md`.

## 4 · Carry-ins (web, display + reconciliation only)
| CI | Fact | Source | Reconciled |
|---|---|---|---|
| CI-1 | Acquired 2026-01-13 from PIT for IF Francisco Loreto | MLB.com trade story | context only |
| CI-2 | 2026: 46 G, 53.2 IP, 26.5% K | FanGraphs player page | **46 outings == log; K% 26.5% == house** |
| CI-3 | Transactions: optioned 03-22; recalled 04-14; recalled 07-09; optioned 08-09, recalled 08-10 | MLB.com transactions | S-1 stint split (gap Jun 29 → Jul 18) consistent |
| CI-4 | Drafted 2018 BOS round 12 (Texas); MLB debut 2024 | MiLB.com / ESPN | context only |

## 5 · Glossary (`business-glossary-agent`)
Inherited terms only for every KPI (K44/K48/K49/K50/K51/K52). New provisional objects (BID 14:12 ET): FR-1, CS-A, CS-B, CS-C, IN-1, CU-1, CW-1, S-1;
LC-1 reuses K63 FN-1's late-close definition unchanged. No term's business meaning was inferred by an agent.
