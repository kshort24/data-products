# 02 — Engineering (Design)

**Layer 2 — Design** · UC #31 · `uc-pps-025` · build `dp_uc30`
**Agents:** `data-architect` → `kpi-calculator` → `join-validator` → `eda-agent`

---

## 2.1 `data-architect` — model blueprint

### Grain

**One row per tracked pitch.** Every KPI in this product is an aggregation over that grain. No row-level join expands it.

### Entity key

`pitcher == 548384` applied at load, asserted immediately after. Named-based filtering is prohibited in this repo.

### Logical model

```
                 ┌──────────────────────────────┐
                 │  raley.parquet (subject)     │
                 │  grain: pitch                │
                 │  key: game_pk, at_bat_number,│
                 │       pitch_number           │
                 └──────────────┬───────────────┘
                                │  partition on game_date
                 ┌──────────────┴───────────────┐
                 ▼                              ▼
        ┌─────────────────┐          ┌────────────────────┐
        │ ERA = Pre-TJ    │          │ ERA = Post-TJ      │
        │ ≤ 2024-04-19    │  ✗ never │ ≥ 2025-07-19       │
        │ 3,162 pitches   │  blended │ 1,022 pitches      │
        └─────────────────┘          └────────────────────┘
                                                │
                 ┌──────────────────────────────┘
                 ▼  scored against (NOT joined to)
        ┌────────────────────────────────────────┐
        │ phils_2015..2026, LHP, ≥300 pitches    │
        │ grain: pitch → aggregated to pitcher   │
        │ n = 28 pitchers                        │
        └────────────────────────────────────────┘
```

### The benchmark is a scoring comparison, not a row join

This is the structural decision worth recording. Raley's pitches are **never joined** to Phillies LHP pitches. Both sides are independently aggregated to a **per-pitcher mean release point**, and Raley's aggregate is then *placed on the same axis* as the population's. There is no key relationship between the two datasets and none is invented.

Consequences:
* No fan-out risk (nothing multiplies).
* The population centroid and standard deviation are computed on the **28 Phillies pitchers only**. Raley is excluded — including him would let the subject drag the yardstick he is being measured against.
* Sample-size asymmetry (Raley 1,018 post-TJ pitches vs Suárez 12,067) affects the *precision* of each pitcher's mean, not the comparability of the means. Pitch counts are published in the benchmark receipt so the reader can weight accordingly.

### Physical partitions

| Partition | Rule | Used for |
|---|---|---|
| `era` | `game_date` vs the two boundaries | every results and process table |
| `tracked` | `pitch_name.notna()` | all usage-share and location work |
| `stand` | L / R | platoon, sightline, pitch × hand |
| `count_state` | first pitch / ahead / behind / even / two-strike | sequencing tables |
| `seq_bucket` | 1st / 2nd / 3rd+ batter within outing | fatigue-within-outing |
| `rest_bucket` | 0–1 / 2 / 3 / 4+ days | workload |

---

## 2.2 `kpi-calculator` — KPI specifications

### Locked KPIs — inherited VERBATIM from `dp_uc29`

Copied byte-identical, not re-derived. Any modification is a breaking change requiring a new spec.

`get_stats` · `nresults` · `whiff_rate` · `chase_rate` · `putaway_rate` · `fpsr` · `hard_hit_rate` · `xwobacon` · `csw_rate`

Two inherited hardening rules travel with them:
* **`xwobacon` supersedes `get_stats.xwoba`** (uc-pps-021 O1). Only the BIP-only form is ever published.
* **`zone_rate_strict` supersedes `chase_rate.in_zone_rate`** (uc-pps-024 O2). A null `zone` is not `> 9`, so untracked rows would otherwise inflate the in-zone numerator.

### NEW KPI 1 — Release Slot Angle (RSA)

| Field | Value |
|---|---|
| **Plain language** | The angle, seen from behind the pitcher, between the horizontal and the line running from the centre of the rubber up to the point where the ball leaves the hand. 90° is straight over the top; lower numbers are lower and wider. |
| **Formula** | `degrees(atan2(release_pos_z, abs(release_pos_x)))` |
| **Grain** | one value per pitch; published as a per-pitcher mean |
| **Population** | any row with non-null `release_pos_x` and `release_pos_z` |
| **CDEs** | `release_pos_x`, `release_pos_z` |
| **Why it exists** | Native `arm_angle` is present in this repo's Phillies files only from 2025. The requested benchmark spans 2015–2026. RSA is computable across the full span. |
| **Edge cases** | null in → null out. `abs()` on the x-term makes RSA directly comparable between left- and right-handers. Makes **no anthropometric assumption** — it describes the release coordinate, which is exactly what a hitter's sightline problem is about. |
| **Calibration requirement** | RSA may not be published as an arm-slot proxy unless `|r| ≥ 0.80` against native `arm_angle` on the overlap. **Enforced as a DQ rule. Achieved r = 0.831 (n = 10).** |
| **Labelling** | the word "proxy" appears wherever RSA is published. Where native `arm_angle` exists, it is preferred. |

### NEW KPI 2 — Release Distinctiveness Index (RDI)

