# 04 · Engineering Build
Agent: `data-engineer`

## 1 · Manifest (MLB data plane root; code lives in the data plane per the RFP)
| File | Role | sha256 (16) |
|---|---|---|
| `dp_uc67_kernel.py` | governed kernel (A imports, B generalizations + TP-1, C new) | `a9c3a3da45cb5f72` |
| `dp_uc67_bohm_recap.py` | T1 build: every published number → `out/dp_uc67_*` + DQ | `b776a84fe7d86ec3` |
| `dp_uc67_hp.py` | HP-01..HP-09 grades from receipts | `5efb41d80340a65b` |
| `dp_uc67_build_figs.py` | F1–F8 PNG + JSON, V1–V7 audit | `cfff007ace36d58e` |
| `dp_uc67_narrative.py` | single narrative source (report and dashboard) | `8acef5ffe8c49dd0` |
| `dp_uc67_build_report.py` · `dp_uc67_build_pdf.py` | markdown report → PDF (weasyprint, RQ-2 guard, page cap 12) | `83a9a54716584f43` · `84be5e4ea1fb5996` |
| `dp_uc67_build_dashboard.py` | dashboard (UC62 shell CSS read from `dp_uc62_build_dashboard.py`, not copied) | `6910fe48e86705a8` |
| `dp_uc67_verification.py` | independent harness (51 checks; raw parquet + pandas, no kernel import) | `7e10890415b44127` |
| `dp_uc67_pins.json` | frozen lineage pins (4 + K61's 23) | `3fdec5bae755b452` |

## 2 · Environment
Laptop VM via the device shell. Python 3.10.12; render stack from `requirements-render.txt` into `/tmp/pyrender` (plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pyarrow 24.0.0, pandas 2.2.3, numpy 2.2.5, scipy 1.15.2, markdown 3.8). `TMPDIR=/tmp/uc67/tmp` (**ENV-3, 4th recurrence**: `/sessions` at 100%). Headless dashboard QA in the cloud workspace (Chrome + Playwright) on a throwaway copy with plotly.js swapped from the CDN tag to the pinned wheel's bundle (CDN host not reachable from the workspace); the shipped file keeps the CDN tag.

## 3 · Run order
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc67_bohm_recap.py        # asserts lineage, entity, regular season, anchor; DQ 11/0/0
python dp_uc67_hp.py                # HP-01..HP-09
python dp_uc67_build_figs.py        # F1–F8; V1–V7 asserted per figure
python dp_uc67_build_dashboard.py   # needs the harness csv for its chip, so run again at the end
python dp_uc67_build_report.py && python dp_uc67_build_pdf.py   # 7 pages
python dp_uc67_verification.py      # 51/51 expected; exit 1 on any FAIL
python dp_uc67_build_report.py && python dp_uc67_build_pdf.py && python dp_uc67_build_dashboard.py   # stamp the harness count
```

## 4 · Build-time assertions
Lineage (4 frozen + 23) · entity lock + EN-2 · anchor · RHB spray convention (pulled grounders on the LF side) · GW-1 one per win · V1–V7 per figure · PDF: every figure exists, every `##` heading survives (RQ-2), page cap · dashboard: plotly by the pinned CDN tag, not inlined.

## 5 · Receipts (`out/dp_uc67_*`, 43 files)
CSV: season_panel, windows_2026, monthly_2026, platoon_by_year, platoon_era, rhp_breaking_by_year, rhp_breaking_era, hand_group_by_year, battedball_era, hitter_pool_kp1, ld_spray, ld_by_year, direction_by_year, game_table, gw1_bohm_log, gw1_by_year_all, phillies_leaderboard_2020_26, pr1_ledger, hp_grades, hp09_parent_career_pa, dq_scorecard, visual_audit, verification. JSON: headlines, g_ld_fit, field_outline, figure_specs, F1–F8. PNG: F1–F8. Key copies in this folder's `data/` and `figures/`.

## 6 · Reuse
Inherited by import: 20+ functions (`03` §0). Written new: GW-1 (3 functions: `game_table`, `pa_table`, `deciding_pa`) + the client-cell reproduction, XC-1, `ols`, `score_pr1`, TP-1 (5 lines). The PDF builder is carried from UC62 (sed of names, CSS unchanged); the dashboard reads UC62's CSS at build time.
