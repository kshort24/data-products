# 04 · Engineering Build: `uc-pps-035`

Agent: `data-engineer`

## 1 · Build manifest (MLB repo root; copies in this folder under `code/`)

| File | Role | Runs on |
|---|---|---|
| `dp_uc51_kernel.py` | governed kernel: imports `dp_uc49_kernel` + `dp_uc50_kernel` (sha256-pinned), IX-1 extractions (ER-1, JR-1, RCI), CF-2b, OU-2, GS-1b, ST-1, NC-1, MX-1, SR-2 | laptop VM |
| `dp_uc51_wheeler_recap.py` | the build: data plane → 39 `out/dp_uc51_*` receipts + `headlines.json` + DQ scorecard | laptop VM (14–15 s) |
| `dp_uc51_build_figs.py` | 13 figures, PNG + JSON; asserts each subtitle; brand + palette checks | cloud (kaleido) |
| `dp_uc51_hp.py` | client reconciliation (18 HP rows) → `hp_reconciliation.csv` | cloud |
| `dp_uc51_build_dashboard.py` | narrative dashboard (offline repo copy + Artifact body variant) | cloud |
| `dp_uc51_build_report.py` | feature report markdown, every number formatted from receipts | cloud |
| `dp_uc51_build_pdf.py` | markdown → weasyprint (inherited from `dp_uc49_build_pdf.py`) | cloud (pango) |
| `dp_uc51_verification.py` | independent harness, 204 checks | laptop VM |

## 2 · Environment disclosure

- **Laptop VM:** Python 3.10.12, pandas 2.3.3, numpy 2.2.6. `/sessions` still 100% full (39 MB free); `pyarrow 25.0.1` and `scipy 1.15.3` reinstalled with `pip --target /tmp/pyl` (`TMPDIR=/tmp/pt`) because the UC49 installs did not survive a VM restart (T-4 in UC49's runbook). Run with `PYTHONPATH=/tmp/pyl PYTHONDONTWRITEBYTECODE=1`.
- **Cloud render:** Python 3.13, pandas 3.0.5, plotly 5.24.1 + kaleido 0.2.1, weasyprint 70, Chromium 1194 for headless QA. Reads only the staged receipts.
- **Bridge:** 39 receipts staged (748 KB); 2 commit batches staged under new paths (`v1/`, `v2/`) per the UC49 rule (same-path recommits can deliver stale bytes). One `device_bash` heredoc over ~20 KB failed with `E2BIG`; scripts are now written in ≤15 KB chunks.

## 3 · Build-time assertions (the build fails rather than publish)

| Assertion | Where |
|---|---|
| 5 parent modules match their sha256 pins; 6 IX-1 segments match theirs | kernel import (`assert_lineage`, `extract`) |
| JR-1's tied-up boundary read from the compiled function equals 32.5 | kernel import |
| regular-season anchor == 2026-09-27 | build §0 |
| DQ scorecard has 0 FAIL (it failed once: DQ-18, see `05` §4) | build §13 |
| each figure's subtitle claim (ranks, p-values, counts, card backtest) | `build_figs` before each `ship` |
| brand checks (Arial, title, subtitle, axis titles, palette) on every figure | `build_figs.ship` |
| every figure the report references exists | `build_pdf.embed` |

## 4 · Receipts (`out/`)

70 files: 41 CSV (incl. `verification_log.csv`, `hp_reconciliation.csv`, `brand_compliance.csv`), 15 JSON (13 figures + `headlines.json` + `figure_specs.json`), 13 PNG, 1 TXT (palette validation).
Key ones: `recap_governed.csv`, `recap_notebook.csv`, `source_receipt.csv`, `milb_rows_excluded.csv`, `lineage_pins.csv`, `outs_by_pa.csv`, `starts_2026.csv`, `periods_2026.csv`, `stretch_windows.csv`, `stretch_tests.csv`, `tied_up_population.csv`, `still_wheeler_card.csv`, `hp_reconciliation.csv`, `dq_scorecard.csv`, `verification_log.csv`, `headlines.json`.

## 5 · Reuse

- **Next recap is the same build with three constants changed** (`SUBJECT_ID`, `SUBJECT_FILE`, anchor). CF-2b is MLB-safe and names the subject correctly; Nola's recap (in flight in `October 2026.ipynb`) can start there.
- **The season card is subject- and window-agnostic.** `october_card(outing_signatures(frame))` on any pitcher and any reference window.
- **IX-1** inherits any governed function from a script or notebook without running it; the pin table is the receipt.
- **SR-2** turns any reported "N-game stretch with ERA x" into a verified window or a refusal.
