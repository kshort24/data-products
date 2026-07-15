# 05 — Quality & Certification · uc-pps-017 (UC #19)

## data-quality-engineer — DQ scorecard (`dp_uc17_dq_scorecard.csv`)

| Check | Result |
|---|---|
| Entity lock (pitcher==666200 only) | **PASS** |
| Dedup (game_pk + at_bat_number + pitch_number unique) | **PASS** |
| Game type (regular season only) | **PASS** |
| wOBA weights join (both seasons) | **PASS** |
| Completeness — pitch-grain CDEs (pitch_name, release_speed, plate coords, zone, description, stand, fielder_2, n_thruorder, scores) | 1.000 |
| Completeness — PA-terminal CDEs (events, woba_value, woba_denom) | ≈0.25 — expected (populated on PA-final pitch only), not a defect |

## certification-agent — independent recomputation

Headline numbers recomputed via a deliberately different code path (tail-of-PA + value_counts mechanics, no kernel reuse):

| Metric | Build | Recompute | Match |
|---|---|---|---|
| K (2026) | 136 | 136 | ✓ |
| PA (2026) | 465 | 465 | ✓ |
| wOBA against (2026) | .295 | .295 | ✓ |
| Sweeper usage (2026) | .371 | .371 | ✓ |
| Starts | 19 | 19 | ✓ |

## Certification readiness

| Artifact | Present | Consistent |
|---|---|---|
| Use-case contract + spine (00) | ✓ | ✓ |
| Intake gap report (01) | ✓ | ✓ |
| KPI specs incl. PD-1..PD-7 (02) | ✓ | ✓ |
| Glossary/tagging/privacy (03) | ✓ | ✓ |
| Lineage sketch (02) + build record (04) | ✓ | ✓ |
| DQ scorecard + freshness manifest | ✓ | ✓ |
| Report — every number traces to a receipt | ✓ | ✓ (spot-audited: §1 table ↔ season_line/season_xwoba; §5 tables ↔ by_stand/tto/battery; figs annotated from their CSVs) |

**Status: READY.** Known flags (not blocking, disclosed in report): July 49 PA, Marchán 70 PA, IP/RA9 reconstructions, 2025-full vs 2026-half asymmetry, All-Star fact as manual carry-in.

**Closure step (offered):** post-All-Star refresh — extend the window through the break, re-run unchanged spec, diff the monthly trend. Non-breaking (03).
