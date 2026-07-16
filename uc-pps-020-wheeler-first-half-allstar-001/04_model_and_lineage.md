# 04 — Model Blueprint & Technical Lineage (data-architect + technical-lineage-builder) · uc-pps-020

## Grain & model
- **Base grain:** pitch (one row per pitch), entity-locked, R-games, deduped, first-half filtered.
- **Derived grains:** PA (last-pitch-per-PA via `pa_last`), start (game_pk), month (2026 only), season(-half), pitch_name × season, stand × season, TTO × season (2025/2026).
- **Join strategy:** single-entity frame — the only join is wOBA/FIP constants on `game_year == Season` (validated: `weights_join` PASS, no fan-out possible at 1:1 season key). No cross-domain joins; join-validator formally waived on single-join grounds (same waiver as dp_uc21).

## Source-to-target lineage (column level)
| Target receipt | Source columns | Transform |
|---|---|---|
| `dp_uc23_wheeler_firsthalf_line.csv` | events, description, woba weights, estimated_woba_using_speedangle, launch_speed, bat_score/post_bat_score | locked kernel: nresults + outs_and_runs → IP/RA9 + fip(cFIP) + hard_hit + csw |
| `dp_uc23_wheeler_process_kpis.csv` | pitch_number, type, zone, description, strikes, events, launch_speed | fpsr / chase / putaway / whiff / csw / hard_hit at season grain |
| `dp_uc23_wheeler_arsenal_yoy.csv` | pitch_name, release_speed, release_spin_rate, pfx_x/z, description, strikes, events, est_woba | groupby pitch_name × season; usage = n/Σn within half |
| `dp_uc23_wheeler_by_stand_yoy.csv` | stand + kernel fields | nresults × stand |
| `dp_uc23_wheeler_tto_yoy.csv` | n_thruorder_pitcher (clip 3) + kernel | 2025/2026 only |
| `dp_uc23_wheeler_start_log_2026.csv` | game_pk grouping + kernel + release_speed (FF) | per-start reconstruction |
| `dp_uc23_wheeler_monthly_2026.csv` | game_date[:7] + kernel | month grain |
| `dp_uc23_staff_benchmark_2026.csv` | full 2026 pitching cache (all pitchers, ≥500 pitches) | nresults × player_name + csw |
| `dp_uc23_wheeler_count_leverage.csv` | strikes, balls, events | 2-strike funnel + ahead-share |
| `dp_uc23_wheeler_velo_by_start.csv` | release_speed, pitch_name, game_pk | start-level mean/max, n≥5 filter |
| `dp_uc23_dq_scorecard.csv` / `dp_uc23_freshness_manifest.csv` | frame metadata | DQ + freshness receipts |

Every figure (fig1 results, fig2 arsenal, fig3 velo) renders exclusively from the receipts above — no number appears in a figure that lacks a CSV receipt.

## Portability
Data-root resolution: `MLB_DATA_ROOT` env var → package-relative → absolute Windows path (dp_uc21 convention). Build executed this session on the sandbox mount; re-runs unchanged on the host machine.
