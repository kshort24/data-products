# 02 — Source Profile & Fitness-for-Purpose (source-system-profiler) · uc-pps-020

## Entity lock
`pitcher == 554430` — resolved from `player_name == 'Wheeler, Zack'` mode within `phillies_role == 'pitching'` in each season cache; single consistent id across all four seasons. Never hand-keyed (Nola/"Nolan Hoffman" rule). Enforced in the build; DQ check `entity_lock` = PASS.

## Sources & windows (all `data/phillies/`, `game_type == 'R'`, deduped on game_pk+at_bat_number+pitch_number)
| Season | File | First-half window used | Cutoff | Pitches | Starts | PA |
|---|---|---|---|---|---|---|
| 2021 | phils_2021.parquet | 2021-04-03..2021-07-07 | ≤ 2021-07-11 | 1806 | 18 | 471 |
| 2024 | phils_2024.parquet | 2024-03-29..2024-07-09 | ≤ 2024-07-14 | 1865 | 19 | 468 |
| 2025 | phils_2025.parquet | 2025-03-27..2025-07-12 | ≤ 2025-07-13 | 1908 | 19 | 467 |
| 2026 | phils_2026.parquet | 2026-04-25..2026-07-12 | none (full cache) | 1453 | 15 | 355 |

2026 cache freshness: file updated 2026-07-13, max game_date 2026-07-12 (T-1 at intake; ASG 2026-07-14 — first half complete).

## Data-visible context facts (profiled, not interpreted)
- 2025 full-season log ends **2025-08-15** — zero Wheeler pitches after that date in phils_2025.
- 2026 log begins **2026-04-25** — zero Wheeler appearances in the March/April window that opens 2026-03-26 for the team cache.

## Fitness against required CDEs
Non-null shares on the entity-locked frame (receipt: `dp_uc23_dq_scorecard.csv`): pitch_name, description, events-at-PA-grain, stand, zone, balls/strikes, pitch_number, bat_score/post_bat_score all ≥ 0.99 → fit for every KPI in scope. `n_thruorder_pitcher` = 0 for 2021/2024 (column absent pre-merge) → TTO scoped to 2025/2026. `release_spin_rate`/`pfx_*` complete in all four seasons → arsenal receipts fit. `launch_speed` non-null on BIP ≈ standard Statcast coverage → hard-hit and xwOBA-proxy fit, with the BIP-proxy caveat carried in the report header.

## Known source quirks carried forward
- Sweeper does not exist as a Statcast label in 2021 (pitch taxonomy change ~2023); 2021 breaking ball is Curveball+Cutter era. Arsenal comparisons across 2021↔2024+ are usage-of-labels, noted in report §3 framing (the 2021 pitcher is presented as a different design, not pitch-for-pitch mapped).
- wOBA weights joined per-season from `wOBA and FIP Constants.csv` (1871–2026 coverage incl. in-season 2026 row); cFIP present for all four seasons.
