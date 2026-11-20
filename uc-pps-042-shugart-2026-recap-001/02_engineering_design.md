# 02 · Engineering Design
Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model
Grain: one pitch (`pitcher, game_pk, at_bat_number, pitch_number`).
| Frame | Definition | Rows |
|---|---|---|
| FR-1 client frame | Phillies pitching role, `pitcher == 663767`, all game types | 944 |
| Governed frame | FR-1 ∩ `game_type == 'R'` | 871 pitches · 223 PA · 46 outings |
| CS-A | Phillies pitcher-seasons, R, 2015–26, RHP, RP-1 (starts ≤ 20% of games), ≥ 150 pitches (CX-1) | 115 (114 + Shugart 2026) |
| CS-B | 2026 RP-1 relievers, either hand, ≥ 150 pitches | 13 (12 + Shugart) |
| CS-C | CS-A pitcher × season × batter hand × pitch type cells, ≥ 50 pitches | `out/dp_uc66_cs_c_pitch_stand.csv` |
| Platoon pool | CS-A seasons with ≥ 60 PA on both sides | 52 (+ Shugart) |
| Shape pool | CS-A pitcher-pitch-seasons, ≥ 50 of the type (K48 `arsenal_table`) | 313 |
| Outing ledger | one row per outing; entry state from first pitch (K63 `outing_ledger`) | 46 |

## 2 · Join validation (`join-validator`)
- Every KPI merge is on the full `level` key (`player_name, game_year, p_throws[, stand, pitch_type, month, stint]`), left joins onto `nresults`; row counts asserted equal to the `nresults` frame.
- CS-A / platoon / CS-C joins on `(pitcher, game_year)` — inner by design (population filter); subject excluded from its own pool before every percentile.
- No fan-out: the pitch key is unique in the governed frame (DQ-02) and in the pooled log (deduped on `pitcher` + pitch key).

## 3 · Metadata mapping (`metadata-mapper`)
All physical columns map to existing glossary terms (Statcast field reference); `plate_x` sign convention (catcher's view: LHB on +x) recorded for IN-1.
`pitch_type` null on 4 rows = automatic balls of an intentional walk (DQ-17).

## 4 · Dashboard / figure specification (`dashboard-specifier`)
| Fig | Question | Form | Context set |
|---|---|---|---|
| F1 | how good was the season? | per-metric small multiples, horizontal box + strip, right = better | CS-A |
| F2 | platoon | per-metric × hand small multiples | CS-A sides ≥ 60 PA |
| F3 | pitch plot (client) | every pitch + 1-SD ellipses; season means vs shape pool | CS-A shape pool |
| F4a | pitch map (client) | every pitch by hand, zone thirds | — (location context in F4b/F8) |
| F4b | where each pitch lives | 4-in density squares, pitch × hand grid | — |
| F5 | cumulative usage (client) | CU-1 lines by hand, option window shaded | his own season |
| F6 | cumulative wOBA (client) | CW-1 wOBA + xwOBA by PA, by hand | CS-A IQR band + median |
| F7 | months | dots sized by PA, never joined | his season value |
| F8 | drivers | pitch × hand scorecard: wOBA, whiff, RV/100 | CS-C |
| F9 | role | late-close share dot plot | CS-B |
| S1 | stretch: command by stint | two discrete dots per metric | CS-A median |
