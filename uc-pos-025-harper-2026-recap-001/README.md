# uc-pos-025 · Bryce Harper 2026 season recap: "Bryce Harper | 3 | The Eye Carried a Softer Bat"
**UC #61 · build `dp_uc61` v1.0.0 · Phillies Offense (`pos`) · Human DPO: Kellen Short · Delivered 2026-11-02 · READY-CONDITIONAL (C1–C6) · harness 25/25 · DQ 14/0/0 · V1–V7 3/3**

## The answer in five lines
1. Still the Phillies' best bat: .269/.380/.485, 29 HR, all 162 games; .375 wOBA led the 10 Phillies with 200+ PA (94th percentile of 122 Phillies hitter seasons).
2. The eye carried it: 15.4% BB (best since 2020), .380 OBP; chase, K% and edge-takes held (AP-1, OZ-H SUPPORTED).
3. The thump stepped back: hard-hit 42.8%, barrels 10.3%, EV p90 106.3, SLG .485, all Phillies-tenure lows (HC-1 SUPPORTED); his most pull-heavy year (49.9% of BIP).
4. Righties paid (.997 OPS, 25 HR; .482 xwOBA on fastballs, .420 on breaking balls); lefties didn't (.657, 4 HR, worst of 12 seasons; lefty fastballs .320 xwOBA vs .410).
5. Not luck: xwOBA vs LHP .314 (wOBA .299). The June "it's luck" read did not survive the season.

## Deliverables
| What | Where |
|---|---|
| **Claude Design kit** (16 files + manifest) and **brief** | `MLB/out/dp_uc61_design_kit/` (`dp_uc61_claude_design_brief.md`); copy in `design-kit/` |
| Reference notecard | `MLB/out/dp_uc61_notecard_reference.png`; copy in `figures/` |
| F1 cumulative wOBA · F2 pitch maps · F3 spray | `MLB/out/dp_uc61_f1..f3.png` + `.json` (plotly); copies in `figures/` |
| Code | `MLB/dp_uc61_kernel.py`, `_harper_recap.py`, `_hp.py`, `_narrative.py`, `_build_figs.py`, `_build_card.py`, `_build_kit.py`, `_verification.py` |
| Receipts | `MLB/out/dp_uc61_*` (34 files) · `MLB/eda/dp_uc61/`; key copies in `data/` |
| Trail | BID, `00`–`07`, `intake/`, contract and ledger-patch copies |

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc61_harper_recap.py && python dp_uc61_hp.py && python dp_uc61_narrative.py && python dp_uc61_build_figs.py && python dp_uc61_build_card.py && python dp_uc61_build_kit.py && python dp_uc61_verification.py
```

## Open items for the DPO
Publish · ratify AP-1 / HC-1 / OZ-H / DMG-1 / CM-2 / NC-1 / DH-2 · `cumulative_metric` v1.1 (CM-2) · Tier B (PDF + dashboard) · ledger paste UC52–UC61.
