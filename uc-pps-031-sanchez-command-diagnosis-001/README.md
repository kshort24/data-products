# Cristopher Sánchez — is he near the zone?

**UC #45 · `uc-pps-031` · `dp_uc45` · v1.0.0 · delivered 2026-09-16 · READY-CONDITIONAL · independently verified (436/436)**
Phillies Pitching (`pps`) value stream · Human DPO: Kellen Short

## Start here

| If you want | Open |
|---|---|
| the argument | `dp_uc45_sanchez_command_report.pdf` |
| to check any split yourself | `dp_uc45_command_dashboard.html` |
| the proof chart | `out/dp_uc45_fig3_chase_beyond_shadow.png` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the new KPI specs, before reusing them | `03_governance.md` §2 |
| the rulebook change every zone UC needs to know about | `05_quality_certification.md` §2 (O-18), `07` §5 |
| the price and how it landed | `BID_2026-09-16_…md`, `07` §3 |

## The finding, in one paragraph

Kellen's four premises (walks up, zone down, chase down, ahead down) are **true since the All-Star break and
mostly false for the season**. For the season, walks are flat (.054 → .055), chase is up (.316 → .362), pitches
thrown ahead are flat (.311 → .313), and in-zone fell (.519 → .465). But **the 2026 zone is a different ruler**:
every hitter now has one fixed, height-based zone whose top is about 2.8 in lower than 2025's. On common rails,
half of his zone drop is his own. Since the break: walks .048 → .068, in-zone .472 → .452, chase .386 → .320
(p = .008), ahead .333 → .278 (p = .002). **Is he near the zone?** He's near the edge as often as ever (governed
Edge Rate .365 → .358), but he misses the one-baseball **shadow** more often (.344 → .407; +.038 of it his own).
In the first half, hitters chased those misses 33.3% of the time and covered for it. Since the break, **26.0%**
(league flat at .276). The leak is the **changeup to right-handed hitters**: 62.1% miss the shadow, and only 30.2%
of those misses get chased.

## Decisions needed

1. **E-1 · O-18:** adopt common-rail re-scoring (ZC-1) as the standing control for any 2025↔2026 zone comparison, and restate affected UCs?
2. **E-2:** paste the governed `edge_rate` into `Baseball Functions.ipynb`. It's approved but was never promoted.
3. **E-3:** the Attack Zone "shadow" (0.33 ft) conflicts with the ratified one-ball constant. Restate or rename?
4. **E-4:** ratify SZ-1/2/3 on second use?

## Package contents

```
00_dpo_orchestration_record.md     spine: ask, gates, finding, internal arguments, escalations, publish call
01_strategy_intake.md              prior art (Rule-1), gaps, premises, source fitness, O-18 discovery
02_engineering_design.md           model, joins, 9 EDA findings, metadata map, dashboard spec
03_governance.md                   three-geometry crosswalk, SZ/CL/PN/ZC specs, lineage, privacy, versioning
04_engineering_build.md            manifest + hashes, inheritance proof, environment, assertions, re-run recipe
05_quality_certification.md       DQ 16/1/0, defect register incl. O-18, verification 436/436, certification
06_consumer_success.md             personas, reading order, dashboard walkthrough, KPI reading guide, FAQ
07_platform_marketing.md           cost audit, bid vs actual, calibration, tripwires, O-18 change notice
BID_2026-09-16_uc-pps-031-sanchez-command.md
uc-pps-031-Cristopher Sanchez Command 20260916.md     use-case contract (repo-root registry copy)
uc_ledger_AI_PATCH_uc-pps-031-sanchez-command.md      pending paste into the MLB ledger
dp_uc45_kernel.py                  A verbatim · A2 governed edge_rate · B access · D new
dp_uc45_sanchez_command.py         the build (29 receipts)
dp_uc45_build_figs.py              6 figures
dp_uc45_build_pdf.py               markdown -> weasyprint
dp_uc45_build_dashboard.py + tpl/  self-contained dashboard
dp_uc45_verification.py            8 families, 436 checks
dp_uc45_sanchez_command_report.md / .pdf
dp_uc45_command_dashboard.html
out/                               receipts, figures, payload, verification log
```
