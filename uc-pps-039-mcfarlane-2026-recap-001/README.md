# Nasty Stuff, Outlier Heater — Alex McFarlane 2026 Recap

**UC #63 · `uc-pps-039` · `dp_uc63` · v1.0.0 · delivered 2026-11-07 · READY-CONDITIONAL (C1–C5) · harness 45/45 · DQ 10/6/0 · V1–V7 8/8**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here
| If you want | Open |
|---|---|
| the story on paper | `dp_uc63_mcfarlane_2026_recap_report.pdf` (10 pages) |
| the story, clickable | `dp_uc63_mcfarlane_2026_dashboard.html` or the Artifact "Alex McFarlane 2026" |
| the deck to animate | `slides/slide_content.md` + `slides/dp_uc63_claude_design_brief.md` |
| the bid and the award | `BID_2026-11-07_uc-pps-039-mcfarlane-2026-recap.md` (acceptance at the end) |
| what the org decided and why | `00_dpo_orchestration_record.md` |

## The answer in five lines
1. The client's line reproduces exactly: 333 pitches, 21 outings (2 Wild Card), .280 wOBA, .633 OPS, 25.9% K, 8.2% BB, 22:7.
2. The four-seam is one of one: 99.4 mph / 2,544 rpm, 99th / 97th pct; no other RHP four-seam season in a Phillies game since 2015 at or above him on both.
3. Lefties: 33.3% K, one walk, slider 38.1% whiff / 50.0% chase. Righties: .179 BA but 41.9% hard-hit, 9.7% barrel, 6 of 7 walks.
4. Bridge to Duran: 4 outings, all from 8/31 (PARTLY on the filed bar). The heater slipped to ~98 over 9/22–9/27.
5. Narrative: 11 confirmed, 7 partly, 1 corrected (Kerkering went to South Florida), 1 not observable (command vs a prior year).

## Package
```
BID_…md (bid + award/acceptance) · 00–07 · README · uc-pps-039 contract (copy) · ledger patch (copy) · intake/client_prompt_2026-11-07.md
dp_uc63_mcfarlane_2026_recap_report.md/.pdf · dp_uc63_mcfarlane_2026_dashboard.html
slides/   slide_content.md, Claude Design brief, copy_registry.json, manifest.json, data/ (per-slide receipts), ref/ (8 PNG + plotly JSON)
data/     key receipts (headlines, HP grades, DQ, verification, visual audit, outing ledger, FO-1 pool, stand × pitch)
figures/  8 PNGs
```
Code and the full 52 receipts live at the MLB root (`dp_uc63_*.py`, `out/dp_uc63_*`, `eda/dp_uc63/`). Re-run: `04` §3.

## Governed objects
Inherited (pinned import via K62): K44 client functions, BR-1, XW-1, WB-1, KP-1, arsenal_table, RP-1, recap_viz. Generalized: BS-1r, CF-M.
New, provisional: FO-1, BD-1, ST-1, FN-1, CL-1. Findings: EN-3, RK-3, AB-1 (recurring).
