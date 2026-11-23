# uc-pos-026 · Alec Bohm, Phillie
**UC #67 · build `dp_uc67` v1.0.0 · Phillies Offense (`pos`) · Human DPO: Kellen Short · Delivered 2026-11-22 · READY-CONDITIONAL (C1–C7) · harness 51/51 · DQ 11/0/0 · V1–V7 8/8**
Continues uc-pos-013 (UC #38). Written on the client's assumption that he does not return (public: no qualifying offer, free agent).

## The answer in five lines
1. **The finish:** uc-pos-013's surge held in the contact, not the results. After the audit window: wOBA .374 → .323 and in-zone whiff 6.8% → 15.3%, but hard-hit 46.9% → 50.0% (120 PA; PR-1 H-F MIXED).
2. **2026 in context:** .308 wOBA, the Phillies median (110 of 220 hitter-seasons since 2015); K% 13.9% (13th-lowest). April cost the season.
3. **Line drives:** his fewest (24.8%), but LD share explains 0.7% of a Phillie's wOBA (G-LD failed). By the filed rule, not the story. The spray chart ships in the dashboard, in the house field outline.
4. **Righties:** results, not process. wOBA vs RHP breaking .301 → .237 (his worst), xwOBA vs RHP flat.
5. **The career:** 63 deciding runs (GW-1), #2 to Schwarber among 11 Phillies regulars 2020–26; BA w/ RISP .314, #1. RS-1 (4 of 7 seasons): the best results of his era, not a repeatable split.

## Start here
| If you want | Open |
|---|---|
| the story on paper | `dp_uc67_bohm_career_retrospective_report.pdf` (7 pages) |
| the story, interactive (incl. the LD spray chart) | `dp_uc67_bohm_career_retrospective_dashboard.html` |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-11-22_uc-pos-026-bohm-career-retrospective.md` → `07` §5 |
| the house-wide defect this run found | `03` §4 TP-1 · `00` E-2 |
| the receipts | MLB `out/dp_uc67_*` (43); key copies in `data/`, figures in `figures/` |

## Package contents
```
00_dpo_orchestration_record.md   framing, gates, capability table, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins, glossary
02_engineering_design.md         data model, joins, EDA, metadata map, dashboard spec
03_governance.md                 Rule-1 search, lineage, GW-1/XC-1/G-LD/RS-1/TP-1 specs, defects, privacy, version
04_engineering_build.md          manifest + shas, environment, run order, assertions, receipts
05_quality_certification.md      DQ 11/0/0, harness 51/51, visual audit, catches, certification
06_consumer_success.md           forms, reading paths, personas, GW-1 snippet, FAQ, catalog entry
07_platform_marketing.md         version, privacy, tripwires, cost, bid vs actual, corrections, marketing line
BID_2026-11-22_uc-pos-026-bohm-career-retrospective.md
intake/client_prompt_2026-11-22.md · intake/client_notebook_2026-11-22.md
uc-pos-026-Alec Bohm Career Retrospective 20261122.md          contract (copy; original at MLB root)
uc_ledger_AI_PATCH_uc-pos-026-bohm-career-retrospective.md     PENDING PASTE (copy at MLB root)
dp_uc67_bohm_career_retrospective_report.md / .pdf · dp_uc67_bohm_career_retrospective_dashboard.html
data/ (19 key receipts) · figures/ (F1–F8 PNG)
```
Code lives in the MLB data plane root: `dp_uc67_kernel.py`, `_bohm_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py`, `_pins.json`. EDA at MLB `eda/dp_uc67/`.

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc67_bohm_recap.py && python dp_uc67_hp.py && python dp_uc67_build_figs.py && python dp_uc67_build_dashboard.py && python dp_uc67_build_report.py && python dp_uc67_build_pdf.py && python dp_uc67_verification.py && python dp_uc67_build_report.py && python dp_uc67_build_pdf.py && python dp_uc67_build_dashboard.py
```

## Open items for the DPO
Ratify GW-1 / XC-1 / G-LD / RS-1 · **TP-1 house fix (breaking)** · uc-pos-013 errata (HP-09, 3 phantom PA) · ENV-3 `TMPDIR` in MLB `CLAUDE.md` · ledger paste UC52–UC67.
