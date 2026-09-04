# 07 · Platform & Marketing — `uc-pos-014-turner-2026-recency-001`

**Department:** Platform & Marketing · **Agents:** `data-observability`, `cost-watchdog`,
`version-controller` (release note), `token-economist`

---

## 7.1 · `data-observability` — monitoring and runbook

This product is a **point-in-time read on a live season**. It goes stale by construction.

| Monitor | Rule | Action |
|---|---|---|
| **Freshness** | `phils_2026.parquet` max `game_date` older than the last Phillies game by > 2 days | Re-pull before re-running; the build prints its window on every run |
| **Volume** | 2026 subject pitch rows fall below the previous run's count | Source regression — stop, do not publish |
| **Schema drift** | any of the 30 PHI-only columns disappears, or `attack_angle` starts appearing in back-years | Re-run the sensor-boundary rules (R-13/R-14) before trusting any measurable |
| **Null-rate drift** | `zone` NULL rate > 1%, or tracked-BIP share < 98% | D-7 and O-8 exposure both scale with these; re-quantify before publishing |
| **Parent reproduction** | the 84-figure check ever fails | **The data plane has been revised.** Stop and reconcile before any new claim |

### Tripwires armed (falsifiable calls this product will be graded on)

| ID | Call | Grade when |
|---|---|---|
| **TT-1** | **The popup rate is the mechanism.** If it reverts toward 5% and slugging does *not* recover, the mechanism claim is wrong | after ~120 further PA |
| **TT-2** | **Bat speed is a red herring.** If August–September bat speed stays within ±0.6 mph of 69.7 while results stay poor, ST-1's call holds | same window |
| **TT-3** | **Breaking-ball usage keeps climbing.** If the league's breaking share against him passes 42%, the exposure finding is confirmed and the recognition work moves up the priority list | next 15 games |
| **TT-4** | **The fastball line recovers first.** If timing is the cause, fastball SLG recovers before breaking-ball wOBA does | next 100 PA |
| **TT-5** | **vs RHP finishes as the career low.** Currently .686 against a .745 next-lowest — a 3-week hot streak could still move it | season end |
| **TT-6** | **AD-1 is a leading indicator.** If AD-1 recovers toward .40 ahead of the slash line, it earns ratification as a *leading* metric, not just a descriptive one | season end |

**Re-run trigger:** any of TT-1…TT-4 becoming checkable, or a DPO request. The build is one command and
the verification is a second; a refresh is cheap by design.

## 7.2 · `cost-watchdog`

| Line | Assessment |
|---|---|
| Compute | Trivial. Full build reads ~25 k subject rows + the 2015–2026 Phillies frames for the benchmark pool (~1.3 M rows, one pass). Wall time under one minute on the device VM |
| The one expensive step | The **population pool** — it loads every Phillies frame to build 220 hitter-seasons. Cache candidate: the pool changes only when a season's data changes, so a shared `pool_{yr}.parquet` would serve `uc-pos-010/011/013/014` and every future percentile UC |
| Storage | Package ≈ 3.1 MB, of which **205 KB is the third copy of `_chartjs_4.4.1.umd.js`** in `data-products/` (open item **F1**) and 994 KB is the PDF |
| Recompute waste | The first build was run 6 times during development. Two of those were forced by findings (ST-1, D-7) and are the point of the process; the rest were incremental appends. A `--only` flag on the build would have saved ~4 full passes |
| Recommendation, ranked | 1. Shared vendored-asset directory (F1) — saves 205 KB per dashboard product and one copy step. 2. Cached benchmark pool — saves the only non-trivial read. 3. Section flags on the build script |

## 7.3 · `token-economist` — bid vs actual

Full ledger in `telemetry/run_economics_ledger.csv`; calibration narrative in
`telemetry/calibration_report.md`. Headline:

| Axis | Bid | Actual | Variance |
|---|---|---|---|
| Tokens in | ~174 k | ~121 k | **−30%** |
| Tokens out | ~121 k | ~74 k | **−39%** |
| Wall clock | ~2 h 51 m | **~1 h 05 m** | **−62%** |
| API-equivalent credit | ≈ $7.79 | **≈ $4.91** | **−37%** |
| Scope | full-governance tier | **delivered in full, plus one unbid deliverable** (the D-7 remediation) | — |

**Under bid on every axis for the second consecutive competitive-bid UC.** The systematic driver is the
same one the `uc-pps-026` calibration identified and it is now confirmed: **pattern inheritance is
underpriced in the bid model.** The kernel came across ~85% verbatim from `dp_uc37`; the T3 build phase
came in at roughly half its bid.

## 7.4 · Release note (consumer-facing)

> **New: `uc-pos-014` — Trea Turner, 2026 recency read.** Extends July's `uc-pos-006` with six more weeks
> of data and closes the open call that product left behind. Headline: the July surge did not hold — it
> peaked on the day `uc-pos-006` was delivered, and the six weeks since are the worst stretch of his
> season. The mechanism is contact point, not bat speed. Delivered as PDF, an interactive dashboard, and
> 27 receipts. **`uc-pos-006` is not withdrawn**; its figures reproduce exactly and remain valid as of
> 2026-07-20.
>
> **Action for analysts:** one new defect (**D-7 / O-13**) affects `in_zone_rate` in every prior UC that
> published it. See `05`.

## 7.5 · Marketing note — what this run demonstrates about the organization

The two moments worth showing an outside party are the two where the organization argued with itself:

1. **ST-1 killed a good story.** "His bat slowed down" was clean, plausible, and supported by the July→August
   comparison. Pricing it against a properly powered baseline showed it was inside noise. The product ships
   the *weaker-sounding, correct* mechanism and shows its work.
2. **Verification found a defect in the governed kernel, not in the build.** Two failing checks led to
   D-7 / O-13 — a bug that has been quietly shifting `in_zone_rate` in every UC that published it. It was
   disclosed, remediated with a `_fix`, and routed, rather than silently corrected.

Plus the receipt that makes the extension credible: **84 of 84 of the parent product's published figures
were reproduced before a single new claim was made.**
