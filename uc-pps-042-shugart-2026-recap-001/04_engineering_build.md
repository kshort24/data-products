# 04 · Engineering Build
Agents: `data-engineer`

## 1 · Manifest (MLB root)
| File | Role |
|---|---|
| `dp_uc66_kernel.py` | governed kernel (imports K64, pinned) |
| `dp_uc66_shugart_recap.py` | T1 build: every published number → `out/dp_uc66_*` |
| `dp_uc66_hp.py` | grades HP-01…HP-12 from receipts |
| `dp_uc66_build_figs.py` | F1–F9, F4a/F4b, S1 + V1–V7 audit + VZ-5 contrast; one figure per process |
| `dp_uc66_build_report.py` / `_build_pdf.py` | report `.md` → `.pdf` (weasyprint, 11 pp, section + NaN guards) |
| `dp_uc66_build_dashboard.py` | dashboard `.html` (CDN plotly via `phillies_dp.render`; Pitch × Hand Explorer) |
| `dp_uc66_verification.py` | independent harness (raw parquet + constants CSV; no kernel KPI import) |
| `uc-pps-042-Chase Shugart 2026 Recap 20261120.md` | use-case contract |

## 2 · Re-run
```bash
# Kellen's machine (conda env snakes):  python <script>
# Device VM (RN-3: session disk full, stack in /tmp/pylib):  PYTHONPATH=/tmp/pylib python3 <script>
python dp_uc66_shugart_recap.py           # receipts + headlines
python dp_uc66_hp.py                      # HP grades
for f in f1 f2 f3 f4a f4b f5 f6 f7 f8 f9 s1; do python dp_uc66_build_figs.py $f; done   # RN-1: one figure per process
python dp_uc66_build_report.py && python dp_uc66_build_pdf.py
python dp_uc66_build_dashboard.py
python dp_uc66_verification.py            # exits 1 on any FAIL
```

## 3 · Receipts (`out/dp_uc66_*`, 64 files)
Tables: `overall`, `fr1_frames`, `by_stand`, `stand_pitch`, `pitch_map_mix`, `arsenal`, `pitches`, `context_percentiles`, `cs_a_rhp_relief_seasons`,
`cs_b_bullpen_2026`, `cs_b_role_lc1`, `platoon_pool`, `platoon_cells`, `shape_pool_cs_a`, `cs_c_pitch_stand`, `cs_c_subject_ranks`, `in1_inner_third`,
`k_by_pitch`, `months`, `usage_by_month`, `cu1_cumulative_usage`, `cw1_cumulative_woba`, `outing_ledger`, `s1_stints`, `f4b_bins`, `hp_grades`,
`dq_scorecard`, `freshness_manifest`, `verification`, `headlines.json`, `build_log.txt`. Figures: 11 × (`.png` scale 2, `.json` spec, `visual_audit_*.json`).

## 4 · Build notes
- **RN-3** device VM `/sessions` at 100%: `pip install -r requirements-render.txt` failed (ENOSPC). Pinned stack (plotly 6.0.1, kaleido 0.2.1, pandas 2.2.3, weasyprint 70.0, pyarrow) installed with `--target /tmp/pylib`, `TMPDIR` and `PIP_NO_CACHE_DIR` on `/tmp`.
- **RN-4** `device_commit_files` reusing a staged path delivered a stale copy twice; fixed by committing from a fresh staged filename and verifying md5 on the device before every run.
- **RN-1** (inherited) kaleido 0.2.1 renders once per process → one figure per invocation. Heatmaps drawn as square markers (RN-2).
- Fixes during build: fpsr column name (`First Pitch Strike Rate`), V6 axis titles (F1 labels moved to margin annotations; shared-axis titles), F6 IQR band drawn as a filled trace (hrect did not render on the subplot), two report tables needing a blank line before them.
