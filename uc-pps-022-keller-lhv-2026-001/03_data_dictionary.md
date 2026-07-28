# 03 — Data Dictionary
## UC #27 · `uc-pps-022` · Layer 2

Agents: `data-dictionary`, `metadata-mapper`, `data-tagger`

---

## 1. Source table

### `data/opponents/lhvp26.parquet`

Pitch-level Statcast for Lehigh Valley IronPigs **pitching**, 2026. One row per pitch.
Grain key: `(game_pk, at_bat_number, pitch_number)`.

| Physical column | Type | Description | Glossary CDE | Mapping |
|---|---|---|---|---|
| `pitcher` | int | MLBAM pitcher id. **Entity lock key** | Pitcher Identity | exact |
| `player_name` | str | "Last, First". Non-unique across Kellers — display only, never a filter | Pitcher Identity (label) | exact |
| `batter` | int | MLBAM batter id | Batter Identity | exact |
| `game_pk` | int | MLBAM game id | Game Identity | exact |
| `game_date` | date | Game date | Game Date | exact |
| `game_type` | str | `R` = regular season. Filtered to `R` | Game Type | exact |
| `game_year` | int | Season; joins to wOBA constants | Season | exact |
| `at_bat_number` | int | Sequential PA within game | Plate Appearance | exact |
| `pitch_number` | int | Sequential pitch within PA | Pitch Sequence | exact |
| `pitch_type` / `pitch_name` | str | Statcast pitch classification (code / label) | Pitch Type | exact |
| `release_speed` | float | Release velocity, mph | Velocity | exact |
| `effective_speed` | float | Perceived velocity adjusted for extension | Effective Velocity | exact |
| `release_spin_rate` | float | Spin rate, rpm | Spin Rate | exact |
| `spin_axis` | float | Spin axis, degrees | Spin Axis | exact |
| `release_extension` | float | Release distance toward plate, ft | Extension | exact |
| `release_pos_x/y/z` | float | Release point coordinates, ft | Release Point | exact |
| `arm_angle` | float | Arm slot, degrees | Arm Slot | exact |
| `pfx_x` | float | Horizontal movement, ft, **catcher perspective**. Negative = arm side for a RHP | Horizontal Break | fuzzy — sign convention documented; `api_break_x_arm` preferred for publication |
| `pfx_z` | float | Induced vertical break, ft, gravity-corrected | Induced Vertical Break | exact |
| `api_break_x_arm` | float | Horizontal break, **inches, arm-side positive**. Published in preference to `pfx_x` | Horizontal Break (arm-relative) | exact |
| `api_break_z_with_gravity` | float | Total vertical drop including gravity, inches | Vertical Break | exact |
| `plate_x` | float | Horizontal plate location, ft, catcher perspective | Pitch Location | exact |
| `plate_z` | float | Vertical plate location, ft above ground | Pitch Location | exact |
| `sz_top` / `sz_bot` | float | Batter-specific strike zone boundaries, ft | Strike Zone Boundary | exact |
| `zone` | int | Statcast zone 1-9 (in-zone) / 11-14 (out-of-zone) | Zone | exact |
| `stand` | str | Batter handedness, `L`/`R` | Batter Handedness | exact |
| `p_throws` | str | Pitcher handedness | Pitcher Handedness | exact |
| `balls` / `strikes` | int | **PRE-pitch** count state | Count State | exact — lag documented in `01_ §C.3` |
| `type` | str | `B` ball / `S` strike / `X` in play | Pitch Result Class | exact |
| `description` | str | Detailed pitch outcome | Pitch Outcome | exact |
| `events` | str | Terminal PA outcome; null on non-terminal pitches | Plate Appearance Outcome | exact |
| `des` | str | Human-readable PA description; populated on terminal pitch only | PA Narrative | exact |
| `bb_type` | str | `ground_ball` / `fly_ball` / `line_drive` / `popup` | Batted Ball Type | exact |
| `launch_speed` | float | Exit velocity, mph | Exit Velocity | exact |
| `launch_angle` | float | Launch angle, degrees | Launch Angle | exact |
| `estimated_woba_using_speedangle` | float | Expected wOBA from EV/LA | Expected wOBA | exact |
| `estimated_ba_using_speedangle` | float | Expected BA from EV/LA | Expected BA | exact |
| `n_thruorder_pitcher` | int | Times through the order for this PA | Times Through Order | exact |
| `inning` | int | Inning | Inning | exact |
| `home_team` / `away_team` | str | Team codes | Team | exact |
| `bat_speed` / `swing_length` | float | **Not captured at AAA — 0% populated.** No product dependency | Bat Tracking | unmapped — documented exclusion |

**Mapping summary: 34 published columns · 33 exact · 1 fuzzy (documented) · 0 ambiguous ·
0 unmapped-in-use.**

### `wOBA and FIP Constants.csv`

Conformed season dimension. One row per season. Joined `game_year → Season`.

