# 01 — Intake Validation & Source Profile

**Layer 1 — Intake & Discovery** · Department: Strategy & Intake
**Agents:** `use-case-validator` → `source-system-profiler` → `domain-steward-proxy`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32` · **Date:** 2026-08-08

---

## 1. `use-case-validator` — gap report

**Verdict: GO.** 0 blocking gaps, 8 non-blocking.

### The ask, as received

> *"I am concerned about the state of Kyle Schwarber's swing. He has lost some pop in his bat as the season has progressed. How do these underlying indicators that I have identified inform decisions that can be made against this use case. Provide an assessment on the state of things then consider personas within the value stream and the types of actions they can take to drive better expected outcomes."*
>
> Plus: a KPI block (barrel rate, EV90, chase rate, whiff rate, in-zone whiff, bat speed, mean LA, mean EV) at the `player_name × game_year × stand` grain over Phillies LHB + Schwarber career; a stated concern about **mean-imputing bat speed NULLs**; a request for **ideal launch angle / sweet spot %** and **anything about swing path**; PDF output; interactive dashboard if sensible.

### Completeness assessment

| Element | Present | Note |
|---|---|---|
| Consumer identified | ✅ | Human DPO (Kellen Short), acting for the hitting/analytics group |
| Business question | ✅ | "Has he lost pop, and what should each persona do about it" |
| Decision to be supported | ✅ | Implicitly: intervene / don't intervene, and *which kind* of intervention |
| Candidate KPIs supplied | ✅ | Eight, supplied as working code |
| Grain specified | ✅ | `player_name × game_year × stand` in the supplied block |
| Population / comparison frame | ⚠️ | Three candidates supplied; **DPO chose within-2026 time trend as primary** |
| Output format | ✅ | PDF required; dashboard requested as an exploration |
| SLA / refresh cadence | ❌ | Not stated. Treated as one-shot with a defined closure step (§9 of report) |
| Acceptance criteria | ❌ | Not stated. Proposed in 00 §Closure and accepted implicitly |

### Gaps raised (all non-blocking)

| # | Gap | Resolution |
|---|---|---|
| G-1 | **"Lost pop" is undefined.** Could mean SLG, ISO, barrel rate, EV, HR rate | Resolved by measuring all five and reporting where they agree and disagree |
| G-2 | **No baseline stated.** Lost pop relative to *what* — last season, career, peers? | DPO selected within-2026 as primary; career and peer framings retained as secondary |
| G-3 | **The supplied grain cannot answer the question.** `game_year` is annual; "as the season has progressed" is intra-annual | Escalated and resolved: the architect added a chronological grain (rolling BIP windows + phase split). **This is the single most consequential intake finding** |
| G-4 | **The supplied query concatenates `nphl` and `pos` without dedup** and without a `game_type` filter | Resolved in build: dedup on `game_pk × at_bat_number × pitch_number`, filter `game_type == 'R'`. 1,275 non-regular-season pitches removed |
| G-5 | **`stand` is in the grain but Schwarber is always LHB** | Retained for the peer pool, dropped from the Schwarber spine as a constant |
| G-6 | **Bat-speed NULL policy is an open decision, flagged by the DPO** | Escalated to DPO before build. Decision recorded: **no imputation + coverage gate** |
| G-7 | **"Swing path" was speculative** — the DPO was unsure the data existed | **It does.** See §2. Materially upgrades the use case |
| G-8 | **The DPO's note says 2023 bat speed has "very limited availability"** | **Contradicted by the source.** Coverage is exactly 0.0% for this batter in 2023. Corrected in the report and pinned by verification check V-20 |

**No gap blocks the build.** G-3 and G-6 changed the design; G-8 changed a stated fact.

---

## 2. `source-system-profiler` — fitness for purpose

### Entity lock

| | |
|---|---|
| Lock | `batter == 656941` (MLBAM) |
| Name-filter contamination probe | **0 extra ids** — `player_name.str.contains('Schwarber')` resolves to the same single id in this dataset |
| Sources | `data/phillies/phils_2015..2026.parquet` (`phillies_role == 'batting'`), `data/opponents/schwarber.parquet` |
| Duplicates dropped | 0 (the two sources do not overlap — `schwarber.parquet` is 2015–2021, `pos` is 2022–2026) |
| Non-regular-season dropped | 1,275 |
| **Locked frame** | **24,891 pitches, 2015 → 2026-08-07** |
| Freshness | max `game_date` 2026-08-07; today 2026-08-08. **T-1, normal** |

### Column fitness against the requested CDEs

| Requested CDE | Physical column | 2026 coverage | Fit |
|---|---|---|---|
| Exit velocity | `launch_speed` | 99.6% of BIP | ✅ |
| Launch angle | `launch_angle` | 99.6% of BIP | ✅ |
| Barrel | `launch_speed_angle == 6` | 99.6% of BIP | ✅ |
| Chase rate | `zone`, `description` | 100% | ✅ |
| Whiff / in-zone whiff | `description`, `zone` | 100% | ✅ |
| **Bat speed** | `bat_speed` | **98.1% of swings, 2024+ only** | ⚠️ **windowed** |
| Swing length | `swing_length` | 98.1% of swings, 2024+ only | ⚠️ windowed |
| **Sweet spot** | derived from `launch_angle` | 99.6% of BIP | ✅ |
| **Swing path** | `attack_angle`, `attack_direction`, `swing_path_tilt` | **98.1% of swings, 2025+ only** | ⚠️ **windowed, 1 comparison season** |
| Contact depth | `intercept_ball_minus_batter_pos_y_inches` | 97.5% of BIP | ⚠️ 2025+ only |
| xwOBA on contact | `estimated_woba_using_speedangle` | 99.6% of BIP | ✅ |

### The sensor-window finding — the governing constraint on this build

Coverage by season, swing denominator for bat tracking (receipt `a2_bat_tracking_coverage`):

| Season | Swings | `bat_speed` | `attack_angle` | Status |
|---|---:|---:|---:|---|
| 2015–2023 | 7,021 | **0.0%** | **0.0%** | not measured |
| 2024 | 1,139 | 93.1% | 0.0% | bat tracking only |
| 2025 | 1,279 | 99.1% | 99.1% | bat tracking + swing path |
| 2026 | 931 | 98.1% | 98.1% | bat tracking + swing path |

**Three distinct evidence windows exist in one table.** Any KPI must declare which window it lives in:

- **Full career (2015–2026)** — results, EV, LA, barrel, sweet spot, discipline.
- **Bat-tracking era (2024–2026)** — bat speed, swing length, fast-swing rate. Three seasons.
- **Swing-path era (2025–2026)** — attack angle, direction, tilt, contact depth. **Two seasons — one comparison.**

**Consequence accepted:** swing-path claims are year-over-year checks, not trends. Stated in the report §4 and in the caveats.

### Fitness for the primary question

The primary question is intra-season. Fitness is **strong**:

| | |
|---|---|
| 2026 plate appearances | 494 |
| 2026 balls in play | **242** |
| Balls in play per phase after midpoint split | 120 / 122 |
| Measured swings, 2026 | 913 of 931 |

242 BIP supports a two-phase split at ~120 per side and a rolling 60-BIP window with 183 window positions. It does **not** support a three-way split or weekly granularity — both were rejected at design.

---

## 3. `domain-steward-proxy` — domain rules, quirks, inherited context

### Business rules asserted

| # | Rule | Source |
|---|---|---|
| R-1 | Regular season only unless stated | `references/data-quality.md`, house standard |
| R-2 | Dedup on `game_pk × at_bat_number × pitch_number` after any concat | house standard; the `pos`/`pps` overlap failure mode |
| R-3 | Entity lock on MLBAM id, never name | the Nola/"Nolan Hoffman" contamination |
| R-4 | Publish batter rate stats at ≥ 50 PA; peer pool threshold raised to 100 PA here | house convention |
| R-5 | Barrel is `launch_speed_angle == 6`; hard hit is `launch_speed >= 95` | locked kernel |
| R-6 | Sweet spot is launch angle 8–32° | Statcast standard |
| R-7 | Rounding: BA/OBP/SLG/OPS/wOBA/xwOBA to three decimals, no leading zero; rates as percentages to one decimal | `Brand Guidelines and Graph Samples.md` |

### Domain quirks surfaced

| # | Quirk | Handling |
|---|---|---|
| Q-1 | **`launch_speed_angle` (barrel) is null when EV/LA are null.** `barrel_rate` excludes them from the numerator but not the denominator | Denominator is all BIP, per the locked function. Coverage is 99.6% so the effect is negligible; documented rather than patched |
| Q-2 | **Statcast parquet uses nullable extension dtypes** (`Int64`/`Float64`). `pd.NA` short-circuits boolean masking with `TypeError: boolean value of NA is ambiguous` | Build coerces 27 numeric columns to numpy `float64` once, up front (`coerce_numeric`). **Encountered live during this build** |
| Q-3 | **Sweet spot % is slugger-blind.** The 8–32° band treats an 8° liner and a 30° fly ball identically | Surfaced as the report's central metrological finding. Drove the SW-2 Ideal-Contact Rate spec and the Damage-Band recommendation (OI-2) |
| Q-4 | **`schwarber.parquet` is a career-backfill cache, not a live feed.** It stops at 2021 | Verified: max `game_year` 2021, no overlap with `pos`. Zero duplicates on concat |
| Q-5 | **Fast-swing and squared-up thresholds (75 mph, 80%) are Statcast conventions, not repo terms** | Declared as report-local constants in 02, with the source named |
| Q-6 | **Statcast's squared-up formula is calibrated on plate speed, not release speed** | Build derives plate-crossing speed from the 9P trajectory fit rather than approximating. Validated: 7.18 mph mean gap (DQ-13) |

### Inherited context from prior UCs

| From | Inherited |
|---|---|
| **UC #21 / `dp_uc20`** (Schwarber first-half) | Same entity, same value stream. Locked KPI kernel and the hitter-retrospective shape |
| **UC #25 / `dp_uc24`** (Turner down-year diagnosis) | The closest structural analogue: *a good hitter is producing less; is it decline or variance*. RF-1/RF-2 trajectory pattern informed the rolling-window design |
| **UC #26 / `dp_uc25`** (Nola) | **`xwobacon` `size`-semantics defect (O4).** Still open. Mitigated here by publishing `xwobacon_n` as an honest denominator |
| **UC #30 / `dp_uc29`** (Kilian) | **O2: locked `in_zone_rate`.** Not material here — in-zone rate is reported but carries no claim |
| **UC #32 / `dp_uc31`** (Arraez) | Receipt naming, DQ scorecard shape, dashboard architecture, the "price both framings" rule |

### Carry-forward defects

| ID | Defect | Status here |
|---|---|---|
| **O4** | `xwobacon` computed with `size` rather than `count` semantics in the locked kernel | **Avoided.** This build computes `xwobacon` with `mean` and publishes `xwobacon_n` alongside. Repo-wide fix still pending |
| **O2** | `in_zone_rate` locked despite a known definitional question | Reported, no claim rests on it |
| **O5** | `truncated_pa` PA fork | Not material — no strict-PA spine in this build |

---

## 4. Handoff

**To `business-glossary-agent` (02):** define the SW-1…SW-9 family and the three evidence windows as first-class governed concepts. Do not let any downstream agent publish a bat-tracking number without a coverage figure.

**To `data-architect` (03/04):** the supplied `game_year` grain is insufficient. Design a chronological grain. The phase split must be data-driven, not calendar-driven.

**Escalated to human DPO and resolved before build:**
1. Bat-speed NULL policy → **no imputation + coverage gate**.
2. Comparison frame → **within-2026 time trend primary**.
3. Deliverables → **PDF + interactive dashboard**.
