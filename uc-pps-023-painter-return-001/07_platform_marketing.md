# 07 — Platform & Marketing

**Departments:** `coa-dept-platform` · `coa-dept-marketing`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 6 verdict:** ✅ backtest harness defined, versioning classified, narrative staged (internal only).

---

# Part A — Platform

Agents run: `data-observability` · `cost-watchdog` · `version-controller`.

## 7.1 `data-observability` — monitoring and backlog

This is a **single-run, expiring** data product. It has no scheduled pipeline, so conventional freshness and volume monitors do not apply. What *does* apply is re-run integrity and the source backlog.

### Re-run guards (armed in the build itself)

| Guard | Mechanism | Fires when |
|---|---|---|
| Entity lock | runtime `assert` on `pitcher.unique()` | any source change admits another pitcher — **build fails loudly** |
| Data-layer reachability | `FileNotFoundError` if `data/phillies` cannot be located | the data layer isn't mounted — this is the **UC-PPS-010 failure mode** and it now halts rather than shipping an empty harness |
| Sample-threshold | RCI returns `NaN` under 15 four-seams; `coverage_ok` flag on XLSD | a start or pitch type is too thin to support the KPI |
| Noise band | `noise_guard` column on every stuff delta | a delta is inside cross-park measurement noise |
| Union integrity | `game_pk` disjointness verified at 02.4 | MiLB and MLB id spaces ever collide |

### Post-game re-run trigger

After tonight, re-run `dp_uc28_painter_vs_orioles.py` with `phils_2026.parquet` refreshed. The MLB tier gains a 15th start and the AAA tier is frozen. **Expected drift on the re-run:** the MLB tier's rates move by roughly 1/15th; the benchmark percentiles shift slightly as the pool gains a game. Neither invalidates the findings, but the report's numbers will no longer match the receipts — see the versioning ruling at 07.3.

### Platform backlog (surfaced by this UC)

| # | Item | Priority | Why |
|---|---|---|---|
| **P1** | **Build an Orioles hitter cache** (`bal26.parquet` or equivalent) | 🔴 high | The DQ FAIL in this package. Any future PHI-vs-BAL use case hits the same wall. |
| **P2** | Generalise the benchmark-pool method into a reusable helper | 🟡 medium | `ff_benchmark()` and `arm_angle_spread()` were written for this UC but are pitcher-agnostic. Every future `uc-pps` report needs a comparison population, and building one ad hoc each time invites inconsistent thresholds. |
| **P3** | League-wide RHP population for `arm_spread_deg` ratification | 🟡 medium | Required to promote the metric out of provisional (03.1). It currently carries a headline claim on a 23-pitcher pool. |
| **P4** | Investigate the cross-level spin offset | 🟢 low | +84 to +118 rpm on four pitch types, +1 on the curveball. Unexplained. No conclusion depends on it, but it will recur on every future multi-level UC. |
| **P5** | Retire or annotate `_scratch_painter_lhv_scouting_20260709.md` | 🟢 low | Superseded by this UC and contradicted on two conclusions (01.3-Q4). Leaving it unmarked in the repo root invites someone to cite it. |

## 7.2 `cost-watchdog`

| Resource | Measure | Assessment |
|---|---|---|
| Compute | single-pass pandas over 1,537 subject rows + 20,228 pool rows; full build under 30 s | 🟢 negligible |
| Storage | 28 CSVs + 5 PNGs ≈ 800 KB; PDF 557 KB; dashboard 73 KB | 🟢 negligible |
| Recompute waste | the benchmark pool loads `phils_2026.parquet` a second time (36,301 rows) | 🟡 **minor** — could share the first read. Not worth the coupling on a build this size; flagged rather than fixed. |
| Dashboard payload | 205 rows inlined as JSON, Chart.js from CDN | 🟢 well within a single-file budget |

**No optimisation recommended.** The one inefficiency identified is a deliberate trade: a second parquet read in exchange for `load_benchmark_pool()` being independently callable and testable.

## 7.3 `version-controller`

**Version: `dp_uc28` v1.0.0** (2026-07-31)

### Change classification

| Change | Class | Notice required? |
|---|---|---|
| Three new KPIs (RCI, FUTR, XLSD) | **additive — non-breaking** | No. Nothing downstream consumed these fields before. |
| Benchmark-pool method | **additive — non-breaking** | No. New capability. |
| `arm_spread_deg` | **additive — PROVISIONAL** | ⚠️ Yes. Consumers must be told it is not a ratified term and is correlational. Delivered in the report text and in 06.2. |
| Opponent dimension **absent** vs the standard `uc-pps` pattern | **breaking — pattern deviation** | ⚠️ **Yes.** Anyone expecting the usual lineup-by-lineup attack plan will not find one. Disclosed in the report's warning box, the capability map (00), and the DQ scorecard. |
| `hb_in` sign flip (arm-side positive) | **non-breaking within this UC** | Documented in 02.1 and the data dictionary. ⚠️ A cross-UC hazard: prior UCs report raw `pfx_x`. Anyone comparing horizontal break across UCs must check the convention. |
| Locked KPI functions | **unchanged** | No. Verbatim inheritance from `dp_uc11` is the point. |