| Column | Description | Note |
|---|---|---|
| `Season` | Season year — join key | |
| `wBB`, `wHBP`, `w1B`, `w2B`, `w3B`, `wHR` | FanGraphs linear weights | **MLB weights applied to AAA events** — see `01_ §C.6` |
| `wOBAScale`, `cFIP`, `R/PA`, `R/W` | Supporting constants | Not used in this product |

---

## 2. Published output tables

All under `out/`. One row per grain stated; every column traces to `06_`.

| File | Grain | Contents |
|---|---|---|
| `dp_uc26_results_headline.csv` | pitcher-population | Season line, Keller vs staff baseline. Carries `ip_computed` (decimal thirds), `ip_baseball` (standard notation), and `outs_recorded` |
| `dp_uc26_game_lines.csv` | start | Per-start line: IP, BF, K, BB, H, HR, pitches, opponent, site |

> **Innings notation — a deliberate redundancy.** `ip` is decimal (`36.67`); `ip_baseball` is
> standard notation (`36.2`, meaning 36 innings and 2 outs); `outs_recorded` is the raw
> integer (`110`). These look like three different numbers and are one. Publishing only one
> representation guarantees a reader eventually reads `36.2` as `36.7` — so all three are
> emitted and the report states which convention it uses.
| `dp_uc26_by_stand.csv` | population × batter stand | Results split L/R with baseline |
| `dp_uc26_arsenal.csv` | pitch type | Usage, velo, movement, slot, process KPIs, contact quality, attack-zone mix |
| `dp_uc26_arsenal_by_stand.csv` | batter stand × pitch type | Usage share |
| `dp_uc26_process_kpis.csv` | population | Full locked process panel + baseline |
| `dp_uc26_process_by_stand.csv` | population × batter stand | Process panel split L/R + baseline |
| `dp_uc26_pitch_kpis.csv` | pitch type | Process panel per pitch |
| `dp_uc26_contact_quality.csv` | pitch type | EV, LA, hard-hit, xwOBAcon, batted-ball mix |
| `dp_uc26_contact_quality_by_stand.csv` | batter stand × pitch type | Same, split |
| `dp_uc26_recency_split.csv` | start-block | Starts 1-4 vs 5-8, full process panel + results |
| `dp_uc26_recency_usage.csv` | start-block × pitch type | Usage share across the same split |
| `dp_uc26_tto.csv` | times through order | Results + process by TTO |
| `dp_uc26_velo_by_inning.csv` | inning | Four-seam velocity by inning |
| `dp_uc26_location_profile.csv` | population × pitch type | Above-zone rate, mean height, attack-zone mix vs baseline |
| `dp_uc26_first_pitch.csv` | batter stand × pitch type | 0-0 usage and strike rate |
| `dp_uc26_two_strike.csv` | batter stand × pitch type | Two-strike usage, whiff, putaway |
| `dp_uc26_home_runs.csv` | home run | All 5 HR: count, pitch, location, EV/LA, TTO |
| `dp_uc26_sr_m1_provisional.csv` | population | **PROVISIONAL** SR-M1 |
| `dp_uc26_sr_m1_by_stand.csv` | population × stand | **PROVISIONAL** |
| `dp_uc26_sr_m1_by_half.csv` | start-block | **PROVISIONAL** |
| `dp_uc26_sr_m1_variants.csv` | population | **PROVISIONAL** — three-variant ratification harness |
| `dp_uc26_sr_m1_leaderboard.csv` | pitcher | **PROVISIONAL** — LHV staff context, min 40 PA |
| `dp_uc26_dq_scorecard.csv` | check | 14 DQ checks with verdict and severity |
| `dp_uc26_freshness_manifest.csv` | source | Window, volume, fitness per source |

Every CSV carrying SR-M1 has a literal `STATUS` column reading
`PROVISIONAL — NOT RATIFIED`. The banner travels with the data, not just the prose.

---

## 3. `data-tagger` classification proposal

| Element | Sensitivity | Domain | Subject area | Product |
|---|---|---|---|---|
| All source columns | **PUBLIC-DERIVED** | Baseball Operations | Pitching | `uc-pps-022` |
| All output CSVs | **INTERNAL** | Baseball Operations | Pitching / Advance Scouting | `uc-pps-022` |
| Reader report + persona card | **INTERNAL** | Baseball Operations | Pitching | `uc-pps-022` |
| SR-M1 outputs | **INTERNAL — PROVISIONAL** | Baseball Operations | KPI Governance | `uc-pps-022` |

**Rationale.** Statcast pitch data is publicly broadcast and commercially available; it is
not confidential player information. The *derived analysis* — specifically the gameplan
recommendations and the identified exposures — is competitively sensitive and classified
INTERNAL. `privacy-watchdog` concurs (`07_ §3`).

**No PII.** Player names and MLBAM ids are public professional identifiers. No health,
contract, biometric, or personal-contact data is present in the source or the outputs.
