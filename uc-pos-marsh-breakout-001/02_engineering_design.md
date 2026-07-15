# 02 — Engineering Design · uc-pos-marsh-breakout-001

## §1 Locked KPI cores (inherited VERBATIM — no redefinition)

From `Baseball Functions.ipynb`: `get_stats`/`measure_calcs` (PA/AB/H/XBH, ba, obp, slg, ops, woba via FanGraphs season weights joined `game_year == Season`), swing/whiff description lists, `chase_rate` (swings at `zone > 9` / pitches at `zone > 9`), `hard_hit_rate` (EV ≥ 95 on `type=='X'`), barrel (`launch_speed_angle == 6`), xwOBA proxy (`estimated_woba_using_speedangle` mean — BIP-weighted, labeled as proxy in all consumables).

## §2 NEW derived indicators (kpi-calculator specs)

| Indicator | Definition | Grain | Purpose |
|---|---|---|---|
| Discipline panel | swing / z-swing / chase / z-contact / ooz-contact / first-pitch-swing / zone-seen, from locked swing+whiff lists and `zone<=9` | season (× p_throws) | Detect swing-decision change |
| Two-strike funnel | distinct PA reaching `strikes==2` ÷ PA | season | Separate count-avoidance from 2-strike skill |
| Early-count damage | locked wOBA over PA ending with `balls+strikes<=1` | season | Value of ending PA early |
| Pulled-air rate | spray angle from `atan2(hc_x−125.42, 198.27−hc_y)`; pull = >15° toward pull side (stand-aware); air = FB+LD | season | Direction-not-force slugging source |
| LHP PA share | PA vs `p_throws=='L'` ÷ PA | season | Role/platoon indicator |
| Pace per 600 | HR and XBH × 600 / PA | season | Cross-season comparability at unequal PA |

## §3 Model / grain

Single entity-locked pitch-grain frame: LAA parquet + five PHI season parquets, filtered `batter==669016`, `game_type=='R'`, deduped on `['game_pk','at_bat_number','pitch_number']`, wOBA weights re-joined idempotently (mirrors `mlb_data._apply_woba_weights`). No cross-domain joins → join-validator scope limited to the weights join (validated: 0 null weight rows, no fan-out — row count unchanged).

## §4 eda-agent notes feeding design

EV/hard-hit flat across 2023–2026 → design emphasis shifted from power metrics to direction (spray) and timing (count-state) indicators. 2025 half-split added after EDA showed results moved in 2H-2025 before the swing profile did.
