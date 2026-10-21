# The Sheriff of the Phillies Bullpen — Tim Mayza 2026 Recap

**UC #52 · `uc-pps-036` · `dp_uc52` · v1.0.0 · delivered 2026-10-14 · READY-CONDITIONAL · independently verified (74/74)**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here
| If you want | Open |
|---|---|
| the story, walked | `dp_uc52_mayza_2026_dashboard.html` (MLB root) or the Artifact "The Sheriff of the Phillies Bullpen" |
| the story on paper | `dp_uc52_mayza_2026_recap_report.pdf` (9 pages) |
| the one picture | `out/dp_uc52_f05_arsenal_movement.png` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-10-14_uc-pps-036-mayza-2026-recap.md` → `07` §3 |

## The finding, in one paragraph
Mayza allowed a .285 wOBA (house basis), the third-best of his nine seasons and #11 of 32 Phillies LHP relief seasons since 2015. On Statcast's basis he allowed .299 against a .288 expectation, so luck did not carry it. He kept runners off with strikes (5.9% walks, #6 of 32), not by finishing at-bats faster (quick-AB rate 57.6%, his career low by a hair). Contact is the watch item: his 45.2% hard-hit rate trailed only his rookie year, and righties carried a .314 xwOBA. A high, tight slot, 6.93 ft of extension (85th percentile) and an 87.4 mph bullet slider explain the profile. His nearest delivery comps are Cristopher Sánchez (2021) and José Alvarado (2026).

## Package contents
```
00_dpo_orchestration_record.md   framing, gates, capability table, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins
02_engineering_design.md         data model, EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, glossary, KPI specs, lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment, build-time assertions, receipts, reuse
05_quality_certification.md      DQ, brand, palette, harness, catches (with "intake could have caught")
06_consumer_success.md           product forms and readers, reading paths, walkthrough, FAQ, catalog entry
07_platform_marketing.md         tripwires, cost audit (Phase 2 fields), bid vs actual, recap comparison, calibration
BID_2026-10-14_uc-pps-036-mayza-2026-recap.md
uc-pps-036-Tim Mayza 2026 Recap 20261014.md        repo-side contract (copy)
uc_ledger_AI_PATCH_uc-pps-036-mayza-2026-recap.md  PENDING PASTE
```
**Data plane (MLB repo root):** `dp_uc52_kernel.py` · `dp_uc52_mayza_recap.py` · `dp_uc52_hp.py` · `dp_uc52_build_figs.py` · `dp_uc52_narrative.py` · `dp_uc52_build_dashboard.py` · `dp_uc52_build_report.py` · `dp_uc52_build_pdf.py` · `dp_uc52_verification.py` · report `.md/.pdf` · dashboard `.html` (+ `_artifact.html`) · `out/dp_uc52_*` (42 files) · `eda/dp_uc52/`.

## Governed objects: inherited vs introduced
**Inherited by import (sha256-pinned):** `dp_uc51_kernel.py` → K49 / K50 / K48 / K44 / barrel_rate: nresults, runs_created, house_percentile, season_recap, load_phils_cols, xwoba_pa, barrel_rate, hard_hit_rate, whiff/chase/putaway, pitch_mix.
**Inherited by extraction (IX-1, second use):** `inds` (Baseball Functions.ipynb), `tm_success_rate` (July 2026.ipynb). HP family only.
**Generalized (non-breaking):** CF-2c `career_frame_ext` (EN-2).
**Introduced (provisional):** QA-1, BS-1, DS-1, RP-1; WB-1 basis companion.

## Reproducing this
```bash
cd "<MLB repo>"
pip install --target /tmp/pyrender -r requirements-render.txt      # device: /sessions is full
export PYTHONPATH=/tmp/pyrender:.
python dp_uc52_mayza_recap.py && python dp_uc52_hp.py
python dp_uc52_build_figs.py && python dp_uc52_build_dashboard.py && python dp_uc52_build_report.py && python dp_uc52_build_pdf.py
python dp_uc52_verification.py                                     # 74/74 expected; DQ 12/12
```
The build refuses a house log past 2026-10-01. A further postseason appearance or verified 2027 status is v1.1.0, not a correction.

## Defects found by building
- **WB-1** house vs Statcast wOBA basis (.285 vs .299): the first draft's "expected agrees" claim was restated.
- **HX-1** NF-1 drops `launch_speed_angle` (client-frame barrel rank wrong).
- **EN-2** CF-2 projection gaps (build failed twice).
- **DEF-1** client `tm_success_rate` reads the pre-pitch count (40.1% vs 59.0%).
- **RQ-1/2/3** render: kaleido string-x; `<` swallowing PDF §7–9; pipe splitting a table. Guards added.
