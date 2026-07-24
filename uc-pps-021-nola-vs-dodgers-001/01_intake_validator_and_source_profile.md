# Layer 1 — Intake & Discovery
### UC-PPS-021 · Use Case Validator + Source System Profiler

---

## A. Use Case Validator — gap report on the incoming use case

Validating the request ("extend the Nola advance file with his last few starts; matchup vs 7 named Dodgers hitters; contextualize approach shifts; tie to persona actions") against feasibility and the locked KPI contract.

### Verdict: **GO** for build — no blocking gaps.

| ID | Field / Section | Issue | Severity | Resolution |
|---|---|---|---|---|
| V1 | Matchup lineup | 7 named hitters given, not a confirmed 1–9 card | Non-blocking | DPO scoped to the 7; labeled a manual carry-in everywhere; confirm pre-game (→ O2) |
| V2 | "his last few starts" | window underspecified | Non-blocking | Fixed to the 3 starts since dp_uc15 (7/05, 7/10, 7/16); recency split + game lines added |
| V3 | Roster timeline | Kyle Tucker as a Dodger is sandbox-specific | Non-blocking | H2H resolved from Nola's own log (des-parse); no hand-keyed ids; 7/7 found |
| V4 | xwOBA metric | which xwOBA? (pitch-level col is unstable) | **Non-blocking (find)** | Standardized on `xwobacon` = mean estimated wOBA on BIP; pitch-level `get_stats.xwoba` deprecated (→ O1) |
| V5 | wOBA methodology | FanGraphs vs Statcast disagree ~.01 | Non-blocking | Locked KPI = FanGraphs; labeled; supersedes dp_uc15's Statcast-side .377 |

All residuals carried as acknowledged assumptions — none silently dropped. No blocking issues.

---

## B. Source System Profiler — CDE fitness for purpose

Profiled against the loaded entity-locked frame (build cache): **28,926 pitches / ~305 games / 12 seasons (2015–2026)**, max `game_date` **2026-07-16** (Nola's last start at build time). 2026 subset = **1,802 pitches / 20 GS**. Source: `data/phillies/phils_2015..2026.parquet`, `phillies_role=='pitching' & pitcher==605400 & game_type=='R'`, deduped on `game_pk+at_bat_number+pitch_number`.

| CDE | Domain | Completeness | Fitness note |
|---|---|--:|---|
| `pitch_name` | Pitch Profile | 100.0% | Arsenal, usage, whiff-by-type; fit |
| `release_speed` | Pitch Profile | 100.0% | Velo tracks; fit |
| `plate_x` / `plate_z` / `sz_top` / `sz_bot` | Strike Zone | 100.0% | Edge rate, location maps; fit |
| `zone` | Strike Zone | 100.0% | Chase (zone>9), OOZ; fit |
| `description` | Pitch Outcomes | 100.0% | Whiff/chase/putaway; fit |
| `stand` | At-Bat Outcomes | 100.0% | L/R splits; fit |
| `events` | At-Bat Outcomes | **25.9%** | Null **by design** — only PA-ending pitches carry an event; fit |
| `woba_value` / `woba_denom` | At-Bat Outcomes | **~25.8%** | Null **by design** — PA-ending only; used for the Statcast cross-check |
| `launch_speed` / `launch_angle` | Batted Ball Profile | **29.5%** | Null **by design** — balls in play only; drives hard-hit; fit |
| `bb_type` | Batted Ball Profile | **17.2%** | Null **by design** — BIP only; drives AIR/GB; fit |
| `estimated_woba_using_speedangle` | Batted Ball Profile | **>99% on BIP** | The xwOBAcon source — verified populated on balls in play every season (see §xwOBAcon fitness) |
| `wBB…wHR` | wOBA Weights | 100.0% | Season weights merged on `game_year` at load |

**Low-completeness columns are expected** — they populate only on the relevant pitch class (contact / PA-ending). No fitness concern.

### Entity lock
`pitcher == 605400` (Aaron Nola). Guards the canonical **Nolan Hoffman (676510)** name-filter contamination. H2H batter ids resolved by des-parse (modal name per batter id) — no hand-keyed MLBAM ids.

### xwOBAcon fitness (the DQ find → O1)
The locked `get_stats.xwoba` column is a **pitch-level mean** of `estimated_woba_using_speedangle` over *all* rows; because a minority of non-BIP rows (some strikeouts) carry a 0.0, that mean is contaminated and swings year-to-year (e.g. 2024 read .303 vs a true .371). Profiled the field directly: it is **>99% populated on balls in play (`type=='X'`) every season 2015–2026**, so `xwobacon` (BIP-only mean) is the fit-for-purpose contact-quality read. The pitch-level column is flagged for deprecation.

### Coverage flag (→ O4)
At build time the cache was fresh through **2026-07-16**. The **2026-07-22 start synced in on 2026-07-24** (post-build). The pre-game product is correctly scoped to the 7/16 window; the refreshed cache (now 29,015 pitches / 306 games) is used only by `08_post_game_backtest.md`.

**Profiler verdict:** source is **fit for purpose** for every KPI at all declared grains. One documented freshness-boundary item (O4).
