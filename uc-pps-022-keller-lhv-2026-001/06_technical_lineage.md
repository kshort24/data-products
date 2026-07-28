# 06 — Technical Lineage
## UC #27 · `uc-pps-022` · Layer 3

Agent: `technical-lineage-builder`

Column-level source→target for every number this product publishes. Nothing appears in the
report that is not traceable through this document to a physical source column.

---

## 1. Pipeline stages

```
STAGE 0  SOURCE
         data/opponents/lhvp26.parquet                              14,960 rows
         wOBA and FIP Constants.csv                                      1 row (2026)
              │
STAGE 1  CONFORM                                        load_lhv()
         ├─ filter  game_type == 'R'
         ├─ dedup   (game_pk, at_bat_number, pitch_number)
         ├─ coerce  22 numeric CDEs via pd.to_numeric(errors='coerce')
         ├─ cast    game_date → datetime64 ; game_year → int
         └─ join    game_year = Season   [LEFT, 1:1]                14,960 rows
              │
STAGE 2  PARTITION
         ├─ KELLER    pitcher == 662144                                533 rows / 146 PA
         └─ BASELINE  pitcher != 662144                             14,427 rows / 3,702 PA
              │
STAGE 3  DERIVE  (row-level columns added to the Keller partition)
         ├─ outs   = events.map(EVENT_OUTS).fillna(0)
         ├─ half   = 'starts 1-4' if game_date in first 4 else 'starts 5-8'
         └─ az     = _attack_zone(plate_x, plate_z, sz_bot, sz_top)
              │
STAGE 4  AGGREGATE   locked KPI functions at 9 declared levels
              │
STAGE 5  PUBLISH     25 CSV receipts + 4 PNG figures under out/
```

---

## 2. Column-level lineage — locked KPIs

| Target metric | Source columns | Transformation | Receipt |
|---|---|---|---|
| `plate_apps` | `events` | count rows where `events ∉ {null, pickoff_1b}` | `results_headline`, `by_stand`, `tto` |
| `at_bats` | `events` | count rows where `events ∉ {null, pickoff_1b, walk, intent_walk, hit_by_pitch, sac_fly, sac_bunt}` | `results_headline` |
| `hits`, `singles`, `doubles`, `triples`, `hrs` | `events` | count by literal event value | `results_headline` |
| `walks`, `strikeouts`, `hbp` | `events` | `walk` / `{strikeout, strikeout_double_play}` / `hit_by_pitch` | `results_headline` |
| `ba` | ↑ | `hits / at_bats` | `results_headline` |
| `obp` | ↑ | `(hits + walks + hbp) / plate_apps` | `results_headline` |
| `slg` | ↑ | `(1B + 2·2B + 3·3B + 4·HR) / at_bats` | `results_headline` |
| `woba` | `events` → `wBB…wHR` (joined) | `Σ(weights) / plate_apps` | `results_headline`, `by_stand`, `tto` |
| `xwobacon` | `estimated_woba_using_speedangle`, `type` | mean over `type=='X'` **only** | `results_headline`, `by_stand`, `pitch_kpis`, `tto` |
| `krate`, `bbrate`, `hr_rate` | `events` | `strikeouts` / `walks` / `hrs` ÷ `plate_apps` | `results_headline` |
| `whiff_rate` | `description` | `count(∈ WHIFFS) / count(∈ SWINGS)` | `process_kpis`, `pitch_kpis` |
| `swstr_rate` | `description` | `count(∈ WHIFFS) / total pitches` | `process_kpis` |
| `chase_rate` | `zone`, `description` | `count(zone>9 ∧ ∈SWINGS) / count(zone>9)` | `process_kpis`, `pitch_kpis` |
| `in_zone_rate` | `zone` | `count(zone≤9) / total pitches` | `process_kpis`, `pitch_kpis` |
| `putaway_rate` | `strikes`, `events` | `strikeouts / count(strikes==2)` | `process_kpis`, `two_strike` |
| `first_pitch_strike_rate` | `pitch_number`, `type` | `count(pitch_number==1 ∧ type≠'B') / count(pitch_number==1)` | `process_kpis`, `first_pitch` |
| `hard_hit_rate` | `launch_speed`, `type` | `count(type=='X' ∧ launch_speed≥95) / count(type=='X')` | `process_kpis`, `contact_quality` |
| `edge_rate` | `plate_x/z`, `sz_top/bot` | Euclidean distance to zone boundary ≤ 0.245 ft (one baseball) | `process_kpis`, `arsenal` |
| `ooz_called_strike_rate` | `zone`, `description` | `count(zone>9 ∧ called_strike) / count(zone>9)` | `process_kpis` |
| `gb_rate`, `fb_rate`, `ld_rate`, `pu_rate`, `air_rate` | `bb_type`, `type` | share of `type=='X'` by `bb_type`; air = fb+ld+pu | `process_kpis`, `contact_quality` |
| `chase_up_rate` | `plate_z`, `sz_top` | `count(plate_z>sz_top ∧ ∈SWINGS) / count(plate_z>sz_top)` | `process_kpis` |
| `az` / `loc_*` | `plate_x/z`, `sz_top/bot` | heart = inner 55% width × middle 60% height; zone-edge = in-zone not heart; shadow = ≤0.33 ft outside; chase = beyond | `arsenal`, `location_profile` |
| `above_zone_rate` | `plate_z`, `sz_top` | `count(plate_z > sz_top) / total pitches` | `location_profile` |