| Field | Value |
|---|---|
| **Plain language** | How far a pitcher's average release point sits from the middle of the comparison population, measured in standard deviations. ~0 means "looks like the average lefty this organization has employed"; ≥1.5 means the look is genuinely atypical. |
| **Formula** | `sqrt( z(rel_x)² + z(rel_z)² )`, standardized by the SD of **pitcher means**, not of individual pitches |
| **Grain** | one value per pitcher |
| **Population** | Phillies LHP 2015–2026, ≥300 tracked pitches (n=28). **Raley excluded from the centroid** |
| **CDEs** | `release_pos_x`, `release_pos_z` |
| **Edge cases** | pitchers below threshold are excluded, never imputed |
| **Known limitation, stated at spec time** | RDI is a **distance** and discards direction. Two pitchers equally far from the centroid in opposite directions score identically. If the finding is directional, RDI will not detect it. *(This limitation duly materialized — see 05.)* |

### NEW KPI 3 — Sightline Offset (SLO)

| Field | Value |
|---|---|
| **Plain language** | The lateral distance, in feet, between where the ball leaves the pitcher's hand and the centre of the batter's box the hitter is standing in. "How far across my body does this ball start?" |
| **Formula** | `abs( release_pos_x − box_center_x(bats) )`, where `box_center_x = +3.208` for a LHH and `−3.208` for a RHH |
| **Grain** | one value per pitch; published as a per-pitcher × batter-hand mean |
| **Population** | rows with non-null `release_pos_x` and non-null `stand` |
| **CDEs** | `release_pos_x`, `stand` |
| **Constant provenance** | 3.208 ft is the rulebook box centre (half-plate 0.708 + 6-in gap + half-box 2.0). An empirical body anchor of 2.10 ft — the observed HBP centroid — is carried alongside as a published sensitivity. Conclusions are identical under either. |
| **Interpretation** | small (<1 ft) = the ball starts on the hitter's own line, appearing from behind his front shoulder; large (>5 ft) = a long cross-body path. |
| **Edge cases** | always non-negative. **Geometry, not outcome** — reported alongside, never in place of, whiff / chase / xwOBAcon. |
| **Depends on** | the coordinate convention asserted in 01.2. If that assertion fails, SLO is meaningless. It is a DQ gate. |

### NEW KPI 4 — Release Tipping Delta (RTD)

| Field | Value |
|---|---|
| **Plain language** | The largest gap, in inches, between the average release points of any two pitches in the arsenal. A self-scout tipping check. |
| **Formula** | `max over pitch-type pairs (i,j) of 12 · hypot(mean_relx_i − mean_relx_j, mean_relz_i − mean_relz_j)` |
| **Grain** | one value per pitcher per era |
| **Population** | tracked pitches; pitch types with **< 25 pitches excluded** (a 6-pitch fifth offering would otherwise dominate a max statistic) — exclusions reported |
| **CDEs** | `release_pos_x`, `release_pos_z`, `pitch_name` |
| **Edge cases** | fewer than two qualifying pitch types → **null, not zero** |
| **Benchmark honesty** | RTD has no league norm. It is interpreted only against the pitcher's **own within-pitch-type release scatter**. A between-pitch gap smaller than the within-pitch noise is not a tipping signal. Both are published side by side. |

---

## 2.3 `join-validator`

| Check | Result |
|---|---|
| Row multiplication after era partition | ✅ `len(pre) + len(post) == len(all)` — asserted |
| Rehab-gap rows silently dropped? | ✅ asserted **0 rows** fall in the gap; the partition is exhaustive, not lossy |
| Benchmark fan-out | ✅ **n/a — no row join exists.** Both sides aggregate independently to pitcher grain |
| wOBA-constants join (`game_year` → `Season`) | ✅ 1:1, no null weights, no row growth. Verification recomputes wOBA from constants by an independent path |
| Outing-log reconciliation | ✅ `sum(outing pitches) == len(post)` and `sum(outing BF) == PA(post)` — asserted |
| Deployment-table reconciliation | ✅ `sum(deployment outings) == 75` |
| Grain drift in pitch × hand | ✅ usage shares sum to 1.0 within each hand |

---

## 2.4 `eda-agent` — pre-build observations that shaped the design

Run before the model was fixed; findings fed back into 2.1 and 2.2.

1. **The era boundary is visible in the raw data**, not imposed: 2024 stops abruptly on 04-19 after 8 outings; 2025 starts on 07-19. No interpolation needed or permitted.
2. **The arsenal shrank across the boundary** — 6 pitch types pre-TJ, 4 post. The curveball and four-seamer have zero post-TJ usage. Any pre/post arsenal table must therefore tolerate ragged pitch-type sets rather than assuming a fixed arsenal.
3. **Release point moved in a consistent direction** (wider and lower) — which is what made the release-point question worth building a benchmark population for rather than answering with a single number.
4. **The sweeper's IVB shifted while its horizontal break did not.** Flagged pre-build as the most likely explanation for any whiff change. It was.
5. **Right-handers see more of him than left-handers** (661 vs 361 post-TJ pitches). This ruled out framing the deliverable as a LOOGY evaluation and forced the RHH exposure into the bottom line.
6. **`estimated_woba_using_speedangle` is ~26% populated overall** and >99% on balls in play — confirming that the inherited BIP-only `xwobacon` rule is the correct treatment and that the pitch-level column must stay quarantined.
