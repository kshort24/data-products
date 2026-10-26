# Use Case uc-pos-022 — Trea Turner 2026 Recap ("Sounding the Alarm")

| Field | Value |
|---|---|
| UC # | 57 |
| Build | `dp_uc57` v1.0.0 |
| Value stream | Phillies Offense (`pos`) |
| Human DPO | Kellen Short |
| Consumers | Hitting coaches, front office, analysts |
| Status | Delivered 2026-10-23 · READY-CONDITIONAL (C1-C6) · verified 34/34 · DQ 10/3/0 |
| Location | Code and outputs at the MLB root (`dp_uc57_*`, `out/dp_uc57_*`, `eda/dp_uc57/`); trail in `Agents for Data Products/data-products/uc-pos-022-turner-2026-recap-001/` |

## Business questions
Q1 how bad was 2026 · Q2 pitch recognition in vs out of the zone, by hand and pitch group · Q3 RHP breaking-ball expansion and contact · Q4 LHP offspeed whiffs and popups · Q5 fastballs by hand (chase, in-zone damage, popups) · Q6 slow lefty fastballs (VS-1) · Q7 flat bat path → popups, full season · Q8 a position change and his offense.

## CDEs consumed
`batter`, `phillies_role`, `game_type`, `game_year`, `game_date`, `events`, `description`, `type`, `zone`, `pitch_type`, `release_speed`, `p_throws`, `stand`, `plate_x`, `plate_z`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `bb_type`, `hc_x`, `hc_y`, `estimated_woba_using_speedangle`, `woba_value`, `woba_denom`, `bat_speed`, `swing_length`, `attack_angle`, `attack_direction`, `swing_path_tilt`, `intercept_ball_minus_batter_pos_x_inches`, `intercept_ball_minus_batter_pos_y_inches`.

## KPIs
Inherited: slash, wOBA, xwOBA, swing, whiff, contact, chase, IZ swing/contact, OOZ contact, HH, barrel, popup (PU-2), pull / pull-air, CM-1, BP-0/1/2, PU-1, PB-1. Generalized: XW-1c (xwOBA on contact), PB-2 (peer delta by pitch group). Defined here: **PR-1** (provisional KPI), **CT-1** and **PP-1** (pre-registered rules), **VS-1** (client definition adopted).

## Acceptance criteria (met)
Endpoints reconcile to the house line and to FanGraphs · UC40a's partial-season cut reproduced exactly · client claims reproduced on the client frame and graded · every change call on bars fixed before any split · carry-ins labelled and never computed on · independent harness all PASS · report ≤ 8 pp (7), dashboard ≤ 7 chapters (6) + graded notebook, ≤ 9 figures (9), ≤ 2 new KPIs (1).
