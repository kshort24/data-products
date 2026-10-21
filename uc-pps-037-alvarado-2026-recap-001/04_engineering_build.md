# 04 · Engineering Build: `uc-pps-037`

Agent: `data-engineer`

## 1 · Build manifest (control-plane folder; kernels imported from the MLB root by path)
| File | Role | Runs on |
|---|---|---|
| `dp_uc53_kernel.py` | governed kernel: imports `dp_uc52_kernel.py` (sha256 `3667f802…`) and `cumulative_metric.py` (`a2888740…`); sections A inherited · B generalized (CF-2d, RP-1t) · C new/provisional (OD-1, DB-1, CM-1a spec) | laptop VM |
| `dp_uc53_alvarado_recap.py` | the build: data plane → `out/dp_uc53_*` receipts + `headlines.json` + DQ scorecard | laptop VM |
| `dp_uc53_hp.py` | HP family on the client's frame → `hp_grades.csv`, `headlines.json["hp"]` | laptop VM |
| `dp_uc53_build_figs.py` | 10 figures, PNG + JSON; asserts each subtitle claim; brand + palette checks | laptop VM (kaleido 0.2.1) |
| `dp_uc53_narrative.py` | single sentence source for report and dashboard | laptop VM |
| `dp_uc53_build_dashboard.py` | dashboard (repo copy + Artifact body variant); shell carried from UC52 | laptop VM |
| `dp_uc53_build_report.py` · `dp_uc53_build_pdf.py` | markdown report → weasyprint PDF (RQ-2 section guard, RQ-3 pipe guard, 10-page cap) | laptop VM |
| `dp_uc53_verification.py` | independent, definition-first harness | laptop VM |

## 2 · Environment disclosure
- **Laptop VM:** Python 3.10.12; render stack installed with `pip --target /tmp/pyrender -r requirements-render.txt`. It holds plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pandas 2.2.3, numpy 2.2.5, pyarrow 24.0.0, scipy 1.15.2 and markdown 3.8. `/tmp` installs vanish on a VM restart.
- **ENV-3 (new):** `/sessions` is 100% full (6.5 MB free). pip's temp dir defaults there, so the first install failed with ENOSPC. Fix: `export TMPDIR=/tmp/uc53/tmp`. Background installs die with their sandbox, so run pip in the foreground in ≤175 s chunks.
- **Cloud sandbox:** render QA only (Playwright/Chromium screenshots, `pdftoppm`), on staged copies. jsDelivr is blocked there, so QA served the identical plotly.js from the pinned plotly 6.0.1 wheel via route interception.
- **Run with:** `TMPDIR=/tmp/uc53/tmp PYTHONPATH=/tmp/pyrender:<MLB root> MLB_DATA_ROOT=<MLB root> PYTHONDONTWRITEBYTECODE=1`.

## 3 · Build-time assertions (the build fails rather than publish)
| Assertion | Where |
|---|---|
| UC52 kernel + `cumulative_metric.py` sha256 match the pins (and UC52's own chain) | kernel `assert_lineage` |
| house log max ≤ anchor 2026-10-01 | kernel `load_house` |
| no pre-2021 pitching-role rows for 621237 (ENT-1) | build §frames |
| tenure frame == house log pitch counts by year | build §frames |
| first / last 2026 appearance == 2026-03-28 / 2026-09-26 | build §frames |
| CM-1a endpoints == WB-1 by season | build §cumulative (`reconcile=`) |
| client name filter selects only 621237 | `hp.py` |
| DQ scorecard has 0 FAIL | build §DQ |
| each figure's subtitle claim (e.g. F9: 2026 above every prior season at > 50% of PAs; observed 75%) | `build_figs` before each `ship` |
| brand checks (Arial, title, subtitle, axis titles, palette) | `build_figs.ship` |
| every referenced figure exists; every section survives rendering; ≤ 10 pages | `build_pdf` |
| ≤ 9 report sections | `build_report` |

## 4 · Receipts (`out/`)
45 files:
- 22 CSV
- 12 JSON: 10 figures + `headlines.json` + `figure_specs.json`
- 10 PNG
- 1 TXT (palette validation)

Key receipts: `headlines.json`, `dq_scorecard.csv`, `verification_log.csv`, `hp_grades.csv`, `db1_ledger.csv`, `appearance_log.csv`, `house_pa_leaderboard.csv`, `brand_checks.csv`. EDA: MLB `eda/dp_uc53/` (2 reports).

## 5 · Reuse
- **Any reliever recap:** change the kernel's subject block (id, file, name, dates). CF-2d, OD-1, DB-1 and the narrative shell carry over.
- **Bullpen board:** one call of `outing_bands(game_score(...))` over `house_pitcher_seasons` ranks every Phillies reliever on clean-outing rate.
- **DB-1 on another arm:** reuse the eight bars exactly, or register new ones in `03` before reading data.
