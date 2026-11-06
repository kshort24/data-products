# 04 · Engineering Build
Agent: `data-engineer`

## 1 · Manifest (MLB data plane root; code is the data plane's per the RFP)
| File | Role | sha256 (16) |
|---|---|---|
| `dp_uc62_kernel.py` | governed kernel (Section A imports, B generalization, C new) | `2adc60059cfaebd2` |
| `dp_uc62_walker_recap.py` | T1 build: every published number → `out/dp_uc62_*` | `0377db402a51daa5` |
| `dp_uc62_hp.py` | HP grades + DQ scorecard | `2571414192149150` |
| `dp_uc62_narrative.py` | single narrative source (report and dashboard) | `09fb52d5e01700f0` |
| `dp_uc62_build_figs.py` | F1–F9 PNG + JSON, V1–V7 audit | `352e0b1e44c2068c` |
| `dp_uc62_build_report.py` · `dp_uc62_build_pdf.py` | markdown report → PDF (weasyprint, RQ-2 guard) | `4c5d0440760543c8 · 10d00a050836cc10` |
| `dp_uc62_build_dashboard.py` | dashboard (repo copy + Artifact body) | `333a725878663e8d` |
| `dp_uc62_verification.py` | independent harness (47 checks) | `14d4afe2c1b0455a` |

## 2 · Environment
Laptop VM via the device shell. Python 3.10; render stack from `requirements-render.txt` into `/tmp/pyrender` (plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pyarrow 24.0.0, pandas 2.2.3, numpy 2.2.5, scipy 1.15.2). `TMPDIR=/tmp/uc62/tmp` (ENV-3 recurrence: pip needs the temp dir off the full volume).

## 3 · Run order
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc62_walker_recap.py      # ~9 s; asserts lineage, entity, game type, anchor
python dp_uc62_hp.py                # HP 7 rows; DQ 15/0/0
python dp_uc62_build_figs.py        # 9 figures; V1–V7 asserted per figure
python dp_uc62_build_report.py && python dp_uc62_build_pdf.py   # 8 pages
python dp_uc62_verification.py      # 47/47 expected; exit 1 on any FAIL
python dp_uc62_build_dashboard.py   # after the harness, so the chip prints the harness count
```

## 4 · Build-time assertions
Lineage (10 pins) · entity lock and regular season · anchor (K53) · EN-2 fan-out · V1–V7 per figure · PDF: every referenced figure exists, every `##` heading survives rendering (RQ-2), page cap · dashboard: plotly by CDN tag.

## 5 · Receipts (`out/dp_uc62_*`, 38 files)
CSV: `career_by_year`, `windows`, `pr1_ledger`, `phillies_pool_kp1`, `phillies_bf_leaderboard`, `pitch_type_pool`, `arsenal_by_year`, `game_log`, `contract_economics`, `ev_tracking_by_year`, `ev_mu_mechanism`, `source_receipt`, `career_milb_dropped`, `hp_grades`, `dq_scorecard`, `visual_audit`, `verification`. JSON: `headlines`, `kr1_fit`, `pr1_rollup`, F1–F9. PNG: F1–F9. Key copies in this folder's `data/` and `figures/`.

## 6 · Reuse
Inherited by import: 20+ functions (§1 of `03`). Written new: KR-1 (2 functions), CE-1 (1), PR-1 (2), KF-1 (1). The PDF builder and dashboard shell are carried from UC53's pattern.
