# 03 — Glossary Alignment & KPI Specs · uc-pos-006 (dp_uc24)

**Agent roles:** business-glossary-agent + kpi-calculator · **Verdict: PASS** — all user KPIs map to locked terms; 2 NEW KPIs specified below (provisional RF-1, RF-2). No business meaning inferred; gaps returned to DPO, none blocking.

## User KPI list → glossary mapping
| User term | Locked term / status | Mechanics (inherited verbatim, dp_uc20 kernel) |
|---|---|---|
| high-level results | BA/OBP/SLG/OPS/HR (locked) | `get_stats` |
| batted ball profile | GB/FB/LD/PU + air rate (locked) | `batted_ball`, `bb_type` shares |
| barrel rate | Barrel% (locked) | `launch_speed_angle==6` on `type=='X'` |
| pull air rate | Pulled-Air Rate (locked, from uc-pos-marsh/004) | spray angle via `hc_x/hc_y`; pulled ∧ (FB∨LD) |
| line drive rate | LD% (locked) | `bb_type=='line_drive'` share of BIP |
| hard hit rate | Hard-Hit% (locked) | `launch_speed>=95` on `type=='X'` |
| "whatever else appropriate" | EV/EV90/LA, sweet-spot, chase, whiff, z-swing, K%, BB%, wOBA, xwOBA, wRC, P/PA, platoon, pitch-group, count-state (all locked) | kernel + inherited SC-1/SC-2 |
| **cumulative KPI trajectory** | **NEW → RF-1** | spec below |
| **"heating up" (rolling form)** | **NEW → RF-2** | spec below |

**xwOBA clarification (glossary note):** the locked `xwoba` field is the PA-level mean of `estimated_woba_using_speedangle`, which is populated on every PA (batted balls by speed/angle, K as 0, BB/HBP at wOBA weight) — so it behaves as **full expected wOBA**, the correct comparator to wOBA. The **on-contact** variant (xwOBACON) is the separate `xwoba_con` receipt column. The two are distinct terms and the report labels which is in use. (This refines the "BIP-weighted proxy" wording carried in prior pos UCs.)

## RF-1 — Season-to-date OPS trajectory — PROVISIONAL
- **Plain language:** the batter's cumulative OPS after each team game, one line per season, so a down/up trend is visible against prior years.
- **Formula:** at game *g*, `OBP = ΣΣ(H+BB+HBP)/ΣPA` and `SLG = ΣTB/ΣAB` over games 1…*g* within the season; `OPS = OBP + SLG`. wOBA-to-date computed in parallel (per-row wOBA numerator = the season weight matching that row's event, cumulated / cum PA).
- **Grain:** (season, game_date). **Population:** all PA, R games, entity-locked.
- **Edge cases:** doubleheaders collapse to one game_date point (97 date-points vs 98 game_pk in 2026 — immaterial to the curve). Early-season points are volatile by construction (small cumulative denominator) — the figure is read for level/late-trend, not the first ~15 games.
- **Receipt:** `out/dp_uc24_turner_2026_review_running_ops_by_game.csv`. **Verification:** each season's final point equals that season's `get_stats` OPS (4/4 PASS in `dp_uc24_verification.py`).

## RF-2 — Rolling-form wOBA/OPS — PROVISIONAL
- **Plain language:** a trailing-100-PA moving average of wOBA and OPS across 2026, to quantify "heating up" as a smoothed process line rather than a calendar-month bucket.
- **Formula:** order PA by game; trailing 100-PA window sums → `roll_obp=(H+BB+HBP)/100`, `roll_slg=TB/AB_window`, `roll_ops=roll_obp+roll_slg`, `roll_woba=Σwoba_num/100`.
- **Grain:** PA index (2026). **Population:** 2026 R PA, entity-locked. **Window:** 100 PA (min_periods=100) → first value at PA 100.
- **Edge cases:** window is PA-based (not games) so it is robust to rest days; interpretation guardrail — a rolling line is a *momentum descriptor*, not a talent estimate. 2026 range: OPS .455 (trough) → .973 (latest); wOBA .204 → .412.
- **Receipt:** `out/dp_uc24_turner_2026_review_2026_rolling_form.csv`.

## Inherited (not new) — SC-1 wRC, SC-2 P/PA
Carried verbatim from uc-pos-004 (03). wRC uses FanGraphs season constants (2026 in-season → provisional ±2%); "wRC", never "wRC+" (no park plane locally). Receipts `_wrc_by_season.csv`, `_ppa_by_season.csv`.

## Duplicate/conflict scan
RF-1/RF-2 introduce no naming conflicts (no prior trajectory or rolling term exists). Pulled-Air Rate, Two-Strike Funnel, Early-Count Damage reused from the Marsh/Schwarber lineage. **Recommend promotion of RF-1/RF-2 to locked after one more hitter reuse.**
