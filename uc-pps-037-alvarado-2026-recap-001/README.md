# The Full Ride — José Alvarado 2026 Recap

**UC #53 · `uc-pps-037` · `dp_uc53` · v1.0.0 · delivered 2026-10-18 · READY-CONDITIONAL · independently verified (163/163)**
Phillies Pitching (`pps`) · Human DPO: Kellen Short

## Start here
| If you want | Open |
|---|---|
| the story, walked | `dp_uc53_alvarado_2026_dashboard.html` (this folder) or the Artifact "The Full Ride" |
| the story on paper | `dp_uc53_alvarado_2026_recap_report.pdf` (10 pages) |
| the one picture | `out/dp_uc53_f10_db1_ledger.png` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-10-18_uc-pps-037-alvarado-2026-recap.md` → `07` §3 |

## The finding, in one paragraph
Alvarado faced 1,273 batters as a Phillie, #14 of 199 Phillies pitchers since 2015 and #3 among relievers; 2022 and 2023 ranked #9 and #10 of 104 Phillies relief seasons. 2026 was his worst season here: a .342 wOBA against (house), 10 blow-ups in 68 outings, and a 68% clean-outing rate, all tenure worsts. Hitters out-hit their contact by .040 (wOBA .351 vs xwOBA .311 on one basis), and his hard-hit rate was a tenure low, so luck played a part. The stuff declined too. The cutter averaged 91.5 mph (1.6 under 2022–24) and its whiff rate fell from 48.9% to 39.1%; his zone rate hit a tenure low; and from August his velocity faded while his xwOBA caught up with his results. The pre-registered DB-1 ledger reads decline SUPPORTED, blip MIXED: **call DECLINE (move on)**, and the call is the same against a 2021–25 baseline.

## Package contents
```
00_dpo_orchestration_record.md   framing, gates, capability table, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins
02_engineering_design.md         data model, EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1 search, glossary, KPI specs (DB-1 bars), lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment, build-time assertions, receipts, reuse
05_quality_certification.md      DQ, brand, palette, harness, catches (with "intake could have caught")
06_consumer_success.md           product forms and readers, reading paths, walkthrough, DB-1 guide, FAQ, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, recap comparison, calibration
BID_2026-10-18_uc-pps-037-alvarado-2026-recap.md
uc-pps-037-José Alvarado 2026 Recap 20261018.md     repo-side contract (copy; original at MLB root)
uc_ledger_AI_PATCH_uc-pps-037-alvarado-2026-recap.md  PENDING PASTE (copy at MLB root)
dp_uc53_kernel.py · _alvarado_recap.py · _hp.py · _build_figs.py · _narrative.py · _build_dashboard.py · _build_report.py · _build_pdf.py · _verification.py
dp_uc53_alvarado_2026_recap_report.md / .pdf · dp_uc53_alvarado_2026_dashboard.html (+ _artifact.html)
out/dp_uc53_*                    45 receipts (22 CSV, 12 JSON, 10 PNG, 1 TXT)
```
EDA reports are at the house location, MLB `eda/dp_uc53/`.

## Governed objects: inherited vs introduced
- **Inherited by import (sha256-pinned):**
  - `dp_uc52_kernel.py`, and through it K51/K49/K50/K48/K44/barrel_rate: nresults, whiff/chase/putaway, hard-hit, barrel, runs on watch, house percentile, XW-1, WB-1, RP-1, GS-1, PA-1.
  - The house `cumulative_metric.py` (CM-1).
  - CSW% as the locked term.
- **Generalized (non-breaking):** CF-2d (CF-2c with the subject passed in) · RP-1t (RP-1 over a span) · CM-1a (corrected wOBA spec passed to CM-1).
- **Introduced (provisional):** OD-1 outing bands · DB-1 decline-or-blip ledger (registered before 2026 rates were read).

## Reproducing this
```bash
cd "<Agents for Data Products>/data-products/uc-pps-037-alvarado-2026-recap-001"
export TMPDIR=/tmp/uc53/tmp                      # laptop VM: /sessions is full (ENV-3)
pip install --target /tmp/pyrender -r "<MLB root>/requirements-render.txt"
export PYTHONPATH=/tmp/pyrender:"<MLB root>" MLB_DATA_ROOT="<MLB root>" PYTHONDONTWRITEBYTECODE=1
python dp_uc53_alvarado_recap.py && python dp_uc53_hp.py          # DQ 11 PASS / 2 WARN / 0 FAIL
python dp_uc53_build_figs.py && python dp_uc53_build_dashboard.py && python dp_uc53_build_report.py && python dp_uc53_build_pdf.py
python dp_uc53_verification.py                                     # 163/163 expected
```
The build refuses a house log past 2026-10-01. A 2027 appearance or a verified signing is v1.1.0, not a correction.

## Defects found by building
- **CM-D1:** the house cumulative wOBA counts `woba_value` on IBB/sac-bunt PA ends with `woba_denom` 0. Lines ran high in 4 of 6 seasons (2026 .360 vs .351).
- **AB-1:** 16 automatic balls/strikes with no pitch in 2026, counted as pitches and as in-zone (zone 42.2% vs 41.4% thrown).
- **RK-2:** K−BB from K44's rounded rates printed 15.6%; from counts it is 15.7%.
- **ENT-1:** 9 rows in 2018 carry his id under a batter's name.
- **ENV-3:** pip ENOSPC on the laptop VM until `TMPDIR` moved to `/tmp`.
