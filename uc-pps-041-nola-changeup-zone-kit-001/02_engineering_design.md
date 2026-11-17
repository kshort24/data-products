# 02 · Engineering Design
Agents: `data-architect` · `kpi-calculator` · `join-validator`

Grain: pitch (house log) → 2026 changeup map (489 rows) and season × side KPI tables. No joins beyond receipt reads (UC64 `prior_reread`, `seq_career`).
| KPI | Formula | Population |
|---|---|---|
| CZ-1 | `CH & called_strike & zone ∈ {7,8,9}` | 2026 MLB (R + F) |
| PNZ-1 | `1.5 + 2.0·(plate_z − sz_bot)/(sz_top − sz_bot)` | map |
| BB-1 | circle diameter 0.242 ft; ref PNG: 50.2 px at 1920×1080 with equal x/y scale (207.9 px/ft) | map |
| EC-1 | CH / pitches in `balls == strikes & strikes < 2` | R, season × side; pool = Phillies SP seasons ≥ 2,000 pitches & ≥ 100 CH |
| TS-1 | group share of `strikes == 2` pitches (K48 GROUP_MAP) | R, season × side |
| ZN-1 / CSB-1 | in-zone 1–9, bottom 7–9, below `plate_z < sz_bot` (tracked zone); take rate = CZ-1 / CH in 7–9 | R CH |
| FP-1 | CH share of `pitch_number == 1`; strike rate `type != 'B'` | R, season × side |
Inherited verbatim: `putaway_rate`, `whiff_rate`, `chase_rate`/`in_zone_rate`, `nresults`, CSW, `rv100` (client Table 1 and Table 2 reproduced at his levels).
