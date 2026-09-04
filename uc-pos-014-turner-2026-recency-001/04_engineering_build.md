# 04 · Engineering Build — `uc-pos-014-turner-2026-recency-001`

**Department:** Engineering Build · **Agents:** `data-engineer`, `technical-lineage-builder` (spec in `03`),
`query-builder` · **Gate:** implements only what `02` modelled and `03` specified.

---

## 4.1 · What was built

| Artifact | Lines | Role |
|---|---|---|
| `dp_uc40_kernel.py` | 700 | Loader + governed KPI kernel. **~85% inherited verbatim from `dp_uc37_kernel.py`**; UC40-new: `load_subject` (two-source), `add_windows`, `bat_tracking` (BT-1), `rolling_form` (RF-2), `breakpoint_scan` (RC-5), `legacy_get_stats` (parent reproduction, deprecated), `in_zone_rate_fix` (D-7) |
| `dp_uc40_turner_recency.py` | 730 | The build. Reads the data plane, writes 27 CSV receipts, 6 figures, `headlines.json`, and a console log |
| `dp_uc40_verification.py` | 340 | Independent harness — **711 checks**, hand-rolled masks, does not import the kernel for anything it verifies |
| `dp_uc40_build_pdf.py` | 74 | Markdown → HTML → WeasyPrint, house Phillies CSS |
| `dp_uc40_build_dashboard.py` | 430 | Receipts → one self-contained HTML file, Chart.js vendored inline |

**Runnable on the DPO's machine, not just the build sandbox.** All three scripts take the data-plane root
from `DP_UC40_DATA`, defaulting to `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB`.

```
DP_UC40_DATA="<MLB repo>" python dp_uc40_turner_recency.py     # build   → out/
DP_UC40_DATA="<MLB repo>" python dp_uc40_verification.py       # verify  → 711/711
python dp_uc40_build_dashboard.py                              # dashboard (reads out/ only)
python dp_uc40_build_pdf.py                                    # PDF (needs weasyprint)
```

## 4.2 · Receipts written (27 CSV + 6 PNG + 1 JSON + 1 log)

| Group | Files |
|---|---|
| Career | `career_by_season`, `career_contact`, `career_approach`, `career_pull_air`, `career_bat_tracking` |
| 2026 windows | `window_split`, `monthly_master`, `phi_reference_2023_2025`, `count_state_window` |
| Recency | `breakpoint_scan`, `rolling_form`, `running_line` |
| Splits | `pitch_group_window`, `pitch_group_season`, `pitch_type_2026`, `platoon_season`, `platoon_window`, `platoon_exposure_window`, `platoon_exposure_season`, `platoon_counterfactual` |
| New KPIs | `approach_differential_season`, `approach_differential_window`, `shift_tests_july_vs_recent` |
| Benchmark | `population_pool`, `profile_percentiles` |
| Governance | `dq_scorecard`, `parent_reproduction`, `verification_results`, `headlines.json`, `build_console.log` |
| Figures | `fig1` career · `fig2` RF-1 + RF-2 · `fig3` mechanism · `fig4` monthly · `fig5` platoon · `fig6` pitch groups |

## 4.3 · Build-time assertions (fail loudly, do not warn quietly)

| Assertion | Why it exists | Result |
|---|---|---|
| RHB pulled ground balls have median `loc_x < 0` | `uc-pps-025`: assert the coordinate convention, never assume it. The build **refuses to publish pull-side output** if this fails | PASS (−46.87) |
| non-null `estimated_woba_using_speedangle` at pitch grain == at PA grain | `uc-pps-028` settled the grain; re-proving it is cheap and it is load-bearing for the xwOBA-vs-wOBA "not luck" claim | PASS (601 == 601) |
| `W1 + W2 + W3` PA == season PA | the classic partition bug | PASS (602) |
| `L + R` PA == season PA | same | PASS (602) |
| parent's 84 published figures reproduce on the parent's own definitions | `uc-pps-028` standing check | PASS (84/84) |

## 4.4 · Environment notes (extends the `uc-pps-028` note — for the next build)

- **The pyarrow redirect is still required and still fragile.** `/sessions` (which holds the mounted
  OneDrive tree) was at **100% / 48 MB free** at build time, so `pip install pyarrow` fails on the *cache*
  as well as the build dir. Working recipe:
  `TMPDIR=/tmp/pipbuild pip install --no-cache-dir --target=/tmp/pylibs pyarrow`, then `PYTHONPATH=/tmp/pylibs`.
- **`weasyprint` still cannot install on the device VM** (native pango/cairo). The PDF remains **the one
  step built in the cloud container** from the staged markdown + figures, then committed back.
  `markdown`, `matplotlib`, `pandas` and `numpy` are all present on the device.
- **`device_bash` heredocs above ~20 KB fail with `spawn E2BIG`.** Every script here was written in 2–4
  appended chunks. This is now a third consecutive UC hitting it — worth a helper.
- **Chart.js was copied from `uc-pos-013`, not re-downloaded.** Open item F1 (a shared vendored asset
  directory) remains open; this is now the third copy of the same 205 KB file in `data-products/`.

## 4.5 · Two build iterations were forced by findings, not by bugs

1. **ST-1 was added after the first build.** The first pass produced a clean, plausible "his bat slowed
   down" mechanism. Pricing it against the well-powered baseline showed it was inside noise. The build was
   extended rather than the claim softened.
2. **`in_zone_rate_fix` was added after verification failed.** Two checks failed on `in_zone_rate`; the
   diagnosis was a defect in the *governed* function, not in the build. The `_fix` was added, the report
   was re-cut onto the corrected values, and the defect was logged (D-7 / O-13) rather than patched
   upstream inside a use-case build.

*Gate decision: **BUILD COMPLETE.** All specified artifacts produced; all build-time assertions pass.*
