# 03 — Data Dictionary & Technical Lineage

**Layer 2 — Design** · Departments: Governance ∥ Engineering (Design)
**Agents:** `metadata-mapper` · `data-dictionary` · `technical-lineage-builder`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

---

## 1. `metadata-mapper` — physical to business term

| Physical column | Type | Business term | Mapping | Note |
|---|---|---|---|---|
| `batter` | Int64 | Batter Identity | **exact** | Entity lock |
| `player_name` | object | Batter Name | exact | Display only; never a filter |
| `game_date` | object→datetime | Game Date | exact | Chronological ordering key |
| `game_year` | Int64 | Season | exact | |
| `game_pk`, `at_bat_number`, `pitch_number` | Int64 | Pitch Key | exact | Composite dedup key |
| `game_type` | object | Game Type | exact | Filtered to `'R'` |
| `type` | object | Pitch Outcome Class | exact | `'X'` = ball in play |
| `description` | object | Pitch Description | exact | Drives swing/whiff classification |
| `events` | object | Plate-Appearance Outcome | exact | Drives the counting kernel |
| `zone` | Float64 | Statcast Zone | exact | `> 9` = out of zone |
| `stand`, `p_throws` | object | Handedness | exact | |
| `launch_speed` | Float64 | Exit Velocity | exact | |
| `launch_angle` | Float64 | Launch Angle | exact | SW-1, SW-2, SW-8 |
| `launch_speed_angle` | Float64 | Batted-Ball Class | exact | `== 6` is Barrel |
| `estimated_woba_using_speedangle` | Float64 | xwOBA on Contact | exact | O4 defect avoided |
| `estimated_slg_using_speedangle` | Float64 | xSLG on Contact | exact | |
| `bat_speed` | Float64 | Bat Speed | **exact, windowed** | 2024+ |
| `swing_length` | Float64 | Swing Length | exact, windowed | 2024+ |
| `attack_angle` | Float64 | Attack Angle | exact, windowed | 2025+ |
| `attack_direction` | Float64 | Attack Direction | exact, windowed | 2025+ |
| `swing_path_tilt` | Float64 | Swing Path Tilt | exact, windowed | 2025+ |
| `intercept_ball_minus_batter_pos_y_inches` | Float64 | Contact Depth (SW-6) | **fuzzy** | Renamed for readability; the physical name is not consumer-facing |
| `intercept_ball_minus_batter_pos_x_inches` | Float64 | Contact Lateral Offset | **unmapped** | Loaded and coerced, not used. No business question required it |
| `vx0,vy0,vz0,ax,ay,az` | Float64 | Pitch Trajectory Parameters | exact | Inputs to derived Plate Speed |
| `release_speed` | Float64 | Release Velocity | exact | Velocity banding (C4) |
| `hc_x`, `hc_y` | Float64 | Hit Coordinates | exact | → `loc_x`/`loc_y` for spray |
| `bb_type` | object | Batted-Ball Type | exact | |
| `balls`, `strikes` | Float64 | Count State | exact | C7 |
| `pitch_type` | object | Pitch Type | exact | → `pitch_group` |
| `phillies_role` | object | Frame Role | exact | `'batting'` selects `pos` |

**Ambiguous mappings requiring DPO resolution: none.**
**Unmapped elements: 1** (`intercept_ball_minus_batter_pos_x_inches`) — loaded but unused; flagged rather than silently dropped.

---

## 2. `data-dictionary` — published output elements

### Receipt `a1_career_season_spine` — grain: one row per `game_year`

