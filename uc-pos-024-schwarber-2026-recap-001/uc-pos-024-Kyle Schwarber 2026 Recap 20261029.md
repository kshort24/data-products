# Use Case uc-pos-024 — Kyle Schwarber 2026 Recap ("Forty-Five and a Question Mark")

| Field | Value |
|---|---|
| UC # | 60 |
| Build | `dp_uc60` v1.0.0 |
| Value stream | Phillies Offense (`pos`) |
| Human DPO | Kellen Short |
| Consumers | Front office, hitting coaches, content (UC58 video), analysts, Tier 3 redesign owners |
| Status | Delivered 2026-10-29 · READY-CONDITIONAL (C1-C6) · verified 28/28 · DQ 11/2/0 · Tier 3 audit 8/8 |
| Location | Code and outputs at the MLB root (`dp_uc60_*`, `out/dp_uc60_*`, `eda/dp_uc60/`, `data/_schema/`, `phillies_dp/recap_viz.py`); trail in `Agents for Data Products/data-products/uc-pos-024-schwarber-2026-recap-001/` |

## Business questions
Q1 what happened · Q2 when it turned · Q3 was it his back · Q4 did he lose his pop · Q5 should we be concerned.

## CDEs consumed
`batter`, `phillies_role`, `game_type`, `game_year`, `game_date`, `game_pk`, `at_bat_number`, `pitch_number`, `sv_id`, `des`, `events`, `description`, `type`, `zone`, `pitch_type`, `p_throws`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `estimated_woba_using_speedangle`, `woba_value`, `woba_denom`, `bat_speed`, `swing_length`.

## KPIs
Inherited: slash, wOBA, xwOBA, xwOBAcon, K%, BB%, chase, whiff, hard-hit, barrel, ISO, EV p90, SW-8 damage band, bat speed (K40/BP-0), cumulative wOBA (CM), RC-5 scans, two-prop z. **No new KPI.** New grade rules (provisional): **BK-1, POP-1, CN-1**. New house assets: **SD-1** comparison sets, **SD-2** eras, **SD-3** recap_viz (Tier 3 V1–V7).

## Acceptance criteria (met)
Season line reconciles to carry-ins (.232/.354/.50x, 45 HR, 156 G, 6 absences) · the four questions graded on pre-registered bars · no medical or causal claim · every figure passes V1–V7 (machine audit + eyeball) · independent harness all PASS · PDF ≤ 10 pp (6) · dashboard ≤ 7 chapters (7).
