# 03 — Data Dictionary & Technical Lineage

**Agents:** `data-dictionary` → `technical-lineage-builder`
**Layer 2 — Design** · UC #32 · `uc-pos-008` · `dp_uc31`

---

## 1. Physical data dictionary — source fields consumed

Every Statcast field that reaches an output, with its role. Fields present in the parquet but unused are omitted.

### 1.1 Identity & partition keys

| Column | Type | Role | Notes |
|---|---|---|---|
| `batter` | int | **Entity lock** | MLBAM id. `== 650333`. Never a name filter (DQ-01/02) |
| `game_pk` | int | Grain key | Part of the pitch key; also the game counter for per-game rates |
| `at_bat_number` | int | Grain key | Sequential across **both** teams within a game; ordering basis for slot reconstruction |
| `pitch_number` | int | Grain key | Within plate appearance |
| `game_date` | date | Window | Freshness bounds |
| `game_year` | int | Partition | Primary vs shadow; wOBA weight join key |
| `game_type` | str | Filter | `'R'` only |
| `phillies_role` | str | Filter | Comparison set only: `'batting'` |

### 1.2 Event & outcome

| Column | Role | Governance note |
|---|---|---|
| `events` | Terminal outcome of a PA | Non-null only on the PA's last pitch. **`truncated_pa` is a continuation marker** — see §3 |
| `description` | Per-pitch result | Basis for `SWINGS`/`WHIFFS` lists |
| `type` | `B`/`S`/`X` | **`'X'` is the only valid gate for contact-quality work** (O3) |
| `des` | Narrative | Name resolution by modal parse only. Never parsed for outcomes |
| `woba_value`, `babip_value` | Statcast-computed | **Not used** — season weights joined from the constants file instead |

### 1.3 Count & context

