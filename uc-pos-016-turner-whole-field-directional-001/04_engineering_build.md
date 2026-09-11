# 04 · Engineering Build — `uc-pos-016-turner-whole-field-directional-001`

**Agent:** `data-engineer`

## What was built

- `dp_uc42_kernel.py` — loader + governed function kernel (`derive_loc`, `hit_direction`, `in_zone` inherited
  verbatim; `sort_rank`, `P_THROWS_COLORS`, `MARKER_SIZE` new)
- `dp_uc42_turner_whole_field.py` — the build script (data plane entry point, `python dp_uc42_turner_whole_field.py`)
- `dp_uc42_verification.py` — independent spot-verification harness (33 checks)
- `dp_uc42_build_pdf.py` — report → branded PDF
- `dp_uc42_build_dashboard.py` — receipts → self-contained interactive HTML dashboard
- `out/` — 5 CSV receipts + 2 figures (see manifest below)

## Environment notes (disclosed — this materially shaped tooling choices, not the analysis)

This build was produced in the cloud container, not Kellen's local `snakes` conda environment, because the
device bridge to his machine (`device_bash`) returned a virtiofs mount error on every call attempted during
this session ("no Plan9 drive shares mounted") — a device-side connectivity issue, not a data-plane problem.
Three consequences, each disclosed rather than worked around silently:

