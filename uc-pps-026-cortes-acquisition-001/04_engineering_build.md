# 04 — Engineering (Build)

**Department:** Engineering (Build) · **Agent:** `data-engineer` (+ `join-validator`)
**Use Case:** `uc-pps-026-cortes-acquisition-001` · **Build:** `dp_uc36` · **Date:** 2026-08-20

---

## Build artifacts

| Artifact | What it is |
|---|---|
| `dp_uc36_cortes_acquisition_read.py` | main build: loaders → locked kernel (verbatim dp_uc29 chain) → UD family → receipts → 5 figures. **Exit 0 first pass**; one post-run patch (DQ cell scoped to 2025 PA), one cosmetic figure patch (legend/xlim). |
| `dp_uc36_build_dashboard.py` | Layer-5 interactive consumable; reads ONLY `out/*.csv`; plotly.js **inlined/vendored** (4.9 MB, no CDN). One render defect found by screenshot QA (V4 secondary axis) and fixed. |
| `dp_uc36_build_pdf.py` | markdown → weasyprint, house CSS (adapted from dp_uc29_build_pdf.py). |
| `dp_uc36_verification.py` | independent recompute — see 05. |
| `out/` | 28 CSV receipts + 5 PNG figures + verification results CSV. New files only; nothing overwritten. |
| `build_console.log` | full console receipt of the delivered build run. |

## Implementation notes (things the next build should inherit)

1. **Appearance grain shortcut, verified against the DPO's method.** The build derives
   entry/exit inning as `inning.min()/max()` per game; the DPO's notebook derives them via a
   min/max-at-bat double merge. Algebraically identical on a single pitcher's log — and the
   verification harness *runs the DPO's original method* as the independent path. All 56 UD
   cells agree exactly.
2. **Rest days derived from appearance-date diffs**, not `pitcher_days_since_prev_game`
   (64% complete in 2018; the derived column is complete by construction after the first
   career appearance).
3. **LHP sign conventions**: `hb_in = +pfx_x*12` (arm-side positive for a lefty — mirror of the
   RHP exemplars); glove side = `plate_x < −0.15`. Asserted empirically in the DQ scorecard
   (SI/CH pfx_x > 0, ST pfx_x < 0) and re-asserted independently in verification.
4. **Populations enforced:** TRACKED (null-`pitch_name` excluded) for every mix/location
   denominator; BIP-only for every EV/xwOBAcon mean (O3); strict zone rate (O2); postseason in a
   separate frame that no rate hop touches.
5. **Join validation:** the only joins are receipt-level left-merges on declared keys
   (`game_year`, `phase`, `stand`, `game_pk`, `month`). Appearance-grain row count (143 games)
   equals `game_pk.nunique()` — no fan-out. Entry-state join is `head(1)` per game (uc-pps-024
   `groupby().first()` trap avoided).

## Environment

Cloud sandbox build against the staged `cortes.parquet` + `wOBA and FIP Constants.csv`;
data-root candidate chain (env var → relative → sandbox mount → Windows path) keeps the script
runnable in the MLB repo Jupyter environment unchanged. pyarrow/plotly/weasyprint installed
at session start (environment tax priced in the bid's contingency).
