# 04 · Engineering Build
```
python dp_uc65_nola_changeup.py     # 16 receipts + headlines.json (~3 s)
python dp_uc65_build_figs.py        # 6 reference figures (PNG 3840×2160 + plotly JSON) + visual audit
python dp_uc65_build_kit.py         # slides/ kit into the control plane (registry, content, data, refs, brief, manifest)
python dp_uc65_verification.py      # 20/20
```
Lineage: `phils_*.parquet` → K64 `load_frame` / `subject_frame` → `dp_uc65_kernel` Section C → `out/dp_uc65_*` → figures / kit. UC64 receipts read for card B (SQ-2 CH→KC) and card E (7/05 pivot).
Build notes: RN-0 (render stack in `/tmp/pylib`, device VM disk full); RN-1 kaleido restart per figure; control-plane path resolves sibling mount (VM) before Documents layout (Windows) — a first run without this wrote a stray folder into the MLB root, since deleted.
