# uc-pos-013 — Alec Bohm: The Second-Half Turnaround, Audited

**UC #38 · `uc-pos-013-bohm-second-half-turnaround-001` · `dp_uc37` · delivered 2026-08-24**
<br>Value stream: Phillies Offense (`pos`) · Data window 2015 → **2026-08-22** · Verification **227/227 PASS**

## Deliverables
| File | What |
|---|---|
| `dp_uc37_bohm_turnaround_report.pdf` | 7-page governed report (house Phillies CSS) |
| `dp_uc37_bohm_turnaround_dashboard.html` | self-contained interactive dashboard — **no network required** |
| `dp_uc37_bohm_turnaround_report.md` | report source |

## Governance receipts
`00_dpo_orchestration_record.md` · `01_strategy_intake.md` · `02_engineering_design.md` ·
`03_governance.md` · `04_engineering_build.md` · `05_quality_certification.md` ·
`06_consumer_success.md` · `07_platform_marketing.md`

## Code
`dp_uc37_kernel.py` (loader + governed KPI kernel) · `dp_uc37_bohm_turnaround.py` (build) ·
`dp_uc37_verification.py` (independent, 227 assertions) · `dp_uc37_build_pdf.py` ·
`dp_uc37_build_dashboard.py` · `_chartjs_4.4.1.umd.js` (vendored, MIT)

## Receipts
14 CSV receipts + `dp_uc37_headlines.json` + `dp_uc37_fig1..6_*.png`

## Headline

**The turnaround is real, process-backed, and boundary-robust — but it is not the story the eye
test suggests.** SLG **.351 → .488**, BA w/ RISP .299 → .462 (42 PA ⚠), runs created per PA
.130 → .207 across the All-Star break, and the 10-point breakpoint scan never finds a negative
delta. Behind it: hard-hit 40.8% → 46.9%, mean EV +1.6 mph, xwOBAcon .313 → .404, and **in-zone
whiff cut nearly in half** (12.0% → 6.8% — ~2nd percentile of 218 Phillies hitter-seasons since
2015). "Rarely whiffs" doesn't just verify; post-break Bohm is the best contact profile in the
Statcast-era Phillies pool.

**What did NOT move:** the approach (chase .257 → .254, first-pitch swing flat) and **pull-air
volume** (10.8% → 10.6%, 14th percentile) — the DPO's pet metric is flat on volume, but its
*quality* spiked (12 post-break pull-airs at 97.7 mph with 3 HR). The breaking-ball fix is the real
mechanism headline: .152/.239 → .340/.460 with whiff on spin 23.4% → 14.3%. The platoon mix did not
flatter him (PL-1 mix effect **−18 wOBA points**); the loudest cell (.812 SLG vs LHP) is 33 PA and
flagged everywhere. Causation for the §5 persona hypotheses is explicitly not identified — the
cleanest candidate is interactive: pitchers moved into the zone (.492 → .539) against a hitter whose
in-zone contact was peaking.

**Governance firsts:** O-7 remediated — `pull_air_rate` executes against the governed schema for the
first time (hc→loc derivation per the cbp-spray convention, boundary logic verbatim, scale-invariance
proven; provisional). O-11 opened: value-stream vs data-domain separation formalized from the DPO's
own `dd = vs` design note.
