# 05 · Quality & Certification
**data-quality-engineer · certification-agent**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0

## 1 · DQ scorecard (`out/dp_uc60_dq_scorecard.csv`): 11 PASS · 2 WARN · 0 FAIL
| Rule | Status | Detail |
|---|---|---|
| LIN-1 | PASS | 22 files pinned (K58 chain + SD-1/2/3) |
| ANC-1 | PASS | max game_date 2026-10-01 == anchor |
| ENT-1 | PASS | id 656941 across both sources; 0 duplicate keys |
| ER-1 | PASS | 0 games in the 7/13–7/15 window; ASB constants equivalent |
| AB-1 | PASS | 6 missed team games == SD-2 absences (stomach ×3, back ×1, GI ×2) |
| CS-1 | PASS | 122 context seasons (≥ 200 PA), 220 rank seasons (≥ 50 PA) |
| REC-1/2/3 | PASS | .232/.354/.502 vs CI-2 .232/.354/.503 (±.0015); 45 HR; 156 G |
| OI-1 | PASS | bat speed NULL ("not measured") before 2024 |
| BK-SCAN | PASS | eligible cuts have ≥ 150 PA on both sides |
| SM-1 | WARN | lefty offspeed 14 PA, marked too few to call |
| CI-2 OPS | WARN | CI-2 prints .853; log .855 |

## 2 · Independent harness (`out/dp_uc60_verification.csv`): **28 / 28 PASS**
Re-derived from the raw parquet with plain pandas:
- lineage and the SD-3 self-test; the SD-2 ASB window;
- the 2026 slash, PA, HR and K; the absence ledger; halves and HR split;
- BK-1 bat speed on both populations, EV p90 and the grade rule;
- barrel rate, chase (26.1%) and SW-8; the CN-1 z by formula;
- the F7 fit (R², n, all 11 seasons above the line); pool size; RHP-fastball PA;
- the Tier 3 audit (8 figures, 0 FAIL; F7 is the only V4 figure);
- report strings and a no-causal-claim regex; PDF freshness; all 8 figures embedded;
- dashboard (8 plots, CDN pin, nothing inlined); HP completeness; DQ; season card.

The first run was 23/28. Four of the five failures were 6-dp rounding in the harness's own tolerances. **The fifth was real (V08):** the F4 subtitle mixed two bat-speed populations. Fixed in the figure.

## 3 · Visual standard: Tier 3 V1–V7
`out/dp_uc60_visual_audit.csv` (`recap_viz.audit`): **8 / 8 figures PASS on every applicable standard.** The audit is backed by eyeball QA of every PNG, the PDF pages and the dashboard (headless Chromium with a local plotly bundle: 24 SVG layers rendered, 0 console errors).

## 4 · Client claims (`out/dp_uc60_hp_grades.csv`)
| HP | Claim | Grade |
|---|---|---|
| HP-01 | "Should we be concerned?" | **NOT SUPPORTED**, on CN-1. Chase is the one flag (z 4.1); K% leans (z 1.2); xwOBA above his tenure low |
| HP-02 | "It was his back?" | **NOT VISIBLE IN THE LOG**. Bat speed rose 0.2 mph after 6/23; EV p90 fell 0.9 (bar 1.5); best xwOBA split 33 games earlier |
| HP-03 | "Did he lose his pop?" | **PARTLY**. 1 of 4 legs (barrel rate) at his tenure low; second-half barrels 10.6% vs 19.3% |
| HP-04 | Halves .254/.367/.560 → .199/.336/.416 | SUPPORTED (H1 within .002, definition gap; H2 exact) |
| HP-05 | K% 31.4%, highest since 2017; 220 K | SUPPORTED, stronger: a career high among full seasons (2017 was 30.9%) |
| HP-06 | Chase 26.1%, from 21.5%, highest since 2020 | SUPPORTED (exact) |
| HP-07 | September .172 / .710 | SUPPORTED (exact) |
| HP-08 | 32 HR / 13 HR by half | SUPPORTED (exact) |

## 5 · Certification: **READY-CONDITIONAL**
| # | Condition (carried into the report caveats) |
|---|---|
| C1 | BK-1 tests one documented event. It is not a medical finding |
| C2 | Bat tracking covers 2024+ only (OI-1) |
| C3 | Two wOBA scales: house weights for seasons and months, Statcast weights in F2 |
| C4 | Context pools are Phillies-only; his 2015–21 seasons sit on Phillies context |
| C5 | BK-1, POP-1, CN-1, SD-1 DRAFT entries and the V1–V7 audit are provisional (first use) |
| C6 | Small cells (lefty offspeed 14 PA) |

**Privacy:** public-figure data, no PII. **Publish decision:** human DPO.
