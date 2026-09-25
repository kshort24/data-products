# 04 · Engineering Build: `uc-pps-033`

Agent: `data-engineer`

## 1 · Build manifest

| File | Role | Reads | Writes |
|---|---|---|---|
| `dp_uc48_kernel.py` | A (import, sha-pinned) · A2 (verbatim `runs_created`, `GROUP_MAP`, `xwobacon`) · C (CF-1, SR-1, KP-1, AR-2, CS-1, US-1, VE-1, PA-1) | parquet | — |
| `dp_uc48_bowlan_recap.py` | The build: frame → recap (both modes) → tests → arsenal → usage → KP-1 → staff/drill → inherited grades → HP → PA-1 → DQ → headlines | parquet + `out/dp_uc47_population_graded.csv` | 29 CSV + 2 JSON |
| `dp_uc48_build_figs.py` | 11 Plotly figures (PNG + JSON). Each asserts its subtitle's claim; brand-center compliance in-process | `out/` | 11 PNG + 11 JSON + compliance CSV |
| `dp_uc48_build_dashboard.py` | Narrative dashboard, plotly.js inlined; repo copy + body-only Artifact variant | `out/` | 2 HTML (6.0 MB each) |
| `dp_uc48_build_pdf.py` | Markdown → weasyprint (inherited from dp_uc47) | report md + PNGs | PDF |
| `dp_uc48_verification.py` | Families A–F | parquet + `out/` + report + HTML + control-plane package | verification log CSV |

Run order (about 70 s end to end in the sandbox, most of it PNG export):

```bash
export MLB_DATA_ROOT="C:/Users/Kellen/OneDrive/Documents/Python Scripts/MLB"   # dp_uc44_kernel.py and out/dp_uc47_* must be there
python dp_uc48_bowlan_recap.py         # refuses to run unless phils_2026 ends 2026-09-23
python dp_uc48_build_figs.py           # kaleido + a Chrome/Chromium (BROWSER_PATH) for PNG export
python dp_uc48_build_dashboard.py
python dp_uc48_build_pdf.py
PKG_DIR="…/Agents for Data Products/data-products/uc-pps-033-bowlan-2026-recap-001" python dp_uc48_verification.py   # expect 153/153
```

## 2 · Environment disclosure

- **Compute:** the cloud sandbox. The laptop VM's `/sessions` volume was 100% full (42 MB free) and its interpreter has no `pyarrow`, and `pip install` failed with *No space left on device*. This matches uc-pps-032 §2 and uc-pos-015 E-1. **16 files were staged** read-only (12 Phillies seasons, `bowlan.parquet`, the wOBA constants, `mlb_data.py`, and the two parent kernels) plus 4 inherited uc-pps-032 receipts. Outputs are **committed** back.
- **Libraries (sandbox):** pandas 3.x, pyarrow, scipy, plotly 7.1 + kaleido 1.4 (preinstalled Chromium), weasyprint, markdown. Nothing depends on pandas-3-only behaviour.
- **MCP:** `brand-center-mcp.py` is not registered as a server; its `validate_brand_compliance` was called **in-process** through `process_tool_call`, the same path an MCP client hits.
- **Egress:** web search was used for the two carry-ins only.

## 3 · Build-time assertions (the build fails rather than publish)

| Assertion | Where |
|---|---|
| Parent kernel sha256 = pinned | build §0 |
| Phillies log anchor = 2026-09-23 | build §0 |
| DQ 0 FAIL | build §10 |
| uc-pps-032 tiers RESULTS-ONLY → ELITE, velocity grade 50 → 60, rank #2 | figs F1 |
| 2026 is the career-high FF velocity at 97.0 | figs F2 |
| velo and spin changes p < 1e-6 | figs F4 |
| ride change < 0.5 in ("the shape held") | figs F5 |
| staff ride rank ≤ 10 ("exceptional carry") | figs F6 |
| sweeper ≥ 10% vs RHB in 2026 and absent in 2025 | figs F7 |
| FF share at 2K and behind, p < .01 | figs F8 |
| VE-1 pitches 1–10 gain ≥ 1.0 mph | figs F9 |
| multi-inning share < 15% in 2026 and > 40% in 2025 | figs F10 |
| every figure the report references exists | pdf |

## 4 · Receipts (`out/`)

| Receipt | Content |
|---|---|
| `dp_uc48_source_receipt.csv` | CF-1 rows / kept / dropped by season × source |
| `dp_uc48_freshness_manifest.csv` | anchors + both carry-ins |
| `dp_uc48_recap_governed.csv` / `_notebook.csv` | SR-1 both modes, with denominators |
| `dp_uc48_rate_tests.csv` | 10 two-proportion tests 2025 → 2026 |
| `dp_uc48_arsenal_by_season.csv` / `_by_stand.csv` / `dp_uc48_count_state_mix.csv` / `dp_uc48_pitch_mix_by_season.csv` | AR-2, CS-1, client `pitch_mix` |
| `dp_uc48_appearances.csv` / `dp_uc48_usage_summary.csv` / `dp_uc48_rc_by_entry_state.csv` | US-1 |
| `dp_uc48_velo_by_outing.csv` / `dp_uc48_monthly_2026.csv` | VE-1, monthly |
| `dp_uc48_house_population.csv` / `dp_uc48_house_percentiles.csv` | KP-1 |
| `dp_uc48_staff_ff_ivb_by_year.csv` / `dp_uc48_staff_ff_seasons.csv` / `dp_uc48_staff_arsenal_centroids.csv` / `dp_uc48_staff_density.json` | staff frame, DQ-11, drill-through |
| `dp_uc48_archetype_inherited.csv` | uc-pps-032 grades (read, not recomputed) |
| `dp_uc48_bowlan_pitches.csv` | pitch-level slim table for charts |
| `dp_uc48_hp_reconciliation.csv` / `dp_uc48_cache_probe.csv` / `dp_uc48_gemini_cell_audit.csv` | human-parent family |
| `dp_uc48_persona_signatures.csv` / `dp_uc48_persona_ledger.csv` | PA-1 |
| `dp_uc48_dq_scorecard.csv` / `dp_uc48_brand_compliance.csv` / `dp_uc48_palette_validation.txt` / `dp_uc48_verification_log.csv` | quality |
| `dp_uc48_headlines.json` | every narrative number |
| `dp_uc48_fig1…fig11.{png,json}` | figures |

## 5 · Reuse

- `career_frame(pitcher_id)` + `season_recap(df)` is the recap for any Phillies pitcher. For an arm with no dedicated `opponents/` file, set `SUBJECT_FILE` to the Phillies log only (or add the file); the precedence dedup still holds.
- `velo_by_outing_bucket` answers "arm or role?" for any reliever whose usage changed.
- The dashboard builder is chapter-driven: a new recap is a new `CH` list and `CALLOUTS` dict over the same receipt names.
