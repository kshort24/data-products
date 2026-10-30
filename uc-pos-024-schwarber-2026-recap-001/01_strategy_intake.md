# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy · business-glossary-agent**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` · written at T0 (2026-10-29 20:14 ET)

## 1 · ID reservation
UC **#60**, contract `uc-pos-024`, build `dp_uc60`.
- **Collision check:**
  - `dp_uc59` belongs to `uc-cat-002`, the catcher corps recap. It was scaffolded 10-28 and built 10-29.
  - Its ledger patch reserves "next: UC #60 / dp_uc60 · pos `uc-pos-024`".
  - Nothing named `dp_uc60*` exists in either plane.
- **Prior UCs on the subject (Rule-1 step 3):**
  - UC21 `uc-pos-004`: first half / Derby.
  - UC33 `uc-pos-009`: swing decay. Gives us the sensor-boundary NULL standard and SW-8 damage band.
  - UC58 `uc-pos-023`: HR animation. Gives us the career loader, DH-1, WP-1, HB-1, SP-1 and HR-quality grades.
  - This is the **fourth Schwarber product of 2026** and the one that closes the season.

## 2 · Gap report (use-case-validator): 9 gaps, 0 blocking → **GO**
| # | Gap | Class | Resolution |
|---|---|---|---|
| G1 | The questions ("What happened… concerned… back… pop?") were parked in UC58's intake, not restated in this RFP | non-blocking | Taken as this UC's business questions (BID §The ask); `intake/Schwarber_2026_Home_Runs.md` copied |
| G2 | "Consider the Tier 3" of a *pitcher* redesign brief, for a *hitter* recap | non-blocking | V1–V7 become this report's acceptance criteria. Shared deps SD-1/2/3 are built as house assets. The 13 pitcher items are Tier B (separate UC trace) |
| G3 | "Concern" has no bar | non-blocking | CN-1 pre-registered |
| G4 | "Back" has no onset date in the reporting (CI-2) | non-blocking | CI-5 gives one documented event: 6/23 scratch, one game. BK-1 tests that date; it never claims cause |
| G5 | "Pop" undefined | non-blocking | POP-1 (4 legs) + UC58 HR-quality grades cited |
| G6 | Chase 26.1% (CI-2) is a Savant figure; the house `chase_rate_g` may differ | non-blocking | HP-06 graded on the house definition, gap printed |
| G7 | Bat tracking starts 2024 and swing path 2025 (OI-1) | non-blocking | F4 2024–26 only; "not measured" before |
| G8 | Three ASB constants in the repo | non-blocking | SD-2 `asb_2026`; equivalence asserted (no games 7/13–15) |
| G9 | Dashboard "if it makes sense" | non-blocking | Built (P2), because monthly and box views reward hover |

