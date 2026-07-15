# 07 — Platform, Observability & Versioning
## uc-pps-019 · data-observability + version-controller + cost-watchdog

## Observability (post-publish monitoring rules)
| Rule | Threshold | Action |
|---|---|---|
| Cache freshness | `phils_2026.parquet` max game_date > 3 days behind last Phillies game | flag stale before any re-run |
| Volume | Sánchez 2026 pitch count decreases vs prior run | upstream rewrite — stop, investigate |
| Schema drift | any 02-lineage column missing/dtype change | block re-run, re-profile |
| QR population | `pitch_number` nulls on PA-final rows > 0 | QR-1 invalid — block the metric only |

## Versioning
v1.0.0 (initial release, 2026-07-14). **v1.1.0 (2026-07-15): additive battery pitch-map addendum** — `dp_uc21a_*` receipts/figures + `dp_uc21a_battery_addendum.md`; non-breaking, no v1.0.0 artifact modified; corrects the *interpretation* of §5's battery split (game-mix confound) without altering its numbers. Additive promotion of QR KPIs = minor bump. Formula change to a ratified QR = **breaking** (consumer notice required). Second-half refresh = new UC or a versioned re-run of this one — never overwrite `dp_uc21_*` receipts.

## Cost-watchdog observations (informational — no action taken this run; full telemetry in `telemetry/run_economics_ledger.csv`)
1. **Kernel inheritance is the dominant saver.** ~85% verbatim reuse of dp_uc17 meant zero design/debug cost for 13 of 17 receipt panels; the build ran exit-0 first pass. Recommendation: keep treating dp_uc17/dp_uc21 as the frozen pitcher-retrospective kernel; diff-only review for siblings.
2. **The skill-embedded ledger lags the repo ledger** (skill said next=#12; repo said #22). Reconciliation cost ~1 read + risk of double-claim. Recommendation: treat `uc_ledger_AI.md` (repo) as sole source of truth; drop the ledger table from the skill copy or mark it explicitly stale-by-design.
3. **Environment cold-start** (pyarrow, matplotlib, weasyprint installs) is a repeated per-session cost across UCs (~2-3 min). Recommendation: note in skill §5 that installs are expected; batch them in one call at session start when a build is planned.
4. **Single-probe intake** (one profiling pass answering entity lock + freshness + QR feasibility together) kept Layer 1 to one tool call. Recommendation: adopt as standard — the profiler question list should be assembled from the use case *before* touching data.
