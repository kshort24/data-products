# 05 — DQ Scorecard Summary (data-quality-engineer) · uc-pps-018

Full receipt: `out/dp_uc19_dq_scorecard.csv` (run 2026-07-13).

| Check | Detail | Result | Class |
|---|---|---|---|
| entity_lock | pitcher==661395 only, all sources | **PASS** | blocking |
| dedup | (game_pk, at_bat_number, pitch_number) unique | **PASS** | blocking |
| game_type | R only; postseason + spring excluded | **PASS** | blocking |
| era_seam | Twins max 2025-07-28 < PHI 2025 min 2025-08-01 | **PASS** | blocking |
| woba_weights | season constants joined, non-null all rows | **PASS** | blocking |
| completeness: pitch/location/zone/description/stand CDEs | non-null share | 1.000 | warning threshold 0.98 — clear |
| completeness: events, woba_value, woba_denom, xwOBA | non-null share ≈ 0.252–0.255 | **expected** | PA-ending-pitch population (126 PA / 515 pitches 2026 ≈ 0.245); consistent with UC8/UC11 profiles — not a defect |

**Blocking checks: 5/5 PASS. Product cleared for certification.**

Known data quirks carried from 02 (not defects): 35 legacy-classified pitches in MIN 2022–24 (Sinker/Slider/1 Sweeper); uniform −0.2 ft release-extension shift in 2026 flagged as probable tracking calibration.