## 3 · Source profile (source-system-profiler)
| Check | Result |
|---|---|
| House log | `phils_2015..2026`; `phils_2026` sha `be5d313d…` unchanged since UC54; max `game_date` 2026-10-01 |
| Career file | `opponents/schwarber.parquet` (CHC 2015–20, WSH/BOS 2021), id-locked, 0 duplicate keys (UC58) |
| 2026 | 156 G of 162 team games · 702 PA (K57 path; 701 under UC58's PA-X1, one `truncated_pa`) · H1 415 PA, H2 287 PA |
| Missed games (log vs team schedule) | 5/18, 5/19, 5/20, 6/23, 7/28, 7/29. **All six reconcile to CI-5/CI-6** |
| 2026 by month (PA / wOBA / xwOBA) | Mar 22 .323/.273 · Apr 118 .428/.422 · May 112 .379/.360 · Jun 115 .413/.404 · Jul 95 .335/.303 · Aug 131 .333/.352 · Sep 109 .321/.364 |
| Bat speed by month (mean) | 74.1–74.9 mph Apr–Aug (≥ 96% coverage); first look: no visible drop |
| ASB window | 0 house-log games dated 7/13–7/15 (SD-2 assertion holds) |
| CS-1 pool | 122 Phillies hitter seasons ≥ 200 PA, 2015–26 (220 at ≥ 50 PA) |
| Lineage | K58 chain 18 + SD 4 = **22 pins PASS** |
| Render stack | `/tmp/pyrender` re-installed (ENV-3, new VM; weasyprint 70 OK) |

## 4 · Carry-ins (domain-steward-proxy): quoted, never computed on
| ID | Fact | Source |
|---|---|---|
| CI-1 | 45 HR, tied with Pete Crow-Armstrong for the MLB lead | [MLB.com](https://www.mlb.com/news/2026-mlb-regular-season-stat-leaders) |
| CI-2 | 156 G, .232/.354/.503 (prints .853 OPS), 130 wRC+, 2.9 fWAR; halves .254/.367/.560 → .199/.336/.416; K% 31.4% (highest since 2017); 220 K; chase 26.1% (2025 21.5%); "mysterious back injury", no onset date | [Yahoo / SB Nation](https://sports.yahoo.com/articles/2026-phillies-report-cards-kyle-150000667.html) |
| CI-5 | Late scratch Tue 6/23 at WSH, "lower back tightness … while he was trying to swing"; sat that game only; pinch-hit 6/24 (10-pitch walk); started 6/25; no IL; Mattingly: "We don't want this to end up being two weeks" | [MLB.com](https://www.mlb.com/news/kyle-schwarber-scratched-with-lower-back-tightness) · [NBCSP](https://www.nbcsportsphiladelphia.com/mlb/philadelphia-phillies/kyle-schwarber-injury-return-aaron-nola-slider/738973/) |
| CI-6 | Stomach illness: out 5/18–5/20, ending a 225-game streak. GI illness: out 7/28 in Miami ("similar problem" to May) | [MLB.com](https://www.mlb.com/phillies/news/kyle-schwarber-out-of-starting-lineup-vs-reds) · [6abc/AP](https://6abc.com/post/phillies-kyle-schwarber-expected-miss-game-miami-illness/19592487/) |
| CI-7 | 32 HR / 59 RBI through the break, 13 / 38 after; September .172 / .710 OPS; age 33; five-year $150M deal; "limited by a back injury in late June" | [Roundtable, 2026-10-27](https://roundtable.io/sports/mlb/phillies/news/philadelphia-phillies-still-have-a-kyle-schwarber-conundrum) |
| CI-8 | (low weight) An 8/5 report of "lower back tightness" after a late scratch; no date or games given. The log shows no missed game near then | [247talksport](https://www.247talksport.co.uk/2026/08/05/breaking-news-philadelphia-phillies-announce-major-kyle-schwarber-injury-decision/) |

## 5 · Glossary (business-glossary-agent)
| Term | Status | Definition |
|---|---|---|
| SD-1 comparison sets | NEW house asset (registry) | `data/_schema/comparison_sets.json`. This UC uses `phi_hitter_seasons_200` (context) and `_50` (ranks) |
| SD-2 eras | NEW house asset (registry) | `data/_schema/eras.json`: `asb_2026`, `schwarber_2026_back`, `schwarber_2026_absences`, `wheeler_2026_slide` |
| SD-3 helpers | NEW house module | `phillies_dp/recap_viz.py`: `trendline_r2`, `above_below`, `context_box`, `discrete_dots`, `sketch_trend`, `audit` (V1–V7 machine check) |
| BK-1, POP-1, CN-1 | NEW grade rules, provisional | BID §3 |
| SW-8 damage band | consumed (UC33) | Share of tracked BIP with 20° < LA ≤ 32° |
| EV p90 | consumed (UC33/K40 pattern) | 90th-percentile exit velocity on tracked BIP |
| HB-1, WP-1, DH-1, PA-X1 | consumed (UC58) | as ratified for UC58 |
| "Concerned", "pop", "back" | client terms | Graded by CN-1 / POP-1 / BK-1; never used as thresholds themselves |
