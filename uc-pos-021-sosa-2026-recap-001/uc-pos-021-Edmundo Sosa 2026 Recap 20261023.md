# Use Case uc-pos-021 — Edmundo Sosa 2026 Recap ("We Really Do Love Sosa")

| Field | Value |
|---|---|
| UC # | 56 |
| Build | `dp_uc56` v1.0.0 |
| Value stream | Phillies Offense (`pos`) |
| Human DPO | Kellen Short |
| Consumers | Front office (free-agency decision), hitting coaches, analysts |
| Status | Delivered 2026-10-23 · READY-CONDITIONAL (C1–C5) · verified 161/161 |
| Location | `Agents for Data Products/data-products/uc-pos-021-sosa-2026-recap-001/` (code, receipts, deliverables) |

## Business questions
Q1 2026 top-line vs prior Phillies years (cumulative wOBA/OPS) · Q2 uptick through the year · Q3 batted-ball indicators of sustained performance · Q4 high-chase/high-contact sustainability · Q5 velocity and breaking balls · Q6 swing rate × wOBA among Phillies RHB · Q7 over-the-hump vs bench value · Q8 walkaway contract number.

## CDEs consumed
`batter`, `phillies_role`, `game_type`, `game_year`, `game_date`, `events`, `description`, `type`, `zone`, `pitch_type`, `release_speed`, `p_throws`, `stand`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `bb_type`, `hc_x`, `hc_y`, `estimated_ba_using_speedangle`, `estimated_woba_using_speedangle`, `delta_run_exp`, `bat_speed`, `fielder_3…9`.

## KPIs
Inherited: slash, wOBA, xwOBA, BB%, K%, swing, contact, chase, whiff, OOZ contact, HH, barrel, pull-air, bat speed, CM-1, TR-1, ER-1, CC-1. Defined here: EV-1 (client definitions), **OZ-1**, **WA-1** (provisional).

## Acceptance criteria (met)
Endpoints reconcile to the house line · client claims graded on the client frame · carry-ins labelled · walkaway rule pre-registered · independent harness all PASS · report ≤ 8 pp, dashboard ≤ 8 chapters + graded notebook.
