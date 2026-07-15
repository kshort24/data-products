# 02 — Source Profile & Fitness (source-system-profiler) · uc-pps-018

**Entity lock:** `pitcher == 661395` (Jhoan Duran, MLBAM). Name filters never used. Verified single id across all three sources.

| Source | Era label(s) | Window | R pitches | Games | Notes |
|---|---|---|---|---|---|
| `data/opponents/duran.parquet` | MIN 2022–2025 | 2022-04-08 → 2025-07-28 | 3,686 | 223 | Pre-trade Twins log. Also contains 57 postseason pitches (2023 WC/ALDS, game_type F/D) — excluded. |
| `data/phillies/phils_2025.parquet` | PHI 2025 | 2025-08-01 → 2025-09-28 | 308 | 23 | Post-trade stint. 66 postseason (D) pitches excluded. **81 PA — small, flagged.** |
| `data/phillies/phils_2026.parquet` | PHI 2026 1H | opening day → 2026-07-12 (cache) | 515 | 34 | Last appearance 2026-07-11. 42 spring (S) pitches excluded. |

**Seam integrity (trade deadline 2025):** zero `game_pk` overlap between the Twins cache and the phils_2025 stint; max Twins date (2025-07-28) < min PHI date (2025-08-01). No double-count risk; DQ check `era_seam` = PASS.

**CDE fitness (career log, 5,024 R pitches after dedup):** pitch_name, release_speed, plate_x/z, zone, description, stand — 100% non-null. events / woba_value / woba_denom / xwOBA ≈ 25.5% non-null = populated only on PA-ending pitches, the expected Statcast pattern (126 PA vs 515 pitches in 2026 ⇒ ~24.5%). Fit for purpose.

**wOBA weights:** season-specific FanGraphs constants joined from `wOBA and FIP Constants.csv` on `game_year`; verified non-null for all rows (DQ `woba_weights` PASS).

**Domain-steward notes (proxy):**
- Duran's splitter is tracked by Statcast as `Split-Finger` at 96–98 mph (the "splinker" — treat as one pitch; no reclassification attempted).
- 3 Sinkers + 31 Sliders in MIN 2022 and 1 Sweeper in MIN 2024 are legacy classification stragglers; left as-is in receipts, immaterial to conclusions.
- Release extension reads uniformly ~0.2 ft lower in 2026 across all pitch types — flagged as probable tracking calibration; report instructed not to over-read.

**Manual carry-ins (logged in `out/dp_uc19_freshness_manifest.csv`):** 24 saves (DPO, 2026-07-13, from DPO's own tracking); 2026 NL All-Star selection.
