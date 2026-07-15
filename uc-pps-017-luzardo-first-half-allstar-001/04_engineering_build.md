# 04 — Engineering Build · uc-pps-017 (UC #19)

**Script:** `dp_uc17_luzardo_first_half.py` (this folder). Run live 2026-07-13 against the mounted parquet layer (`MLB_DATA_ROOT` → `data/phillies`). Portable data-root candidates (env var → relative → absolute) per house convention.

## Receipts written (NEW files, `MLB/out/`)

| File | Feeds report |
|---|---|
| `dp_uc17_luzardo_season_line.csv` | §1 results table (incl. PD-1/2/3) |
| `dp_uc17_luzardo_season_xwoba.csv` | §1 xwOBA row (supplemental, added at certification review) |
| `dp_uc17_luzardo_start_log_2026.csv` | §1 start-by-start, fig 2 |
| `dp_uc17_staff_benchmark_2026.csv` | §1 staff context |
| `dp_uc17_luzardo_arsenal_yoy.csv` | §3, fig 1 |
| `dp_uc17_luzardo_process_kpis_yoy.csv` | §4 |
| `dp_uc17_luzardo_by_stand_yoy.csv` | §5 stands (incl. xwOBA by stand) |
| `dp_uc17_luzardo_tto_yoy.csv` | §5 TTO, fig 3 |
| `dp_uc17_luzardo_battery_2026.csv` | §5 battery |
| `dp_uc17_luzardo_monthly_2026.csv` | §2 |
| `dp_uc17_luzardo_count_leverage_yoy.csv` | §4 |
| `dp_uc17_dq_scorecard.csv` | 05 |
| `dp_uc17_freshness_manifest.csv` | 05 / report warning box |
| `dp_uc17_fig1_arsenal_shift.png` `_fig2_start_trend.png` `_fig3_tto_leash.png` | figures (copies embedded in package) |

## Build notes

- Two in-session revisions before receipts were finalized: (1) stand table extended with xwOBA (results-vs-process check demanded it); (2) season-level xwOBA written as a supplemental receipt — season line lacked it because locked `nresults` intentionally drops the column. Both are additive; no locked mechanics touched.
- OneDrive sync briefly served a truncated script copy to the build sandbox; run repeated from a verified full copy. No impact on receipts (all writes precede the truncation point; final run exit 0).
- No repo file overwritten. `machine-learning-engineer` not engaged — no forecasting requirement in this UC.