| Column | Type | Definition | Nullable |
|---|---|---|---|
| `game_year` | int | Season | no |
| `plate_apps`, `at_bats`, `bip`, `hits`, `hrs`, `walks`, `strikeouts` | int | Counting stats from the locked event classification | no |
| `ba`, `obp`, `slg`, `ops`, `iso` | float(3) | Rate stats. Display without leading zero | no |
| `krate`, `bbrate`, `hr_rate` | float(3) | Per plate appearance | no |
| `xwobacon` | float(3) | Mean xwOBA over BIP | no |
| `xwobacon_n` | int | **Honest denominator** — count of non-null xwOBA. Published because of carry-forward defect O4 | no |
| `ev_mu`, `ev90`, `ev_max`, `la_mu`, `la_sd` | float | Contact-quality descriptives over BIP | no |
| `sweet_spot_rate` | float(3) | SW-1 | no |
| `ideal_contact_rate` | float(3) | SW-2 | no |
| `barrel_rate`, `hard_hit_rate` | float(3) | Locked | no |
| `bat_speed_mu`, `bat_speed_p90`, `bat_speed_sd` | float(3) | **NULL for every season before 2024** — coverage gate | **yes, by design** |
| `fast_swing_rate` | float(3) | SW-3. NULL pre-2024 | yes, by design |
| `swing_length_mu` | float(3) | NULL pre-2024 | yes, by design |
| `attack_angle_mu`, `attack_dir_mu`, `swing_path_tilt_mu`, `aa_fit_rate` | float(3) | NULL for every season before 2025 | **yes, by design** |
| `squared_up_rate`, `squared_up_pct_mu`, `blast_rate` | float(3) | SW-4, SW-9. NULL pre-2024 | yes, by design |
| `contact_depth_mu`, `contact_depth_n` | float/int | SW-6. NULL pre-2025 | yes, by design |
| `bt_swings`, `aa_swings` | int | Measured denominators | no |
| `bt_coverage`, `aa_coverage` | float(3) | **SW-7 — the coverage gate** | no |
| `chase_rate`, `in_zone_rate`, `whiff_rate`, `whiff_rate_iz` | float(3) | Locked discipline metrics | no |
| `team_context` | str | `pre-PHI (nphl)` or `PHI (pos)` — provenance flag | no |

> **Nullability is a feature.** A null in `bat_speed_mu` is the coverage gate working. Any downstream consumer that fills it violates the governing policy. DQ-10 and DQ-11 fail the build if a value appears.

### Receipt `b6_phase_delta` — grain: one row per metric

| Column | Definition |
|---|---|
| `metric` | Metric name |
| `phase_a`, `phase_b` | Value in each phase |
| `delta` | `phase_b − phase_a` |
| `pct_change` | `100 × delta / phase_a`, null where `phase_a ≈ 0` |
| `phase_a_label`, `phase_b_label` | Human-readable phase boundaries |
| `phase_a_pa/bips`, `phase_b_pa/bips` | **Sample size travels with every row** |

### Full receipt register (24)

| # | Receipt | Grain | Feeds |
|---|---|---|---|
| 1 | `a1_career_season_spine` | season | Report §1, dashboard Overview |
| 2 | `a2_bat_tracking_coverage` | season | Report §7, dashboard NULL policy |
| 3 | `x1_imputation_harm` | season | Report §7, Fig 4 |
| 4 | `b1_monthly_2026` | month | Report §2, dashboard Decay |
| 5 | `b2_monthly_2025` | month | Comparison backdrop |
| 6 | `b3_rolling_bip_2026` | BIP index | Fig 1, dashboard Decay |
| 7 | `b4_rolling_swings_2026` | swing index | Fig 2, dashboard Decay |
| 8 | `b5_phase_split_2026` | phase | Report §2 |
| 9 | `b6_phase_delta` | metric | Report §2, dashboard delta table |
| 10 | `c1_la_distribution` | phase × LA band | **Report §3, Fig 3** — the mechanism |
| 11 | `c2_pitch_group_phase` | phase × pitch group | Report §3 |
| 12 | `c3_handedness_phase` | phase × `p_throws` | Supporting |
| 13 | `c4_velocity_band_phase` | phase × velocity band | Report §3 |
| 14 | `c5_batted_ball_mix` | window × `bb_type` | Supporting |
| 15 | `c6_spray_direction_phase` | phase × direction | Report §3 |
| 16 | `c7_count_state_phase` | phase × count state | Report §8.2 |
| 17 | `d1_swing_path_year` | season | Report §4 |
| 18 | `d2_swing_path_group` | season × pitch group | Supporting |
| 19 | `d3_attack_angle_outcome` | season × AA bucket | Report §4 |
| 20 | `d4_contact_depth` | season / phase | Report §4 |
| 21 | `e1_phillies_lhb_pool` | player × season | Peer context |
| 22 | `e2_lhb_percentiles_2026` | metric | Report §5 |
| 23 | `dq_scorecard` | rule | Report header, 05, 07 |
| 24 | `freshness_manifest` | source | 07 |

Plus `dp_uc32_headline.json` (report/dashboard binding) and `dp_uc32_verification_results.csv` (written by the harness).

---

## 3. `technical-lineage-builder` — column-level lineage

### Hop map

```
HOP 0  data/phillies/phils_{2015..2026}.parquet   [12 files]
       data/opponents/schwarber.parquet           [1 file, 2015-2021]
         |
HOP 1  filter phillies_role == 'batting'                    -> pos
       filter batter == 656941 on both sources              -> ENTITY LOCK
       concat(nphl_sch, pos)
         |
HOP 2  drop_duplicates(game_pk, at_bat_number, pitch_number)   [0 dropped]
       filter game_type == 'R'                                 [1,275 dropped]
       sort(game_date, game_pk, at_bat_number, pitch_number)
         |                                          -> car  (24,891 rows)
HOP 3  coerce_numeric(27 cols: Int64/Float64 -> float64)       [Q-2 fix]
       add_swing_features()
         |
HOP 4  aggregate -> 24 receipts
         |
HOP 5  figures (5) + headline.json
         |
HOP 6  report.md -> PDF ; receipts -> dashboard.html
```

