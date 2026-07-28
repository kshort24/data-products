# 01 — Intake Validation & Source Profile
## UC #27 · `uc-pps-022` · Layer 1

Agents: `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`

---

## Part A — `use-case-validator` gap report

**Verdict: GO.** 0 blocking gaps, 5 non-blocking. All five were resolved at intake by DPO
scope decision rather than by agent inference.

| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Performance" undefined — results, process, or both? | Non-blocking | DPO: both, sequenced. Results first, then the indicators explaining them. Encoded as report §2 → §3 |
| G2 | No decision threshold stated. What does a "good" number trigger? | Non-blocking | DPO: this is an informational + gameplan product, not a promote/don't-promote gate. Recommendations are framed as *plausible actions*, never as roster decisions |
| G3 | Personas listed as "including but not limited to" — open set | Non-blocking | DPO: four named personas are in scope (Keller, manager, pitching staff, Realmuto). Advance scouting added as a fifth read-only consumer |
| G4 | Competition level for the gameplan not stated | Non-blocking | DPO: projected MLB call-up. Forces the level-translation caveat to blocking-documentation status |
| G5 | `tm_success_rate` supplied as code without a written definition | Non-blocking **for this UC**, blocking for the KPI itself | Routed to `04_ §SR-M1` as a ratification packet. KPI published PROVISIONAL and marked non-inheritable |

**Feasibility check:** the use case asks four questions. All four are answerable from a single
source at a single grain. No external data acquisition required. No modelling required.

**Internal consistency check:** one tension found and flagged. The user's stated prior —
"I would expect his performance to be pretty good but in a limited sample size" — is
*correct on results* and *only partly correct on process*. The report is written to confirm
the first half and complicate the second, which is the honest read rather than the flattering
one.

---

## Part B — `source-system-profiler` fitness report

### Source

| Property | Value |
|---|---|
| File | `data/opponents/lhvp26.parquet` |
| Contents | Lehigh Valley IronPigs **pitching**, 2026 season, pitch-level Statcast |
| Total rows | 14,960 pitches · 42 pitchers · 3,860 PA |
| Cache max `game_date` | 2026-07-23 |
| Report date | 2026-07-24 (T-1 — normal) |

### Entity lock

```
pitcher == 662144        # Brian Keller
```

> **Contamination trap — do not use a name filter.** The same file contains
> **Brad Keller (641745)**. `player_name.str.contains('Keller')` returns *both* pitchers.
> This is the same failure mode as the Nola / "Nolan Hoffman" contamination that motivated
> the entity-lock rule. The lock is asserted at runtime in the build script and re-tested
> as a blocking DQ check.

### Keller slice

| Property | Value |
|---|---|
| Pitches | 533 |
| Batters faced | 146 |
| Starts | 8 |
| Innings (computed from event→out mapping) | 36.7 |
| Date range | 2026-05-30 → 2026-07-17 |
| `game_type` | `R` only |
| Throws | RHP |
| Age (`age_pit`) | 32 |
| Opponents | BUF, ROC ×2, SWB, WOR, SYR, COL, OMA |
| Duplicate pitch keys | 0 |

### CDE fitness-for-purpose

| CDE group | Fields | Populated | Verdict |
|---|---|---|---|
| Location | `plate_x`, `plate_z`, `sz_top`, `sz_bot`, `zone` | 100% | **FIT** |
| Velocity / movement | `release_speed`, `pfx_x`, `pfx_z`, `api_break_*` | 100% | **FIT** |
| Spin | `release_spin_rate`, `spin_axis` | 99.4% | **FIT** |
| Release / slot | `release_extension`, `arm_angle`, `release_pos_*` | 97.4% | **FIT** |
| Outcome | `description`, `events`, `type`, `bb_type` | 100% of applicable rows | **FIT** |
| Contact quality | `launch_speed`, `launch_angle` | **96 / 96 BIP (100%)** | **FIT** |
| Expected outcomes | `estimated_woba_using_speedangle` | **96 / 96 BIP (100%)** | **FIT** |
| Bat tracking | `bat_speed`, `swing_length` | **0%** | **UNFIT — not captured at this level.** No KPI in this product depends on it |
| Sequencing context | `balls`, `strikes`, `pitch_number`, `n_thruorder_pitcher`, `inning` | 100% | **FIT** |

