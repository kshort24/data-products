# 05 — Data Quality Scorecard · uc-pos-006 (dp_uc24)

**Agent role:** data-quality-engineer · **Verdict: PASS (no blocking)** — executes rules against the built product; does not fix data. Receipt: `out/dp_uc24_turner_2026_review_dq_receipts.csv`.

## Scorecard
| Dimension | Rule | Result | Class |
|---|---|---|---|
| Uniqueness | 0 duplicate `[game_pk, at_bat_number, pitch_number]` | **0 dupes / 23,250 rows** | PASS |
| Uniqueness | single entity id | **1 id (607208)** | PASS |
| Completeness | zone non-null | 99.98% | PASS |
| Completeness | EV/LA non-null on BIP | 99.06% | PASS |
| Completeness | spray (`hc_x`) non-null on BIP | 99.30% | PASS |
| Completeness | xwOBA field non-null on BIP | 99.06% | PASS |
| Completeness | wOBA weights non-null | 100% (0 nulls) | PASS |
| Coverage | bat-tracking (2024+) | 49% of swings; `attack_angle` 2025+ | WARN → labeled directional |
| Validity | rates in [0,1]; slash components ≤ PA | all valid | PASS |
| Consistency | RF-1 season endpoint == `get_stats` OPS | 4/4 seasons match | PASS |
| Consistency | receipt KPIs == independent recompute | **33/33** (`dp_uc24_verification.py`) | PASS |
| Timeliness | freshness ≤ T-1 | max `game_date` 2026-07-20 (T-1) | PASS |

## Threshold register (sub-50-PA lines — published only as directional, labeled inline)
| Split | PA / sample | Handling |
|---|---|---|
| Post-ASB 2H | 14 PA / 3 games | labeled "cameo, directional only" (report §5/§7) |
| vs LHP 2026 | 144 PA | flagged "real enough to note, not to close the book" |
| Monthly buckets | 23–117 PA | PA printed on every line/figure |

## Issue caught & remediated (honesty gate)
- **DQ-1 (corrected):** initial report drafted pulled-air (.117) and pull rate (.352) as **"career low."** Verification recompute showed **2020 was lower** (pulled-air .111, pull .322). Claim corrected to **"Phillies-era low, lowest since 2020"** across §Bottom-line/§4/§6, and a standing verifier assertion (`honesty: 2020 pulled-air < 2026`) now guards the phrasing. No number changed — only the superlative. This is the intended function of the certification gate and is logged here per the "candid caveats are part of the product" rule.

## Not remediated (by design)
- The 2024+ bat-tracking coverage gap is a source limitation, not a defect — carried as WARN, never blended into full-history tables.
