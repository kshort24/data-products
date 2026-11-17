# 04 · Engineering Build
Agents: `technical-lineage-builder` · `data-engineer`

## 1 · Run order (MLB root)
```
pip install -r requirements-render.txt          # T0 (device VM: --target /tmp/pylib, see RN-0)
python dp_uc64_nola_recap.py                     # 63 receipts + headlines.json (~28 s)
python dp_uc64_build_figs.py                     # 10 figures (PNG + plotly JSON) + visual audit
python dp_uc64_build_report.py                   # report .md
python dp_uc64_build_pdf.py                      # report .pdf (12 pp)
python dp_uc64_build_dashboard.py                # dashboard .html (Sequence Explorer)
python dp_uc64_verification.py                   # independent harness 43/43
```

## 2 · Lineage
`phils_2015..2026.parquet` → `K49.load_phils_cols` (LP-1, wOBA weights) → `K.subject_frame` (605400) → `K.harmonize` (PT-H) → `K.outcome_cols`
→ {`windows` → `add_lift` → `seq_table` → `seq_career` / `seq_2026` / `seq_by_era` / `era_drift` / `catcher_pairs*` / `book_test`},
{`pa_table` → `endings` → `ending_table` → `endings_*`}, {inherited K44/K48/K49/K50/K51/K53 → `seasons`, `sp_pool`, `context_pct`, `starts_*`,
`halves_*`, `months_2026`, `arsenal`, `prior_reread`, `catcher_2026`, `wc_2026`}, {`predictability` → `pi1_pool`}.
Figures, report, dashboard read receipts only (`dp_uc64_narrative.py`); none computes a KPI.

## 3 · Code receipts (sha256, first 12)
| File | sha256 |
|---|---|
| `dp_uc64_kernel.py` | see `05` §4 (pinned at certification) |
| `dp_uc64_nola_recap.py`, `_build_figs`, `_build_report`, `_build_pdf`, `_build_dashboard`, `_narrative`, `_verification` | `05` §4 |

## 4 · Build notes
- **RN-0** device VM `/sessions` volume full → render stack installed with `pip --target /tmp/pylib`; `PYTHONPATH=/tmp/pylib:<MLB>`. No repo change.
- **RN-1** kaleido 0.2.1 on the device VM fails every render after the first in a process → `pio.kaleido.scope._shutdown_kaleido()` after each figure.
- **RN-2** the same kaleido cannot render `go.Heatmap` at all (even 2×2) → F5 drawn as a square-marker grid on the same diverging colorscale.
- **Nullable dtypes:** `delta_run_exp` etc. arrive as pandas `Float64`; `outcome_cols` casts to `float64` (NA → nan) before list aggregation.
- **Hoffman guard:** the substring 'Nola' matches 'Hoffman, Nolan' (676510); the guard maps exact name → ids and passes.
- **Dashboard test:** headless Chrome in the workspace (plotly.js CDN intercepted and served from the pinned 3.0.1 package); 0 page errors; explorer returns 49 RHB triples / 13 endings at default filters.
