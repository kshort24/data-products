# Use Case uc-pos-023 — Kyle Schwarber 2026 Home Runs, animated ("Forty-Five and a Question Mark")

| Field | Value |
|---|---|
| UC # | 58 |
| Build | `dp_uc58` v1.0.1 (copy-only over v1.0.0) |
| Value stream | Phillies Offense (`pos`) |
| Human DPO | Kellen Short |
| Consumers | Claude Design (motion), the editor, the parent Schwarber 2026 recap UC |
| Status | Released v1.0.1 2026-10-27 · DPO-approved (Release Sign-Off) · READY-CONDITIONAL (C1-C7) · verified 31/31 · DQ 10/3/0 |
| Location | Code and outputs at the MLB root (`dp_uc58_*`, `out/dp_uc58_*`, `eda/dp_uc58/`); trail in `Agents for Data Products/data-products/uc-pos-023-schwarber-2026-hr-animation-001/` |

## Business questions
Q1 cumulative HR by PA across 12 seasons, eras colored · Q2 the 2026 line with highlight stops and clip cuts · Q3 where 45 ranks · Q4 spray on the CBP outline by hand, with thump context · Q5 pitch maps by hand and pitch group, LHP and RHP clips · Q6 three-screen wrap.

## CDEs consumed
`batter`, `phillies_role`, `game_type`, `game_year`, `game_date`, `game_pk`, `at_bat_number`, `pitch_number`, `sv_id`, `events`, `des`, `type`, `inning`, `inning_topbot`, `home_team`, `away_team`, `bat_score`, `fld_score`, `post_bat_score`, `delta_home_win_exp`, `pitcher`, `p_throws`, `pitch_type`, `release_speed`, `plate_x`, `plate_z`, `sz_top`, `sz_bot`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `hit_distance_sc`, `hc_x`, `hc_y`, `bb_type`, `stand`.

## KPIs
Inherited: cumulative count by PA (`cumulative_metric`), barrel rate (K54), DR-1 direction, PA-L1 loc, CPG-1 pitch group. Defined here: **HB-1** HR barrel share (provisional KPI); rules **CP-1, WP-1, HL-1, SP-1/2/3, PM-1, GR-1**; defect fix **DH-1**.

## Acceptance criteria (met)
Curve endpoints reconcile to an independent count and to carry-ins (45; 385) · highlights chosen by rules fixed before looking · client claims graded on his own frame (15 rows) · every on-screen number templated from receipts · prompt DATA == design data · independent harness all PASS · clip list runs in the client's resolver.
