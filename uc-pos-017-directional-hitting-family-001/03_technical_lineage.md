# 03 · Technical Lineage
**`dp_uc46` · column-level, source → KPI**

## 1. Lineage table

| CDE | Source data domain | Physical column | Transformation logic | Lands in |
|---|---|---|---|---|
| Pitch Result Type | Pitch Outcomes | `type` | `df[df.type == 'X']` — retains balls in play only | `classifiable_bip` |
| Hit Coordinate X | Hit Coordinates | `hc_x` | `notna()` gate, then `loc_x = 2.495671 × (hc_x − 125.42)` | `derive_loc` → `loc_x` |
| Hit Coordinate Y | Hit Coordinates | `hc_y` | `notna()` gate, then `loc_y = 2.495671 × (198.27 − hc_y)` — sign flipped because `hc_y` increases *toward* the plate | `derive_loc` → `loc_y` |
| Batter Handedness | Batter Identity | `stand` | Branch selector: `'R'` takes the first `np.select` ladder, anything else the mirrored one | `hit_direction` |
| — (derived) | — | `loc_x`, `loc_y`, `stand` | Wedge test at slope ±4.7. RHB: `loc_y ≤ −4.7·loc_x` → Pull; `loc_y > −4.7·loc_x ∧ loc_y > 4.7·loc_x` → Straightaway; `loc_y ≤ 4.7·loc_x` → Oppo. LHB: signs mirrored. | `hit_direction` → `hit_direction` |
| Batted Ball Type | Batted Ball Classification | `bb_type` | Added to the grouping key; no filtering, no imputation | `bb_type_profile`, `pull_air_rate` |
| Plate Appearance Description | Game Events | `des` | `size()` of this column is the row counter. No semantic use — inherited from cell 50 verbatim so the share arm reproduces. | all counts |
| Launch Angle | Batted Ball Tracking | `launch_angle` | `count/min/max/mean/std/quantile(.05)/quantile(.95)` per cell. `count()` excludes NULL → `n_la` | `bb_type_profile` |
| Exit Velocity | Batted Ball Tracking | `launch_speed` | same seven aggregates → `n_ev`, `min_ev`, `max_ev`, `mu_ev`, `std_ev`, `p5_ev`, `p95_ev` | `bb_type_profile` |
| Hit Distance | Batted Ball Tracking | `hit_distance_sc` | same seven aggregates → `n_dist`, … | `bb_type_profile` |

## 2. Transformation chain

```
pos (pitch grain, 70,021 rows 2024-26 R)
 │
 ├─ classifiable_bip(level, df)            DR-0 · DEN-1
 │    type=='X'                            → 12,360 BIP
 │    hc_x.notna() & hc_y.notna()          → 12,351 classifiable BIP   (9 dropped)
 │
 ├─ derive_loc(level, bip)                 PA-L1 · RATIFIED (closes O-7)
 │    loc_x, loc_y in feet from home plate
 │
 ├─ hit_direction(level, bip)              DR-1 · VERBATIM cell 56
 │    → {Pull, Straightaway, Oppo}          'not grouped' count: 0
 │
 ├─ assert_spray_convention(level, bip)    O-15 control · raises on inversion
 │
 ├─► direction_rate(level, bip)            DR-2 · grain: level
 │      n_bip, pull_n, straight_n, oppo_n
 │      pull_rate, straight_rate, oppo_rate     ← KPIs, sum to 1 (DR-3)
 │      below_floor                              ← FL-1
 │
 ├─► bb_type_profile(level, bip)           BB-1 · grain: level × bb_type
 │      SHARE arm    bips, total_level, share    ← reproduces cell 50 exactly
 │      PROFILE arm  n/min/max/mu/std/p5/p95 × {la, ev, dist}
 │      │
 │      └─ level = [..., 'hit_direction']  ⇒ total_level becomes DIRECTION BIP
 │            filter Oppo × line_drive ⇒ share IS oppo_ld_rate   ← LD-1
 │
 └─► pull_air_rate(level, bip)             PATCHED cell 56
        pull_airs = Pull ∧ bb_type != 'ground_ball'
        pull_air_rate = pull_airs / classifiable BIP    ← BREAKING, see 08
```

## 3. Why `oppo_ld_rate` has no function of its own

`bb_type_profile` computes `total_level` by grouping at the **passed** `level`.
Adding `hit_direction` to that level therefore moves the denominator from
"all BIP" to "BIP in this direction" — with no new code, and with the LD-1
ruling satisfied by construction rather than by a second implementation that
could drift from the first.

```python
prof = bb_type_profile(['player_name', 'hit_direction'], bip)
oppo_ld_rate = prof.query("hit_direction == 'Oppo' and bb_type == 'line_drive'").share
```

This is the DPO's "one function, one grain" instruction applied to the second
KPI as well as the first, and it is the direct mitigation for the drift that
produced four copies of `hit_direction`.

## 4. Impl binding

| Object | Source of truth | Binding |
|---|---|---|
| `hit_direction` | `dp_uc46_kernel.py` | Supersedes cell 56's embedded copy and the `dp_uc37`/`dp_uc40`/`dp_uc42` transcriptions |
| `derive_loc` | `dp_uc46_kernel.py` | Supersedes the PA-L1 copies in `dp_uc37`/`dp_uc40`/`dp_uc42` |
| `direction_rate` | `dp_uc46_kernel.py` | Supersedes `dp_uc42_kernel.directional_rate_table` |
| `pull_air_rate` | `dp_uc46_kernel.py` | Supersedes cell 56, `pull_air_rate_fix`, and the three `pulled_air(df, level)` copies |

`impl_hash` is **UNAVAILABLE** — no mechanism exists in this environment to compute
and bind it. This is F1, the standing friction the `get_function_source` MCP tool
(`MCP_SERVER_DESIGN_2026-06-30` §4.5) is designed to close. Carried as certification
condition **C-3** in `06`, not silently omitted.
