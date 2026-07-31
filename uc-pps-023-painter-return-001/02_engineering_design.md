# 02 — Engineering (Design)

**Department:** `coa-dept-engineering` · **Lead:** `engineering-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 2 verdict:** ✅ complete — model v1.0, 6 locked KPIs inherited verbatim, 3 new KPIs specified, union validated.

Agents run: `data-architect` → `kpi-calculator` → `eda-agent` → `join-validator` → `technical-lineage-builder`.

---

## 2.1 `data-architect` — model blueprint

### Grain

**One row per pitch.** `(game_pk, at_bat_number, pitch_number)` is the natural key at both tiers. Confirmed unique after dedup in both feeds.

### Structure — a stacked union, not a join

The two tiers are **concatenated with a `level` discriminator**, not joined. This is the single most important structural decision in the build and it is deliberate:

```
phils_2026.parquet ──filter(role, id, game_type)──► mlb  [level = "MLB"]
                                                      │
lhvp26.parquet ────filter(id)──────────────────────► aaa  [level = "AAA"]
                                                      │
                                          pd.concat ──┴──► both
```

**Why a union and not a join:** there is no shared dimension to join on. The tiers describe the same pitcher in disjoint time windows against disjoint hitter populations. A join would be meaningless; a union with a discriminator preserves the separation the governance rule requires.

**The blending guard is structural, not procedural.** Every rate KPI in the build is computed inside `groupby(['level', ...])`. There is no code path that pools MLB and AAA pitches into one denominator. This satisfies the UC#11 multi-level rule by construction rather than by discipline.

### Physical layout

| Table | Grain | Rows | Purpose |
|---|---|---|---|
| `mlb` | pitch | 1,141 | MLB tier |
| `aaa` | pitch | 396 | AAA supporting tier |
| `both` | pitch | 1,537 | Union with `level` discriminator |
| `pool` | pitch | 20,228 | Benchmark population (2026 RHP, both roles, all pitchers) |

### Derived columns (mechanical, specified here, not KPIs)

| Column | Definition | Why |
|---|---|---|
| `ivb_in` | `pfx_z * 12` | Statcast movement is in feet; the pitching department reads inches. |
| `hb_in` | `-pfx_x * 12` | **Sign-flipped** so arm-side run reads positive for a RHP. Raw `pfx_x` is catcher-perspective; unflipped it inverts every horizontal-break statement in the report. |
| `loc_tier` | heart / shadow / chase / waste | Mechanical partition of `zone`, `plate_x`, `plate_z`, `sz_top`, `sz_bot`. Definition in the build docstring. |
| `count_state` | ahead / even / behind | `strikes` vs `balls`. |
| `tto` | times through the order | n-th distinct `at_bat_number` per `(game_pk, batter)`. |
| `arc` | early / late block | Within-tier split. Boundary is a domain call — see 2.3. |

---

## 2.2 `kpi-calculator` — specs

### Inherited verbatim — DO NOT RE-DERIVE

Copied character-for-character from `dp_uc11_rangel_vs_pirates.py`, which inherited from `dp_uc8` / Baseball Functions:

`get_stats` · `nresults` · `whiff_rate` · `chase_rate` · `putaway_rate` · `fpsr` · `hard_hit_rate`

Two mechanical helpers were added (`csw_rate`, `strike_rate`). Both are simple ratios over existing CDEs with no judgment content; they are documented in the build but are not claimed as new KPIs.

### NEW KPI 1 — Release Consistency Index (RCI)

```
RCI = 12 × ( SD(release_pos_x | FF) + SD(release_pos_z | FF) ) / 2
```

| Field | Value |
|---|---|
| **Plain language** | How tightly does he repeat his release point within a single start? |
| **Grain** | one row per `(level, game_date)` |
| **Population** | `pitch_name == '4-Seam Fastball'`, ≥15 such pitches in the start |
| **CDEs** | `release_pos_x`, `release_pos_z`, `pitch_name`, `game_date` |
| **Units** | inches |
| **Direction** | **lower is tighter** |
| **Why four-seam only** | Restricting to one pitch type prevents arsenal mix from moving the number. A start with more sweepers would otherwise look "less consistent" purely from pitch selection. |
| **Edge cases** | starts with <15 four-seams return `NaN` and are excluded from any aggregate (this fires once: 2026-06-17, 12 four-seams). Null release coordinates dropped pairwise. |

### NEW KPI 2 — Fastball Upper-Third Rate (FUTR)

```
upper_third_floor = sz_bot + (2/3) × (sz_top − sz_bot)
FUTR = count(FF with plate_z ≥ upper_third_floor) / count(FF)
```

| Field | Value |
|---|---|
| **Plain language** | How often does he actually elevate the four-seam? |
| **Grain** | any group (level, start, stand, arc) |
| **Population** | `pitch_name == '4-Seam Fastball'` with `plate_z`, `sz_top`, `sz_bot` all non-null |
| **CDEs** | `plate_z`, `sz_top`, `sz_bot`, `pitch_name` |
| **Direction** | **context-dependent — NOT a quality score.** For a high-ride four-seam, ride converts to whiffs mainly at the top rail, so higher is *usually* better. It is an intent measure, not an outcome measure. |
| **Design note** | Uses each batter's **own** `sz_top`/`sz_bot`, not a fixed zone, so tall and short hitters are treated correctly. |
| **Design note** | **Counts pitches above the zone.** Elevation intent is what is being measured, not strike-throwing. `above_zone_rate` is reported alongside so the two can be separated. |

### NEW KPI 3 — Cross-Level Stuff Delta (XLSD)

```
XLSD_<trait> = mean(<trait> | AAA) − mean(<trait> | MLB)      per pitch type
traits: release_speed, release_spin_rate, ivb_in, hb_in
```

| Field | Value |
|---|---|
| **Plain language** | Did the pitch itself physically change at Triple-A? |
| **Grain** | one row per `pitch_name` |
| **Population** | same pitcher id, same season, ≥15 pitches of that type **in both tiers** (`coverage_ok` flag) |
| **CDEs** | `pitch_name`, `release_speed`, `release_spin_rate`, `pfx_x`, `pfx_z` |
| **Mandatory noise guard** | deltas under **0.5 mph** and **1.0 inch** are labelled `within measurement noise` and must not be reported as adjustments. MiLB and MLB Hawk-Eye installs are calibrated separately. |
| **Interpretation guard** | this is a **stuff** comparison only. It says nothing about effectiveness. |

### Provisional — arm-angle spread (tipping proxy)

```
arm_spread_deg = max(mean arm_angle by pitch type) − min(mean arm_angle by pitch type)
```

Population: RHP, 2026, ≥15 pitches of a type counted, ≥3 types, ≥120 total pitches. **Held at provisional** — see 03.1. It carries the report's central causal claim and the report states its limits in its own voice.

---

## 2.3 `eda-agent` — exploration that changed the design

Three observations from exploration materially changed what got built.

**EDA-1 — The four-seam is the anomaly, not the secondaries.**
MLB whiff/swing by pitch: slider .377, splitter .384, curveball .250, sweeper .210, **four-seam .106**, sinker .087. The secondaries are fine. The fastball is the outlier and it is his most-thrown pitch.
→ *Design change:* a dedicated four-seam section and a **benchmark population** were added. A .106 whiff rate means nothing without knowing what normal is.

**EDA-2 — A release-point discontinuity, not a drift.**
Four-seam mean `release_pos_x` across 13 MLB starts sits in a 2.1-inch band. Two starts (2026-06-17 and 2026-06-28) sit ~5 inches away. This is a step function, not a trend.
→ *Design change:* the Release Consistency Index was specified as **within-start** dispersion, and a separate **between-start** mean-position receipt was added. The two measure different things and conflating them would have hidden the finding — RCI is essentially flat across the whole sample (he repeats whatever he is doing), while the between-start mean moves 5 inches.

**EDA-3 — Arm angle varies enormously by pitch type.**
Curveball 52.1° down to sweeper 38.2°. Before benchmarking there was no way to know whether that is normal.
→ *Design change:* the arm-spread pool was added. It is not normal — pool median is 4.25°.

**Arc boundary decision.** The AAA stint splits at **2026-07-10**. Rationale: the first two starts (80 and 69 pitches) are the stretch-out block, and 7/4 is the start where the release point returned to its historical band. This is a **domain call, not a data-driven changepoint**, and it is recorded here so it can be challenged. The finding survives the alternative 3/2 split; it is not knife-edge.

---

## 2.4 `join-validator` — union validation

There is no join, so the classic fan-out risks do not apply. Validated what *is* at risk in a union:

| Check | Method | Result |
|---|---|---|
| Row multiplication | `len(both) == len(mlb) + len(aaa)` | ✅ 1,537 = 1,141 + 396 |
| Key collision across tiers | `game_pk` overlap between MLB and AAA sets | ✅ **empty** — MiLB and MLB game_pk spaces are disjoint |
| Duplicate pitch keys | `drop_duplicates(['game_pk','at_bat_number','pitch_number'])` applied per tier before concat | ✅ zero survive |
| Grain drift | both tiers confirmed pitch-level; no aggregation before union | ✅ |
| Discriminator completeness | `level` non-null on every row | ✅ |
| Entity purity post-union | `both.pitcher.unique() == {691725}` | ✅ **asserted at runtime**, build fails loudly otherwise |
| Schema mismatch | MLB carries 120 columns, AAA 120; all CDEs used are present in both | ✅ |
| wOBA-constant fan-out | merge on `Season` is many-to-one; pre-dropped colliding columns before merge | ✅ no multiplication |

**Verdict: PASS, no remediation.**

---

## 2.5 `technical-lineage-builder` — column-level lineage

```
CDE                      SOURCE                         TRANSFORM                      TARGET
─────────────────────────────────────────────────────────────────────────────────────────────
release_speed            phils_2026 / lhvp26            to_numeric                     velo, velo_max,
                          .release_speed                 groupby(level[,pitch]).mean    XLSD_velo, sep_mph
