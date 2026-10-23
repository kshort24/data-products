# Exactly as Advertised — Justin Crawford 2026 Recap

**UC #54 · `uc-pos-019` · `dp_uc54` · v1.0.0 · delivered 2026-10-20 · READY-CONDITIONAL · independently verified (157/157)**
Phillies Offense (`pos`) · Human DPO: Kellen Short · first pos-side season recap

## Start here
| If you want | Open |
|---|---|
| the story, walked | `dp_uc54_crawford_2026_dashboard.html` (this folder) or the Artifact "Crawford 2026 Recap" |
| the story on paper | `dp_uc54_crawford_2026_recap_report.pdf` (10 pages) |
| the one picture | `out/dp_uc54_f1_cumulative_slash.png` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-10-20_uc-pos-019-crawford-2026-recap.md` → `07` §3 |

## The finding, in one paragraph
Crawford hit .264/.309/.353 (.294 wOBA, .284 xwOBA) in 465 PA. That is 8th of 9 Phillies primary-CF seasons since 2015 in wOBA at matched volume, ahead of only Rojas 2024. He hit .343 with runners in scoring position (34 for 99).

"Better from June 1" is half right. His batting average rose .234 → .283 on BABIP, but wOBA moved only +.014, walks fell, and the pre-registered TR-1 ledger reads **NO TURN**. What actually happened was a mid-June hole followed by a June-to-August surge.

The approach was exactly as advertised:
- swing 53.3% (80th percentile)
- chase 37.6% (better than only 15% of 220 Phillies hitter-seasons)
- whiff 17.7% (better than 88%)
- out-of-zone contact better than 94%

That contact keeps the strikeouts down and turns chases into weak contact instead of walks. He reached a three-ball count in just 12.0% of PA (10th percentile).

The ball goes into the ground: 58.9% grounders, a 0.9° launch angle (2nd-lowest of 189, lowest with 100+ PA) and a 1.7° attack angle (lowest of 31).

In centre field, the notebook's own method says he made the plays (261 outs vs 260.5 expected), but it only counts balls he reached. Across every CF-sector air ball the XO-2 proxy has him **−9.8**, 6th of 9 Phillies CF seasons, in line with −8 OAA on record (CI-2).

## Package contents
```
00_dpo_orchestration_record.md   framing, gates, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins, glossary
02_engineering_design.md         data model, EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, inheritance, specs (TR-1, CC-1, XO-2), lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment, build-time assertions, run order, reuse
05_quality_certification.md      DQ, brand, palette, harness, catches (with "intake could have caught")
06_consumer_success.md           forms and readers, reading paths, walkthrough, FAQ, query templates, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, recap comparison, calibration
BID_2026-10-20_uc-pos-019-crawford-2026-recap.md
uc-pos-019-Justin Crawford 2026 Recap 20261020.md      repo-side contract (copy; original at MLB root)
uc_ledger_AI_PATCH_uc-pos-019-crawford-2026-recap.md   PENDING PASTE (copy at MLB root)
dp_uc54_kernel.py · _crawford_recap.py · _hp.py · _build_figs.py · _narrative.py · _build_report.py · _build_pdf.py · _build_dashboard.py · _verification.py
dp_uc54_crawford_2026_recap_report.md / .pdf · dp_uc54_crawford_2026_dashboard.html (+ _artifact.html)
out/dp_uc54_*                    69 receipts (47 CSV, 12 JSON, 10 PNG)
```
EDA reports are at the house location, MLB `eda/dp_uc54/`.

## Governed objects: inherited vs introduced
- **Inherited by import (sha256-pinned, 12 files):**
  - K40 (pos spine, uc-pos-014)
  - K34 (CX-1, uc-pos-011)
  - K53 → K52 → K51/K50/K48/K44/barrel_rate (XW-1, WB-1, KP-1, PA-1, IX-1)
  - `cumulative_metric.py` (CM-1)
- **Inherited by IX-1 extraction:** UC22 attack regions; the client's `find_similar_hits` (XO-1).
- **Generalized (non-breaking):** CM-1 spec dicts · CM-1b multi-panel ghost lines · RF-2x rolling xwOBA.
- **Introduced (provisional):**
  - TR-1 June-turn ledger (registered in the BID)
  - CC-1 chase cost
  - XO-2 sector expected outs (proxy)

## Reproducing this
See `04` §4. The build refuses a house log past 2026-10-01. Expect `157/157` from `dp_uc54_verification.py`.

## Defects found by building
- **SF-1:** K40 drops `sac_fly_double_play` from OBP/wOBA denominators. Found by the CM-1 endpoint reconcile.
- **TP-1:** K40 counts `truncated_pa` as a PA/AB (34 pool PA).
- **CM-D2:** the house hard-hit cumulative spec raises on nullable exit velocity.
- **ENT-2:** `crawford.parquet` is J.P. Crawford, who also batted for PHI in 2017–18.
- **SRC-2:** an opponent file duplicates 3 of his 2026 MLB pitches.
- **ENV-3** (second occurrence): `/sessions` full on the laptop VM; install with `TMPDIR=/tmp/...`.