**Fitness verdict: FIT FOR PURPOSE**, with the bat-tracking exclusion documented and no
downstream dependency on it.

> **Note on the standing AAA-fidelity caveat.** The `pitcher-scouting-report` skill instructs
> that minor-league Statcast EV/xwOBA fields are lower fidelity and that an AAA *supporting*
> tier should be restricted to usage, velo, whiff, and outcome counting. That restriction was
> written for the case where AAA sits *underneath* an MLB primary tier and blending would
> corrupt the MLB rates. It does not apply here, because there is no MLB tier to corrupt and
> the fields are 100% populated. The profiler's ruling: **EV / LA / xwOBA are admissible in
> this UC**, on two conditions — (a) they are only ever compared against a *same-league,
> same-season* population, never against an MLB benchmark; (b) `n` is printed on every line.
> Both conditions are enforced in `04_` and honoured in the report.

### Comparison population

Because Keller has no MLB book and no prior-season AAA book, a raw number would be
uninterpretable. The profiler defines the benchmark:

| Property | Value |
|---|---|
| Population | LHV 2026 pitching staff, **excluding Keller** |
| Size | 41 pitchers · 14,427 pitches · 3,702 PA · 2,385 BIP |
| Why this one | Same league, same season, same park mix, same tracking installation. Removes level, era, and park as confounders in one move |
| Known impurity | The population includes MLB rehab and spot appearances (e.g. Zack Wheeler, 45 PA; Andrew Painter, 79 PA). This makes the benchmark *slightly harder* than a true AAA-only baseline, i.e. it is conservative with respect to Keller |

---

## Part C — `domain-steward-proxy` notes

Surfaced from repo documentation, prior UC specs, and the data itself. These are the domain
rules a human steward would hand over.

1. **AAA→MLB translation is real and is not modelled here.** The historical rule of thumb is
   that strikeout rates compress and walk rates inflate on promotion, and that fastballs
   which play at AAA get punished at MLB. This report applies **no** translation factor
   because none exists in the repo. Every AAA rate should be read as an upper bound on the
   MLB equivalent, and every *direction* (e.g. "the sinker suppresses contact better than the
   four-seam") as far more transferable than any *magnitude*.

2. **Age changes the meaning of the profile.** Keller is 32. The correct frame is major-league
   depth / spot-start / bulk-relief readiness, not prospect development. Recommendations are
   written as approach adjustments a veteran can execute inside a start, not as multi-year
   development plans.

3. **`strikes` and `balls` are PRE-pitch counts.** The count columns describe the state the
   batter walked into on that pitch, not the state after it. Any KPI that reasons about
   "reaching a count within N pitches" must account for the one-pitch lag. This is the single
   most consequential quirk in this UC — it is the root cause of the SR-M1 intent gap in
   `04_ §SR-M1`.

4. **`pfx_x` sign is catcher-perspective, not arm-relative.** For this RHP, arm-side run is
   *negative* `pfx_x`. The build script publishes `api_break_x_arm` (arm-side-positive,
   inches) instead of raw `pfx_x` so that no reader has to reason about the sign convention.

5. **`des` is populated only on the terminal pitch of a plate appearance** (146 of 533 rows
   here). Any `groupby(...).agg(('des','size'))` is counting rows, not non-null `des` values —
   which is correct behaviour for the locked KPI kernel, but is a trap for anyone writing a
   new aggregation.

6. **wOBA constants are MLB constants.** `wOBA and FIP Constants.csv` carries FanGraphs MLB
   season weights. Applying them to AAA events yields a *comparable* wOBA, not an official
   International-League wOBA. Because Keller and the benchmark population are weighted
   identically, the comparison is valid; the absolute level is approximate. Flagged in the
   freshness manifest.
