# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## 1 · Manifest (data plane, MLB root, per the RFP)
| File | Role |
|---|---|
| `dp_uc55_kernel.py` | inheritance spine: 14 sha256 pins (K54 + K40a + 12 through K54); ER-1, GS-1, IO-1; era metrics; ER-1 notebook cell |
| `dp_uc55_stott_recap.py` | build: 58 CSV receipts, `headlines.json` (55+ keys), DQ scorecard (20 rules), EDA to file |
| `dp_uc55_hp.py` | the client's frame and functions → HP-01…HP-14 |
| `dp_uc55_build_figs.py` | 10 figures (PNG for the PDF, JSON for the dashboard); claim + brand assertion per figure |
| `dp_uc55_narrative.py` | every sentence, formatted from `headlines.json` |
| `dp_uc55_build_report.py` · `dp_uc55_build_pdf.py` | markdown report (RQ-3 pipe guard) → 10-page PDF (section-loss guard, page cap 10) |
| `_dp_uc55_make_dashboard_builder.py` → `dp_uc55_build_dashboard.py` | recorded shell carry from UC54, then the 7-chapter dashboard + Artifact body variant |
| `dp_uc55_verification.py` | independent harness, 185 checks, families A–L |
| `out/dp_uc55_*` | 82 receipts: 58 CSV, 12 JSON, 10 PNG, 1 notebook cell (md), 1 palette validation (txt) |
| `eda/dp_uc55/` | 3 EDA reports |

Control-plane folder: BID, 00–07, README, contract copy, ledger patch copy, and delivered copies of the report (.md/.pdf) and dashboard (.html, _artifact.html).

## 2 · Environment
- Laptop VM: Python 3.10.12. `/sessions` 100% full again (ENV-3), so `pip install --target /tmp/pyrender -r requirements-render.txt` with `TMPDIR=/tmp/uc55/tmp` ran as the first T0 step, before any data read (MLB `CLAUDE.md` rule).
- Pinned stack: plotly 6.0.1 · pandas 2.2.3 · weasyprint 70.0 · kaleido 0.2.1 · pyarrow 24.0.0 · scipy 1.15.2 · markdown 3.8 · numpy 2.2.5.
- `phillies_dp.selftest` 3/3.
- Dashboard QA ran in the cloud workspace (Playwright Chromium, plotly inlined for the screenshot only; Google Fonts blocked there): desktop, phone (390 px, no horizontal scroll) and dark; 10/10 plots rendered; no console errors besides the blocked font host.

## 3 · Build-time assertions (a failure halts the build)
- Lineage: 14 pins.
- Anchor: house log ≤ 2026-10-01.
- EN-2: no fan-out on the subject. Seasons exactly 2022-26. Name ↔ id one-to-one.
- K40a `assert_conventions` C1–C8 re-proven on 2025-26 Phillies swings (12/12).
- CM-1 endpoints == K40 for every season (tol 1e-9).
- ER-1 labels cover every subject pitch.
- DR-1: LHB pull median `loc_x` > 0 (+76 ft). IO-0: 3B-fielded median spray −35°, 2B +24°.
- 2025 All-Star gap found in the schedule (≥3 days) → 2025-07-18.
- Thump ledger: one id per name.
- IO-1 opportunities on the Phillies fielding side only.
- Every figure asserts its subtitle's claim before writing. This caught Q-2.

## 4 · Run order and timings (laptop VM)
`dp_uc55_stott_recap.py` (~16 s) → `dp_uc55_hp.py` (~15 s) → `dp_uc55_build_figs.py` (~35 s) → `dp_uc55_build_report.py` → `dp_uc55_build_pdf.py` (~20 s) → `dp_uc55_build_dashboard.py` → `dp_uc55_verification.py` (~60 s)

```bash
cd "<MLB root>"
export TMPDIR=/tmp/uc55/tmp; pip install --target /tmp/pyrender -r requirements-render.txt
export PYTHONPATH=/tmp/pyrender:"<MLB root>" PYTHONDONTWRITEBYTECODE=1
python dp_uc55_stott_recap.py && python dp_uc55_hp.py && python dp_uc55_build_figs.py
python dp_uc55_build_report.py && python dp_uc55_build_pdf.py && python dp_uc55_build_dashboard.py
python dp_uc55_verification.py      # 185/185 expected
```
The kernel finds the control plane through `DP_CONTROL_ROOT`, the sibling `Agents for Data Products` folder (laptop VM mount), or the Windows path.

## 5 · Reuse
- **Imported:** see `03` §0–1.
- **Shells carried:** UC54 figure helpers; UC54 report/PDF builders (pipe guard, section-loss guard, page cap); UC54 dashboard CSS/JS (by the recorded generator).
- **Rebuilt from the client's notebook:**
  - cumulative wOBA/OPS (→ F1, house cumulative-chart skill)
  - the Good/Bad KPI tables (→ F4 signature ledger)
  - the platoon × pitch-group tables (→ F7)
  - the velocity split (→ F8)
  - the attack-angle × attack-direction scatter with its `add_hrect` band (→ F6 left, governed band, sign flipped per O-15)
