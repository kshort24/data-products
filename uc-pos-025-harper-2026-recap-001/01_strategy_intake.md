# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` · written at T0 (2026-11-02 18:05 ET)

## 1 · ID reservation
UC **#61**, contract `uc-pos-025`, build `dp_uc61`.
- **Collision check:** the UC60 ledger patch reserves "next: UC #61 / dp_uc61 · pos `uc-pos-025`". No `dp_uc61*` file or `uc-pos-025` folder in either plane. The repo ledger still reads UC52 (UC52–UC60 patches pending paste).
- **Prior UCs on the subject (Rule-1 step 3):** UC #23 `uc-pos-005` / dp_uc22, "Own the Zone" (first half 2026, verified 18/18). The client's "I think there was just one" is correct for governed UCs.
- **Ungoverned prior art (cited, not inherited):** `harper_vs_lhp_deep_dive.py` + `_report.md` (Jun 6), `harper_high_leverage_splits_2026.py` (May 31), `harper_2026_visuals.py` and `harper_cumulative_bb_rate.py` (Oct 12, October 2026 notebook).

## 2 · Gap report (use-case-validator): 7 gaps, 0 blocking → **GO**
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Career since 2015 or at least pre-Phillies": which band? | non-blocking | Both: Washington 2015–18 (dashed) and Phillies 2019–25 (solid + min–max band); 2026 red |
| G2 | "Option to filter to OPS and maybe other metrics" | non-blocking | CM-2 ships BA/OBP/SLG/OPS/wOBA/HR per PA for all 12 seasons; one chart (wOBA) rendered, as the client allowed |
| G3 | "Pitches he likes to hit and do damage against" has no definition | non-blocking | DMG-1: damage = hard-hit BIP (≥ 95 mph, house) or HR; xwOBA by hand × pitch group for the callouts |
| G4 | "Use of the whole field" undefined | non-blocking | House DR-1 direction (pull / straightaway / oppo) + K46 pull-air, with his 2019–25 range |
| G5 | "Very basic outline" vs every park | non-blocking | One outline (house CBP wall, K54 `CBP_DIMS`), captioned "every park, drawn on one outline" (UC58 rule) |
| G6 | One-line summary unspecified | non-blocking | Written at T3 from graded findings only (HP-02 + HP-03) |
| G7 | Deliverable format: pieces for Claude Design | non-blocking | Design kit (data + copy + reference PNGs + brief); PDF/dashboard Tier B |

## 3 · Source profile (source-system-profiler)
| Check | Result |
|---|---|
| House log | `phils_2019..2026`; 2026 regular season max `game_date` 2026-09-27 (anchor 10-01 holds) |
| Career file | `opponents/harper.parquet`: WSH 2015–18, 10,288 rows, one batter id (547180); 2016–17 NLDS rows excluded by `game_type` |
| 2026 | 2,747 regular-season pitches · 693 PA · 161 G with a PA · H1 408 PA, H2 285 PA · 76 non-regular-season pitches excluded (49 Wild Card, 27 spring training) |
| Missing game | 5/9 vs COL: no PA, fielding play at 1B in the log → 162 G appearances (= CI-1) |
| Positions (log) | 1B 109 G, RF 43 G (first 8/4), DH/none-with-PA 11 G |
| Doubleheaders | 2026-04-30 game_pk order is wrong (UC58 DH-1: 823472 was Game 1) → sourced override DH-2. 27 earlier DH days on game_pk fallback (intra-day order only; season totals unaffected) |
| Untagged / unlocated | 13 2026 pitches (no pitch_type or no plate location); drawn grey or not drawn, excluded from group KPIs |
| EDA | `eda/dp_uc61/harper_reg_2015_26.md` (27,237 × 97), `harper_reg_2026.md`; never printed to context |
| Render stack | `/tmp/pyrender` installed (`requirements-render.txt`; TMPDIR moved off the full `/sessions` disk, ENV-4) |

## 4 · Carry-ins (domain-steward-proxy): quoted, never computed on
| ID | Fact | Source |
|---|---|---|
| CI-1 | 2026: 162 G, 577 AB, 93 R, 155 H, 32 2B, 29 HR, 87 RBI, 148 SO, 7 SB, .269/.380/.485, .865 OPS | [MLB.com player page](https://www.mlb.com/ja/player/547180) |
| CI-2 | ".269/.380/.485, 29 HR, 87 RBI, 93 R, 7 SB across 693 PA"; "approach and discipline held up but hard contact faded"; ".997 OPS vs RHP, .657 vs LHP"; 8/4 move to the outfield (first OF work since 2022) to make room for Luis Arraez; 9/27 HR No. 29 vs TB, "once in his prior 27 games" | [RotoWire player page](https://www.rotowire.com/baseball/player/bryce-harper-11036) |
| CI-2x | RotoWire's injury list (wrist inflammation in June, thumb, forearm, hamstring) mixes in 2025 items | **not used**; the card makes no injury claim |
| CI-3 | UC #23 headline: "He is owning the edge" (H1 OZ-1 .411, best in five years) | `dp_uc22_harper_own_the_zone_report.md` |

## 5 · Glossary (business-glossary-agent)
| Term | Status | Definition |
|---|---|---|
| CM-2 cumulative slash | NEW generalization (provisional) | Running BA/OBP/SLG/OPS/ISO/wOBA/HR/K%/BB% by PA within season on `nresults_unrounded` definitions; rates blank before 25 PA; endpoints asserted equal to the season panel |
| Career envelope | NEW (provisional) | Per-PA min / median / max of a cumulative metric across a season set, with `n_seasons` per PA; never extrapolated |
| DMG-1 damage | NEW (provisional) | Hard-hit BIP (launch_speed ≥ 95) or HR |
| AP-1 / HC-1 / OZ-H | NEW grade rules (provisional) | BID §3 |
| NC-1 notecard copy rule | NEW (provisional) | Every printed number is generated from a headline key and registered; harness re-formats each and scans the copy for unregistered numbers |
| DH-2 | NEW (provisional) | A sourced doubleheader order overrides the DH-1 game_pk fallback |
| OZ-1..OZ-4, shadow band | consumed (UC #23) | One ball width (0.25 ft) either side of the rulebook edge |
| PA-L1, DR-1, K46 pull-air, CR-1, XW-1, WB-2 | consumed | House definitions via the K57 chain |