release_spin_rate        .release_spin_rate             to_numeric → mean              spin, XLSD_spin
pfx_z                    .pfx_z                         × 12 → mean                    ivb_in, XLSD_ivb
pfx_x                    .pfx_x                         × −12 → mean  [SIGN FLIP]      hb_in, XLSD_hb
release_pos_x            .release_pos_x                 filter FF → std × 12 ─┐
release_pos_z            .release_pos_z                 filter FF → std × 12 ─┴─ mean  RCI  [NEW]
                                                        filter FF → mean × 12          mean_x_ft_in
release_extension        .release_extension             mean by (level, game_date)     ext_ft
                         effective_speed − release_speed                                velo_added_by_ext
arm_angle                .arm_angle                     mean by (level, pitch_name)    arm_angle
                                                        max − min across pitch types   arm_spread_deg
plate_z, sz_top, sz_bot  .plate_z/.sz_top/.sz_bot       sz_bot + 2/3·(sz_top−sz_bot)
                                                        → plate_z ≥ floor → mean       FUTR [NEW]
zone, plate_x, plate_z   .zone/.plate_x/.plate_z        4-way partition                loc_tier
                         + sz_top/sz_bot
description              .description                   isin(SWINGS)/isin(WHIFFS)      whiff_rate  [LOCKED]
                                                        isin(CALLED_STRIKE)            csw_rate
                                                        != 'B'                         strike_rate
