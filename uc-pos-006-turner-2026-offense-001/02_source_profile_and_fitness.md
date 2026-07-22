# 02 — Source Profile & Fitness-for-Purpose · uc-pos-006 (dp_uc24)

**Agent role:** source-system-profiler · **Verdict: FIT** — all requested CDEs present and within tolerance; entity clean; freshness T-1. Characterizes what exists before the architect models it.

## Entity lock
- **batter == 607208 (Trea Turner).** Single id across all sources — `turner.parquet` resolves to 607208 for 100% of rows; PHI frames filtered `batter==607208 & phillies_role=='batting'`. No name-filter used (avoids the Nola/"Nolan" contamination class). 0 secondary ids.

## Sources & windows
| Era | Source | Seasons | Rows (R, deduped) | Notes |
|---|---|---|---|---|
| WSN | `data/opponents/turner.parquet` | 2015–2021 | (part of 15,279) | 2021 split WSN→LAD handled at row level via batting-team |
| LAD | `data/opponents/turner.parquet` | 2021–2022 | — | |
| PHI | `data/phillies/phils_{2023..2026}.parquet` | 2023–2026 | 2,883 / 2,121 / 2,479 / 1,795 (all rows) | `phillies_role=='batting'` |
| **Total** | concat, deduped on `[game_pk, at_bat_number, pitch_number]` | 2015–2026 | **23,250 pitch rows** | 0 duplicate keys |

- **Team-per-row** derived from `inning_topbot` + home/away team (robust to the 2021 mid-season trade); era = {WSH→WSN, LAD, PHI}.
- **Freshness:** max `game_date` = **2026-07-20** (T-1 vs prepare date 2026-07-21). 2026 = 98 team games — first half **plus 3 post-All-Star-break games** (07-18…07-20). All-Star break date (07-16) is a manual carry-in.

## CDE fitness (null rates on balls-in-play unless noted)
| CDE / field | Coverage | Fitness |
|---|---|---|
| `events`, `description`, `type`, `zone` | zone null 0.02% | PASS — PA/AB/discipline safe |
| `launch_speed`, `launch_angle` (EV/LA) | BIP null 0.94% | PASS — barrel/hard-hit/EV safe |
| `launch_speed_angle` (barrel enc.) | BIP null 0.94% | PASS |
| `estimated_woba_using_speedangle` (xwOBA) | non-null on 100% of PA-ending events (K=0, BB at weight, BIP by speed/angle) | PASS — supports PA-level xwOBA + xwOBACON |
| `hc_x` / `hc_y` (spray → pulled-air) | BIP null 0.70% | PASS |
| wOBA weights (`wBB…wHR`) | 0 nulls after `Season==game_year` join | PASS |
| `bat_speed`, `swing_length`, `attack_angle` | **2024+ only; ~49% of swings**; `attack_angle` 2025+ | PARTIAL — labeled directional; not used pre-2024 |

## Fitness verdict
**FIT for all requested indicators.** The only sub-census field is the 2024+ bat-tracking tier (coverage ~49%, `attack_angle` from 2025) — flagged directional in the report §1/§7 and never blended with the full-history rate tables. No park/league adjustment plane exists locally → wRC (not wRC+) only; stated in 03/06.
