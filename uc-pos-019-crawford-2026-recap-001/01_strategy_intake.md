# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**

## 1 · ID reservation
UC **#54** · contract `uc-pos-019` · build `dp_uc54` · folder `uc-pos-019-crawford-2026-recap-001`. Ledger tail said next = #52 (pos next `uc-pos-019`). Pending patches UC52 and UC53 claim #52 and #53 and win, so this run takes **#54**. Collision check: no `dp_uc54*` anywhere; `uc-pos-019` appears only as "next available".

## 2 · Gap report (use-case-validator)
| # | Gap | Class | Disposition |
|---|---|---|---|
| G-1 | "Better from ~June 1" is a requester-chosen breakpoint (uc-pos-011 RC-5) | non-blocking | TR-1 pre-registered + RC-5 scan beside it |
| G-2 | Defense: no catch probability, routes, jumps or positioning in the log | non-blocking | XO-1 (client) + XO-2 (proxy) + CI-2/CI-3 carry-ins, labelled |
| G-3 | Client's 2025 is a different level (AAA) | non-blocking | SRC-3 supporting tier, never blended |
| G-4 | "Hitter we expected" has no stated expectation | non-blocking | graded against the uc-pos-011 profile (HP-14) |
| G-5 | Improvement question invites projection | non-blocking | no projection bid; CC-1 arithmetic labelled (C5) |
| G-6 | Platoon deployment (Derek Hill) context | non-blocking | carried as CI-2; PL-1 re-run deferred (Tier B) |

## 3 · Source profile (source-system-profiler)
| Source | Rows for subject | Note |
|---|---|---|
| `phils_2026.parquet` (batting role) | 1,831 (R 1,681 · S 125 · F 25) | 144 regular-season games with a PA; 465 PA; 0 duplicate keys; 0 null zone/pitch type; 4 of 353 BIP without EV |
| `phils_2026.parquet` (pitching role, `fielder_8`) | 18,625 R defensive pitches | 146 regular-season CF games; 506 BIP with `hit_location == 8`; 488 CF-sector air balls ≥150 ft |
| `lhvb25.parquet` | 1,938 (507 PA) | AAA 2025, 25 BIP without EV, `woba_denom` mostly null (supporting tier) |
| `white-sox-of-25-26.parquet` | 3 | **SRC-2:** duplicates of 2026 MLB rows; survive `nphl`'s own de-dupe |
| `atlp26.parquet`, `kilian.parquet` | 101, 6 (by id, other player_name) | pitcher-keyed pulls; not in the client's name-filtered frame |
| `crawford.parquet` | 0 | **ENT-2:** J.P. Crawford (641487, SEA 2019–23) |
| Phillies logs 2017–18 | 1,011 for 641487 | J.P. Crawford batted for PHI; a substring filter on "Crawford" leaks (harness HC-1) |

## 4 · Carry-ins (domain-steward-proxy): labelled at every use, never computed on
| ID | Fact | Source |
|---|---|---|
| CI-1 | Debut 2026-03-26 as starting CF vs TEX; contract selected 2026-03-25 | Wikipedia, "Justin Crawford (baseball)" |
| CI-2 | 149 G, .264/.309/.353, 3 HR, 17 SB in 21, OPS+ 78, −0.2 WAR, −2 DRS, −8 OAA; mostly platooned after Derek Hill emerged, mostly hit ninth | 97.5 The Fanatic, "Phillies Rookie Report Cards: Justin Crawford", 2026-10-14 |
| CI-3 | −3 OAA in March/April (2nd-worst MLB CF), 0 in May; 97th-percentile sprint speed; benched 2026-06-05 in a slump | Philadelphia Inquirer, 2026-06-05 |
| CI-4 | 2025 AAA Lehigh Valley: .334, 7 HR, 46 SB in 112 G | Wikipedia |
| CI-5 | Derek Hill first PHI game 2026-06-13 | derived in uc-pos-011 (inherited constant `K34.HILL_DEBUT`) |

The log reconciles to CI-2's slash line (465 PA; 112 H / 425 AB = .264; OBP .309 on K40's basis).

## 5 · Glossary (business-glossary-agent)
| Term | Status | Definition |
|---|---|---|
| TR-1 June-turn ledger | **NEW, provisional** | 10 pre-registered pre/post signatures (4 results, 6 process), PA-1 verdicts, roll-up rule in `03` §2 |
| CC-1 Chase cost | **NEW, provisional** | Σ over chases of (E[out-of-zone take run value \| count] − swing run value); house take reference 2023–26 |
| XO-2 Sector expected outs | **NEW, provisional** | out share among similar CF-sector air balls (neighbourhood v3) summed over his opportunities; proxy |
| Three-ball reach rate | companion to CC-1 (no new arithmetic) | share of PA reaching a 3-ball count |
| CX-1, CR-1, CR-2, PL-1 | inherited (uc-pos-011) | consumed unchanged |
| Attack regions (heart / shadow / waste) | inherited (uc-pos-005 OZ, IX-1) | ball width 0.25 ft, per-pitch zone |
| XO-1 | client-authored, extracted (IX-1) | `find_similar_hits`: EV ±2, LA ±1, distance ±5 ft |
