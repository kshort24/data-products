# 07 · Platform & Marketing
**data-observability · version-controller · cost-watchdog**

## Version manifest

| Field | Value |
|---|---|
| Product | `uc-pos-013-bohm-second-half-turnaround-001` |
| Version | **v1.0.0** (first release; first-touch subject) |
| Data window | 2015 → **2026-08-22** (2026 through last completed game at build) |
| Build id | `dp_uc37` |
| Verification | 227/227 PASS (`dp_uc37_verification.py`) |
| Breaking changes | none (new product). `running_line_pa.cum_slg` = additive minor to a shared provisional function (AP-6 bundle) |
| Consumer comms | headline + floor warnings in `README.md`; deprecations: none |

## Observability — monitoring rules & runbook

| Rule | Trigger | Action |
|---|---|---|
| **Freshness** | any figure quoted with as-of ≠ `phils_2026.parquet` max `game_date` | re-run build (deterministic, ~40 s) before quoting; the dashboard header carries the as-of |
| **Post-window growth** | post-break PA crosses **200** (≈ mid-September) | scheduled refresh: below-floor cells (RISP 42, LHP 33, offspeed 12) may clear the floor and change §4's reliability labels — that is a *content* change requiring v1.1.0 |
| **RB-style tripwire — the regression question** | post-break BABIP (.355) falls below .300 while hard-hit stays ≥ 45% | the "correction vs heater" call in §3 becomes testable; grade the report's three falsifiable calls: (1) BA settles below .336 even if process holds, (2) whiff stays ≤ 14%, (3) pull-air volume stays ≤ 12% |
| **Schema drift** | `hc_x/hc_y` NULL rate on BIP > 1% in a refresh | PA-F1's `hc_tracked` column exposes it; pull-air goes NULL-flagged, not silently wrong |
| **Season end** | last regular-season game loaded | final refresh + close-out: full-season percentiles replace the descriptive post-window percentiles |

On-call: any FAIL in a refresh's verification run blocks re-publish; the receipt diff (window_split
old vs new) is the first artifact to read.

## Cost watchdog

Build is single-machine pandas over ~66 MB of parquet; full pipeline (build + dashboard + pdf +
verification) ≈ 90 s wall, no recompute waste (receipts are written once, consumed by both
renderers). One ranked recommendation: the vendored `_chartjs_4.4.1.umd.js` (205 KB) is now copied
into its third product folder — the shared `_assets/` proposal from uc-pps-026 (open item F1) would
save ~200 KB per product and, more importantly, give chart-lib upgrades one location. No action taken
here (out of scope); recommendation forwarded.

## Marketing one-liner (internal)

*"The audit says the Bohm surge is real: hardest contact of his career on the same swing decisions,
breaking balls solved, and it survives every way you slice the calendar — with exactly three numbers
you should refuse to quote without their sample size."*
