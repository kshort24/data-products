# 05 — DQ Scorecard · uc-pos-004 (dp_uc20)

**Agent roles:** dq-rule-definer + data-quality-engineer · **Verdict: PASS** (0 blocking, 2 warnings)
Machine receipt: `out/dp_uc20_schwarber_first_half_dq_receipts.csv` · run 2026-07-14

| # | Rule (dimension) | Threshold | Result | Status |
|---|---|---|---|---|
| 1 | Entity purity — all rows batter==656941 (accuracy) | 100% | 100% (filter-enforced, verified in verification script) | PASS |
| 2 | Duplicate pitch keys after concat (uniqueness) | 0 | **0** / 24,562 | PASS |
| 3 | game_type=='R' only (validity) | 100% | 100% (filter-enforced) | PASS |
| 4 | Null zone rate (completeness) | <2% | 0.21% | PASS |
| 5 | Null launch_speed on BIP (completeness) | <2% | 0.49% | PASS |
| 6 | Null hc_x/hc_y on BIP (completeness) | <3% | 1.11% | PASS |
| 7 | Null xwOBA proxy on BIP (completeness) | <2% | 0.49% | PASS |
| 8 | wOBA weight nulls after Season join (consistency) | 0 | **0** | PASS |
| 9 | Freshness — max game_date ≥ ASG-break cutoff (timeliness) | 2026-07-12 | 2026-07-12 | PASS |
| 10 | Sample floors — 50-PA convention on published rate splits (validity) | flag below floor | July 2026 = 48 PA → **flagged directional in report §7**; 2016 = 5 PA → excluded from narrative | PASS w/ flags |
| W1 | bat_speed coverage 2026 = 43.3% of pitches | info | expected (tracked on swings only, ≈ swing rate .443) | WARNING (definitional) |
| W2 | 2026 wOBA/wRC constants in-season | info | SC-1 outputs provisional ±2%; restated in report | WARNING (upstream) |

**Independent verification (beyond DQ):** `dp_uc20_verification.py` recomputed 18 headline claims by a non-kernel code path — **18/18 PASS** (PA, HR, slash line, wOBA, wRC, P/PA, in-zone swing, pulled-air, count-state wOBA, platoon, HR log, games, freshness).
