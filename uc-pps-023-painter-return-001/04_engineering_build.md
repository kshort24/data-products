# 04 — Engineering (Build)

**Department:** `coa-dept-engineering` · **Lead:** `engineering-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 3 verdict:** ✅ complete — build ran clean, 23 CSV receipts + 5 figures + console receipt emitted.

Agents run: `data-engineer` (implementation) · `data-quality-engineer` (execution — scorecard at 05).
`machine-learning-engineer` **not invoked** — no prediction or forecasting in scope.

---

## 4.1 Implementation

**Artifact:** `dp_uc28_painter_vs_orioles.py` (MLB repo root)
**Renderers:** `dp_uc28_build_pdf.py`, `dp_uc28_build_dashboard.py`
**Runtime:** clean, no warnings, no unfilled slots.

### Build discipline

| Rule | How it was honoured |
|---|---|
| Implement only what was specified | Every function traces to a spec in 02.2 or a locked inheritance from `dp_uc11`. |
| Locked KPIs inherited **verbatim** | `get_stats`, `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate` copied character-for-character. Not re-derived, not "improved". |
| Portable data root | env var `MLB_DATA_ROOT` → repo-relative → absolute Windows path. Runs on the sandbox mount and on Kellen's machine unchanged. |
| New files only | Every output is `dp_uc28_*`. No prior UC output is touched. |
| Entity lock asserted at runtime | `assert set(mlb.pitcher.unique()) == {691725}` and the same for `aaa`. The build **fails loudly** rather than silently producing a contaminated report. |
| Never publish a number the build didn't compute | Every table and figure in the report and dashboard traces to a CSV in `out/`. The dashboard **reads the CSVs directly** and inlines them — it cannot drift from the report. |

### The one thing worth calling out

The report's PDF and the interactive dashboard are generated from **the same receipts**, not from two independent queries. `dp_uc28_build_dashboard.py` reads `out/dp_uc28_*.csv` and inlines them as JSON; it performs **no recomputation in the browser**. Two consumer surfaces, one source of truth. If a number is wrong, it is wrong identically in both places and one fix corrects both.

---

## 4.2 Receipts emitted

### Analysis receipts (`out/`)

| File | Contents |
|---|---|
| `dp_uc28_level_summary.csv` | MLB vs AAA tier — all locked process KPIs + results |
| `dp_uc28_start_log.csv` | 19 starts, both levels, KPIs + FF velo + extension + FUTR |
| `dp_uc28_arsenal_by_level.csv` | usage / velo / spin / IVB / HB / zone / whiff / chase / CSW / arm angle |
| `dp_uc28_stuff_delta.csv` | **NEW KPI** — Cross-Level Stuff Delta, with coverage + noise guard |
| `dp_uc28_release_by_start.csv` | **NEW KPI** — Release Consistency Index, per start |
| `dp_uc28_release_by_level_pitch.csv` | release point / extension / arm angle / perceived-velo gain |
| `dp_uc28_fastball_elevation.csv` | **NEW KPI** — Fastball Upper-Third Rate, by level and stand |
| `dp_uc28_fastball_whiff_by_location.csv` | four-seam whiff by zone tier and by elevation band |
| `dp_uc28_location_tiers.csv` | heart / shadow / chase / waste mix by level × pitch |
| `dp_uc28_velo_separation.csv` | separation ladder from the four-seam, both levels |
| `dp_uc28_usage_by_stand.csv` | platoon usage + whiff, by level |
| `dp_uc28_platoon.csv` | full KPI block by level × stand |
| `dp_uc28_count_usage.csv` | usage by count state + two-strike mix |
| `dp_uc28_times_through_order.csv` | KPI block by level × pass |
| `dp_uc28_aaa_arc.csv` | AAA early (2 GS) vs late (3 GS) |
| `dp_uc28_mlb_arc.csv` | MLB first 8 GS vs last 7 GS |
| `dp_uc28_contact.csv` | batted ball, directional only |
| `dp_uc28_ff_benchmark_pool.csv` | 31-pitcher benchmark population, full detail |
| `dp_uc28_ff_benchmark_painter.csv` | Painter vs pool, with percentiles |
| `dp_uc28_arm_spread_pool.csv` | 23-pitcher arm-spread population |
| `dp_uc28_arm_spread_painter.csv` | Painter vs pool |

### Governance receipts

| File | Contents |
|---|---|
| `dp_uc28_dq_scorecard.csv` | 25 checks across 6 DQ dimensions |
| `dp_uc28_freshness_manifest.csv` | 5 sources with window, row count, fitness ruling |
| `dp_uc28_console_receipt.txt` | full stdout of the build — every table as computed |

### Figures (Phillies brand: red `#E81828`, navy `#002D72`)

