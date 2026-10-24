# 04 · Engineering Build
**data-engineer · technical-lineage-builder**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` v1.0.0 · built 2026-10-23 21:05-21:20 ET

## 1 · Code (MLB root)
| File | Role |
|---|---|
| `dp_uc57_kernel.py` | Section A imports (pinned), B generalizations, C new rules (CT-1, PR-1, VS-1, PP-1) |
| `dp_uc57_turner_recap.py` | build → 50+ `out/dp_uc57_*.csv`, `headlines.json`, DQ scorecard (≈10 s) |
| `dp_uc57_hp.py` | client frame + client functions (K44 verbatim, `barrel_rate.py`) → HP-01…HP-12 |
| `dp_uc57_build_figs.py` | 9 figures, claim asserted before write, brand checks |
| `dp_uc57_narrative.py` · `_build_report.py` · `_build_pdf.py` | prose from H → markdown → 7-page PDF |
| `dp_uc57_build_dashboard.py` | 6-chapter dashboard (+ bottom line and graded notebook), plotly from the pinned CDN |
| `dp_uc57_verification.py` | definition-first harness (34 checks) |

Full pipeline: 31 s end to end on the device; deterministic (the rebuilt Artifact HTML is byte-identical to the published v1).

## 2 · Lineage (headline numbers)
| Number | Source columns | Transform |
|---|---|---|
| 2026 wOBA .298 | `events`, `game_year` | K40 `nresults_unrounded` (house weights) |
| IZ swing 73.9% → 68.9% | `zone`, `description`, `pitch_type` | K54 `zone_swing_whiff` on `pitch_type.notna()` rows; CT-1 |
| RHP breaking OOZ contact 34.1% → 29.5% | + `p_throws`, `pitch_type` | 1 − K54 `ooz_whiff_rate` |
| Breaking popup 4.9% → 11.6% | `type`, `bb_type` | K40a PU-2 |
| Tilt 27.9 → 25.3 (net −1.4) | `swing_path_tilt` on BP-0 tracked swings | K40a BP-1, PB-1 |
| xwOBA vs RHP .318 → .277 | `estimated_woba_using_speedangle`, `woba_value`, `woba_denom` | K54 XW-1 |

## 3 · Build findings
- **SRC-PA (BID reconciliation):** the BID profile gave 2023 = 692 regular-season PA and a 1,874-PA baseline. The build gives **689 / 1,871**: the BID counted `events.notna()`, which includes 3 `caught_stealing_2b` rows that end an inning but not a PA (K40 `NON_PA`). 2024-26 are unaffected; 2026 = 700 reconciles to FanGraphs.
- **Tracked swings:** BID 2025 1,177 / 2026 1,290; build 1,176 / 1,287 (BP-0 drops bunts and sub-25 mph swings; the BID count was the raw `attack_angle` gate). UC40a's 2026-09-02 row reproduces exactly (1,100 swings, tilt 25.5083, side 39.1763).
- **NA-1:** nullable `Float64` / `string` columns made `np.where` on `bb_type == 'popup'` raise ("boolean value of NA is ambiguous"). Fixed with `.fillna(False)` / `.astype(float)` in the build; the kernel functions were not affected.
- **CAT-1:** `pd.concat` without `ignore_index` duplicated the index in the career-rank frame; fixed.
- No inherited defect found this run.

## 4 · Environment
Device `/sessions` at 100% (ENV-3, sixth occurrence); the render stack ran from `/tmp/pyrender` (plotly 6.0.1, kaleido 0.2.1, weasyprint 70.0, pandas 2.2.3), matching `requirements-render.txt`.
