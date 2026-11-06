# uc-pps-038 · Taijuan Walker, Phillie
**UC #62 · build `dp_uc62` v1.0.0 · Phillies Pitching (`pps`) · Human DPO: Kellen Short · Delivered 2026-11-05 · READY-CONDITIONAL (C1–C6) · harness 47/47 · DQ 15/0/0 · V1–V7 9/9**

## The answer in five lines
1. **What they got:** 1,772 batters (#8 of 199 Phillies pitchers since 2015) over 402.2 innings reconciled to the out. 2023 was near the Phillies median (.311 wOBA); 2024 (.412) and 2026 (.455) are the #3 and #1 worst of 198 Phillies pitcher-seasons.
2. **What they bought:** a contact manager. In 2021–22 he allowed .027 less wOBA than the Phillies line expects at his 21.4% K (KR-1), and Statcast called most of it real (luck gap −.008).
3. **What broke:** the stuff (H-S STRONG). K% 21.4 → 16.9, whiff 23.6 → 18.9, four-seam 94.2 → 92.4 mph (and gone by 2026), splitter whiff 28.2% → 21.6%.
4. **The luck:** the Mets-era luck went away (H-L STRONG), but his Phillies luck gap (+.013) is below the Phillies pool median (+.019). 2026 alone was unlucky.
5. **The cost (AAV basis):** $179K per inning over the deal; $794K per inning in 2026, before his April 23 release and two Angels minor-league deals. Registered call: **both, and the price was set on a residual.**

## Start here
| If you want | Open |
|---|---|
| the story on paper | `dp_uc62_walker_phillies_career_recap_report.pdf` (8 pages) |
| the story, interactive | `dp_uc62_walker_phillies_career_dashboard.html` or the Artifact "Taijuan Walker, Phillie" |
| what the organization decided and why | `00_dpo_orchestration_record.md` |
| the bid, and how it went | `BID_2026-11-05_uc-pps-038-walker-phillies-career-recap.md` → `07` §5 |
| the receipts | MLB `out/dp_uc62_*` (38); key copies in `data/`, figures in `figures/` |

## Package contents
```
00_dpo_orchestration_record.md   framing, gates, capability table, arguments, escalations, conditions
01_strategy_intake.md            ID reservation, gaps, source profile, carry-ins, glossary
02_engineering_design.md         data model, joins, EDA, metadata map, dashboard spec
03_governance.md                 Rule-1 search, lineage, KR-1/CE-1/PR-1 specs, defects, privacy, version
04_engineering_build.md          manifest + shas, environment, run order, assertions, receipts
05_quality_certification.md      DQ 15/0/0, harness 47/47, visual audit, catches, certification
06_consumer_success.md           forms, reading paths, personas, KR-1 snippet, FAQ, catalog entry
07_platform_marketing.md         version, privacy, tripwires, cost, bid vs actual, corrections, marketing line
BID_2026-11-05_uc-pps-038-walker-phillies-career-recap.md
intake/client_prompt_2026-11-05.md
uc-pps-038-Taijuan Walker Phillies Career Recap 20261105.md   contract (copy; original at MLB root)
uc_ledger_AI_PATCH_uc-pps-038-walker-phillies-career-recap.md PENDING PASTE (copy at MLB root)
dp_uc62_walker_phillies_career_recap_report.md / .pdf · dp_uc62_walker_phillies_career_dashboard.html
data/ (14 key receipts) · figures/ (F1–F9 PNG)
```
Code lives in the MLB data plane root: `dp_uc62_kernel.py`, `_walker_recap.py`, `_hp.py`, `_narrative.py`, `_build_figs.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py`. EDA at MLB `eda/dp_uc62/`.

## Re-run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc62_walker_recap.py && python dp_uc62_hp.py && python dp_uc62_build_figs.py && python dp_uc62_build_report.py && python dp_uc62_build_pdf.py && python dp_uc62_verification.py && python dp_uc62_build_dashboard.py
```

## Open items for the DPO
Ratify KR-1 / CE-1 / PR-1 · O-26 pitcher-id loader · EV-1 `ev_mu` footnote · ENV-3 `TMPDIR` in MLB `CLAUDE.md` · ledger paste UC52–UC62 · external publish review (cost chapter).
