# uc-pos-010 — Bryson Stott Approach Change

**UC #34 · `uc-pos-010-stott-approach-change-001` · `dp_uc33` · delivered 2026-08-15**
<br>Value stream: Phillies Offense (`pos`) · Data window 2015 → **2026-08-13** · Verification **86/86 PASS**

## Deliverables
| File | What |
|---|---|
| `dp_uc33_stott_approach_change_report.pdf` | 8-page governed report (house Phillies CSS) |
| `dp_uc33_stott_approach_change_dashboard.html` | self-contained interactive dashboard |
| `dp_uc33_stott_approach_change_report.md` | report source |

## Governance receipts
`00_dpo_orchestration_record.md` · `01_strategy_intake.md` · `02_engineering_design.md` ·
`03_governance.md` · `04_engineering_build.md` · `05_quality_certification.md` ·
`06_consumer_success.md` · `07_platform_marketing.md`

## Code
`dp_uc33_kernel.py` (loader + KPI kernel) · `dp_uc33_verification.py` (independent, 86 assertions)

## Receipts
`dp_uc33_monthly_master.csv` (46 cols) · `dp_uc33_monthly_panel.csv` · `dp_uc33_context_pool.csv`
(217 hitter-seasons) · `dp_uc33_rolling_woba.csv` · `dp_uc33_streak_games.csv` ·
`dp_uc33_headlines.json` · `dp_uc33_fig1..5_*.png`

## Headline
The approach change is **real and measurable** — chase 33.8% → 21.5%, first-pitch swing 24.0% → 7.1%.
It is **not the whole story**: first-pitch strike rate against Stott fell 67.1% → 41.1% over the same
window. Both moved; causation is not identified. The video's "14 walks between strikeouts" claim
**verifies exactly** (11 games, 46 PA, Jul 29 → Aug 9). The stated 3:2 OBP:K is **understated** — his
career figure is 1.85:1, 83rd percentile among 217 Phillies hitter-seasons since 2015.

**Three defects found in the governed kernel** (`whiff_rate`, `hard_hit_rate`, `fpsr` silently drop
zero-numerator groups) — reported in `05`, not patched. See `00` for the 6 open items.
