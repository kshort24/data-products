# 05 — DQ Scorecard · uc-pos-005 (dp_uc22)

**Agent roles:** dq-rule-definer + data-quality-engineer · **Verdict: PASS** — 0 blocking, 2 documented dispositions
Receipts: `out/dp_uc22_harper_own_the_zone_dq_receipts.csv` · run 2026-07-15

| # | Rule (plain language) | Dimension | Result | Status |
|---|---|---|---|---|
| 1 | No duplicate pitches after dedup key | Uniqueness | 0 dupes / 16,017 rows | PASS |
| 2 | Single entity id behind the name lock | Consistency | {547180} only | PASS |
| 3 | Regular-season population only | Validity | game_type ∈ {R} | PASS |
| 4 | Location fields complete enough for OZ | Completeness | 10 null rows (0.06%) excluded from OZ only | PASS (disposition A) |
| 5 | Statcast zone null rate within tolerance | Completeness | 0.06% | PASS |
| 6 | BIP launch_speed nulls within tolerance | Completeness | 0.27% | PASS |
| 7 | BIP xwOBA nulls within tolerance | Completeness | 0.31% | PASS |
| 8 | wOBA weights joined for every row | Completeness | 0 null weights | PASS |
| 9 | Freshness = full first half | Timeliness | max game_date 2026-07-12 (ASG break) | PASS |
| 10 | Geometric in-zone vs Statcast `zone<=9` | Consistency | 95.5% agreement | PASS (disposition B) |
| 11 | Monthly HR reconciles to season HR | Accuracy | 20 == 20 | PASS (verification #16) |
| 12 | OZ denominators above spec floors (season grain) | Accuracy | min shadow_in 171, shadow_out 156 (2020) | PASS |

**Disposition A (rule 4):** the 10 location-null pitches remain in locked-kernel aggregates (results/discipline/batted-ball) and are excluded only from region tagging. Effect on any OZ rate < 0.001.

**Disposition B (rule 10):** expected, not a defect. Statcast `zone` uses fixed vertical rails; the OZ geometry uses per-pitch `sz_top`/`sz_bot` (sd 0.14/0.08 ft — see 02). Both definitions are retained by design: locked discipline panel keeps `zone`, OZ family keeps geometry. Consumables never mix the two in one denominator.

**Known limitations carried to the report:** 2020 = 58 G and 2022 = 99 G short seasons (flagged in trend reads); 2026 wOBA constants in-season; xwOBA season aggregate is the locked BIP-weighted proxy; 2026 platoon OZ-4 vs LHP = 24 BIP (below the 40-BIP floor, labeled small-sample in consumables).
