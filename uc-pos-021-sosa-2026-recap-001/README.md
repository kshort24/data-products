# We Really Do Love Sosa — Edmundo Sosa 2026 Recap

**UC #56 · `uc-pos-021` · `dp_uc56` · v1.0.0 · delivered 2026-10-23 · READY-CONDITIONAL · independently verified (161/161)**
Phillies Offense (`pos`) · Human DPO: Kellen Short · third pos-side season recap; first written as a possible end-of-tenure recap for a hitter; everything lives in this folder

## Start here
| If you want | Open |
|---|---|
| the story, walked | `dp_uc56_sosa_2026_dashboard.html` (this folder) or the Artifact "Love Sosa" |
| the story on paper | `dp_uc56_sosa_2026_recap_report.pdf` (8 pages) |
| the one picture | `out/dp_uc56_f2_season_card.png` (worst wOBA, best xwOBA and EV90) |
| the number | `out/dp_uc56_f9_walkaway.png` ($6.0M a year, up to 2 years) |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-10-23_uc-pos-021-sosa-2026-recap.md` → `07` §3 |

## The finding, in one paragraph
Sosa hit .247/.283/.429 in 2026 (.307 wOBA), the worst of his four full Phillies seasons, and his cumulative line ran last at every 50-PA checkpoint. The bat did not decline: his .330 xwOBA and 105.9 mph EV90 were the best of his four full Phillies seasons, bat speed held, and none of six pre-registered decline flags tripped. The late uptick was results catching up (wOBA .272 → .371 after the break) while xwOBA fell (.344 → .305). His chase rate (52.8%) was the highest of 42 Phillies RHB seasons since 2022, but his out-of-zone contact is above the median and his out-of-zone BA was earned, not lucky. He was never strong against breaking balls (2026 was his best expected year against them), velocity didn't beat him on process, and offspeed is where he swings and misses. He is a platoon bat (.362 wOBA vs LHP, .286 vs RHP, 2023–25) with five positions on his Phillies résumé and a .320 Phillies wOBA. **Walkaway: $6.0M AAV, no more than two years.**

## Package contents
```
BID_2026-10-23_uc-pos-021-sosa-2026-recap.md
00_dpo_orchestration_record.md   framing, gates, arguments, escalations, conditions
01_strategy_intake.md            ID, gaps, source profile, carry-ins CI-1…CI-7, glossary
02_engineering_design.md         data model, EDA findings, metadata map, dashboard spec
03_governance.md                 Rule-1, pins, OZ-1/WA-1 specs, lineage, defects, privacy, versioning
04_engineering_build.md          manifest, environment, assertions, run order, reuse
05_quality_certification.md      DQ, harness A–N, brand, verdict
06_consumer_success.md           readers, reading paths, FAQ, query templates, catalog entry
07_platform_marketing.md         tripwires, cost audit, bid vs actual, calibration, ledger
uc-pos-021-Edmundo Sosa 2026 Recap 20261023.md        contract
uc_ledger_AI_PATCH_uc-pos-021-sosa-2026-recap.md     PENDING PASTE
dp_uc56_*.py                     kernel, build, HP, figures, narrative, report, PDF, dashboard, harness
dp_uc56_sosa_2026_recap_report.md / .pdf · dp_uc56_sosa_2026_dashboard.html (+ _artifact.html)
out/                             58 receipts · eda/dp_uc56/  2 EDA reports
```

## Governed objects
- **Inherited by import (16 pins):** K55 (uc-pos-020 → K54 → K40 chain, K40a), K46 (uc-pos-017 directional family), `barrel_rate.py`.
- **Generalized (non-breaking):** `client_frame(name)`, EV-1, `asb_first_game`, **WB-2 pooled-wOBA wrapper**.
- **Introduced (provisional):** OZ-1 out-of-zone damage · WA-1 walkaway number.

## Reproducing this
See `04` §4. Expect `161/161` from `dp_uc56_verification.py`.

## Defects found by building
WB-2 (inherited pooled-wOBA weights; escalated) · D-1 · J-2 · J-3 · H-1 · Q-1 · Q-2 · Q-3 · SH-1 · CL-2 (client `inds`) · ENV-3 (fourth). Details in `03` §4.
