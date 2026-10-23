# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## 1 · Manifest (control-plane folder)
| File | Role |
|---|---|
| `dp_uc54_kernel.py` | inheritance spine: 12 sha256 pins (K40, K34, K53 → K52 → K51/K49/K50/K48/K44/barrel_rate, CM-1, UC22); IX-1 extractions; TR-1/CC-1/XO-2 |
| `dp_uc54_crawford_recap.py` | build: 47 CSV receipts, `headlines.json` (125 keys), DQ scorecard, EDA to file |
| `dp_uc54_hp.py` | the client's frame and functions → HP-01…HP-14 grades |
| `dp_uc54_build_figs.py` | 10 figures (PNG for the PDF, JSON for the dashboard); claim + brand assertion per figure |
| `dp_uc54_narrative.py` | every sentence, formatted from `headlines.json` |
| `dp_uc54_build_report.py` · `dp_uc54_build_pdf.py` | markdown report → 10-page PDF (section-loss guard, page cap) |
| `dp_uc54_build_dashboard.py` | 7-chapter dashboard + Artifact body variant |
| `dp_uc54_verification.py` | independent harness, 157 checks |
| `out/dp_uc54_*` | 69 receipts: 47 CSV, 12 JSON, 10 PNG |

## 2 · Environment
- **Laptop VM:** Python 3.10.12. `/sessions` was 100% full again, so the render stack was installed to `/tmp/pyrender` with `TMPDIR=/tmp/uc54/tmp`, in the foreground (**ENV-3**, second occurrence).
- **Pinned stack:** plotly 6.0.1 · pandas 2.2.3 · weasyprint 70.0 · kaleido 0.2.1 · pyarrow 24.0.0 · scipy 1.15.2 · markdown 3.8. `phillies_dp.selftest` 3/3.
- **Dashboard QA** ran in the cloud workspace (Playwright Chromium) against a copy with plotly inlined for the screenshot only. Google Fonts are blocked there, so the QA frames show fallbacks.

## 3 · Build-time assertions (a failure halts the build)
- Lineage: 12 pins.
- Anchor: house log ≤ 2026-10-01.
- EN-2: no fan-out on the subject.
- Subject is in the pool exactly once.
- Crawford 2026 is in CX-1.
- **CM-1 endpoints == K40 for every CX-1 series and metric (tol 1e-9).** This caught SF-1 on the first run.
- DR-1 convention: LHB pull median `loc_x` > 0 (+63 ft).
- RV-1: `delta_run_exp` positive on walks (+0.229).
- XO-2 coverage ≥ 90%. This caught the v1 neighbourhood at 18–45%.
- Every figure asserts its subtitle's claim before writing. This caught F1 comparing the CX-1 endpoint with the season line (464 vs 465 PA).

## 4 · Run order and timings
`dp_uc54_crawford_recap.py` (18 s) → `dp_uc54_hp.py` (~70 s; scans 130 opponent files twice) → `dp_uc54_build_figs.py` (~40 s) → `dp_uc54_build_report.py` → `dp_uc54_build_pdf.py` (~20 s) → `dp_uc54_build_dashboard.py` → `dp_uc54_verification.py` (~90 s).

```bash
cd "<Agents for Data Products>/data-products/uc-pos-019-crawford-2026-recap-001"
export TMPDIR=/tmp/uc54/tmp; pip install --target /tmp/pyrender -r "<MLB root>/requirements-render.txt"
export PYTHONPATH=/tmp/pyrender:"<MLB root>" MLB_DATA_ROOT="<MLB root>" PYTHONDONTWRITEBYTECODE=1
python dp_uc54_crawford_recap.py && python dp_uc54_hp.py && python dp_uc54_build_figs.py
python dp_uc54_build_report.py && python dp_uc54_build_pdf.py && python dp_uc54_build_dashboard.py
python dp_uc54_verification.py      # 157/157 expected
```

## 5 · Reuse
- **Imported:** see `03` §1.
- **Shells carried:**
  - UC53 figure helpers (`base`, `ship`, brand walk)
  - UC53 report and PDF builders (pipe guard, section-loss guard, page cap)
  - the house `dashboard_shell.md`
- **Rebuilt from the client's plots:** the mean-location scatter (→ F7), the EV box (→ F8 left), the hit pitch map (→ F8 right) and the spray chart (→ F9). The CBP field is drawn from `cbp-spray_AI.md` park dimensions.
