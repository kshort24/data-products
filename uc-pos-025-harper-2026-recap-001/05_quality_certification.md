# 05 · Quality & Certification
**data-quality-engineer · certification-agent**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0

## 1 · DQ scorecard (`out/dp_uc61_dq_scorecard.csv`): 14 PASS · 0 WARN · 0 FAIL
| Rule | Detail |
|---|---|
| LIN-1 | 23 files pinned |
| ANC-1 | 2026 max game_date 9/27 ≤ anchor 10/01 |
| ENT-1 | id 547180 across both sources; 0 duplicate keys |
| DH-2 | 4/30 order sourced; 27 earlier DH days on fallback (disclosed) |
| REC-1 | .269/.380/.485, 29 HR, 577 AB vs CI-1 |
| AB-1 | 161 G with a PA + 1 defensive-only (5/9) = 162 |
| CS-1 | 122 pool seasons; subject row reconciles |
| CM-2 | 12 seasons: cumulative endpoint == panel (BA/OBP/SLG/wOBA/HR/PA) to 1e-9 |
| CM-ENV | envelopes print `n_seasons`; no extrapolation |
| SM-1 | lefty offspeed (18 PA / 9 BIP) flagged |
| PG-1 / LOC-1 | 13 pitches untagged or unlocated |
| OZ-REP | UC #23 parent reproduction: H1 OZ-1 .411 = published .411 |
| SPR-1 | 155 hits (29 HR) on the spray frame = season line; all have coordinates |

## 2 · Independent harness (`out/dp_uc61_verification.csv`): **25 / 25 PASS**
Re-derived from the raw parquet with plain pandas (no kernel functions):
- 2026 slash, wOBA on house weights, games and appearances (V02–V04);
- every season 2015–26: raw = season panel = cumulative endpoint (V05); 2026 cumulative order incl. the 4/30 DH (V06);
- OPS by hand (V07); hand × group xwOBA and HR, six cells (V08);
- HC-1 and AP-1 legs over 2019–26 (V09–V10); OZ-1 by half with an independent geometry (V11);
- pull / oppo shares from raw hc (V12); 155 hits and HR direction (V13); LHP low-away share and whiff (V14);
- pool percentile (V15); HR No. 29 claim (V16);
- **NC-1** (V17): all 87 registered numbers re-format from their keys; no unregistered number on the card;
- no causal / medical language (V18); V1–V7 audit (V19); PNG freshness (V20); kit manifest + 6 metrics × 12 seasons (V21); HP and DQ (V22–V23); era sourcing (V24).

**First run 19/25.** All six failures were the harness's own: 1e-9 tolerances against 6-dp headlines (V07 ×2, V09, V12), the percentile test counting Harper's own row as "worse" (V15), and "90th-percentile" read as a data number (V17). No product defect.

## 3 · Visual standard V1–V7
`out/dp_uc61_visual_audit.csv`: **3 / 3 PASS** on every applicable standard, plus two rounds of eyeball QA on each PNG and the composed card.

## 4 · Client claims (`out/dp_uc61_hp_grades.csv`)
| HP | Claim | Grade |
|---|---|---|
| HP-01 | .269/.380/.485, 29 HR, 155 H, 32 2B, 148 SO, 577 AB, 162 G | **SUPPORTED (exact)** |
| HP-02 | "Approach and discipline held up" | **SUPPORTED** (3/3: chase 32.4% ≤ 35.7%; BB% 15.4%, best since 2020; K% 21.4% ≤ 26.5%) |
| HP-03 | "Hard contact faded" | **SUPPORTED** (3/3 at a tenure low: hard-hit 42.8%, barrel 10.3%, EV p90 106.3); H2 hard-hit 46.2% → 37.4%, z −1.82 LEANS |
| HP-04 | .997 OPS vs RHP, .657 vs LHP | **SUPPORTED (exact)**; vs-LHP OPS 12th of 12 seasons |
| HP-05 | HR No. 29 on 9/27 vs TB; one HR in the prior 27 games | **SUPPORTED (exact)** |
| HP-06 | "Owning the edge" holds for the full season | **SUPPORTED (HELD)**: OZ-1 .424 vs .397 (2025); H1 .411 → H2 .446, z 0.78 SAME |

## 5 · Certification: **READY-CONDITIONAL**
| # | Condition (carried into the card caveats and the brief) |
|---|---|
| C1 | AP-1, HC-1, OZ-H, DMG-1, CM-2, NC-1, DH-2 are provisional (first use) |
| C2 | Washington seasons come from the opponent file; 2020 (58 G) stays in every band |
| C3 | One outline for every park; 14 hits are drawn past a foul line where they were fielded |
| C4 | Pitch-map marks are locations, not to scale; the zone is the 2026 average |
| C5 | Small cell: lefty offspeed (18 PA) is drawn, never called out |
| C6 | The bars were written after the T0 profile printed season-level rates (disclosed in the BID) |

**Privacy:** public-figure data, no PII. **Publish decision:** human DPO.
