# 01 · Source Profile & Fitness for Purpose
**`dp_uc46` · profiled 2026-09-17 against the live parquet cache**

## 1. Rule-1 search receipt (Layer 1, mandatory)

Run before any element was called new. Scope: `data-products/`, `contract/`,
`Baseball Functions.ipynb`.

```
grep -rn "def [a-z_]*\(oppo\|direction\|spray\|pull\)[a-z_]*(" data-products contract
grep -rli "oppo" data-products contract
grep -rn "Oppo'" data-products --include=*.py
grep -rn "def battedball_profile\|min_la\|la_std\|dist_std" data-products --include=*.py
```

| Element | Prior art found | Disposition |
|---|---|---|
| `oppo_rate` | `dp_uc42_kernel.directional_rate_table` L144 (`oppo_rate`, `oppo_n`); asserted in `dp_uc42a_verification.py` L156-158 | **PROMOTE** — provisional WF-1/WF-2 → governed KPI of `direction_rate` |
| `hit_direction` | `Baseball Functions.ipynb` cell 56 (authority); verbatim copies at `dp_uc37_kernel.py:461`, `dp_uc40_kernel.py:471`, `dp_uc42_kernel.py:87` | **EXTRACT** — 4 copies → 1 object |
| `derive_loc` / PA-L1 | `dp_uc37_kernel.py` (origin), reused `dp_uc40`, `dp_uc42` | **RATIFY** — provisional → governed, closes O-7 |
| `pull_air_rate` | cell 56 (unrunnable); `pull_air_rate_fix` in `dp_uc37`/`dp_uc40`; `pulled_air(df, level)` in `dp_uc24`, `dp_uc31`, `marsh_breakout_analysis` | **PATCH + RECONCILE ALIASES** |
| `bb_type` shares | `bb_type_by_level`, cell 50 — governed, glossary + lineage present | **EXTEND** — share arm reproduced exactly (family D) |
| `battedball_profile` | `dp_uc34_kernel.py:295`, `dp_uc37:396`, `dp_uc40:406` (CR-1) | Design pattern reused; different output |
| min/max/std of `launch_angle`/`launch_speed`/`hit_distance_sc` | **0 matches repo-wide** | **NEW** |
| `oppo_ld_rate` | 0 matches | **NEW**, materialised not functionised |

**Aliases reconciled** (Rule 3 — a notebook alias is not a name):
`pull_air_rate` (governed) ← `pulled_air`, `pulled_air_rate`, `pull_air_rate_fix`.
`hit_direction` (governed) — no competing alias.

## 2. Source system

Pandas/parquet cache at `data/phillies/phils_<year>.parquet`, 122 columns,
delegated through `mlb_data.py`. `pos` = Phillies batting rows, selected by
`(home_team=='PHI' & inning_topbot=='Bot') | (away_team=='PHI' & inning_topbot=='Top')`.
Window profiled: **2024–2026, `game_type=='R'`**, 70,021 pos pitch rows.
`phils_2026.parquet` mtime 2026-09-17 22:03 — current.

**O-7 re-confirmed at intake:** `'loc_x' in df.columns → False`, `'hc_x' in df.columns → True`.
Cell 56 as written cannot execute against this schema. Unchanged since first reported
on uc-pos-011 (2026-08-15).

## 3. CDE fitness

| CDE | Physical column | 2026 null on BIP | Fitness |
|---|---|---|---|
| Hit Coordinate X | `hc_x` | 3 / 3,905 (0.077%) | **FIT.** Sensor arm of the direction classifier. |
| Hit Coordinate Y | `hc_y` | same rows | **FIT.** |
| Batter Handedness | `stand` | 0 | **FIT.** Required — the boundary is stand-aware. |
| Pitch Result Type | `type` | 0 | **FIT.** `'X'` gates the BIP population. |
| Batted Ball Type | `bb_type` | **0 (0.00%)** | **FIT — complete classifier.** The reason shares and profile split into two populations. |
| Launch Angle | `launch_angle` | 12 (0.307%) | **FIT with sensor boundary.** Own `n_la`. |
| Exit Velocity | `launch_speed` | 12 (0.307%) | **FIT with sensor boundary.** Own `n_ev`. |
| Hit Distance | `hit_distance_sc` | 15 (0.384%) | **FIT with sensor boundary + a value quirk.** Own `n_dist`. See §5. |
| Plate Appearance Description | `des` | 0 | **FIT.** Counted for size only (cell 50 convention, inherited). |

Full profile: `out/01_source_profile.csv`.

## 4. The finding that shaped the design — three different null regimes

| Year | BIP | untracked hc | `bb_type` null | `la` null | `ev` null | `dist` null |
|---|---|---|---|---|---|---|
| 2024 | 4,217 | 0 (0.000%) | 0 | 8 (0.190%) | 11 (0.261%) | 16 (0.379%) |
| 2025 | 4,238 | 6 (0.142%) | 0 | 6 (0.142%) | 8 (0.189%) | 9 (0.212%) |
| 2026 | 3,905 | 3 (0.077%) | 0 | 12 (0.307%) | 12 (0.307%) | 15 (0.384%) |

Four columns, four different null rates, on the same rows. `bb_type` is complete;
the three sensors are not; and the sensors do not agree with each other.

**This is why the profile carries `n_la`, `n_ev` and `n_dist` separately** rather than
one `n` per cell. A single shared `n` would be wrong for at least two of the three
statistics in almost every cell, and wrong in the direction that makes the data look
better than it is. It is also why `hit_direction`'s exclusion population
(`hc_x`/`hc_y` null) is **not** the same as the profile's exclusion population
(`launch_angle` null) — a BIP can be directionally classifiable and un-profileable,
or the reverse.

## 5. Two data quirks found while profiling

1. **`hit_distance_sc == 0` on 22 ground balls** (2024–26). Zero feet is a sensor
   placeholder, not a measurement — it is inside the non-null population and will
   drag `min_dist` and `mu_dist` for every ground-ball cell. Raised as **DQ-07
   (WARN, not FAIL)** in `05`; not silently filtered, because filtering a published
   value on suspicion is a bigger governance problem than reporting it with a flag.
2. **`launch_angle` spans exactly −90.0 to 89.0.** The bounds are suspiciously round.
   Raised as **DQ-05 (range validity)**; no action, but any future cell whose
   `min_la`/`max_la` lands exactly on ±90 should be read as a clip, not an observation.

## 6. Coordinate convention, derived not assumed (O-15)

| stand | direction | median `loc_x` (ft) |
|---|---|---|
| R | Pull | **−64.18** |
| R | Oppo | +104.37 |
| R | Straightaway | −3.79 |
| L | Pull | **+82.82** |
| L | Oppo | −102.35 |
| L | Straightaway | 0.00 |

Negative `loc_x` is the left side of the field. A right-handed hitter's pulled balls
sit there; a left-handed hitter's sit opposite. `assert_spray_convention` enforces
both signs and **raises** rather than publishing — verified to fire on an inverted
frame (family A).

`not grouped` count across 12,351 classified BIP: **0**. The three-way wedge is
exhaustive, so the DR-3 sum-to-1 guarantee is structural, not coincidental.

## 7. Fitness verdict

**FIT FOR PURPOSE** for the whole directional family at season, season×stand, and
player×season grain, with two standing conditions:

- **C-1.** Any grain finer than player×season must carry FL-1 suppression. At
  player×season in 2026, 17 of the Phillies' hitters clear 25 classifiable BIP;
  the rest are suppressed, not published.
- **C-2.** `hit_distance_sc` statistics on ground-ball cells are WARN-flagged
  until DQ-07 is adjudicated.
