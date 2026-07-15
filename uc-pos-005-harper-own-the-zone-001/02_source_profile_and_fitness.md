# 02 — Source Profile & Fitness · uc-pos-005 (dp_uc22)

**Agent role:** source-system-profiler · **Verdict: FIT** for all four KPI families

## Entity resolution
`player_name == 'Harper, Bryce'` in `pos` (phillies_role == 'batting') resolves to a single MLBAM id: **547180**. Entity locked on `batter == 547180` for the build (name-join only used for resolution).

## Coverage (R games, dedup on game_pk/at_bat_number/pitch_number)
| Season | Pitches | Games | Max date |
|---|---|---|---|
| 2019 | 2,787 | 157 | 2019-09-29 |
| 2020 | 973 | 58 | 2020-09-27 |
| 2021 | 2,401 | 141 | 2021-10-03 |
| 2022 | 1,594 | 99 | 2022-10-04 |
| 2023 | 2,021 | 126 | 2023-09-30 |
| 2024 | 2,469 | 145 | 2024-09-28 |
| 2025 | 2,172 | 132 | 2025-09-28 |
| 2026 | 1,600 | 96 | **2026-07-12** |

16,017 pitch rows total. 2026 cache is fresh through the All-Star break — the full first half. 2020 (COVID) and 2022 (injury: 99 G) are short seasons; kept in trend views, flagged in report interpretation.

## Field fitness for the OZ family
| Field | Null rate | Fitness |
|---|---|---|
| plate_x / plate_z | 0.06% | FIT — geometry inputs |
| sz_top / sz_bot | 0.06% | FIT — per-pitch zone rails (mean 3.24 / 1.62, sd 0.14 / 0.08 — real per-pitch variation, justifies per-pitch geometry over fixed rails) |
| zone | 0.06% | FIT — locked discipline panel input |
| description / events / type | 0% | FIT — swing/take + outcome classification |
| launch_speed_angle / launch_speed | 0.27% of BIP | FIT — barrel/hard-hit |
| estimated_woba_using_speedangle | 0.31% of BIP | FIT — xwOBAcon |
| pitch_type / p_throws | 0.07% / 0% | FIT — group + platoon dims |

**Decision:** rows with null location (10 pitches, 0.06%) are excluded from the OZ family only; they remain in the locked kernel aggregates. Documented in 05 and in the build DQ receipts.

## Source
Local parquet cache (`data/phillies/phils_{2019..2026}.parquet`) built from Baseball Savant Statcast via `mlb_data.py`. No pre-2019 load needed: the use case benchmarks the **Phillies tenure** only (contract signed 2019). wOBA weights: `wOBA and FIP Constants.csv` (FanGraphs), 2026 row is in-season.
