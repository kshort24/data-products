# 04 — Data Model & Lineage · uc-pos-004 (dp_uc20)

**Agent roles:** data-architect + technical-lineage-builder · **Verdict: LOCKED**

## Model
- **Grain:** pitch (one row per pitch). All KPI tables are aggregations of this single grain — no joins across grains, no fan-out risk (join-validator trivial pass; the only merge is constants keyed Season==game_year, 1:many by design, validated 0 weight nulls).
- **Entity key:** `batter == 656941`, `game_type == 'R'`, dedup `(game_pk, at_bat_number, pitch_number)`.
- **Derived dimensions:** `era` (CHC ≤2020 / WSN-BOS 2021 / PHI ≥2022), `season`, `pitch_group` (FF/SI/FC→fastball; SL/ST/CU/KC/SV/CS→breaking; CH/FS/FO/SC/KN→offspeed), `count_state` (two_strike / ahead / even_or_behind), `month` (2026 only), `early` (balls+strikes ≤1).

## Source → receipt lineage (all receipts `out/dp_uc20_schwarber_first_half_*`)
| Receipt | Level | Source columns (beyond keys/events) |
|---|---|---|
| `_results_by_season` | season | events, description, w* weights, estimated_* |
| `_wrc_by_season` (SC-1) | season | + constants: wOBA(lg), wOBAScale, R/PA |
| `_ppa_by_season` (SC-2) | season | pitch count / PA count only |
| `_battedball_by_season` | season | type, launch_speed, launch_angle, launch_speed_angle, bb_type |
| `_discipline_by_season` | season | description, zone, balls, strikes |
| `_spray_by_season` | season | hc_x, hc_y, stand, bb_type |
| `_battracking_by_season` | season | bat_speed, swing_length, attack_angle (2024+) |
| `_platoon_by_season` | season × p_throws | + p_throws |
| `_pitchgroup_by_season` | season × pitch_group | + pitch_type |
| `_countstate_by_season` | season × count_state | + balls, strikes |
| `_firstpitch_bip`, `_earlycount_pa` | season | + balls, strikes filters |
| `_twostrike_discipline` | season | strikes==2 slice of discipline |
| `_pa_funnel` | season | PA-terminal events, two-strike reach, LHP share, games |
| `_2026_monthly` | month | 2026 slice |
| `_2026_hr_log` | HR event | game_date, pitch_type, release_speed, launch_*, hit_distance_sc |
| `_dq_receipts` | run | structural checks |
| `_fig1/2/3.png` | — | every plotted number traces to a receipt above |

## Portability
Build script takes `MLB` root and `OUT` dir as argv (env-portable per skill standard); runs on sandbox mount and on Kellen's machine (`conda env snakes`). No writes outside `out/`; never overwrites prior-UC receipts (STEM-prefixed).
