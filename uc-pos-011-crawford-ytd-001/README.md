# uc-pos-011 — Justin Crawford Year-to-Date Read

**UC #35 · `uc-pos-011-crawford-ytd-001` · `dp_uc34` · delivered 2026-08-15**
<br>Value stream: Phillies Offense (`pos`) · Data window 2015 → **2026-08-13** · Verification **127/127 PASS**

## Deliverables
| File | What |
|---|---|
| `dp_uc34_crawford_ytd_report.pdf` | 10-page governed report (house Phillies CSS) |
| `dp_uc34_crawford_ytd_dashboard.html` | self-contained interactive dashboard — **no network required** |
| `dp_uc34_crawford_ytd_report.md` | report source |

## Governance receipts
`00_dpo_orchestration_record.md` · `01_strategy_intake.md` · `02_engineering_design.md` ·
`03_governance.md` · `04_engineering_build.md` · `05_quality_certification.md` ·
`06_consumer_success.md` · `07_platform_marketing.md`

## Code
`dp_uc34_kernel.py` (loader + KPI kernel) · `dp_uc34_crawford_ytd.py` (build) ·
`dp_uc34_verification.py` (independent, 127 assertions) · `dp_uc34_build_pdf.py` ·
`dp_uc34_build_dashboard.py` · `_chartjs_4.4.1.umd.js` (vendored, MIT)

## Receipts
17 CSV receipts + `dp_uc34_headlines.json` + `dp_uc34_fig1..6_*.png`

## Headline

**The premise holds directionally; the mechanism does not match it.** Results improved after 15 June —
wOBA .276 → .321, BA .231 → .312, OBP .289 → .345. But the on-base gain is **entirely batting average**
(walk rate *fell* 6.6% → 4.6%), power *fell* (ISO .097 → .072, zero HR after 15 June), and the two
developmental red flags **did not move**: mean launch angle 2.28° → 2.22° (**2nd percentile** among 217
Phillies hitter-seasons since 2015), ground-ball rate 58.9% → 53.3% (89th percentile).

The durable gain is **contact** — strikeout rate 20.9% → 15.2%, whiff rate 20.5% → 15.9%. Everything
above that is a **79-point BABIP swing on ground balls he is hitting 4.4 mph softer than before**.

**The Derek Hill platoon hypothesis is falsified as posed** — LHP share is 15.0% after his 13 June
debut versus 15.3% before, and direct standardisation puts the mix effect below 0.0002 on every
metric. **The shielding is real but starts in August** (1 of 42 PA), which makes the strongest month
also the least readable — and it is 42 PA, **below the 50-PA floor**.

Against the eight Phillies centre-field seasons of the Statcast era, at matched volume he ranks
**7th of 8 in wOBA and 4th of 8 in OBP**.

**Six defects in the governed KPI kernel** — D1–D4 inherited, **D5's diagnosis corrected**
(`pull_air_rate` reads `loc_x`/`loc_y`, which are not columns in the schema — **O-7**) and **D6 new**
(`hard_hit_rate` scores an untracked ball in play as "not hard hit" — **O-8**). Reported in `05`,
not patched.