1. **No `pyarrow` in the cloud container, and PyPI/npm/apt are all outside this session's egress allowlist**
   (`pypi.org` and `registry.npmjs.org` both returned `403 host_not_allowed`; `apt-get update` failed the
   same way). The four `phils_{2023..2026}.parquet` files were read with a **purpose-built pure-Python
   Parquet reader** (`pq_reader.py` — Thrift compact-protocol footer parsing, a hand-rolled raw-Snappy
   decompressor, and RLE/dictionary page decoding for exactly the encodings these files use), rather than
   the standard `pandas.read_parquet(engine='pyarrow')` path every other UC in this repo uses. Validated
   against a coordinate-convention assertion (median `loc_x` < 0 for Turner's Pull BIP) and 33 independent
   spot-checks, both of which passed; freshness spot-checked against the known max `game_date` in the file
   (2026-09-09, consistent with the parquet cache's auto-refresh behavior).
2. **No `weasyprint`** (the house markdown→HTML→PDF tool other UCs use) — the PDF was built directly with
   `reportlab` instead (`dp_uc42_build_pdf.py`), which is installed and network-free.
3. **`dp_uc42_kernel.py` / `dp_uc42_turner_whole_field.py` are written to run on the real data plane**
   (`pandas.read_parquet`, standard pyarrow path) so they reproduce cleanly in Kellen's actual environment —
   they are *not* wired to the pure-Python fallback reader. `pq_reader.py` is a build-time-only tool for this
   session; it is not part of the shipped kernel and is not intended to replace `pyarrow` going forward.

None of this affected the MLB-repo-side conventions used (governed `hit_direction`/`derive_loc`/`in_zone`,
brand colors, entity lock) — those came from the actual repo files, staged and read directly.

## Build-time assertions (the build refuses to publish if these fail)

- Coordinate-convention assertion: median `loc_x` for Turner's `Pull`-classified BIP must be negative (an
  RHB's pull side is left field). **PASSED** (median = −66.3 ft).
- Stand-mix check: `bip.stand.nunique() == 1` and `== 'R'` — verified before any `sort_rank`/`hit_direction`
  branch logic is trusted. **PASSED.**
- Zero untracked BIP for this subject in this window (no `hc_x`/`hc_y` imputation needed). **Confirmed, not
  assumed** — 0 of 1,832 BIP.

## Receipt manifest

| File | Rows/description |
|---|---|
| `out/dp_uc42_turner_bip_extract.csv` | 1,832 rows — every Turner regular-season BIP, 2023-2026, with `loc_x`/`loc_y`/`hit_direction`/`ooz`/`sort_rank` |
| `out/dp_uc42_kpi_directional_by_zone_year.csv` | 12 rows — pull/oppo/straightaway counts + rates x (`outside`, `in_zone`, `all`) x (2023-2026) |
| `out/dp_uc42_significance_2026_vs_pooled.csv` | 6 rows — pooled two-proportion z-test, 2026 vs 2023-25, x (`outside`, `in_zone`) x (pull, oppo, straightaway) |
| `out/dp_uc42_ooz_share_by_year.csv` | 4 rows — share of Turner's BIP that came from an outside-zone pitch, by year |
| `out/dp_uc42_verification_results.csv` | 33 rows — independent spot-check results |
| `out/dp_uc42_fig1_facet_grid.png` | Whole-field directional map: `hit_direction` (cols) x `game_year` (rows) x `p_throws` (color), outside-zone BIP ringed |
| `out/dp_uc42_fig2_pull_oppo_trend.png` | Pull/oppo rate by season, split on zone |

---

# v1.1.0 AMENDMENT — Engineering Build (`dp_uc42a`, 2026-09-10)

**Agent:** `data-engineer`

## What was built

| File | Role |
|---|---|
| `dp_uc42a_kernel.py` | Addendum kernel. **Imports v1.0.0's kernel rather than copying it** — `derive_loc`, `hit_direction`, `in_zone`, `sort_rank`, `pooled_two_prop_z`, `directional_rate_table`, the brand constants and the entity lock all come `from dp_uc42_kernel import …`. Adds the pyarrow-optional loader, the seven verbatim `Baseball Functions.ipynb` transcriptions, and the six NEW-UC42a objects. |
| `dp_uc42a_build.py` | The build. Reproduces v1.0.0's three tables first, then computes the additions. |
| `dp_uc42a_build_dashboard.py` | Receipts → self-contained interactive HTML. |
| `dp_uc42a_context_animation.py` | The DPO's Plotly cell, governed and animated, for JupyterLab. |
| `dp_uc42a_verification.py` | 155-check harness across six families (was 33). |
| `tpl/style.css`, `tpl/body.html`, `tpl/app.js` | Dashboard sources, assembled at build time — editable without touching a 600 KB generated file. |
| `out/` | 15 receipts (was 5) + the dashboard payload. |

**v1.0.0's files are untouched and still run.** `dp_uc42_kernel.py` and `dp_uc42_turner_whole_field.py`
reproduce v1.0.0 exactly as delivered; this build depends on the first and does not modify either.

## Environment notes (round two — disclosed, materially different from v1.0.0's)

1. **`device_bash` failed again**, identically: `sandbox-helper: no Plan9 drive shares mounted under
   /mnt/.virtiofs-root/shared`, on every call, never recovered. This is now the **second consecutive session**
   in this project pairing with a broken device bridge. It is no longer an anomaly to price as a contingency —
   it is the current state of this pairing and should be the *baseline* assumption in the next bid.
2. **Egress remained locked** — `pip install plotly` returned `No matching distribution found`, as did every
   other package. Consequences: `pq_reader.py` (v1.0.0's build-time-only pure-Python Parquet reader) was
   **reused unmodified** to read the four parquet files, and **`plotly` could not be imported at all**, so
   `dp_uc42a_context_animation.py`'s figure builders are **shipped untested**. Its data-preparation half *was*
   exercised (with `plotly` stubbed) and produces the expected 65-row context frame; the `go.Figure`
   construction is written against long-stable Plotly APIs (`go.Scatter`, `go.Frame`, `updatemenus`,
   `sliders`, `make_subplots`) but has not been rendered. **Stated plainly rather than implied to be tested.**
3. **Folder access to the data plane was requested and granted this session** — `C:\Users\Kellen\OneDrive\
   Documents\Python Scripts\MLB`. v1.0.0 had to work without it. This is what made the context pool, the
   pitch-level frame, the widened Rule-1 search, and the verbatim `Baseball Functions.ipynb` transcriptions
   possible; without it, none of this revision's new objects could have been built on governed logic.
4. **Charts are hand-drawn SVG**, not a charting library — see `02` §Design-3. No CDN, no external
   stylesheet, no font download, no runtime fetch. `dp_uc42a_verification.py` family E asserts the absence of
   any external `src`/`href` in the shipped HTML, so the vendor-don't-CDN rule is now **checked**, not just
   observed.

## Build-time assertions (the build refuses to publish if these fail)

- Coordinate-convention assertion, inherited: median `loc_x` for `Pull` must be negative. **PASSED** (−66.3).
- wOBA-weight merge must not change row count (fan-out guard). **PASSED.**
- wOBA constants must have no duplicate `Season` rows after de-duplication. **PASSED.**
- `pitch_uid` unique across all 9,485 pitch rows. **PASSED.**
- BIP frame is a strict subset of the pitch frame. **PASSED.**
- Direction vocabulary closed — no `not grouped` rows may ship. **PASSED.**

## Receipt manifest (v1.1.0)

| File | Contents |
|---|---|
| `out/dp_uc42a_turner_bip_extract.csv` | 1,832 rows — v1.0.0's BIP frame plus `pitch_uid`, `plate_x`, `plate_z`, `launch_speed`, `launch_angle`, `events`, `bb_type` |
| `out/dp_uc42a_turner_pitch_extract.csv` | 9,485 rows — **new** — every regular-season pitch Turner saw, with plate location |
| `out/dp_uc42a_context_player_seasons.csv` | 65 rows — **new** — the rug population, on governed KPIs, with RC-1 |
| `out/dp_uc42a_kpi_directional_by_zone_year.csv` | 12 rows — reproduces v1.0.0 exactly |
| `out/dp_uc42a_significance_2026_vs_pooled.csv` | 6 rows — reproduces v1.0.0 exactly, **column names held identical** so the parent check is a straight compare rather than a mapping |
| `out/dp_uc42a_ooz_share_by_year.csv` | 4 rows — reproduces v1.0.0 exactly |
| `out/dp_uc42a_in_zone_decomposition.csv` | 45 rows — **new** — pull/oppo/straight by zone row, zone column and zone cell |
| `out/dp_uc42a_zone_cell_direction_mix.csv` | **new** — PM-2 |
| `out/dp_uc42a_pitch_location_profile.csv` | 4 rows — **new** — PM-1 per-season profile |
| `out/dp_uc42a_attack_stability.csv` | 3 rows — **new** — PM-1a/b/c χ², df, p, TVD |
| `out/dp_uc42a_bip_value_by_direction.csv` · `..._in_zone.csv` | **new** — `slg_bip` by direction × season |
| `out/dp_uc42a_value_decomposition.csv` | 2 rows — **new** — DC-1, all BIP and in-zone |
| `out/dp_uc42a_defect_exposure.csv` | 4 rows — **new** — known kernel defects measured against this build |
| `out/dp_uc42a_verification_results.csv` | **155 rows** — every check, its family, expected and got |
| `out/dp_uc42a_payload.json` | The dashboard's inlined data (528 KB) |
| `dp_uc42a_turner_whole_field_dashboard.html` | ~600 KB, self-contained, opens offline |
