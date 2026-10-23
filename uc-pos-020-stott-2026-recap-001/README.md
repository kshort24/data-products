# Another Level? — Bryson Stott 2026 Recap

**UC #55 · `uc-pos-020` · `dp_uc55` · v1.0.0 · delivered 2026-10-22 · READY-CONDITIONAL · independently verified (185/185)**
Phillies Offense (`pos`) · Human DPO: Kellen Short · second pos-side season recap; first with code in the data plane

## Start here
| If you want | Open |
|---|---|
| the story, walked | `dp_uc55_stott_2026_dashboard.html` (this folder) or the Artifact "Stott 2026 Recap" |
| the story on paper | `dp_uc55_stott_2026_recap_report.pdf` (10 pages) |
| the one picture | MLB `out/dp_uc55_f6_bat_path.png` (the contact point moved out front) |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-10-22_uc-pos-020-stott-2026-recap.md` → `07` §3 |
| a better `hot_or_not` for your notebook | MLB `out/dp_uc55_er1_notebook_cell.md` |

## The finding, in one paragraph
Stott hit .256/.334/.401 in 2026, a career-best .325 wOBA and .330 xwOBA. His xwOBA has risen in every season (.280 → .303 → .309 → .319 → .330).

The "good eras" don't hold up as eras:
- ER-1 finds no real change point in any season.
- None of the three hand-set eras clears a hindsight-corrected test.
- GS-1 agrees with the client that he was the same hitter in good and bad stretches. The exception is summer 2026, when walks and xwOBA really moved.

The level-up that did happen was mechanical. After the 2025 stance change his contact point moved out front (25.7 → 29.3 → 31.8 in) and his swing turned pull-side. He pulled more and went the other way less than ever, so he is *not* using all fields.

The level left is the zone: 2026 was his worst chase and whiff season, and his best month (August) had his lowest chase.

On defense, the IO-1 proxy reads second base as a down year (−9 after +12/+13/+19). That agrees with DRS (−9) and not with OAA (+8). Third base is too small to settle, and moving him there trades Bohm's bat for Arraez's (ISO .133 vs .090).

## Package contents
```
BID_2026-10-22_uc-pos-020-stott-2026-recap.md
00_dpo_orchestration_record.md   framing, gates, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins, glossary, data-dictionary carry-forward
02_engineering_design.md         data model, EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, inheritance, specs (ER-1, GS-1, IO-1 + A-1/A-2), lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment, build-time assertions, run order, reuse
05_quality_certification.md      DQ, harness (A–L), brand, palette, catches
06_consumer_success.md           forms and readers, reading paths, walkthrough, FAQ, query templates, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, recap comparison, calibration
uc-pos-020-Bryson Stott 2026 Recap 20261022.md        repo-side contract (copy; original at MLB root)
uc_ledger_AI_PATCH_uc-pos-020-stott-2026-recap.md     PENDING PASTE (copy at MLB root)
dp_uc55_stott_2026_recap_report.md / .pdf · dp_uc55_stott_2026_dashboard.html (+ _artifact.html)   delivered copies
```
Code and receipts live in the data plane (MLB root): `dp_uc55_kernel.py`, `_stott_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py` (+ generator `_dp_uc55_make_dashboard_builder.py`), `_verification.py`; `out/dp_uc55_*` (82 receipts); `eda/dp_uc55/`.

## Governed objects: inherited vs introduced
- **Inherited by import (14 pins):** K54 (uc-pos-019 spine → K40/K34/K53 chain, CM-1); K40a (uc-pos-014 bat path, O-15/C2 conventions).
- **Inherited for the HP family:** K44 (client functions verbatim), `inds` by IX-1, `barrel_rate.py`.
- **Generalized (non-breaking):** `era_metrics` (TR-1 atom + counts); GS-1 = TR-1's ledger on labelled eras.
- **Introduced (provisional):** ER-1 form eras · GS-1 good-era signatures · IO-1 infield sector expected outs (proxy; amendments A-1, A-2).

## Reproducing this
See `04` §4. The build refuses a house log past 2026-10-01. Expect `185/185` from `dp_uc55_verification.py`.

## Defects found by building
SRC-4 (client frame game types) · CL-1 (client std-as-mean) · ERA-1 (2025 window pre-break) · Q-1 (F9 axis) · Q-2 (F7 overclaim) · Q-3 (harness O-8 denominator) · J-1 (JSON default) · ENV-3 (third) · ENV-4 (stale commits, platform) · ENV-5 (Py 3.10 f-strings). Details in `03` §4.
