# 01 · Strategy & Intake
Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent` · `token-economist`

## 1 · ID reservation
UC #63 · `uc-pps-039` · `dp_uc63` · folder `uc-pps-039-mcfarlane-2026-recap-001`. Collision check in the BID (UC62 patch reserved #63; no `dp_uc63*`).

## 2 · Use-case validation: GO (0 blocking, 5 non-blocking)
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | "Stuff model" subtitle names a model not in either plane | non-blocking | quoted as the client's read; not graded |
| G2 | No AA Statcast (client says so) | non-blocking | AA line as carry-in CI-3; AAA supporting tier from `lhvp26` |
| G3 | "Improved command" needs a pre-2026 baseline | non-blocking | HP-12 NOT OBSERVABLE; AA BB% shown as carry-in |
| G4 | "Bridge to Duran" / "Circle of Trust" undefined | non-blocking | BD-1 specified in the BID; "Circle of Trust" stays commentary |
| G5 | Client chart draws ~137k points | non-blocking | governed figure draws a seeded 20k sample + every McFarlane FF; stated on the chart |

## 3 · Source profile (`source-system-profiler`; full EDA at MLB `eda/dp_uc63/client_frame.md`)
| Source | Rows used | Window | Notes |
|---|---|---|---|
| `data/phillies/phils_2015..2026.parquet` | all roles (FO-1 context) | max game_date 2026-10-01 | client frame: 313 R + 20 F = 333 pitches; 0 S/E rows for him |
| `data/opponents/lhvp26.parquet` | 73 (him) | 7/29–8/8 | AAA, regular season; no wOBA weights (K44 rule) |
| `wOBA and FIP Constants.csv` | Season 2026 | — | weights joined to every 2026 row |
Null profile (client frame): pitch_type 1 (automatic ball 9/27, AB-1); release_speed/spin 1 (same row); zone 1 (same row); arm_angle 176 (display only); BIP launch_speed 0 of 56.

## 4 · Carry-ins (quoted, never computed on)
| CI | Fact | Source |
|---|---|---|
| CI-1 | Recalled 2026-04-24 from Double-A Reading before a weekend series in Atlanta; Walker released, Rangel optioned; no appearance | MLB.com "Phillies call up No. 19 prospect McFarlane"; Heavy.com 4/24 |
| CI-2 | Rob Thomson dismissed 2026-04-28 (9-19); 10-game skid snapped in Atlanta that Sunday; Don Mattingly interim | MLB.com "Dombrowski details Thomson's dismissal" |
| CI-3 | Second recall 2026-07-20 (Dodgers series); AA: 2.06 ERA, 35 IP, 32.9% K, 12.6% BB, 50% GB; sinker "better than 97" | MLB Trade Rumors 2026/07 |
| CI-4 | McFarlane: 4th round 2022, University of Miami | MLB Trade Rumors; miamihurricanes.com (4/24/2026) |
| CI-5 | Kerkering: 5th round 2022, University of South Florida; MLB debut Sept 2023 | gousfbulls.com (7/18/2022); Inquirer / Billy Penn (9/22/2023); log (2023-09-24) |

## 5 · Glossary (`business-glossary-agent`): terms consumed, none redefined
wOBA (house, K44 weights) · xwOBA (XW-1) · K%, BB% (per PA) · whiff (whiffs / swings, K44 lists) · chase (swings out of zone / pitches out of zone) ·
hard-hit (EV ≥ 95 on BIP) · barrel (BR-1, `launch_speed_angle` = 6) · putaway (K / 2-strike pitches) · usage (K44 `pitch_mix`) · IVB / HB (pfx × 12, inches, catcher's view).
New, provisional (BID): FO-1, BD-1, ST-1, FN-1, BS-1r. Copy rules: CL-1 (new), NC-1 (UC #61).
