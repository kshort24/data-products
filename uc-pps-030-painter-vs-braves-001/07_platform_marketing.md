# 07 · Platform & Marketing — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Platform & Marketing department
Agents: `data-observability` (tripwires only), `cost-watchdog`, `token-economist`, `version-controller`

---

## 1 · Monitors / tripwires

This is a point-in-time advance, not a published pipeline, so there is no freshness SLA to monitor. There are
six conditions that would invalidate something in the package, and each has a cheap check.

| # | Tripwire | Check | If it fires |
|---|---|---|---|
| T-1 | **The cache advances past 2026-09-12** | `max(game_date)` in `phils_2026.parquet` | The build refuses to run. This is correct: a new game is a new use case, not a correction to this one. Open UC #45 |
| T-2 | **Painter throws a splitter** | `(pitch_type=='FS').sum()` on any start after 2026-07-31 | The card's `FS` line comes out of the freezer and AR-1 must be recomputed. The .395-to-LHH number is the best evidence this shop has on that pitch |
| T-3 | **A sweeper population reaches 25 pitcher-seasons at the 100-pitch floor** | `len(benchmark_population(allp,'ST','R'))` at `GRADE_FLOOR_PRIMARY` | The THIN stamp comes off and every sweeper grade in this package is superseded. Currently 14; the tag is young and this will fire within a season or two |
| T-4 | **`arm_angle` completeness rises above ~80% in a refreshed cache** | null rate on the graded window | The `uc-pps-023` arm-spread finding becomes refreshable. This is the single highest-value blocked analysis in the Painter file |
| T-5 | **League splitter share falls sharply** | `dp_uc44_tag_drift.csv` rebuilt on a newer cache | The AR-1 "pitcher decision" verdict flips to "possible classifier drift" and the headline finding needs a caveat |
| T-6 | **Any downstream artefact quotes a grade without its population** | Manual, on review | C2 violation. A grade without its population is a number with no contract |

## 2 · Cost / efficiency audit (`cost-watchdog`)

| Item | Reading | Judgement |
|---|---|---|
| Data staged | 13 parquet files, ~63 MB, **one** `device_stage_files` call | Efficient. Batched deliberately after the mount failure |
| Benchmark frame | 12 seasons loaded once into one frame, sliced 12 times by `benchmark_population` | Efficient. The alternative — one parquet read per pitch type — would have been 72 reads |
| Recompute waste | The build was re-run 3 times (two receipt additions, one KPI addition) at ~8 s each | Acceptable. The build is cheap **because** the expensive frame is loaded once |
| Figure rebuilds | 6 | Two were layout fixes caught by reading the rendered PNG rather than by guessing. Cheap, and the alternative is shipping a collision |
| Verification cost | 247 assertions, ~35 s | **The best-value line item in the engagement.** It caught three real errors in the report prose |
| Storage | 31 receipts + 5 PNG + 1 PDF + 1 HTML ≈ 2.1 MB | Negligible |
| Avoidable cost incurred | The first folder-access request timed out unanswered (~4 min) | Structural, not a build decision. Recorded as a recurring tax |
| **Optimisation for next time** | The 2015–2026 benchmark frame is rebuilt from parquet on every run and is **identical across use cases**. Caching it as a single `benchmark_pitcher_seasons.parquet` would cut ~40% off every future SG-1 build | **Recommended.** One artefact, reusable by the whole family |

## 3 · Bid vs. actual (`token-economist`)

**Method.** "Actual" is the session budget meter (cumulative billed input + output across all turns of this
engagement), read at the point of writing this section, plus a projected remainder for the commit-back and
hand-off. Wall clock is measured from the first tool call to the same point. Both are stated as measured
quantities with their method attached rather than as estimates dressed as facts.

| | Bid | Actual | Variance |
|---|---|---|---|
| Tokens (in + out, combined) | ~412k | **~421k** at this section, **~450k** projected at hand-off | **+2% / +9%** |
| Wall clock | ~2 h 28 m | **41 min** at this section, **~55 min** projected | **−63%** |
| Credit value (list rates) | ~$9.56 | ~$9.80–10.50 | **+3% to +10%** |
| Deliverables | 8 | 8 | On |
| Receipts bid | ~30 CSV, 5 figures, 1 payload | 24 CSV, 5 figures, 1 payload, 1 log | −6 CSV |
| New governed objects | 7 | 7 | On |
| Verification checks | "7 families" | 7 families, 247 checks | On |

### Where the variance came from

