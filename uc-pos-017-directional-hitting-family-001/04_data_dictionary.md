# 04 · Data Dictionary
**`dp_uc46` · physical elements consumed, and every column published**

## 1. Consumed physical columns

| Column | Type | Domain | Definition | Null regime (2026 BIP) | CDE |
|---|---|---|---|---|---|
| `type` | str | Pitch Outcomes | Pitch result class. `'X'` = ball in play, `'S'` = strike, `'B'` = ball. | complete | Pitch Result Type |
| `hc_x` | float | Hit Coordinates | Horizontal hit location in Statcast display units. Increases toward the right side of the field. Origin is **not** home plate. | 0.077% | Hit Coordinate X |
| `hc_y` | float | Hit Coordinates | Vertical hit location in Statcast display units. **Decreases** as the ball travels away from the plate. | 0.077% | Hit Coordinate Y |
| `stand` | str | Batter Identity | Batter handedness, `'L'` or `'R'`. Never NULL on a BIP. | complete | Batter Handedness |
| `bb_type` | str | Batted Ball Classification | Statcast batted-ball class: `ground_ball`, `line_drive`, `fly_ball`, `popup`. A **derived classifier**, not a sensor — complete wherever a BIP exists. | **0.000%** | Batted Ball Type |
| `launch_angle` | float | Batted Ball Tracking | Vertical launch angle in degrees. Observed range −90.0 to 89.0. | 0.307% | Launch Angle |
| `launch_speed` | float | Batted Ball Tracking | Exit velocity off the bat, mph. Observed 11.5 to 117.2. | 0.307% | Exit Velocity |
| `hit_distance_sc` | float | Batted Ball Tracking | Estimated travel distance, feet. **`0` appears as a sensor placeholder on 22 ground balls** — see DQ-07. | 0.384% | Hit Distance |
| `des` | str | Game Events | Plate appearance description text. Used only as a row counter (`size()`), per the cell-50 convention. | complete | PA Description |
| `game_pk`, `at_bat_number`, `pitch_number` | int | Game Events | `PITCH_KEY`, the dedup grain. | complete | Pitch Identity |

## 2. Published columns — `direction_rate(level, df)`

| Column | Type | Definition | Null behaviour |
|---|---|---|---|
| *level columns* | — | As passed by the caller | — |
| `n_bip` | int | Classifiable balls in play in the cell. The denominator for all three rates. | never NULL |
| `pull_n` / `straight_n` / `oppo_n` | int | Count in each direction. Count columns **are** zero-filled — a direction with no batted balls genuinely has zero. | never NULL |
| `pull_rate` / `straight_rate` / `oppo_rate` | float | Count ÷ `n_bip`. Sum to 1 by construction. | **NULL when `n_bip == 0`** — not 0.0. A cell with no tracked BIP has no rate. |
| `below_floor` | bool | `n_bip < 25` (FL-1). True means computed but not publishable unflagged. | never NULL |

## 3. Published columns — `bb_type_profile(level, df)`

Grain: *level* × `bb_type`.

### Share arm — over the complete classifier
| Column | Type | Definition |
|---|---|---|
| `bips` | int | Balls in play of this `bb_type` in this cell |
| `total_level` | int | Balls in play across all `bb_type` at the passed `level`. **When `hit_direction` is in the level, this is direction BIP** — the mechanism behind `oppo_ld_rate`. |
| `share` | float | `bips / total_level`. Reproduces cell 50's `share` exactly. |
| `below_floor` | bool | `total_level < 25` (FL-1) |

### Profile arm — over the incomplete sensors
Emitted once per sensor, suffix `la` (`launch_angle`), `ev` (`launch_speed`),
`dist` (`hit_distance_sc`).

| Column | Type | Definition | Caution |
|---|---|---|---|
| `n_<sfx>` | int | Non-null observations of that sensor in the cell. **Each sensor has its own.** | `n_la ≠ n_ev ≠ n_dist` is normal, not a bug. Never substitute `bips`. |
| `min_<sfx>` / `max_<sfx>` | float | Extremes | **Single observations.** Outlier-fragile. Not a range estimate. |
| `mu_<sfx>` | float | Arithmetic mean of non-null values | Not re-aggregable across cells |
| `std_<sfx>` | float | Sample standard deviation, ddof=1 | **NULL when `n < 2`** |
| `p5_<sfx>` / `p95_<sfx>` | float | 5th / 95th percentile | The intended range display. Use these, not min/max, on any visual. |

### Naming note (O-20)
This build uses the DPO's stated convention: **statistic first, sensor second**
(`mu_la`, `min_ev`, `p95_dist`). The notebook's `inds` (cell 42) uses the reverse
(`la_mu`, `ev_mu`, `dist_mu`). Both conventions now exist in the repo. Not
reconciled here — `inds` has 74 call sites across 14 files. Open item for the
next pass.

## 4. Published columns — `pull_air_rate(level, df)`

| Column | Type | Definition |
|---|---|---|
| `total_bips` | int | **Classifiable** BIP in the cell (narrowed from all BIP — breaking, see `08`) |
| `pull_airs` | int | Pulled batted balls that are not ground balls |
| `pull_air_rate` | float | `pull_airs / total_bips`. NULL when `total_bips == 0`. |
| `below_floor` | bool | FL-1 |

## 5. Derived intermediates (present on the BIP frame, not a KPI)

| Column | Type | Definition |
|---|---|---|
| `loc_x` | float | Feet from home plate, horizontal. **Negative is the left side of the field**, both handednesses. |
| `loc_y` | float | Feet from home plate, toward the outfield. Positive. |
| `hit_direction` | str | `Pull` / `Straightaway` / `Oppo`. `not grouped` is a defined default that has never fired (0 of 12,351). |
