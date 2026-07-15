# 02 — Engineering Design · uc-pps-017 (UC #19)

## Locked KPIs — inherited VERBATIM (no re-derivation)

`get_stats` / `nresults`, `whiff_rate`, `chase_rate`, `putaway_rate`, `fpsr`, `hard_hit_rate` — copied from dp_uc11 (which inherited from dp_uc8 / Baseball Functions). Mechanics unchanged; values reconcile with prior UCs by construction.

## NEW derived KPIs — kpi-calculator specs (provisional PD-1..PD-7, ratification pending)

| ID | KPI | Plain language | Formula | Grain | Population | Edge cases |
|---|---|---|---|---|---|---|
| PD-1 | Outs recorded / IP-from-log | Innings reconstructed from the pitch log | Σ event→outs map over PA-terminal pitches; IP = outs/3 | any slice | entity-locked R-game log | DP/TP mapped 2/3; CS & pickoffs included; may differ ~1 out vs official — labeled reconstruction |
| PD-2 | Runs on mound / RA9 | Runs scored while he pitched, per 9 | Σ clip(post_bat_score − bat_score, 0) over PA-terminal pitches; RA9 = runs/(outs/3)×9 | game or season | same | Not earned-run accounting; bequeathed runners after exit not captured — labeled, ERA never published |
| PD-3 | FIP | Defense-independent run estimate | (13·HR + 3·(BB+HBP) − 2·K)/IP + cFIP(season) | season | same | cFIP from `wOBA and FIP Constants.csv` (2025: 3.135, 2026: 3.111); IP from PD-1 |
| PD-4 | CSW rate | Called strikes + whiffs per pitch | (called_strike + WHIFFS)/pitches | any slice | all pitches | uses locked WHIFFS list |
| PD-5 | TTO split | Results by times through the order | locked `nresults` grouped by clip(n_thruorder_pitcher, ≤3) | season × TTO | pitches with n_thruorder (1.000 complete) | 3 = "3rd+" |
| PD-6 | Battery split | Results by catcher | locked `nresults` + PD-4 + locked chase/putaway grouped by fielder_2→name | season × catcher | 2026 log | names data-resolved, never hand-keyed; PA printed (Marchán 70 PA flag) |
| PD-7 | Count-leverage funnel | Share of PA reaching 2 strikes; pitch share ahead | distinct PA with a 2-strike pitch / PA; pitches with balls<strikes / pitches | season | same | intent_walk counted in BB (PD-3) but PAs unchanged |

None redefines a governed term; all seven flagged NEW in the build script header.

## Persona → KPI map

| Persona | Primary views | Receipts |
|---|---|---|
| Manager | start log (leash, pitch counts), TTO split, monthly trend | `start_log`, `tto_yoy`, `monthly` |
| Pitching dept | arsenal YoY (usage/velo/movement/whiff/xwOBA), process KPIs | `arsenal_yoy`, `process_kpis_yoy` |
| Luzardo | process KPIs, count leverage, monthly BB% path | `process_kpis_yoy`, `count_leverage_yoy`, `monthly` |
| Catcher | battery split, chase/zone/CSW/putaway, 2-strike funnel | `battery_2026`, `process_kpis_yoy`, `count_leverage_yoy` |

## Model / lineage sketch

```
phils_2025.parquet ─┐  entity lock 666200 · R only · dedup(game_pk,ab,pitch) · weights join
phils_2026.parquet ─┴─► luzardo pitch log (4,849 rows)
        ├─ locked kernel ──► season_line · by_stand · tto · battery · monthly · staff_benchmark
        ├─ PD-1/2/3 (PA-terminal rows) ──► IP · RA9 · FIP · start_log
        ├─ PD-4/7 ──► csw · count_leverage
        └─ figures 1–3 (each traces to a CSV receipt)
```
