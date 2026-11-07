# 04 · Engineering Build
Agents: `data-engineer`

## 1 · Manifest (MLB root)
| File | Role |
|---|---|
| `dp_uc63_kernel.py` | governed kernel (imports K62, pinned) |
| `dp_uc63_mcfarlane_recap.py` | T1 build: every published number → `out/dp_uc63_*` |
| `dp_uc63_hp.py` | grades HP rows from receipts |
| `dp_uc63_narrative.py` | single narrative source (CL-1 copy, specs, governed read) |
| `dp_uc63_build_figs.py` | F1–F6, F5b, S1 + V1–V7 audit |
| `dp_uc63_build_report.py` / `_build_pdf.py` | report `.md` → `.pdf` (weasyprint, 10 pp) |
| `dp_uc63_build_dashboard.py` | dashboard `.html` + Artifact body |
| `dp_uc63_build_slides.py` | slide content + Claude Design kit (`out/dp_uc63_design_kit/`) |
| `dp_uc63_verification.py` | independent harness (no kernel import) |

## 2 · Environment
Laptop VM via device shell; `/sessions` full (ENV-3) → `TMPDIR=/tmp/uc63/tmp`, `pip install --target /tmp/pyrender -r requirements-render.txt` (plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pyarrow 24.0.0, pandas 2.2.3).
Deletes are not permitted in connected folders: the slide builder overwrites the kit in place and excludes `manifest.json` from its own hash list.

## 3 · Re-run
```bash
cd "<MLB root>"
export TMPDIR=/tmp/uc63/tmp PYTHONPATH=/tmp/pyrender:"<MLB root>" MLB_DATA_ROOT="<MLB root>" PYTHONDONTWRITEBYTECODE=1
python dp_uc63_mcfarlane_recap.py && python dp_uc63_hp.py && python dp_uc63_build_figs.py && python dp_uc63_build_report.py \
 && python dp_uc63_build_pdf.py && python dp_uc63_build_slides.py && python dp_uc63_verification.py && python dp_uc63_build_dashboard.py
```
(dashboard last so its harness chip reads the fresh verification.)

## 4 · Build-time assertions
lineage (11 pins) · anchor ≤ 2026-10-01 · O-26 id frame = name frame · no S/E rows in the client frame · dedup key unique · Kerkering id ↔ name 1:1 · every figure passes V1–V7 or a registered exception · PDF ≤ 14 pages and no lost sections.

## 5 · Receipts (52 in `out/dp_uc63_*`)
Tables: `overall`, `overall_by_phase`, `by_stand`, `stand_pitch`, `pitch_map_mix`, `arsenal_shapes`, `bs1r_subject`, `bs1r_rhp_pool`, `context_pool_cx1`,
`context_percentiles`, `pitch_type_pool_rhp`, `fo1_pool`, `fo1_pitch_sample`, `fo1.json`, `outing_ledger`, `aaa_outings`, `aaa_mix`, `stint_ledger`,
`s1_twins`, `s1_mix_*`, `pitches`, `hp_grades`, `dq_scorecard`, `freshness_manifest`, `verification`, `visual_audit`, `headlines.json`; 8 figures × (PNG + JSON); design kit.
Key copies in this folder's `data/`, `figures/`, `slides/`.

## 6 · Reuse
Imported: 20+ governed functions through K62. Dashboard shell and PDF CSS carried from UC #62. Kit pattern (brief + manifest + registry) from UC #61.
