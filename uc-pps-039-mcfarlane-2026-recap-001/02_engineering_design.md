# 02 · Engineering Design
Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model
Grain: one pitch (`pitcher, game_pk, at_bat_number, pitch_number`). Frames:
| Frame | Definition | Rows |
|---|---|---|
| CF-M client frame | Phillies pitching role, `pitcher == 686934`, all game types | 333 |
| CX-1 context | Phillies pitching, regular season 2015–26, pitcher-seasons ≥ 150 pitches | 259 seasons (258 + McFarlane 2026) |
| FO-1 pool | RHP FF in any Phillies game (pps + pos), not S/E, deduped, pitcher-seasons ≥ 100 FF | 239 seasons, 137,203 pitches |
| Pitch-type pool | Phillies RHP pitcher-pitch-seasons, regular season, ≥ 150 of the type (K48 `arsenal_table`) | 420 |
| Outing ledger | one row per McFarlane outing; entry state from his first pitch; Duran's first AB in the game | 21 |
| AAA tier | `lhvp26` rows for 686934 | 73 pitches / 4 outings |
| S-1 | first 21 MLB outings (date order, postseason kept) for 686934 and 689147 | 333 / 355 pitches |

## 2 · Joins (`join-validator`)
All KPI blocks merge on the level keys (left joins from `nresults`); no fan-out (dedup key unique, DQ-02). BD-1 joins Duran's per-game first
at-bat to McFarlane's per-game last at-bat on `game_pk` (2026 pitching rows only). FO-1 dedups pps ∪ pos on the pitch key before grouping (DQ-14).
**EN-3 (found here):** in batting-role rows `player_name` is the hitter, so pitcher names come from pitching-role rows only.

## 3 · EDA notes (`eda-agent`)
- His FF clusters at 12.9–16.5 in IVB (10th–90th) and 6.6–12.1 in of run; SI at 14.5–18.6 in of run; SL near the bullet box (4.7 / −2.0 in); ST 12.9 in sweep, flat.
- Velocity by outing: ~100 mph through 9/13, 97.8–98.3 over 9/22–9/27, 99.6 in the Wild Card.
- 6 of 7 walks came against righties; postseason is 6 PA.

## 4 · Dashboard spec (`dashboard-specifier`)
House shell (UC #62). Tiles: wOBA/OPS, K%·BB%, four-seam, bridge outings. Outing inspector (select any of 21 outings). Ten chapter tabs in the
client's order (story, hand-in-hand, arrival, bridge, overall year, pitch plot, pitch maps, by handedness, outlier fastball, receipts); each
chapter = **Commentary** (his words) then **The data**. Plotly from the pinned CDN. Figures: F1 context boxes · F2 pitch plot · F3 pitch map ·
F4 whiff by pitch × hand · F5 velocity vs spin (client chart) · F5b season averages · F6 outings · S1 twins.