| Column | Role |
|---|---|
| `balls`, `strikes` | Count state. `strikes == 2` defines the AR-1/AR-2 population |
| `on_1b`, `on_2b`, `on_3b` | Base state. **Non-null = runner present** (the value is the runner's id) |
| `outs_when_up` | Out state |
| `inning`, `inning_topbot` | Team attribution for the comparison set |
| `bat_score`, `post_bat_score` | Runs scored on the PA = difference |
| `delta_run_exp` | **AR-6 foundation.** Statcast's per-pitch run-expectancy delta |

### 1.4 Pitch characteristics

| Column | Role |
|---|---|
| `pitch_type` | AR-3 grain, via `PITCH_GROUP` map |
| `p_throws` | AR-3 grain |
| `stand` | Asserted `== 'L'` on every row (DQ-05) |
| `zone` | `<= 9` = in zone (locked inherited definition) |

### 1.5 Contact quality

| Column | Role | Caution |
|---|---|---|
| `launch_speed` | EV, hard-hit | **Populated on fouls 2023+.** Always gate on `type == 'X'` |
| `launch_angle` | LA, sweet spot | Same |
| `launch_speed_angle` | Barrel (`== 6`) | Same |
| `bb_type` | GB/FB/LD/PU | Non-null only on balls in play |
| `estimated_woba_using_speedangle` | xwOBA, xwOBAcon | **Denominator varies by event type** — O4. Honest count published as `xwoba_con_n` |
| `hc_x`, `hc_y` | Spray angle | Locked `pulled_air()` formula |
| `bat_speed`, `swing_length`, `attack_angle` | Bat tracking | **2023+ only.** Era-limited, disclosed |

---

## 2. Derived elements produced by this build

| Element | Grain | Definition | Consumed by |
|---|---|---|---|
| `pa_frame` (strict PA spine) | 1 row / plate appearance | Terminal pitch of each PA, excluding `{NA, pickoff_1b, truncated_pa}` | All AR-* KPIs |
| `men_on`, `risp`, `bases_empty` | PA | `on_*` non-null combinations | AR-4, AR-5, AR-6 |
| `ctx` | PA | 3-level factor: `BASES_EMPTY` / `MEN_ON_NO_RISP` / `RISP` | **AR-6 weight dimension** |
| `base_out` | PA | `base_state` + `_` + outs — 24 states | Receipt `e3` |
| `n_risp_runners` | PA | count of `on_2b`, `on_3b` non-null | AR-4 denominator |
| `runs_on_pa` | PA | `post_bat_score − bat_score` | AR-4 numerator |
| `runs_excl_batter` | PA | `runs_on_pa − 1 if home_run else 0` | AR-4 numerator |
| `reached_2k` | PA | any pitch in the PA had `strikes == 2` | AR-1, AR-2 |
| `pitch_group` | pitch | `PITCH_GROUP[pitch_type]` (locked map) | AR-3 |
| **`slot`** | PA | **`(PA index within game) mod 9 + 1`** | AR-5, AR-6, AR-7 |
| `woba_num` | PA | season-weight matching that row's event | Slash reconciliation |
| `xwoba_con_n` | group | `estimated_woba.notna().sum()` | **O4 honest denominator** |

---

## 3. Column-level lineage — source to published number

Notation: `physical field` → *transformation* → **published element** (receipt).

### 3.1 Season line (report §1)

```
events, wBB..wHR, batter, game_type, game_year
  → entity lock (batter==650333) + game_type=='R' + dedup(pitch key)
  → merge wOBA constants on game_year
  → LOCKED get_stats(level='game_year')
  → ba, obp, slg, ops, woba, xwoba, iso, krate, bbrate
                                        (dp_uc31_a1_season_line.csv)
```
**Locked-kernel boundary.** `get_stats` is inherited byte-identical from `dp_uc24`. Its PA rule excludes only `{NA, pickoff_1b}` — the `truncated_pa` fork enters here and nowhere else.

### 3.2 Two-strike family (report §3 — AR-1, AR-2)

```
strikes
  → groupby(game_pk, at_bat_number).transform(max) >= 2   → reached_2k
events → pa_frame(strict)                                  → PA spine
  → filter reached_2k
  → count strikeouts / count PAs                           → TSSR        (c1, c3)
  → line_from_pa()                                         → 2K slash    (c1, c3)
description, zone, strikes==2
  → swing/whiff/foul/called masks                          → economy     (c2)
```
**Independence note.** `line_from_pa()` is a **new** function that recomputes the slash from the PA spine using explicit masks. It does not call `get_stats`. DQ-12/DQ-13 assert the two agree to 0.006 on the 2026 window — which they do, because 2026 has no `truncated_pa`.

### 3.3 Damage map (report §4 — AR-3)

```
pitch_type → PITCH_GROUP (locked map)                      → pitch_group
p_throws
  → pa_frame(strict) grouped by (pitch_group, p_throws)
  → line_from_pa()                                         → BA/SLG/ISO/wOBA
type=='X' filtered by (pitch_group, p_throws)
  → launch_speed, launch_speed_angle, estimated_woba
                                                           → EV, hard-hit, barrel,
                                                             xwOBAcon, xwoba_con_n
  → bip < 15                                               → thin flag
                                                    (dp_uc31_d1_group_x_hand_2026.csv)
```
**Two populations, one table.** Slash columns are keyed on the pitch that *ended* the PA; contact columns use *all* balls in play off that group. Documented in 02 §3 AR-3 and enforced by never combining the families arithmetically.

### 3.4 Scoring position (report §5 — AR-4)

```
on_2b, on_3b                    → risp, n_risp_runners
bat_score, post_bat_score       → runs_on_pa
events=='home_run'              → runs_excl_batter = runs_on_pa − 1
  → risp_scored = min(runs_excl_batter, n_risp_runners)
  → SPCR = sum(risp_scored) / sum(n_risp_runners)
                                        (dp_uc31_e1, dp_uc31_e4)
```
**The `min()` is load-bearing.** It prevents crediting a runner from first who scored on a double as a scoring-position conversion. Guarded by DQ-18 (bounded 0–1) and DQ-19 (runs never exceed runners + batter).

### 3.5 Lineup model (report §6 — AR-5, AR-6, AR-7)

```
phils_2026, phillies_role=='batting', game_type=='R'
  → pa_frame(strict)
  → sort(game_pk, at_bat_number) → cumcount() mod 9 + 1     → slot
  → groupby(slot): PA/game, men_on share, risp share, ...   → AR-5   (f1)
  → groupby(slot, ctx) / groupby(slot)                      → W(s,c) (f4)

arraez 2026 pa_frame → groupby(ctx) → delta_run_exp.mean()  → RE24/PA per context (f3)

  → SPRC(h,s) = Σ_c W(s,c) · RE24/PA(h,c) × PA/g(s) × 162   → AR-6   (f5)
  → pair sums                                               → scenarios (f7)

is_onbase × PA/g(s)                                         → supply
following two slots → SPCR, RE24/PA men-on                  → realisation
                                                            → AR-7   (f6, f8)
```

**Lineage completeness statement.** Every column in every published table traces to a source field through the paths above. No published number originates outside `dp_uc31_arraez_acquisition_read.py`. The PDF and the dashboard both read from the CSV receipts and compute nothing of their own — with the single exception of the dashboard's slot-explorer sum, which reproduces the `f7` arithmetic and is asserted equal to it by V-130 – V-132.

---

## 4. Receipt index

| Receipt | Contents | Report section |
|---|---|---|
| `a1_season_line` | Season slash, 2019–2026 | §1 |
| `a2_wrc` | SC-1 wRC / wRC+ approximation | §1 |
| `a3_pitches_per_pa` | SC-2 P/PA — the "wild at-bats" test | Bottom line, §2 |
| `a4_window_headline` | Primary vs shadow, PA-spine basis | §1 |
| `b1_discipline` | Swing/chase/contact panel | §2 |
| `b2_batted_ball` | Contact quality + `xwoba_con_n` | §2 |
| `b3_spray` | Pull/oppo/pulled-air | — (supporting) |
| `b4_bat_tracking` | Bat speed, attack angle | §2 |
| `b5_running_line` | RF-1 trajectory | — (supporting) |
| `c1_two_strike_by_year` | AR-1/AR-2 by season | §3 |
| `c2_two_strike_economy` | Two-strike swing economy | §3 |
| `c3_two_strike_vs_phillies` | AR-1/AR-2 roster benchmark | §3 |
| `d1_group_x_hand_2026` | AR-3 primary | §4 |
| `d2_group_x_hand_career` | AR-3 shadow | — |
| `d3_pitch_type_2026` | Pitch-type detail | §4 |
| `d4_by_hand_2026` | Platoon split | §4 |
| `e1_context_2026` | AR-4 by context | §5 |
| `e2_context_by_year` | AR-4 stability | §5 |
| `e3_base_out_2026` | 24-state detail | — |
| `e4_spcr_vs_phillies` | AR-4 roster benchmark | §5 |
| `f1_slot_opportunity` | AR-5 | §6.2 |
| `f2_slot_occupancy` | Who hit where (all slots) | — |
| `f3_context_profiles` | AR-6 input: RE24/PA by hitter × context | §6.1 |
| `f4_slot_context_weights` | AR-6 input: W(s,c) | §6.1 |
| `f5_sprc` | **AR-6 output** | §6.3 |
| `f6_table_setting` | AR-7 supply / realisation | §6.4 |
| `f7_swap_scenario` | **Scenario pricing, both framings** | §6.3 |
| `f8_table_setting_supply` | AR-7 extension | §6.4 |
| `f9_observed_top_of_order` | Premise-conflict evidence | §6, OI-1 |
| `g1_league_reference` | League aggregate, **max year 2023** | — (labelled non-benchmark) |
| `dq_scorecard` | 24 build assertions | 05, 07 |
| `freshness_manifest` | Window + manual carry-ins | §9 |
| `verification_results` | 368 independent checks | 07 |
| `receipt_index` | This index, machine-readable | — |
| `fig1` – `fig6` | Figures | §2–§6 |