**Tokens came in on the bid; time came in at a third of it.** That asymmetry is the finding, and it repeats
the `uc-pps-029` pattern (bid 2 h 31 m, and the same over-estimate). This shop is **systematically
mis-estimating wall clock by roughly 3×** while estimating tokens to within 10%. The cause is that the bid
prices phases as if they were sequential human work; in practice profiling, figure building and document
drafting interleave, and the token meter — not the clock — is the real constraint.

**Calibration action:** future bids should quote **tokens as the primary price** and wall clock as a derived
estimate at roughly **0.10 minutes per 1k tokens** (this build: 450k → 45 min; `uc-pps-029`: 313k → its
actual). Quoting a two-and-a-half-hour clock on a 45-minute job is a credibility problem in a competitive RFP,
not a conservatism.

**Six fewer CSV receipts than bid** — not a shortfall. Three bid receipts collapsed into `mix_by_stand` once
the by-stand design settled, and three planned per-figure receipts were unnecessary because every figure reads
from an existing table. Receipt count is a poor proxy for coverage; **narrative-assertion count** (family E, 40
checks) is the better one and should replace it in future bids.

**The environmental contingency was correctly sized and correctly spent.** `device_bash` was down for the
entire engagement; the +15% contingency covered staging the data plane in and committing the package back. The
bid called this "the BASE CASE in this pairing" — for the second engagement running, it was.

## 4 · Calibration findings

1. **Wall-clock estimates are 3× high, twice running.** Move to tokens-primary pricing. (See §3.)
2. **The falsification pass is where the value is, and it is cheap.** Reconciling three client-supplied numbers
   took under 20k tokens and produced the entire engagement. Every future bid should carry an explicit
   "premise stress-test" line item and price it visibly, because it is the thing a competitor optimizing for
   agreeableness will not do.
3. **A verification family that reconciles the *prose* pays for itself immediately.** Family E caught three
   errors that would have shipped: a wrong Shapiro p-value quoted from the wrong floor, "five" for "six", and
   "all twelve" for "eleven of twelve". Receipt-to-receipt checking would have caught none of them, because
   every receipt was correct. **Recommendation: family E becomes mandatory for every uc-pps report.**
4. **Confirming an opponent id externally costs ~2k tokens and removes an escalation.** `uc-pps-029` shipped an
   inferred opponent starter and escalated it to the human DPO. This build confirmed it and did not. Standing
   defect O-10 has a cheap workaround; use it.
5. **Reading the rendered figure is not optional.** Two of six figure rebuilds were collisions and a false
   title, both invisible in the code and obvious in the PNG. The figure-title assertion added in this build
   (`assert set(_multi.game_date) == ...`) should become a house pattern: **if a chart title makes a claim, the
   figure build asserts it.**

## 5 · Publication

| | |
|---|---|
| Classification | **Internal — Restricted**. External publication blocked |
| Distribution | Manager, pitching coach, catcher, pitching analyst |
| Surface | PDF (10 pp) + interactive card + the notecard figure |
| Valid for | The 2026-09-13 start only (condition C1) |
| Supersedes | Nothing. `uc-pps-023` remains valid as a return read; its arm-spread finding is **not** refreshed here |
| Superseded by | The post-game backtest, when run |

## 6 · Closure step — post-game backtest

Eight checks, to be run after the 2026-09-13 game against a refreshed cache. This is the cheapest available
ratification of the SG/AR/PM family (a second independent use) and the only honest test of the attack rule.

| # | Check | What it tests |
|---|---|---|
| B-1 | Sweeper usage to LHH: was it below 17%? | Whether the single attack rule was adopted |
| B-2 | Changeup usage to RHH: was it above 13%? | The cheapest-gain recommendation |
| B-3 | Actual pitch mix vs the post-option projection, by stand | Whether the card's usage picture predicts |
| B-4 | Four-seam above-zone rate: still ~.35? | Whether the elevation design is stable or was a phase |
| B-5 | Pitch count at the end of the 5th | The 90-pitches-for-23-batters claim |
| B-6 | xwOBA allowed to LHH vs the .305 projection | The platoon lean, tested once |
| B-7 | Any splitter thrown? | Tripwire T-2 |
| B-8 | Grade movement: rerun SG-1 including this start | Does a single start move a grade? If it does, the window is too short and the floors need raising |

**One start records evidence, not a verdict.** B-8 is the check that matters most for the KPI family: a grading
scheme whose output swings on 90 pitches is not measuring what it claims to measure.
