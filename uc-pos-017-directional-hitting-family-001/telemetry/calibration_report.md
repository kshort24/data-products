# Telemetry — bid vs actual · `uc-pos-017` / `dp_uc46`

**Bid filed 2026-09-17, awarded same session, delivered same session.**
Fourth instrumented competitive bid; **first for a LIBRARY build** rather than an
analysis UC.

| Axis | Bid | Actual | Variance |
|---|---|---|---|
| Tokens in | ~142k | ~117k | **−18%** |
| Tokens out | ~124k | ~95k | **−23%** |
| Wall clock | ~2 h 35 m (155 min) | **~66 min** | **−57%** |
| Credit value @ $10/M in, $50/M out | ~$7.62 | **~$5.92** | **−22%** |

*Method: chars/4 on every artifact written and every tool result read. Prices
working tokens, not harness overhead — comparable to the uc-pos-014/015 lines by
construction.*

## Calibration history

| UC | Bid (in/out/min) | Actual (in/out/min) | Bid $ | Actual $ |
|---|---|---|---|---|
| `uc-pps-026` | 150k / 105k / 150 | 110k / 44k / 93 | $6.75 | $3.32 |
| `uc-pos-014` | 174k / 121k / 171 | 121k / 74k / 65 | $7.79 | $4.91 |
| `uc-pos-015` | 172k / 128k / 171 | 118k / 105k / 50 | $8.12 | $6.43 |
| **`uc-pos-017`** | **142k / 124k / 155** | **117k / 95k / 66** | **$7.62** | **$5.92** |

## Findings

1. **Four for four under bid on every axis.** The −20%-ish output variance is now
   stable enough to price into the bid rather than discover after. **Recommend the
   next bid be filed at ~0.85× the naive estimate**, with the calibration stated.
2. **The 5% contingency consumed 0% again** — as it did at 10% on the previous
   three. The reduction from 10% to 5% recommended on `uc-pos-015` was correct and
   still conservative. Environmental blockers this run (no `pyarrow` in the local
   VM interpreter) were diagnosed in one step and redirected to the cloud sandbox,
   as on the previous two runs. **In this pairing the redirect is the base case.**
3. **T2 came in at 25% of bid** (9k/6k vs 20k/22k). Speccing collapsed because the
   Rule-1 search in T1 had already resolved every element to PROMOTE / EXTRACT /
   PATCH — there was almost nothing left to *design*. **A thorough T1 does not add
   to the total; it moves spend from T2 into T1 and reduces both.** This is the
   clearest economic argument for Gate 1 the ledger has produced.
4. **T4 and T6 are the only phases over bid.** T4 (+3k out) because the Function
   Certification Checklist was scoped as a section and became a standalone
   generalisable artifact. T6 (+2k in, +2k out) is entirely the V-2..V-6
   remediation — family F failing five checks and the fix cycle. **That overrun is
   the harness paying for itself**; without it a rounding-flattered claim and two
   wrong-column checks ship.
5. **Reuse credits realised:** `directional_rate_table`, `hit_direction` (×4
   transcriptions), PA-L1, `battedball_profile` design, cell 50 share arm, the
   SVG-no-library dashboard pattern, family F itself. A library build is unusually
   reuse-dense because promotion *is* the work.

## Recommendation for the next library build

Library builds price differently from analysis UCs: **T1 is heavier, T2 is much
lighter, T6 is heavier** (two harnesses, not one). Suggested shape for a
comparable family: 40/8/20 · 8/6/5 · 22/19/12 · 14/30/16 · 6/9/5 · 18/13/10 ·
8/11/6, contingency 5%.