| File | Traces to |
|---|---|
| `dp_uc28_fig1_arsenal_movement.png` | `arsenal_by_level.csv` |
| `dp_uc28_fig2_velo_by_start.png` | `start_log.csv` |
| `dp_uc28_fig3_release_drift.png` | `release_by_start.csv` |
| `dp_uc28_fig4_location_tiers.png` | `location_tiers.csv` |
| `dp_uc28_fig5_usage_whiff.png` | `arsenal_by_level.csv` |

Figure 1's subtitle (start counts and date range) is **generated from the data**, not hardcoded — an earlier draft hardcoded "15 starts" when the correct regular-season count is 14. Caught in build review; the fix removes the class of error, not just the instance.

---

## 4.3 Findings the build produced

Reported here as engineering output. Interpretation lives in the reader report.

**F1 — Stuff did not change.** Cross-Level Stuff Delta on the four-seam: **+0.64 mph, −0.25" ride, −0.55" horizontal**. Sinker, slider, sweeper, curveball all within or near the noise band. **Only the splitter moved materially: +2.75 mph, +2.43" arm-side.**

**F2 — Usage changed a great deal.** Four-seam **33.1% → 49.2%** (+16.1 pts), slider **21.4% → 8.3%** (−13.1), sweeper **11.4% → 19.7%** (+8.3), splitter **14.4% → 6.8%** (−7.6).

**F3 — The four-seam is the anomaly.** vs a 31-RHP pool: velocity 55th pctile, ride 52nd, extension 52nd, FUTR 48th — but **whiff/swing 26th (.106 vs .200 median)** and **upper-third whiff 23rd (.101 vs .250)**.

**F4 — Elevation did not convert at the major-league level.** MLB four-seam whiff: **.101 upper third vs .111 lower two thirds.** At AAA: **.259 vs .169.**

**F5 — Release-point discontinuity.** 13 MLB starts inside a 2.1-inch band; 2026-06-17 and 2026-06-28 sit ~5 inches toward centre; 7/4 onward back in band. **Same-park control: 6/28 and 7/10 both at Lehigh Valley, 5.6 inches apart** — mechanical, not calibration.

**F6 — Monotonic mechanical drift across the AAA stint.** Extension **6.451 → 6.397 → 6.337 → 6.334 → 6.293 ft**. Arm angle **47.1° → 45.4° → 44.0° → 42.2° → 40.6°**. Four-seam velocity rising over the same window (96.6 → 97.8).

**F7 — Arm-slot spread is extreme.** MLB **13.85°** vs pool median **4.25°**, p90 **9.93°** → **96th percentile** (n=23). AAA **14.97°**. The splitter moved from 46.1° to 40.9°, leaving the fastball cluster.

**F8 — The platoon weapon was shelved.** Splitter vs LHH: **21.4% → 10.6%** usage; sweeper vs LHH **4.4% → 17.6%**. AAA whiff vs LHH **.150 (65 PA)** vs MLB **.215 (185 PA)**. Zero splitters and zero curveballs thrown to RHH at AAA.

**F9 — The AAA arc improved.** Early (37 PA) → late (64 PA): strike .617→.660, CSW .195→.275, chase .321→.354, first-pitch strike .595→.672, hard-hit .458→.273, FUTR .444→.553.

**F10 — What preceded the option.** MLB first 8 GS → last 7: chase **.357→.265**, in-zone **.447→.522**, four-seam usage **.367→.277**, K% .198→.150, BB% .070→.094, wOBA .367→.408. Four-seam velocity flat (96.5→96.6).

**F11 — Contact degrades every pass.** Hard-hit by times through: MLB **.315→.359→.429**, AAA **.261→.353→.455**. Results columns noisy (MLB wOBA falls on the third pass); the process column is monotonic at both levels.

---

## 4.4 Build issues encountered and resolved

| Issue | Resolution |
|---|---|
| `pyarrow` and `matplotlib` absent from the execution environment | Installed. **Build was not run until the data layer was actually reachable** — the UC-PPS-010 failure mode (shipping an unfilled harness) was explicitly guarded against. |
| Figure 3 crashed on `NAType` when plotting RCI | RCI is `NaN` by design for starts under 15 four-seams (2026-06-17). Coerced to float and annotated "n/a <15 FF" on the axis rather than silently zero-filled. |
| Dashboard JSON serialisation failed on `NaN` | Receipt reader sanitises `NaN`/`Inf` → `null` before serialising. |
| Benchmark pool initially n=9 | `min_ff` threshold of 150 admitted only Phillies starters. Lowered to 40 → n=31; arm-spread filter relaxed → n=23. **Population rule is stated in the report**, and the report calls the pool small and directional. |
| Figure 1 hardcoded "15 starts" | Regenerated from `groupby('level').game_date.nunique()`. Correct count is **14** regular-season MLB starts. |
