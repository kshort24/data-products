# uc-pos-024 · Kyle Schwarber 2026 season recap: "Forty-Five and a Question Mark"
**UC #60 · build `dp_uc60` v1.0.0 · Phillies Offense (`pos`) · Human DPO: Kellen Short · Delivered 2026-10-29 · READY-CONDITIONAL (C1-C6) · harness 28/28 · DQ 11/2/0 · Tier 3 visual audit 8/8**

## The answer in five lines
1. A good year, not a lost one: 45 HR (tied for the MLB lead), .232/.354/.502, wOBA .367 (90th percentile of 220 Phillies hitter seasons), xwOBA .366.
2. It turned in July: first half .394 wOBA, second half .329. By August and September the expected line had recovered faster than the results.
3. "It was his back?" **Not visible in the log.** Bat speed 74.1 → 74.4 mph across the 6/23 scratch; the biggest xwOBA break sits 33 games earlier (5/16).
4. "Did he lose his pop?" **Partly.** Barrel rate 15.5% was a tenure low by a hair, and 10.6% after the break; EV p90, ISO and HR rate stayed in his range.
5. "Should we be concerned?" **Not on the evidence**, with one real flag: chase 26.1% (z 4.1), and the leak on righty fastballs (.495 → .386).

## Deliverables
| What | Where |
|---|---|
| **PDF report** (6 pp) | `MLB/dp_uc60_schwarber_2026_recap_report.pdf` (+ `.md`); copy here |
| **Dashboard** (7 chapters) | `MLB/dp_uc60_schwarber_2026_dashboard.html` (+ `_artifact.html`); copy here |
| Season card | `MLB/out/dp_uc60_season_card.png`; copy in `figures/` |
| **Tier 3 shared dependencies** | `MLB/data/_schema/comparison_sets.json` (SD-1), `MLB/data/_schema/eras.json` (SD-2), `MLB/phillies_dp/recap_viz.py` (SD-3); copies in `data/` |
| Code | `MLB/dp_uc60_kernel.py`, `_schwarber_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_build_card.py`, `_verification.py` |
| Receipts | `MLB/out/dp_uc60_*` (37 files) · `MLB/eda/dp_uc60/`; key copies in `data/`, figures in `figures/` |
| Trail | BID, `00`–`07`, `intake/` (the client's two briefs), contract and ledger-patch copies |

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc60_schwarber_recap.py && python dp_uc60_hp.py && python dp_uc60_build_figs.py && python dp_uc60_build_report.py && python dp_uc60_build_pdf.py && python dp_uc60_build_dashboard.py && python dp_uc60_build_card.py && python dp_uc60_verification.py
python -m phillies_dp.recap_viz
```

## Open items for the DPO
Publish · ratify the SD-1 DRAFT pitcher sets · adopt SD-2 ASB · Tier B (pitcher redesign items 1–4) · `cumulative_metric` v1.1 (from UC58) · ledger paste UC52–UC60.
