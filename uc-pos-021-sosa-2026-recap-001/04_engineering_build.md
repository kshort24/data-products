# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## 1 · Manifest (control plane, this folder, per the RFP)
| File | Role |
|---|---|
| `dp_uc56_kernel.py` | 16 sha256 pins (K55, K46, `barrel_rate.py` + 14 through K55); EV-1, pull-air wrapper, OZ-1, WA-1, WB-2 wrapper, schedule-gap ASB, client frame |
| `dp_uc56_sosa_recap.py` | build: 33 CSV receipts, `headlines.json`, DQ scorecard (17 rules), EDA to `eda/dp_uc56/` |
| `dp_uc56_hp.py` | the client's frame and functions → HP-01…HP-11 |
| `dp_uc56_build_figs.py` | 9 figures (PNG + JSON); claim + brand assertion per figure; UC55 shell carried |
| `dp_uc56_narrative.py` | every sentence, formatted from `headlines.json` |
| `dp_uc56_build_report.py` · `dp_uc56_build_pdf.py` | markdown (RQ-3 pipe guard) → 8-page PDF (section-loss guard, page cap 8) |
| `dp_uc56_build_dashboard.py` | 8-chapter dashboard + Artifact body variant |
| `dp_uc56_verification.py` | independent harness, 161 checks, families A–N |
| `out/dp_uc56_*` | 58 receipts: 37 CSV (incl. HP, harness log), 11 JSON (9 figures, headlines, figure specs), 10 PNG (9 figures + PDF QA contact sheet) |
| `eda/dp_uc56/` | 2 EDA reports |

## 2 · Environment
- Laptop VM: Python 3.10.12. `/sessions` 100% (ENV-3) → `pip install --target /tmp/pyrender -r requirements-render.txt` with `TMPDIR=/tmp/uc56/tmp` as the first T0 step (MLB `CLAUDE.md`).
- Pinned stack: plotly 6.0.1 · pandas 2.2.3 · weasyprint 70.0 · kaleido 0.2.1 · pyarrow 24.0.0 · scipy 1.15.2 · numpy 2.2.5 · markdown 3.8. `phillies_dp.selftest` 3/3.
- Dashboard QA in the cloud workspace (Playwright Chromium; plotly inlined for the screenshot only; Google Fonts blocked there): desktop, phone 390 px (no horizontal scroll: scrollWidth 390), dark; 27/27 plot SVGs rendered.

## 3 · Build-time assertions (a failure halts)
Lineage (16 pins) · anchor ≤ 2026-10-01 · EN-2 on the subject · seasons exactly 2022–26 · name ↔ id 1:1 · stand R · K46 spray convention (inside `build_bip`) · CM-1 endpoints == house line (tol 1e-9) · All-Star gap ≥ 3 days · every figure asserts its subtitle's claim · dashboard has 9 sections and 9 figures · PDF ≤ 8 pages, no section lost.

## 4 · Run order and timings (laptop VM)
```bash
cd "<MLB root>"     # the kernel finds MLB via MLB_DATA_ROOT, ~/mnt/MLB, or Documents/Python Scripts/MLB
export TMPDIR=/tmp/uc56/tmp; pip install --target /tmp/pyrender -r requirements-render.txt
export PYTHONPATH=/tmp/pyrender:"<MLB root>" PYTHONDONTWRITEBYTECODE=1
P="<Agents for Data Products>/data-products/uc-pos-021-sosa-2026-recap-001"
python "$P/dp_uc56_sosa_recap.py"      # ~12 s
python "$P/dp_uc56_hp.py"              # ~10 s
python "$P/dp_uc56_build_figs.py"      # ~25 s
cd "$P" && python dp_uc56_build_report.py && python dp_uc56_build_pdf.py && python dp_uc56_build_dashboard.py
cd "<MLB root>" && python "$P/dp_uc56_verification.py"   # 161/161 expected, ~40 s
```

## 5 · Reuse
Imported: `03` §0–1. Shells carried: UC55 figure helpers (`base`, `ship`, brand palette check), UC55 PDF builder (section-loss guard), UC55 report builder pattern (RQ-3 guard, now real). Rebuilt from the client's notebook: the KPI panel (→ F2 season card), the swing-rate × wOBA scatter (→ F7, house pool, regular season, ≥50 PA, Sosa's seasons connected).