### Deprecation notices carried forward

- `estimated_woba_using_speedangle` at pitch level — deprecated by UC-PPS-021, **upheld and extended here** to bar all expected-outcome metrics from this report.
- `_scratch_painter_lhv_scouting_20260709.md` — **superseded** by this UC. Two of its conclusions are contradicted (01.3-Q4).

### Re-run policy

If the build is re-run after tonight's game, it produces **v1.1.0** and the published report is **stale, not wrong**. The report is a *pre-game projection* and is dated as such. **Do not silently regenerate the PDF against post-game data** — issue it as the backtest (07.4) instead.

## 7.4 Closure step — post-game backtest

The UC is not closed until tonight's start is compared against it. Backtest checklist:

| # | Projection | Measure tonight | Verdict |
|---|---|---|---|
| 1 | Four-seam usage near 49% (not 28%) | actual FF usage | ☐ |
| 2 | Four-seam release-x in the −25 in band, not near −20 | actual mean `release_pos_x` × 12 | ☐ |
| 3 | Extension at or above 6.29 ft | actual mean `release_extension` | ☐ |
| 4 | Splitter usage vs LHH above 10.6% (ideally back toward 21%) | actual, by stand | ☐ |
| 5 | Four-seam whiff/swing — does it clear .106? | actual | ☐ |
| 6 | **Tipping hypothesis** — whiff after same-slot vs different-slot sequences | instrumented per 06.2 | ☐ supported / unsupported / still open |
| 7 | Hard-hit climb by times through the order | actual by pass | ☐ |
| 8 | Pitch count 85–90, 5–6 innings | actual | ☐ |

Item 6 is the one that matters. **A single start cannot settle it** — record it as evidence, not a verdict, and roll it into the P3 ratification study.

---

# Part B — Marketing

Agents run: `product-narrator` · `brand-guardian` · `communications-agent`.
`slide-builder` **not invoked** — no deck requested.

## 7.5 `product-narrator` — the story

**The one-liner:** *Painter's stuff was never the problem. His fastball is dead average in every measurable way and misses half as many bats as it should — and the most likely reason is that his arm tells you what's coming.*

**Why this package is worth talking about internally:** it is the first `uc-pps` report where the standard pattern **didn't fit** and the organisation said so instead of forcing it. The opponent dimension was descoped at the intake gate, the gap was published to the reader rather than buried, and the freed budget went into delivery mechanics — which is where the actual finding turned out to live. A pipeline that can decline part of its own brief and be more useful for it is working correctly.

**The methodological contribution:** benchmarking. A .106 whiff rate is just a number. A .106 whiff rate at the 26th percentile, on 55th-percentile velocity and 52nd-percentile ride, is a diagnosis. Every future scouting report in this repo should carry a comparison population, and P2 exists to make that cheap.

## 7.6 `brand-guardian` — compliance

| Check | Result |
|---|---|
| Phillies red `#E81828` / navy `#002D72` in all figures, PDF, dashboard | ✅ |
| Figures traceable to a CSV receipt | ✅ all five |
| Sample size shown on every small-sample claim | ✅ verified (05.3, 05.5-H) |
| House voice — bottom line first, honest error bars | ✅ |
| No fabricated numbers, no unfilled harness slots | ✅ 76/76 verification |
| Report dated and marked as a pre-game projection | ✅ |
| Subject dignity — the pitcher is a named consumer of this product | ✅ 06.2 written developmentally per privacy ruling R4 |

## 7.7 `communications-agent` — distribution

**Classification: INTERNAL ONLY.** External publish blocked (03.4 R1). Need-to-know distribution: Painter, Realmuto, pitching department, manager, human DPO.

**Advance-meeting note (internal, ≤200 words):**

> Painter goes tonight in Baltimore after five Triple-A starts. Short version: the stuff is unchanged and it was never the issue. Velocity, ride, and extension all sit mid-pack against big-league right-handers. What he fixed at Triple-A is his attack plan — fastball usage from 33% to 49%, and the fastball started missing bats again.
>
> The open question is why a 96-mph four-seam with average ride got a 10.6% whiff rate in the majors — 26th percentile, half the league median. The best candidate we have: his arm slot varies 13.8° across his arsenal, against a league median of 4.25°. That's 96th percentile. It's a hypothesis, not a finding, and we're instrumenting tonight to test it.
>
> Two things to watch. His release point jumped five inches for two starts around the option and has since come back — if it moves again, that's the tell. And he shelved his splitter against lefties, which was his best pitch by a distance (.395 whiff on 76 swings). It needs to come back tonight.
>
> Full report and dashboard on the shared drive. Internal only.
