# 01 · Strategy & Intake: `uc-pps-038`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · Ledger and ID reservation
- Ground truth for numbering: `uc_ledger_AI_PATCH_uc-pos-025-harper-2026-recap.md` (pending paste; wins over the repo ledger tail's "#52") → **UC #62, `uc-pps-038`, `dp_uc62`**.
- Collision check 2026-11-05 20:17 ET: no `dp_uc62*` in the MLB root or `out/`; no `uc-pps-038*` folder in the control plane.
- Prior art for this subject: none governed. The client's turn-1 code and CSV (`KS Taijuan Walker Analysis.csv`) and this session's ungoverned turn-1 reply are the parents; both are graded as HP rows, not inherited.
- Shape inherited from the pitcher recaps UC48/49/51/52/53 (PDF + dashboard + Artifact) and UC61 (code in the MLB root, trail here).

## 2 · Use-case validation (gap report)
| # | Gap | Class | Resolution |
|---|---|---|---|
| V-1 | "Tell me the story" names no question | Non-blocking | Five client questions Q1–Q5 written into the BID; chapters follow them |
| V-2 | "Highlight his Career Overall" undefined | Non-blocking | Two era totals (2015–22, 2023–26) as diamonds on F1; no single blended career dot, because the two eras answer different questions |
| V-3 | The client chart has no PA floor (`games > 3`) | Non-blocking | KP-1 house floor (≥ 100 PA) for every rank and the KR-1 line; HP-04/HP-07 grade the difference |
| V-4 | "Paid nearly $18 million" is a money claim with no source | Non-blocking | CI-1 (MLBTR); CE-1 on the AAV basis only |
| V-5 | "Angels minor league system": no data in the house store | Non-blocking | Carry-ins CI-2..CI-4; never computed on |
| V-6 | Client frame mixes postseason (SRC-1) and loses pitches to name-dedup (O-26) | Non-blocking | Governed frame is id-locked, regular season; HP-01 reproduces the client frame exactly first |
| V-7 | Turn-1 reply made seven claims of its own | Non-blocking | Graded as HP-01..HP-07 against bars set in the BID |

**Go.** No blocking gap.

## 3 · Source profiling (`source-system-profiler`)
| Source | Rows for 592836 | Notes |
|---|---|---|
| `data/opponents/walker.parquet` (pitcher-keyed) | 13,902 (13,854 R + 48 D) | SEA 2015–16, ARI 2017–19, SEA/TOR 2020, NYM 2021–22. 2017 NLDS rows (D) excluded |
| Other `data/opponents/*.parquet` | 662 rows with `pitcher == 592836` | batter-keyed files; deduplicated on the pitch key by CF-2d (receipt `out/dp_uc62_source_receipt.csv`) |
| `data/phillies/phils_2023…2026.parquet` (pitching) | 6,757 R (2,837 / 1,435 / 2,061 / 424) | + 18 NLDS pitches 2025, + 60 spring pitches 2026, both excluded. File anchor 2026-10-01 |
| Non-MLB rows dropped by CF-2b | 0 | receipt `out/dp_uc62_career_milb_dropped.csv` |
| Minor-league 2026 (ACL, AAA Salt Lake) | none | not in the house store; carry-in only |

Governed career frame: 20,611 pitches, 5,313 PA, 2015–26. EDA to file: MLB `eda/dp_uc62/career_frame.md`.

## 4 · Domain context and carry-ins (`domain-steward-proxy`)
| CI | Fact | Source | Used for |
|---|---|---|---|
| CI-1 | Released 2026-04-23 to clear a rotation spot for Wheeler; 5 G (4 GS), 23 ER, 8 HR in 22.2 IP; $18MM final year of 4/$72MM; Angels owe only the prorated minimum for MLB time | MLB Trade Rumors, 2026-05 ("Angels sign Taijuan Walker to minor league deal") | HP-02, CE-1 AAV, DQ-06/07 reconciliation |
| CI-2 | Opted out of the first Angels deal; contract ended with a 5.12 ERA in 402.2 IP; 9.13 ERA in 2026 | MLB Trade Rumors, 2026-06 ("Taijuan Walker opts out of Angels contract") | DQ-06 tenure outs (1,208), epilogue |
| CI-3 | Re-signed by the Angels 2026-06-11, assigned to AAA Salt Lake | Heavy.com | epilogue |
| CI-4 | 4/22 vs CHC (called "a start"); 4/23 released; 5/23 signed; 6/8 released; 6/11 re-signed; 6/21 released; 5 MiLB starts, 21 IP, 3.86 ERA, 12 K / 7 BB; never promoted | RotoWire player news | HP-03, epilogue |
| CI-5 | 2024: 7.10 ERA in 83.2 IP; 2025 split SP/RP | MLB Trade Rumors, 2026-05 | DQ-06 2024 outs |
| CI-6 | Club by season (SEA, ARI, SEA/TOR, NYM, PHI) | public transaction record | display labels only |

**Conflicts resolved:**
- CI-4 calls 4/22 at Chicago a start. The log shows Kyle Backhus threw the first inning and Walker entered in the 2nd (64 pitches, innings 2–5). CI-1's "four starts" agrees with the log. Recorded as **bulk relief**.
- CI-2 ("three Triple-A starts, 11 IP") and CI-3 ("11 innings between rookie ball and Salt Lake") describe the first Angels stint. CI-4's 5 starts / 21 IP is the full total. The report prints CI-4's total and labels it.

## 5 · Glossary (`business-glossary-agent`)
| Term | Status | Definition |
|---|---|---|
| **KR-1 K-expected residual** | NEW, provisional | House wOBA allowed minus the wOBA the Phillies pitcher-season pool (2015–26, regular season, ≥ 100 PA, subject excluded) allows at the same K%, from an unweighted OLS line |
| **Luck gap** | Existing basis pair (WB-1 − XW-1), named here | Statcast-basis wOBA minus xwOBA on the same PA ends |
| **CE-1 contract economics** | NEW, provisional | AAV divided by outs recorded (OU-2) ÷ 3, and by batters faced, per season; AAV basis only |
| **PR-1 ledger** | NEW, provisional | Ten pre-registered signatures in three families (H-S stuff, H-L luck, H-R residual), scored by PA-1 |
| **Bulk relief** | Existing usage | First pitch after inning 1 in a game the club opened with another pitcher |
| Tenure | Scoped | Phillies regular seasons 2023–26 |
| Market years | Scoped | 2021–22 (the two seasons before the contract) |
