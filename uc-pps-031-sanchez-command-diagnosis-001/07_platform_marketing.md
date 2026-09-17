# 07 · Platform & Marketing — `uc-pps-031`

Agents: `data-observability` (tripwires only) · `cost-watchdog` · `token-economist`

## 1 · Observability posture

This is a point-in-time diagnosis, not a pipeline. The build's anchor assertion is the freshness control. It
**fails on purpose** when the cache moves past 2026-09-15.

## 2 · Cost audit (cost-watchdog)

| Hotspot | Cost | Recommendation |
|---|---|---|
| Six-season load of every pitcher in Phillies games (281,623 rows) | most of a ~24 s build | Fine at this size. A shared `phils_2021_2026_R.parquet` would help every multi-season UC |
| PN-1 runs 27 metric × basis combinations | ~5 s | Fine. Cache the cohort frame if PN-1 becomes standard |
| `count_leverage` uses `groupby.apply` for distinct PA keys | the slowest function at start grain | Replace with `drop_duplicates` + `groupby.size` when promoting to the notebook |
| Dashboard | 684 KB, no vendored library | The pattern to copy: resolves the F1 item (4.7 MB plotly per product) for map-style dashboards |
| Staging round-trip | ~35 MB each way | Needed only because the device VM had no free disk. A persistent device-side env with pyarrow/weasyprint would remove it |

## 3 · Bid vs actual (token-economist)

| Axis | Bid | Actual | Variance |
|---|---|---|---|
| Tokens (session-budget drawdown) | ~555k (411k in / 144k out) | **~490k** (≈ 410k in / ≈ 80k out, estimated split) | **−12%** |
| Wall clock | ~67 min | **~43 min** (22:24 → ~23:07 UTC) | **−36%** |
| API-equivalent credit | ≈ $11.31 | ≈ **$8.10** | **−28%** |
| Scope | 8 deliverables | 8 delivered, plus split tests, start distribution, and SZ-5 | full scope, additive |

**How actuals were metered.** Drawdown = the session budget counter at close minus its value at intake. The in/out
split is estimated from bytes written to disk (~205k characters of code and prose ≈ 55k tokens) plus reasoning
and conversation. The minutes are wall clock from the first device call to the final commit.

**Calibration findings**

- **C-1 · Pricing the reconnaissance you've already spent was right.** T0 (intake, cross-plane search, staging) came
  to about 190k of the drawdown, a third of the whole job. Bids that price only the build under-count by that much.
- **C-2 · Deriving minutes from tokens narrowed the miss but didn't close it.** The bid used ≈ 0.12 min per 1k and
  landed 36% high (the last two bids were ~3× high). This job ran at **≈ 0.09 min per 1k** (43 min / 490k). Use
  0.09–0.10 until two more jobs confirm it.
- **C-3 · Price a confound line when the comparison crosses a season boundary.** O-18 cost about 35k tokens
  (rail audit, ZC-1, PN-1 on two bases, decomposition) and changed three of five bottom-line statements. Any
  2025↔2026 zone UC should carry this line by default.
- **C-4 · Family F keeps paying for itself.** 60 narrative checks cost about 6k output tokens and caught a
  number that every data check passed.
- **C-5 · Device-side disk is now the limiting resource**, not device_bash availability. Budget the staging
  round-trip (8%) until a persistent device env exists.

## 4 · Tripwires

| # | Watches | Fires when | Action |
|---|---|---|---|
| T-1 | CH vs RHB Shadow Miss (2H .621) | two more starts at ≤ .50 | Re-read §6 and the E-5 recommendation |
| T-2 | Chase beyond the shadow (2H .260) | rolling 3-start value ≥ .33 | The first-half bailout is back; re-test P3/P4 |
| T-3 | 2026 rails | any batter's `sz_top` changes mid-season (`share_constant_1cm` < .95) | O-18 has a second regime; ZC-1 rails must be dated |
| T-4 | League 2026 in-zone | 2027 rails differ from 2026 | Re-baseline ZC-1 to the newer season |
| T-5 | `edge_rate` in the notebook | E-2 pasted | Family H's "absent from notebook" check fails by design; flip it |
| T-6 | Attack Zone constant | E-3 resolved | Re-run the `geometry_crosswalk` row |

## 5 · Change notice for other UC owners (O-18)

> **Subject: 2026 strike-zone rails are not comparable to 2025.** In `phils_2026.parquet`, `sz_top`/`sz_bot` are a
> single fixed value per hitter (height-based ABS zone). For the same hitters, the top of the zone is a median 0.23 ft
> lower than in 2025. League in-zone rate in Phillies games fell .503 → .465, and Shadow Miss rose .370 → .411.
> Any 2025↔2026 comparison of zone-based KPIs (`in_zone_rate`, `chase_rate`, `edge_rate`, OZ-1…4, Attack Zone,
> `ooz_called_strike_rate`, SG-2 in-zone benchmarks) should be re-scored with `dp_uc45_kernel.common_rail_rescore`
> and netted against the league run through the same re-score. Within-2026 comparisons are unaffected.

## 6 · Closure step offered

**Next-start backtest (3 checks).** After Sánchez's next start: (1) is CH-vs-RHB Shadow Miss ≤ .55? (2) is chase
beyond the shadow when ahead ≥ .32? (3) did pitches thrown ahead return to ≥ .31? Each check is falsifiable from
the next day's cache with `dp_uc45_sanchez_command.py` after an anchor bump.
