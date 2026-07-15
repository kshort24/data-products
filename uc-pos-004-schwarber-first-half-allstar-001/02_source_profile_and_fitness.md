# 02 — Source Profile & Fitness-for-Purpose · uc-pos-004 (dp_uc20)

**Agent role:** source-system-profiler · **Verdict: FIT** for all requested CDEs

## Sources
| Source | Rows (entity) | Window | Role |
|---|---|---|---|
| `data/opponents/schwarber.parquet` | 11,449 | 2015-06-16 .. 2021-10-03 | CHC/WSN/BOS era |
| `data/phillies/phils_{2022..2026}.parquet` (`phillies_role=='batting'`, `batter==656941`) | 13,113 | 2022 .. 2026-07-12 | PHI era |
| `wOBA and FIP Constants.csv` | 1 row/season | 2015–2026 | wOBA weights + SC-1 constants |
| **Combined, deduped, R-only** | **24,562** | 2015-06-16 .. **2026-07-12** | build population |

Freshness: 2026 cache max `game_date` = **2026-07-12** = final game before the All-Star break (93 games appeared). T-1 convention satisfied; window is *complete* for the stated scope.

## CDE fitness (BIP null rates from `out/dp_uc20_*_dq_receipts.csv`)
| CDE / field | Fitness | Evidence |
|---|---|---|
| events / description / zone | FIT | null zone 0.21% overall |
| launch_speed, launch_speed_angle (barrel), EV≥95 (hard-hit) | FIT | 0.49% null on BIP |
| estimated_woba_using_speedangle (xwOBA proxy) | FIT | 0.49% null on BIP |
| hc_x/hc_y (spray, pulled-air) | FIT | 1.11% null on BIP |
| wOBA weights (wBB..wHR) | FIT | 0 null after Season join; 2026 row present, **in-season values — flagged** |
| wOBAScale, R/PA (SC-1) | FIT | present all seasons 2015–2026 |
| bat_speed / swing_length / attack_angle | FIT 2024+ ONLY | 2026 coverage 43.3% of pitches (= swings, by design); attack_angle null in 2024 |
| All-Star / Derby facts | NOT IN PLANE | manual carry-in (01 gap 3) |

## Known quirks surfaced (domain-steward pass)
- 2016 = 5 PA (season-ending injury year): retained in receipts, **excluded from narrative claims**.
- 2020 = 223 PA (COVID short season): pace metrics per-600 handle it; flagged on any counting-stat comparison.
- 2021 spans WSN and BOS stints; era label 'WSN/BOS'.
- A pitch can appear in both `pos` and `pps` after concat — dedup on (game_pk, at_bat_number, pitch_number) mandatory (0 dupes after).
- `intent_walk` counts in PA but is excluded from BB per locked definitions (report footer notes it).