### Column-level transformation for every derived CDE

| Target | Source column(s) | Transformation | Hop |
|---|---|---|---|
| `is_swing` | `description` | `∈ SWINGS` (8 values) | 3 |
| `is_whiff` | `description` | `∈ WHIFFS` (5 values) | 3 |
| `is_bip` | `type` | `== 'X'` | 3 |
| `ss_flag` (SW-1) | `launch_angle`, `type` | `1` if BIP and `8 ≤ la ≤ 32`; `0` if BIP; else NULL | 3 |
| `ideal_flag` (SW-2) | `launch_angle`, `launch_speed`, `type` | `1` if BIP and `8 ≤ la ≤ 32` and `ev ≥ 95`; `0` if BIP; else NULL | 3 |
| `bt_measured` (SW-7) | `bat_speed`, `description` | `is_swing AND bat_speed IS NOT NULL` | 3 |
| `fast_swing` (SW-3) | `bat_speed` | `bat_speed ≥ 75` where measured; **NULL where not measured** | 3 |
| `plate_speed` | `vx0,vy0,vz0,ax,ay,az` | Solve `t` at `y = 17/12` from `y(t) = 50 + vy0·t + ½·ay·t²`; `‖v(t)‖ × 0.681818` | 3 |
| `squared_up_pct` (SW-4) | `launch_speed`, `bat_speed`, `plate_speed` | `ev / (1.23·bat_speed + 0.2306·plate_speed)` | 3 |
| `squared_up` | `squared_up_pct` | `≥ 0.80` | 3 |
| `blast` (SW-9) | `squared_up`, `fast_swing` | both `== 1`, NULL if either unmeasured | 3 |
| `aa_fit` (SW-5) | `attack_angle` | `5 ≤ aa ≤ 20` where measured, else NULL | 3 |
| `contact_depth` (SW-6) | `intercept_ball_minus_batter_pos_y_inches`, `type` | passthrough on BIP | 3 |
| `pitch_group` | `pitch_type` | 14-value map → Fastballs / Offspeed / Breaking / Other | 4 |
| `loc_x`, `loc_y` | `hc_x`, `hc_y` | `2.5·(hc_x − 125.42)`, `2.5·(198.27 − hc_y)` | 4 |
| `hit_direction` | `loc_x`, `loc_y` | LHB rule: Pull if `loc_y ≤ 4.7·loc_x`; Oppo if `loc_y ≤ −4.7·loc_x`; else Straightaway | 4 |
| `phase` | `game_date` | `< split_date` → A, else B. `split_date` = date of the median-index BIP | 4 |
| `la_bucket` | `launch_angle` | 6 bins: −90/−10/8/20/32/50/90, left-closed | 4 |
| `velo_band` | `release_speed` | 4 bins: 0/88/93/96/110 | 4 |
| `count_state` | `balls`, `strikes` | `strikes == 2` → Two strikes; `balls > strikes` → Ahead; else Even/Behind | 4 |
| `bt_coverage` (SW-7) | `bat_speed`, `is_swing` | `count(bat_speed) / count(swings)` | 4 |
| `damage band share` (SW-8) | `la_bucket` | share of the `Ideal high (20-32)` bin | 4 |

### The coverage-gate suppression step — lineage of a *deliberate* null

In `bat_tracking_block()`, after aggregation:

```python
for col, cov in [("bat_speed_mu","bt_swings"), ..., ("aa_fit_rate","aa_swings")]:
    out[col] = out[col].where(out[cov] > 0)
```

Nine output columns are set to NULL wherever the measured denominator is zero. **This is the only place in the pipeline where a computed value is deliberately discarded**, and it is the mechanical implementation of the DPO's no-imputation decision. Verified by DQ-10, DQ-11 and V-16 through V-18.

### Lineage completeness

| Check | Result |
|---|---|
| Every published column traces to a physical source or a documented transformation | ✅ 100% |
| Every transformation is reproducible from this document alone | ✅ |
| Any hop where row count changes is quantified | ✅ (dedup 0, game_type 1,275) |
| Any hop where a value is deliberately nulled is documented | ✅ (the coverage gate, above) |
| Circular dependencies | none |
| Manual carry-ins | **none** — no hand-keyed value enters this build |
