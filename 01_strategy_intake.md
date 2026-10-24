# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**
`uc-pos-022-turner-2026-recap-001` · UC #57 · `dp_uc57` · written at the BID hard stop (2026-10-23 20:49 ET)

## 1 · ID reservation
UC **#57**, contract `uc-pos-022`, build `dp_uc57`, folder `uc-pos-022-turner-2026-recap-001`.
- **Collision check:** no `dp_uc57*` in the MLB root, `out/`, `eda/` (before this run) or the control plane. The IDs appear only as "next available" in the UC56 ledger patch and UC56 `07`.
- **Stale ledger:** the repo ledger's "Next available" line still reads UC52. The UC52–UC56 patches are pending paste, oldest first.

## 2 · Gap report (use-case-validator): 8 gaps, 0 blocking → **GO**
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Atrocious" has no bar | non-blocking | Graded against his 2023–25 Phillies seasons (baseline) and shown against his 2016–22 career band (context). House population rule for any rank |
| G2 | "The conversation I started last night" is not attached | non-blocking | Read as the 2026-10-22 bat-tracking CDE interpretation, already carried forward in UC55 `01` §5. **DPO to confirm** |
| G3 | "Perhaps playing a different position improves his offense" cannot be tested on his data (he played shortstop all season) | non-blocking | HP-12 pre-graded NOT TESTABLE; carry-ins only (CI-2). No proxy model |
| G4 | "Swing path visualization": the Single-Swing Pilot is the obvious tool, but its Gate 2 is open | non-blocking | Tier A uses observed bat-path fields only (BP-1/BP-2, contact-point map). The reconstructed swing is Tier B, conditional on the pilot's Gate 2 and the PL-1 fix |
| G5 | Client frame: name filter, no `game_type` filter, two teams (SRC-4, SRC-5) | non-blocking | Every HP row is reported in both frames; the governed frame locks by MLBAM 607208 + batting role, regular season |
| G6 | Velo segment puts nulls in "< 95" (`fillna(0)`) | non-blocking | Adopted as VS-1 with nulls excluded in the governed frame; 0 affected pitches vs LHP in 2026 |
| G7 | Bat-path fields exist only for 2025–26 | non-blocking | Swing-path comparisons are 2025 vs 2026, peer-netted (PB-1). No 2023–24 swing-path claim |
| G8 | Midseason findings (UC25, UC40a) were measured on partial seasons | non-blocking | Re-graded on the full season with the same code; partial-season values quoted alongside for continuity |

## 3 · Source profile (source-system-profiler)
| Check | Result |
|---|---|
| File | `data/phillies/phils_2026.parquet`, sha `be5d313d…`, rewritten 2026-10-23 19:53. Max `game_date` 2026-10-01 (F); regular season ends 09-27. Anchor **unchanged** from UC54–UC56 |
| Entity | MLBAM 607208, one name, bats R; 0 duplicate pitch keys (game_pk × at_bat_number × pitch_number), 2023–26 |
| Regular-season PA | 2023 692 · 2024 541 · 2025 641 · 2026 700 (reconciles to CI-1) |
| 2026 line from the log | 157 G · 645 AB · 156 H · 19 HR · .242/.297/.378 (reconciles to CI-1) |
| Non-regular rows in the client frame | 2023 D 68 · F 33 · L 107 · 2024 D 78 · 2025 D 72 · 2026 S 153 · E 15 · F 46 pitches |
| Bat-path coverage (share of swings with `attack_angle`) | 2023 0 · 2024 0 · 2025 0.951 · 2026 0.964. `intercept_*` follows the same gate (K40a C6b/C6c) |
| Pitch-group mapping | K54 `PITCH_GROUP`; unmapped 2023–26: EP 4, FA 3, null 4 |
| Small cells | 2026 LHP fastballs ≥ 95 mph: 107 pitches, 22 BIP. 2026 LHP offspeed: 31 BIP. 2026 breaking-ball popups: RHP 15 / 125 BIP, LHP 5 / 47 |
| Full EDA | `eda/dp_uc57/turner_reg_2023_26.md` (9,778 × 42; written by `phillies_dp.eda.to_file`, never printed to context) |
| Lineage | K55 `assert_lineage()` 14/14 pins PASS at bid time |

