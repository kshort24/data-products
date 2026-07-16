# 05 — DQ Scorecard & Verification (data-quality-engineer) · uc-pps-020

## Structural checks (receipt: `out/dp_uc23_dq_scorecard.csv`)
| Check | Detail | Result |
|---|---|---|
| entity_lock | pitcher==554430 only rows in frame | **PASS** |
| entity_resolution | id from player_name mode, consistent across 4 seasons | **PASS** |
| dedup | game_pk+at_bat_number+pitch_number unique | **PASS** |
| game_type | regular season only | **PASS** |
| first_half_windows | max game_date ≤ cutoff per year | **PASS** |
| weights_join | wOBA weights joined all seasons | **PASS** |
| completeness | 15 key CDEs, non-null share on locked frame | all ≥ .97 except known-sparse BIP fields; `n_thruorder_pitcher` = 2025/2026 only (scoped in 01/G4) |

## Independent verification (receipt: `out/dp_uc23_verification.csv`) — **23/25 PASS, 2 method-variance dispositions**
Recomputed via alternative method paths (Statcast `woba_value/woba_denom` instead of the FanGraphs-weight kernel; direct event counts; pitch-grain velo instead of start-grain): all counting stats (starts/K/BB, all four years), IP/RA9 2026, chase/in-zone/hard-hit/splitter-usage 2026, FF velo 2021/2026, and the staff-best-starter claim reproduce exactly or within tolerance.

**Dispositions (2):** `woba_2021` (.240 kernel vs .249 alt) and `woba_2024` (.258 vs .275). Cause: two weight systems — the locked kernel uses FanGraphs season constants over all PA; the alt method uses Statcast's internal `woba_value/woba_denom` (466–471 denominator agreement confirmed; zero IBB in both halves, so no population gap). The governed number is the kernel's, consistent with every prior pps/pos UC. **Rank order and every report claim are invariant under both methods** (2024 is the worst wOBA half and 2021/2025/2026 cluster tightly in both). Classification: method variance, not error — same disposition class as uc-pps-019's single variance.

## Sample-size ledger (inline-flag obligations, all honored in report)
July 2026 = 71 PA · April 2026 = 20 PA (1 start) · TTO-3 2026 = 85 PA · per-pitch-type cells range 118–522 pitches (usage grain) — season-grain cells all clear the 100-BF convention.

## Blocking classification
No blocking findings. Report shipped with all warnings carried inline.
