# `uc-pos-014-turner-2026-recency-001` · UC #40 · `dp_uc40`

**Trea Turner — the 2026 season, and the six weeks since the last product on him shipped.**
Phillies Offense (`pos`) value stream · delivered 2026-09-03 · data as of **2026-09-02**
**v1.1.0** (bat-path addendum, 2026-09-03) · **Verification 711/711 + 180/180 PASS · conventions 12/12 ·
DQ 22/3/0 (v1.0.0) + 10/3/0 (addendum) · Certification READY**

Extends **`uc-pos-006-turner-2026-offense-001` / `dp_uc24`** (2026-07-21). All **84** of that product's
published figures were reproduced exactly, on its own window and its own definitions, before a single new
claim was made.

---

## Start here

| If you want… | Open |
|---|---|
| The answer | `dp_uc40_turner_recency_report.pdf` (13 pp) — §1 is a verdict table, before any explanation |
| **How** he is meeting the ball (**v1.1.0**) | `dp_uc40a_bat_path_report.pdf` — the bat-path addendum |
| What the bat-path columns mean (**v1.1.0**) | `03a_bat_path_semantics_and_lineage.md` — sourced definitions, 12 proven conventions, dictionary, specs, lineage |
| To explore it yourself | `dp_uc40_turner_recency_dashboard.html` — self-contained, no network, 6 tabs |
| The one-paragraph finding and the escalations | `00_dpo_orchestration_record.md` §5 and §7 |
| To reuse the code | `dp_uc40_kernel.py` — but read `05` §5.3 (defect register) first |
| To check a number | `out/dp_uc40_*.csv` (27 receipts) and `out/dp_uc40_verification_results.csv` |
| What it cost, and what it was bid at | `BID_2026-09-03_uc-pos-014-turner.md` and `telemetry/` |

## The finding

The lowest of his **eleven qualified seasons** on BA, OBP, SLG, OPS, ISO, wOBA and BABIP — and the six
weeks since 1 August are the worst stretch of it (.207/.279/.276, one home run in 129 PA). The parent
product's open call — *"July .980 OPS / 62 PA, real-but-young"* — **resolved against the optimistic
reading**: rolling form peaked at **.421 on 2026-07-21**, the day `uc-pos-006` was delivered, and now
reads **.238**. The breakpoint scan flips sign on exactly that date.

The mechanism is **contact point, not bat speed**: popup rate **15.2% of balls in play vs a 5.0% Phillies
norm (z = 4.12)** — the only measure in the product that clearly clears sampling noise — with launch angle
up and exit velocity down, while his strikeout and walk rates are the best of his season.

## v1.1.0 — the bat-path addendum

Statcast's bat-path columns describe the *swing*; v1.0.0 could only describe the *outcome*. The addendum
defines all six columns for the data plane (none had a governed definition), proves their conventions
against the data, and finds that **two things changed and both clear the noise bar**: his swing plane
flattened **27.9° → 25.5°** — peer-netted −1.20°, the largest drop in the cohort, and the **flattest of
all 11 Phillies** with 200+ tracked swings against an MLB average of ~32° — and his contact point moved
**1.35″ further from his body**. Popup rate on **breaking balls went 3.9% → 12.1%** while fastball and
offspeed sat still; he moved from **rank 6 of 12 (the peer median) to rank 1 of 10**.

**Still not bat speed** (+0.49 mph peer-netted). v1.0.0 ruled it out from the outcome side; the path data
rules it out from the input side.

**Four new open items — O-15 is the one that leaves this product:** `attack_direction` is **pull-negative**
here, the inverse of the published MLB glossary convention. See `03a` §3.

## Package contents

