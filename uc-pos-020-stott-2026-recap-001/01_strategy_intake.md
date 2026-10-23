# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**

## 1 · ID reservation
UC **#55** · contract `uc-pos-020` · build `dp_uc55` · folder `uc-pos-020-stott-2026-recap-001`.

Collision scan at bid time:
- `dp_uc55*` absent at the MLB root, in `out/`, in `eda/` and in the control plane.
- `uc-pos-020` named only as "pos next" in the UC54 patch.
- Prior Stott work: `uc-pos-010` / dp_uc33 (approach change through 2026-08-13) and `uc-pos-stott-qab-001` (intake only).

## 2 · Gap report (use-case-validator)
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Good" eras are hand-set from memory of outcomes | Non-blocking | ER-1 (governed detector) + hindsight-corrected p for each client era |
| G2 | The A/B test compares results that defined the eras (circular) | Non-blocking | GS-1 scores process signatures only; results reported, not scored |
| G3 | Defense question has no fielding metric in the log | Non-blocking | IO-1 proxy + OAA/DRS carry-ins beside it |
| G4 | "Thump" is undefined | Non-blocking | Defined as ISO / HR / barrel per BIP on Phillies PA, 2026 (thump ledger); no new KPI |
| G5 | Client frame has no game-type filter (SRC-4) | Non-blocking | HP rows reproduced on both frames |
| G6 | Bat path exists 2025-26 only; 2023 era has none | Non-blocking | Bat-path chapter limited to 2025-26 and labelled |
| G7 | Stance change date is not in the log | Non-blocking | Carry-in CI-2; the post-break first game is derived from the schedule (2025-07-18) |

## 3 · Source profile (source-system-profiler)
| Item | Value |
|---|---|
| House log | `phils_2015..2026.parquet`, 556,863 rows; anchor 2026-10-01 |
| Subject, regular season | 11,834 pitches 2022-26; PA 466 / 638 / 569 / 562 / **608** |
| Non-regular PA in the client frame | 182 (2026: 37 spring, 3 exhibition, 13 Wild Card) |
| Bat tracking (tracked swings) | bat speed 2024+; attack angle/direction, tilt and intercepts 2025+; coverage 97-98% of swings |
| Defense | games at 2B 47 / 149 / 137 / 135 / 116 · games at 3B 2026: 43 (first 2026-08-04, the day Arraez's Phillies PA begin) |
| Untracked BIP | 4 without EV across 2022-26 (O-8) |

## 4 · Carry-ins (domain-steward-proxy): quoted, never computed on
| CI | Fact | Source |
|---|---|---|
| CI-1 | 2026: .256, 10 HR, 62 BB (career high), 155 G, 4.14 P/PA | thatballsouttahere, 2026-10-22 |
| CI-2 | 2B 2026 +8 OAA / −9 DRS (953⅓ inn); Mar–May .217, Jun–Aug .286 (2.8 fWAR), Sep .692 OPS; 27/27 SB; 2025 1H .234/.637 → 2H .294/.855 after a stance change under Kevin Long; Dombrowski quote | On Pattison, 2026-10-18 |
| CI-3 | Moved to 3B after the Arraez trade: +2 OAA / +3 DRS in 129 inn; Dombrowski "not … a third baseman for the long term" | Inquirer / Central Bucks News, 2026-08-19/20 |
| CI-4 | Career 2B +33 OAA / +8 DRS (as of 2026-08-22) | The Sun Papers, 2026-08-22 |
| CI-5 | Bohm in the final year of his contract | NBC Sports Philadelphia, 2026-05-06 |
| CI-6 | 2023: franchise-record 17-game streak to open, .280/.329/.419 | Wikipedia |

Reconciliations: the log gives .256, 10 HR and 62 BB, matching CI-1. The 2023 log OBP is .327 against CI-6's .329, which is the K40 OBP convention (SF-1 family).

## 5 · Carry-forward from this session's data-dictionary read
Turn 1 of this session interpreted the client's six-CDE card. K40a's proven conventions answer that read's open items:
- **`attack_direction` is stand-normalised and PULL-NEGATIVE** in this data plane, the inverse of the published glossary (O-15). Turn 1 had guessed "probably not normalised for handedness", and that guess is withdrawn.
- `intercept_y` is the **depth** axis (C2).
- Bat path ships from 2025.
- `arm_angle` is out of scope for a hitter recap.

## 6 · Glossary (business-glossary-agent)
| Term | Status | Definition |
|---|---|---|
| **ER-1 form eras** | NEW, provisional | Within-season segments of the PA-ordered wOBA atom, split only where the SSE gain beats 500 order permutations at α .10; ≥100 PA each; ≤3 per season; labelled Good / Par / Bad at career ± .020 |
| **GS-1 good-era signatures** | NEW, provisional | Ten process metrics compared Good minus Bad with pre-set bars, scored by PA-1; roll-up → DIFFERENT / PARTLY DIFFERENT / SAME HITTER |
| **IO-1 infield sector expected outs** | NEW, provisional | Ground balls in a position's sector while the subject plays it, scored against the out share of similar grounders (EV, LA, spray) fielded by anyone else in Phillies games 2023-26. Proxy |
| Contact depth | consumed (K40a) | `intercept_ball_minus_batter_pos_y_inches`, mean on BP-0 tracked swings |
| Swing direction (pull +) | consumed (K40a) | `−attack_direction` (O-15) |
| Thump ledger | descriptive | ISO, HR, barrel/BIP, xwOBA on 2026 Phillies PA; no new KPI |