zone + description       .zone > 9 & isin(SWINGS)       chases / ooz                   chase_rate  [LOCKED]
strikes + events         .strikes==2, .events isin K    K / 2-strike pitches           putaway_rate [LOCKED]
pitch_number + type      .pitch_number==1, .type=='B'   (n − balls) / n                fpsr        [LOCKED]
launch_speed + type      .launch_speed>=95 & type=='X'  hard_hits / bips               hard_hit_rate [LOCKED]
events + woba weights    .events + wOBA constants       Σ w<event> / plate_apps        woba        [LOCKED]
at_bat_number + batter   .at_bat_number, .batter        cumcount per (game_pk,batter)  tto
p_throws + pitch_name    pool (all 2026 RHP)            ≥150 FF → per-pitcher agg      benchmark pool
─────────────────────────────────────────────────────────────────────────────────────────────
NOT PROPAGATED (blocked at source by 01.3-Q3):
estimated_woba_using_speedangle ─── 26% populated, deprecated at pitch level (UC-PPS-021) ─── ✗
estimated_ba_using_speedangle   ─── same ─── ✗
```

**Hop count:** every published number is **≤3 hops** from a physical Statcast CDE. No intermediate materialisation, no cached aggregate, no hand-keyed constant.

**One hand-carried input in the entire build:** none. The `LINEUP` constant used by prior `uc-pps` builds is absent here because the opponent dimension was descoped — which removes the only manual carry-in the pattern normally has.
