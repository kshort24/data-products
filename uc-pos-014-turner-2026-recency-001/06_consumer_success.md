# 06 · Consumer Success — `uc-pos-014-turner-2026-recency-001`

**Department:** Consumer Success · **Agents:** `analytics-enabler`, `consumer-onboarding-agent`,
`dashboard-specifier`, `query-builder`

---

## 6.1 · What this product is, in one paragraph

A governed read on Trea Turner's 2026 season and on the six weeks since the last product on him shipped.
It answers eight questions, adjudicates three premises the requester embedded in the ask, and refuses to
answer a ninth (causation) that the data plane cannot support. It is delivered as a 13-page PDF, a
self-contained interactive dashboard, 27 CSV receipts, and a governance trail.

## 6.2 · Persona onboarding

### Hitting coach / assistant hitting coach — **the primary consumer**
- **Read first:** report §4 (mechanism) and §8 rows 1–2.
- **The one number:** popup rate **15.2%** of balls in play since 1 August, against a **5.0%** Phillies
  norm — the only measure in the product that clearly clears sampling noise (z = 4.12).
- **The one thing not to chase:** bat speed. August (69.2 mph) is *within noise* of his own 2023–25 norm.
  July was the spike; August is normal. A "get his bat speed back" program is chasing a five-week artifact.
- **Read-out if an intervention lands:** popup rate toward 5%, mean launch angle back toward 11°, fastball
  xwOBAcon rising. **Not** whiff rate — his contact skills are already the best of his season.
- **Dashboard tab:** *Mechanism*, metric selector on Popup % and Exit velocity.

### Advance scouting
- **Read first:** report §7 (splits).
- **The exposure:** sweepers + sliders are **27.8% of every pitch he sees** and rising (breaking-ball usage
  34.6% → 40.3% across the three windows), and he posts **.182 / .243 wOBA** against them.
- **Watch:** whether the league's breaking-ball share keeps climbing. That number is the league's opinion
  of him, updated weekly.
- **Dashboard tab:** *Pitches & platoon*, "What he is being thrown".

### Manager / lineup construction
- **Read first:** report §7 (platoon) and §8 rows 6–7.
- **The honest answer:** there is no platoon lever here. He is worst against right-handers — **.686 OPS,
  the lowest of his eleven qualified seasons** — and right-handers are two-thirds of his plate appearances.
  The left-handed edge that made him a matchup weapon in 2020–21 has not existed since 2022.
- **What PL-1 rules out:** the recent slump is **not** a scheduling artifact. Re-weighting the recent
  window to either earlier platoon mix moves wOBA by less than three thousandths.
- **Out of scope:** batting-order effects. Lineup slot is not a column in this data plane.

### Analyst / R&D
- **Read first:** `05` (defect register) and `03` (KPI specs) before reusing anything.
- **Reusable immediately:** the kernel's `_fix` lineage, PL-1, the RC-5 breakpoint scan, `pool_percentile`.
- **Provisional, do not reuse without ratification:** AD-1, ST-1, BT-1, and PA-L1/PA-F1.
- **New defect to route:** **D-7 / O-13** — `chase_rate_g.in_zone_rate` counts NULL `zone` as in-zone.
  Every prior UC that published `in_zone_rate` carries this.

### Player-facing brief (scoped surface — mechanics only)
Per the privacy assessment in `03` §3.4, the player-facing version of this product is limited to:
contact point and launch profile, the fastball-timing observation, and the breaking-ball exposure. It
**excludes** the decline framing, the population percentile placement, the persona-action table, and the
career-low language.

---

## 6.3 · Common questions this product can answer directly

| Question | Where |
|---|---|
| Is he actually worse this year, or is it luck? | §2 — xwOBA .292 vs wOBA .294; xwOBAcon .341, his Statcast-era low |
| When did it turn? | §3 — RF-2 peaked 2026-07-21; the breakpoint scan flips sign on the same date |
| Is "recently" just a cherry-picked window? | §3 — the ten-cut sensitivity scan; the sign is robust, the size is not |
| Has he stopped hitting fastballs? | §7 — .173/.231 since 1 August, against .279/.437 through June |
| Is he being pitched differently? | §6 (zone rate, first-pitch strike) and §7 (breaking-ball usage) |
| Is he chasing more? | §6 — chase .343, 10th of 11 career seasons; AD-1 .345, 2nd lowest |
| Is he being platooned into or out of trouble? | §7 — PL-1, mix effect < .003 |
| What did "good" look like? | §5 — two different baselines, and 2026 has neither |
| Can we say the hitting department caused any of this? | **No.** §8 states the limit before the table |

## 6.4 · Queries a consumer can run against the receipts

```python
import pandas as pd
R = lambda n: pd.read_csv(f'out/dp_uc40_{n}.csv')

# "How does the recent window compare to his Phillies norm on any measure?"
w = R('window_split'); ref = R('phi_reference_2023_2025')
m = 'pu_rate'
print(w[['window', m]], '\nPHI 2023-25 norm:', ref[m].iloc[0])

# "Is that difference bigger than noise?"
print(R('shift_tests_july_vs_recent').query("baseline.str.startswith('PHI')")[
      ['measure','baseline_value','recent','delta','z','band']])

# "Does the finding survive a different breakpoint?"
print(R('breakpoint_scan')[['breakpoint','pre_pa','post_pa','d_ops','d_woba']])

# "Which pitches is he worst against, above the floor?"
pt = R('pitch_type_2026'); print(pt[~pt.below_floor].sort_values('woba')[
      ['pitch_type','pitches','woba','whiff_rate']])
```

## 6.5 · Dashboard specification (as built)

Six tabs — Overview · Recency · Mechanism · Pitches & platoon · Career & approach · Governance.
Three interactive controls (percentile mode, monthly metric, mechanism measure). 14 charts, 18 tables.
**Self-contained**: Chart.js is vendored inline (the `uc-pos-011` vendor-don't-CDN rule), there is no
network call, and every chart call degrades to a visible placeholder rather than taking the tables and
tab navigation down. Every below-floor cell renders ⚠. The Governance tab carries the DQ scorecard, the
parent-reproduction receipt, and the declared limits — a consumer cannot reach a number without being
able to reach its caveat in two clicks.
