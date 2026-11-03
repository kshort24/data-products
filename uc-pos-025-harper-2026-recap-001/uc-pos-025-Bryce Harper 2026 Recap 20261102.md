# Use Case uc-pos-025 — Bryce Harper 2026 Recap ("The Eye Carried a Softer Bat")

| Field | Value |
|---|---|
| UC # | 61 |
| Build | `dp_uc61` v1.0.0 |
| Value stream | Phillies Offense (`pos`) |
| Human DPO | Kellen Short |
| Consumers | Client (Claude Design build + animation), front office, hitting coaches, content, analysts |
| Status | Delivered 2026-11-02 · READY-CONDITIONAL (C1–C6) · verified 25/25 · DQ 14/0/0 · V1–V7 3/3 |
| Location | Code and outputs at the MLB root (`dp_uc61_*`, `out/dp_uc61_*`, `out/dp_uc61_design_kit/`, `eda/dp_uc61/`); trail in `Agents for Data Products/data-products/uc-pos-025-harper-2026-recap-001/` |

## Business questions
Q1 what kind of year · Q2 how it built (cumulative vs career) · Q3 what he hunts and punishes, by pitcher hand · Q4 where the ball goes.

## CDEs consumed
`batter`, `phillies_role`, `game_type`, `game_year`, `game_date`, `game_pk`, `at_bat_number`, `pitch_number`, `sv_id`, `des`, `events`, `description`, `type`, `zone`, `pitch_type`, `p_throws`, `plate_x`, `plate_z`, `sz_top`, `sz_bot`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `estimated_woba_using_speedangle`, `woba_value`, `woba_denom`, `bb_type`, `hc_x`, `hc_y`, `hit_distance_sc`, `fielder_2`..`fielder_9`.

## KPIs
Inherited: slash, wOBA (house weights), xwOBA (XW-1), K%, BB%, chase, whiff, hard-hit, barrel, EV p90, LD/GB/FB/PU (CR-1), DR-1 direction, K46 pull-air, OZ-1..OZ-4 (UC #23), KP-1 percentile, `ch1`. **No new KPI.** New, provisional: grade rules AP-1, HC-1, OZ-H; DMG-1 damage flag; CM-2 cumulative slash; NC-1 copy rule; DH-2.

## Acceptance criteria (met)
Season line reconciles to CI-1 exactly (693 PA, .269/.380/.485, 29 HR, 162 G) · claims graded on bars pre-registered at 18:05 ET · every printed number registered to a headline key (NC-1) · every figure passes V1–V7 + eyeball · independent harness all PASS · OPS/OBP/SLG/BA/HR shipped beside wOBA for the cumulative region · no causal or medical claim.