```
00_dpo_orchestration_record.md    delivery spine, gate checks, capability fulfilment, escalations
01_strategy_intake.md             8 questions, 3 premises, gap report, DPO's declared discretion
02_engineering_design.md          source profile, data model, join validation, EDA-forced changes
03_governance.md                  Rule-1 grep, KPI specs (AD-1, ST-1, RF-2, BT-1), lineage, privacy
04_engineering_build.md           what was built, build-time assertions, environment notes
05_quality_certification.md       711-check design, DQ scorecard, defect register, certification
06_consumer_success.md            persona onboarding, query patterns, dashboard spec
07_platform_marketing.md          monitors, 6 tripwires, cost audit, bid-vs-actual, release note
BID_2026-09-03_uc-pos-014-turner.md   the competitive bid, retained as the pricing receipt
telemetry/                        run_economics_ledger.csv + calibration_report.md

dp_uc40_kernel.py                 loader + governed KPI kernel (~85% inherited from dp_uc37)
dp_uc40_turner_recency.py         the build → out/
dp_uc40_verification.py           independent harness, 711 checks
dp_uc40_build_pdf.py              markdown → PDF (house Phillies CSS)
dp_uc40_build_dashboard.py        receipts → one self-contained HTML file
_chartjs_4.4.1.umd.js             vendored charting library (MIT) — never a CDN

dp_uc40_turner_recency_report.md / .pdf
dp_uc40_turner_recency_dashboard.html
out/                              27 CSV receipts + 6 figures + headlines.json + build console log
uc_ledger_AI_PATCH_uc-pos-014-turner.md    ledger row, pending paste into the MLB repo

── v1.1.0 bat-path addendum ───────────────────────────────────────────────
ADDENDUM_v1.1.0_bat_path.md              the addendum spine — ask, gates, package delta
03a_bat_path_semantics_and_lineage.md    sourced semantics · 12 proven conventions · dictionary ·
                                         KPI specs (BP-0/1/2, PU-1/2, PB-1) · column-level lineage
05a_bat_path_certification.md            180-check design · DQ · O-15..O-18 · versioning · E-8..E-12
dp_uc40a_kernel.py                       bat-path kernel; imports dp_uc40_kernel unchanged
dp_uc40a_bat_path.py                     the addendum build
dp_uc40a_verification.py                 180 independent checks
dp_uc40a_bat_path_report.md / .pdf       the consumable
out/dp_uc40a_*.csv                       17 receipts + headlines + console log
out/dp_uc40a_fig1..4.png                 4 figures
```

## Reproducing it

```bash
DP_UC40_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB" python dp_uc40_turner_recency.py
DP_UC40_DATA="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB" python dp_uc40_verification.py
python dp_uc40_build_dashboard.py     # reads out/ only
python dp_uc40_build_pdf.py           # needs weasyprint (cloud container, not the device VM)
```

## What this product does **not** claim

- **No causation.** There is no coaching, medical, or intervention log in this data plane. The persona
  section is testable hypotheses mapped to remit, and says so before the table.
- **No lineup-slot analysis.** Batting order is not a column here.
- **No swing-measurable comparison to his 2020–21 peak.** Bat tracking begins in 2024 and exists only in
  the Phillies frames — a sensor boundary, left NULL and never imputed.
- **Nothing ranked below the 50-PA floor.** March (23 PA) and September (9 PA) carry ⚠ everywhere.

## Reproducing the addendum

```bash
DP_UC40_DATA="<MLB repo>" python dp_uc40a_bat_path.py      # build   → out/dp_uc40a_*
DP_UC40_DATA="<MLB repo>" python dp_uc40a_verification.py  # verify  → 180/180
```

## One new defect, disclosed not patched

**D-7 / O-13** — the governed `chase_rate_g` derives `in_zone_rate` by subtraction, so NULL-`zone` rows
are silently counted as in-zone pitches. Found by this build's own verification harness. Exposure here:
.4719 published vs **.4710** corrected at 2026 season grain, .4528 vs **.4482** in the recent window.
`in_zone_rate_fix` ships beside the governed original, which is untouched. **This affects every prior UC
that published `in_zone_rate`** — see `05` and escalation E-1.