Fitness: **fit for Tier A.** The only structural limit is G7, the 2025–26 bat-path window.

## 4 · Carry-ins (domain-steward-proxy): quoted, never computed on
| ID | Fact | Source |
|---|---|---|
| CI-1 | 2026: 157 G, 700 PA, 19 HR, .242/.297/.378, wOBA .298, wRC+ 83, 1.1 WAR | [FanGraphs, Trea Turner batting](https://www.fangraphs.com/players/trea-turner/16252/stats/batting), read 2026-10-23 |
| CI-2 | Dombrowski (2026-10-15): "If he plays shortstop like he did in '25, he can play shortstop. But if he plays it like he did in '26, he can't." Second base or the outfield are the named alternatives. 2026 OAA −10 (2025 +17); DRS −17, worst among MLB shortstops; 21 errors, tied for the MLB lead; 507 outs, most in MLB; K% 21% (2025 16.7%); 2025 AVG/OBP .304/.378; seven years and $190M remaining, full no-trade clause | [NBC Sports Philadelphia](https://www.nbcsportsphiladelphia.com/mlb/philadelphia-phillies/trea-turner-shortstop-dave-dombrowski-2027-season/758821/) |

Unread leads (not used): Inquirer pieces of 2026-10-06, 10-09 and 10-15 on a Turner position change.

## 5 · Carry-forward from the prior-chat bat-tracking read and UC40a
- `attack_direction` is **stand-normalised and pull-negative** here (K40a C4/C5, O-15). Pull-side swing direction = `−attack_direction`.
- `intercept_ball_minus_batter_pos_x_inches` is the **lateral** axis and `_y_inches` is **depth** (K40a C1/C2). **No height component ships** (C3).
- `swing_path_tilt` is the plane over the final ~40 ms; `attack_angle` is the sweet spot's vertical direction at impact. They are related but not interchangeable.
- Competitive-swing filter: BP-0 (bunts and sub-25 mph checked swings excluded), as in K40a.
- **PL-1 (this chat's pilot):**
  - the house log holds the pilot HR's intercept fields (intercept_y 23.46 in), so the pilot can source from it;
  - the pilot spec treats `attack_direction` as a raw azimuth and ignores O-15;
  - its contact height uses `plate_z`, which C3 supports.

  These are logged for the pilot's own trail, not fixed here.

## 6 · Glossary (business-glossary-agent)
| Term | Status | Definition |
|---|---|---|
| **PR-1 pitch-recognition gap** | NEW, provisional | Per hand × pitch group × season: in-zone swing rate − out-of-zone swing rate (swing gap), and in-zone contact − out-of-zone contact (contact gap). Zone 1–9 vs 11–14. Change test vs 2023–25 per BID §Pre-registered |
| **VS-1 velo segment** | ADOPTED (client definition) | "High Velo" = `release_speed > 94.9`; "Less than 95 mph" otherwise. Governed frame excludes null velo; client frame (`fillna(0)`) keeps it |
| Popup rate | consumed (K40a PU-2) | Popups / BIP |
| Swing path profile, path by pitch group | consumed (K40a BP-1, BP-2) | Mean tilt, attack angle, contact depth on BP-0 tracked swings |
| Peer-netted delta | consumed (K40a PB-1) | Subject's 2026 − 2025 change minus the cohort's |
| Contact depth | consumed (K40a) | `intercept_ball_minus_batter_pos_y_inches`, mean on BP-0 swings |
| Chase cost, OOZ whiff | consumed (K54 CC-1, `ooz_whiff_rate`) | As certified in UC54 |
| "Atrocious" | client term, not defined | Reported, never used as a threshold |
