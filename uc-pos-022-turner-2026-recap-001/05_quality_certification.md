# 05 · Quality & Certification
**data-quality-engineer · certification-agent**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0

## 1 · DQ scorecard (`out/dp_uc57_dq_scorecard.csv`): 10 PASS · 3 WARN · 0 FAIL
| Rule | Status | Detail |
|---|---|---|
| LIN-1 | PASS | 17 unique files pinned |
| ANC-1 | PASS | max game_date 2026-10-01 == anchor |
| BP-C | PASS | K40a C1-C8 re-proven on 2025-26 Phillies swings |
| ENT-1 / DUP-1 | PASS | id 607208, one name, bats R, 0 duplicate keys |
| SRC-4 | WARN (by design) | client frame carries 2023 D/F/L, 2024-25 D, 2026 S/E/F pitches; excluded from governed rates |
| SRC-5 | PASS | 2016-22 context locked by id |
| CI-1 | PASS | 700 PA, .242/.297/.378 == FanGraphs |
| CM-1 | PASS | 11 cumulative endpoints == nresults (tol 1e-9) |
| PR-1 floors | PASS | bars and floors == BID |
| REC-40a | PASS | UC40a 2026-09-02 cut reproduced exactly |
| BP-W | WARN | bat path 2025-26 only (G7) |
| SM-1 | WARN | small cells; n printed everywhere |

## 2 · Independent harness (`out/dp_uc57_verification_results.csv`): **34 / 34 PASS**
Re-derived from the raw parquet with plain pandas (no kernel KPI function): slash line, IZ swing (both periods) and its z by formula, RHP breaking OOZ contact, popup rates, PR-1 gap and its Wald z, tracked-swing counts and tilt means for 2025-26, the PB-1 cohort size / peer median / net, the cumulative endpoint, the UC40a reconcile, HP completeness, figure brand checks, CDN pin, report numbers, PDF page cap.

## 3 · Certification: **READY-CONDITIONAL**
| # | Condition (carried into every consumer surface) |
|---|---|
| C1 | Bat-path comparisons are 2025 vs 2026 only, peer-netted against an 8-hitter cohort (G7, O-16) |
| C2 | Small cells (lefty offspeed 31 BIP, lefty 95+ fastballs 22 BIP, 17 tracked breaking-ball popups); CT-1 floors applied |
| C3 | HP-11 rests on an association that is not controlled for pitch height |
| C4 | HP-12 not testable; position carry-ins only |
| C5 | PR-1 and PP-1 are provisional (first use) |
| C6 | Pooled 2023-25 wOBA via the inherited WB-2 wrapper |

Privacy: internal; public-figure performance data only (privacy-watchdog, 07). Publish decision: human DPO.