---

## 3. Column-level lineage — derived report constructs

| Target | Source columns | Transformation | Receipt |
|---|---|---|---|
| `ip` / `ip_baseball` (per start) | `events` | `Σ EVENT_OUTS.map(events) / 3` (decimal) and `outs//3 "." outs%3` (baseball notation) | `game_lines` |
| `bf` (per start) | `at_bat_number` | `nunique()` within `game_pk` | `game_lines` |
| `opponent` | `home_team`, `away_team` | the team that is not `LHV` | `game_lines` |
| `site` | `home_team` | `'home' if home_team=='LHV' else 'away'` | `game_lines` |
| `pitches_per_bf` | `pitch_number`, `at_bat_number` | `count(pitches) / nunique(at_bat_number)` | `game_lines` |
| `usage` (arsenal) | `pitch_name` | `count(pitch) / 533` | `arsenal` |
| `usage_within_stand` | `pitch_name`, `stand` | pitch count ÷ stand total, within the filtered subset | `first_pitch`, `two_strike` |
| `half` | `game_date` | first 4 dates → `starts 1-4`; last 4 → `starts 5-8` | `recency_split`, `recency_usage` |
| `arm_side_break_in` | `api_break_x_arm` | mean, inches, arm-side positive. **Published in preference to `pfx_x`** to avoid the catcher-perspective sign trap | `arsenal` |
| `ff_velo` (by inning) | `release_speed`, `pitch_name`, `inning` | mean `release_speed` where `pitch_name=='4-Seam Fastball'`, grouped by `inning` | `velo_by_inning` |
| `above_zone` (HR) | `plate_z`, `sz_top` | `plate_z > sz_top` | `home_runs` |
| `in_heart` (HR) | `plate_x/z`, `sz_top/bot` | `_attack_zone(...) == 'heart'` | `home_runs` |

---

## 4. Column-level lineage — PROVISIONAL SR-M1

**Flagged non-inheritable. See `04_ §SR-M1`.**

| Target | Source columns | Transformation | Receipt |
|---|---|---|---|
| `total_pas` | `game_pk`, `at_bat_number` | count of distinct PA groups at the published level | `sr_m1_provisional` |
| `total_success` (variant A) | `strikes`, `pitch_number`, `type`, `bb_type` | `(max(strikes) over pitch_number<4 == 2) OR (∃ pitch_number<4 with type=='X' ∧ bb_type=='ground_ball')` | `sr_m1_provisional` |
| `success_rate` | ↑ | `total_success / total_pas` | `sr_m1_provisional` |
| `rate_A_as_written` | as above | independent recomputation of variant A by a second code path | `sr_m1_variants` |
| `rate_B_two_strike_by_p2` | `type`, `pitch_number`, `bb_type` | cumulative `type != 'B'` reaches 2 by pitch 2, OR early GB | `sr_m1_variants` |
| `rate_C_two_strike_by_p3` | `type`, `pitch_number`, `bb_type` | cumulative `type != 'B'` reaches 2 by pitch 3, OR early GB | `sr_m1_variants` |

> **Lineage note on the strike-accrual path.** Variants B and C do not read the `strikes`
> column at all. They reconstruct count progression from `type != 'B'` (called strike, swinging
> strike, foul, ball in play) and take a cumulative sum within the PA. This is deliberate: it
> is an *independent* derivation of the same quantity, so agreement between the A path (which
> reads `strikes`) and the B/C path is evidence, not tautology.

---

## 5. Figure lineage

Every figure traces to a CSV receipt. No figure computes its own numbers.

| Figure | Source receipt(s) | Hard-coded reference lines |
|---|---|---|
| `fig1_arsenal.png` | `arsenal.csv` | Staff whiff 26.3% and hard-hit 38.0% — both from `process_kpis.csv` baseline row |
| `fig2_recency.png` | `recency_split.csv`, `recency_usage.csv` | none |
| `fig3_location.png` | Keller partition rows, filtered by `pitch_name` × `stand`; hard-hit ring = `type=='X' ∧ launch_speed≥95`. Counts reconcile to `arsenal_by_stand.csv` and `contact_quality_by_stand.csv` | none |
| `fig4_gameplan.png` | `two_strike.csv` (cells with n ≥ 4) | none |

---

## 6. Reproducibility

| Property | Value |
|---|---|
| Build script | `dp_uc26_keller_lhv_2026.py` |
| Entry point | `python dp_uc26_keller_lhv_2026.py` |
| Data root resolution | `MLB_DATA_ROOT` env var → local `./data/opponents` → sandbox mount → absolute Windows path |
| External dependencies | `pandas`, `numpy`, `pyarrow`, `matplotlib` |
| Determinism | Fully deterministic. No sampling, no randomness, no model fitting, no wall-clock dependency |
| Outputs | 25 CSV + 4 PNG, all new files; no prior UC output is overwritten |
| Independent recompute | `dp_uc26_verification.py` — recomputes headline numbers by a second code path (`07_ §2`) |
