# uc-pos-012-nola-alcantara-showdown-001 · dp_uc35

**If Aaron Nola against the Marlins were a Phillies hitter — the Nola–Alcantara showdown.**
UC #36 · Phillies Offense value stream · delivered 2026-08-19 (pre-game) · data through 2026-08-17
· verification **79/79 PASS**.

Nola (PHI) vs Alcantara (MIA), Citizens Bank Park, Wed 2026-08-19 6:05 PM ET — the rematch of the
7/28 duel (MIA 1–0).

## Read this first

| File | What it is |
|---|---|
| `dp_uc35_nola_alcantara_report.pdf` | The read — premises adjudicated up front (P1–P5), 5 figures, house voice |
| `dp_uc35_nola_alcantara_dashboard.html` | Self-contained interactive dashboard (vendored Chart.js, works offline) |
| `00_dpo_orchestration_record.md` | DPO spine: decision log (HD-1 floor ruling), gates, verdicts, publish recommendation |

## Governance trail

`01_strategy_intake.md` (validator GO + 5 conditions, profiler, steward rulings) ·
`02_engineering_design.md` (model, KF-1/SB-1 specs, join validation) ·
`03_governance.md` (glossary, deviation register DV-1..3, tags, privacy, DQ rules) ·
`04_engineering_build.md` (pipeline, column-level lineage, build notes) ·
`05_quality_certification.md` (79/79 verification map, DQ scorecard, CERTIFY-READY) ·
`06_consumer_success.md` (persona guides, query patterns, FAQ) ·
`07_platform_marketing.md` (monitoring, backtest trigger, versioning, follow-ups)

## Code & receipts

`dp_uc35_kernel.py` (governed KPI kernel; D1/D2 `_fix`; `runs_created` verbatim) ·
`dp_uc35_nola_alcantara.py` (build → 24 CSV receipts + headlines.json) ·
`dp_uc35_build_figures.py` / `_build_pdf.py` / `_build_dashboard.py` ·
`dp_uc35_verification.py` (independent, raw-parquet recomputation) ·
`out/` (all receipts + fig1–fig5 PNG) · `_chartjs_4.4.1.umd.js` (vendored, MIT).

Runs on the DPO's machine as-is; set `DP_UC35_DATA` to point elsewhere.

## Headline numbers (all receipt-backed)

- **Noles** (what Nola makes of Miami, career): .239/.278/.381 · wOBA .288 · 26.3% K · **0.090 RC/PA** · 696 PA / 28 G
- **Wheeler vs MIA** (2017–26): wOBA .280 · 0.084 RC/PA · 593 PA
- **Harper vs MIA**: .282/.380/.522 · wOBA .389 · 0.150 RC/PA · 401 PA — above the Noles constant in 7 of 8 seasons
- **Alcantara vs PHI**: #2 exposure of the era (2,278 pitches; Scherzer 3,137) · career .303 wOBA allowed · 2026: .226 / 55 PA
- **Harper vs Alcantara** (his #1 most-faced in-frame): .319/.389/.574 · wOBA .409 · 64.9% HH · 54 PA

Ledger: claims **UC #36 / uc-pos-012 / dp_uc35**; next free **UC #37 / dp_uc36** (pps next uc-pps-026 — flagged in the Week Ahead as the Nola candidate; pos next uc-pos-013). Patch file: `uc_ledger_AI_PATCH_uc-pos-012-nola-alcantara.md`.
