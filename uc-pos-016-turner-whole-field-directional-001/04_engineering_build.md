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
