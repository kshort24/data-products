# 04 · Engineering Build: `uc-pps-036`

Agent: `data-engineer`

## 1 · Build manifest (MLB repo root)
| File | Role | Runs on |
|---|---|---|
| `dp_uc52_kernel.py` | governed kernel (imports `dp_uc51_kernel.py`, sha256-pinned; A inherited · A2 IX-1 · B CF-2c · C QA-1/BS-1/DS-1/RP-1 + WB-1) | laptop VM |
| `dp_uc52_mayza_recap.py` | the build → `out/dp_uc52_*` + `headlines.json` | laptop VM |
| `dp_uc52_hp.py` | HP family: client frames + client functions → `hp_grades.csv`, `hp_values.json` | laptop VM |
| `dp_uc52_build_figs.py` | 10 figures, PNG + JSON; asserts each subtitle; brand + palette checks | laptop VM (kaleido 0.2.1) |
| `dp_uc52_narrative.py` | every published sentence, formatted from receipts; word-form claims asserted | laptop VM |
| `dp_uc52_build_dashboard.py` | dashboard (repo copy + Artifact body variant) | laptop VM |
| `dp_uc52_build_report.py` · `dp_uc52_build_pdf.py` | report markdown → weasyprint PDF (page cap, figure-exists and section-survival guards) | laptop VM |
| `dp_uc52_verification.py` | independent harness + DQ scorecard | laptop VM |

## 2 · Environment disclosure
- **Laptop VM:** Python 3.10.12. `/sessions` 100% full (29 MB free). The render stack was pinned per `requirements-render.txt` (plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pyarrow 24.0.0, pandas 2.2.3, numpy 2.2.5, scipy 1.15.2, markdown 3.8) and installed with `pip --target /tmp/pyrender`; run with `PYTHONPATH=/tmp/pyrender:.`. The install vanishes on VM restart.
- **Cloud:** viewing only (staged PNG/PDF), plus Playwright headless screenshots of the dashboard with plotly.js served locally (jsdelivr is blocked from the cloud).
- **Bridge findings:** the delete-free shell means render-QA copies go to `eda/dp_uc52/render_qa/` (versioned names) rather than temp files.

## 3 · Build-time assertions (the build fails rather than publish)
| Assertion | Where |
|---|---|
| `dp_uc51_kernel.py` sha256 and its transitive pins | `K.assert_lineage()` at build start |
| house log ≤ anchor 2026-10-01 | `load_house` |
| first/last 2026 RS appearance = 2026-03-28 / 2026-09-25 | build frame block |
| CF-2b dropped 0 non-MLB rows; EN-2 no fan-out | `career_frame_ext` |
| subject season present in each population | build (LHP RP, barrel, DS-1, BS-1, QA-1) |
| each figure's subtitle claim; brand + palette | `build_figs.ship` |
| narrative word-form claims (third-best of nine, Alvarado #2/#3, low-and-in, PA ranges, same-basis luck) | `dp_uc52_narrative.py` |
| every referenced figure exists; ≤ 10 pages; every `##` section survives HTML rendering | `build_pdf` |
| ≤ 9 report sections | `build_report` |

## 4 · Receipts (`out/`)
42 files: 19 CSV, 12 JSON (10 figures + `headlines.json` + `hp_values.json`), 10 PNG, 1 TXT (`palette_validation.txt`). Key ones: `dp_uc52_headlines.json`, `dp_uc52_career.csv`, `dp_uc52_house_lhp_rp.csv`, `dp_uc52_hp_grades.csv`, `dp_uc52_dq_scorecard.csv`, `dp_uc52_verification_log.csv`, `dp_uc52_figure_specs.csv`, `dp_uc52_brand_checks.csv`. EDA: `eda/dp_uc52/mayza_2026_regular.md`.

## 5 · Reuse
- Any LHP reliever recap: change the `SUBJECT_*` constants and the anchor in `dp_uc52_kernel.py`; QA-1, BS-1, DS-1 and RP-1 are subject-agnostic.
- `dp_uc52_narrative.py` is the first recap where report and dashboard share one sentence source. Reuse the pattern.
