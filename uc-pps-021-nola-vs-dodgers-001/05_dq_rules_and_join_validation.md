# Layer 2/3 — DQ Rule Definer + Join Validator
### UC-PPS-021

## A. DQ Rule Definer — candidate rules per CDE

Plain-language rules grounded in the CDE definitions and observed distributions (Source Profiler). Handed to the Data Quality Engineer for execution (`07_dq_scorecard.md`).

| Rule ID | CDE | Dimension | Rule | Threshold |
|---|---|---|---|---|
| DQ1 | `pitcher` | Uniqueness | Single entity id `== 605400` (Nolan Hoffman 676510 excluded) | 100% |
| DQ2 | `game_pk+at_bat_number+pitch_number` | Uniqueness | No duplicate pitch keys after dedup | 100% |
| DQ3 | `game_type` | Validity | Regular season only (`== 'R'`) | 100% |
| DQ4 | season coverage | Completeness | Career log spans 2015..2026 | 100% |
| DQ5 | `game_date` | Timeliness | Max == Nola's last start (build freshness) | exact |
| DQ6 | H2H resolution | Completeness | All 7 named hitters resolve to a unique batter id | 7/7 |
| DQ7 | locating CDEs (`pitch_name,plate_x/z,zone,description,stand`) | Completeness | Non-null on every pitch | 100% |
| DQ8 | `estimated_woba_using_speedangle` | Fitness | Non-null on balls in play (`type=='X'`) | ≥99% |

## B. Join Validator — executed on real data

This product has **no cross-domain fact join** (no `gms`), so the fan-out surface is limited to two joins: the season **wOBA-weights merge** and the **H2H batter-id resolution**. Both tested against the live parquet.

| Check | Result | Verdict |
|---|---|---|
| wOBA-constants merge on `game_year` | rows **29,015 → 29,015** | **No fan-out** ✓ (many:1; one constants row per season) |
| Null weights after merge | 0 | PASS |
| Dedup on (`game_pk,ab,pitch`) | 0 duplicate keys | PASS |
| H2H name→id resolution (7 named) | each resolves to **exactly one** MLBAM id | PASS |
| — Mookie Betts → 605141 | 1 match | ✓ |
| — Shohei Ohtani → 660271 | 1 match | ✓ |
| — Freddie Freeman → 518692 | 1 match | ✓ |
| — Max Muncy → 571970 | 1 match | ✓ |
| — Kyle Tucker → 663656 | 1 match | ✓ |
| — Andy Pages → 681624 | 1 match | ✓ |
| — Tommy Edman → 669242 | 1 match | ✓ |
| Modal-stand per id (switch handling) | Edman → L vs RHP; all others single-stand | PASS |

**Join Validator verdict: PASS.** No row multiplication, no orphaned/duplicate ids, no grain drift. The des-parse resolution is 1:1 name→id with no collisions across the 7. (Row counts here reflect the post-refresh cache including 7/22; the pre-game build was identical in structure at 28,926 rows.)
