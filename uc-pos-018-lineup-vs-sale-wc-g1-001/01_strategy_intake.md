# 01 · Strategy & Intake: `uc-pos-018`

Agents: `use-case-validator` · `source-system-profiler` · `domain-steward-proxy` · `business-glossary-agent`

## 1 · ID reservation

| Item | Value |
|---|---|
| UC | **#50** (ground truth: `uc_ledger_AI_PATCH_uc-pps-034…md`, "Next available: UC #50 … pos next `uc-pos-018`") |
| Contract | `uc-pos-018` |
| Build | `dp_uc50` |
| Folder | `data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/` |
| Collision check | `ls dp_uc50* uc-pos-018*` at the MLB root → none; `out/dp_uc50*` → none; control plane → none |
| Lineage | `uc-pos-001` (dp_uc14, Phillies vs Wacha, first lineup-vs-starter card) → **uc-pos-018**. Directional parts from `uc-pos-017` (dp_uc46). Pitcher-side Sale section from the `uc-pps` pattern (`dp_uc44` PM-1 style) |

## 2 · Gap report (`use-case-validator`)

| # | Gap | Class | Resolution |
|---|---|---|---|
| G-1 | Lineup given by name only | **Blocking** | Resolved from `phils_2026` batting rows: batter id × modal `player_name` (DQ-03). No id was hand-keyed |
| G-2 | "Index card" has no spec beyond the three examples | Non-blocking | Card spec derived from the three: header + 2026 vs LHP + career vs Sale + a narrative + one visual (`02` §5) |
| G-3 | Grains for the six new hitters unspecified | Non-blocking | Inherited the client's three (2026 vs LHP, career vs Sale, LHP rank). Added pitch group vs LHP (2024–26 and 2026), HL-1 thirds and last 30 days, because Sale's arsenal splits that way |
| G-4 | Consolidated card format unspecified | Non-blocking | One-page notecard + report table (`02` §5) |
| G-5 | Postseason / spring PA vs Sale? | Non-blocking | None exist for these nine (DQ-07). Rates are regular season |
| G-6 | Game time and starter confirmation | Non-blocking | Carry-ins: 2:00 p.m. ET on NBC (worldbaseball.com; MLB.com game page); Sale named G1 starter (Battery Power) |

**Client claims graded at intake** (full grading in `03` §6 and `out/dp_uc50_hp_reconciliation.csv`): Turner ×5 · Schwarber ×2 · Harper ×1 · Sale subtitle ×1 · Sale frame completeness ×1 · Sosa (cell 137) ×1 · Hill barrels (cell 152) ×1.

## 3 · Source profile (`source-system-profiler`)

**Method:** an id scan over every parquet in `data/opponents/` (columns `batter`, `pitcher`, `game_year`, `game_type` only), not a byte search (BS-1) and not a name filter (O-26).

| Source | What it holds for this UC | Precedence in BF-1 |
|---|---|---|
| `data/phillies/phils_2015…2026.parquet` | Every Phillies-tenure PA; Sale vs the Phillies in every year | 0 |
| `sale.parquet` | Sale, pitcher-keyed, 2015-04-12 → **2025-05-23** (22,211 pitches) | 1 |
| `turner` / `schwarber` / `harper` / `realmuto` / `derek_hill` / `bdlc` / `edmundo` `.parquet` | Pre-Phillies careers, batter-keyed | 1 for that id |
| `atlp26.parquet` | Braves 2026 pitching; Sale **2,575** pitches (27 starts, last 9/23) | 2 |
| 17 other opponent files | Sale pitches keyed to other batters (e.g. `arraez`, `castellanos`, `hays`, `whit`); lineup PAs vs other pitchers | 3 |
| minor-league tiers (`lhvo26`, `lhvp25`, `lhvb25`, `clw*`, …) | De La Cruz and Bohm AAA rows | **excluded** |

**Per-hitter coverage** (regular season, after dedup; `out/dp_uc50_coverage.csv`):

| Hitter | First | Last | Pitches | Sources |
|---|---|---|---|---|
| Turner | 2015-08-21 | 2026-09-27 | 24,276 | 13 |
| Schwarber | 2015-06-16 | 2026-09-27 | 25,803 | 11 |
| Harper | 2015-04-06 | 2026-09-27 | 27,237 | 13 |
| Bohm | 2020-08-13 | 2026-09-27 | 13,126 | 7 |
| Hill | 2020-09-04 | 2026-09-24 | 3,120 | 4 |
| De La Cruz | 2021-04-11 | 2026-09-26 | 7,649 | 7 |
| Stott | 2022-04-08 | 2026-09-27 | 11,834 | 5 |
| Sosa | 2018-09-23 | 2026-09-27 | 5,897 | 7 |
| Realmuto | 2015-04-15 | 2026-09-27 | 23,170 | 13 |

**Known coverage gaps (WARN, disclosed):**
- **DQ-12:** Sale's 2025 after 5/23 exists only against the Phillies. His profile is therefore 2026 only. The 2025 row in `sale_yoy.csv` is labelled PARTIAL.
- **DQ-13:** De La Cruz's non-Phillies MLB 2025 after 4/16 is outside the repo. His 2025 vs-LHP row (13 PA) is thin for that reason.

**Frame size:** 378,334 raw rows → 360,327 after precedence dedup (all game types; rates filter to `R`).

## 4 · Carry-ins (`domain-steward-proxy`)

| Fact | Source | Used for |
|---|---|---|
| Batting order 1–9 | Client prompt ("safe to assume") | Card order, notecard |
| NLWCS G1, PHI @ ATL, Truist Park, 2026-09-29, 2:00 p.m. ET, NBC | worldbaseball.com; MLB.com game page | Headers |
| Sale is the G1 starter | Client notebook cell 140; Battery Power preview | Scope |
| Harper: "the best left-handed pitcher in baseball" | Client notebook cell 151 | Quoted as the client's carry-in; not repeated as fact |
| Hill "cleared the bases off Sale" on 9/11 | Client notebook cell 43 | **Not used as a computed claim.** The card says what the log shows (104.3-mph double on a four-seam, 2nd inning) |

## 5 · Glossary deltas (`business-glossary-agent`)

| Term | Definition | Why it needed one |
|---|---|---|
| **THIN** | Under 10 PA. The line is printed and marked directional only | House convention (`uc-pos-001`), now in the glossary |
| **Sale rank (LR-1)** | Rank of Sale by OPS (1 = lowest) among LHP the hitter has faced ≥ 20 PA, regular season 2015–2026 | The client's Harper cut, generalised. Population size is always printed |
| **Inner / Middle / Away third (HL-1)** | `plate_x` relative to the batter, split at ±0.28 ft (thirds of the house ±0.83 ft plate) | Tests "pulls on pitches away" |
| **xwOBA (XW-1)** vs **xwOBAcon** | XW-1 is per PA: expected on BIP, actual on everything else. `xwobacon` (dp_uc48) is BIP only | The house had only the contact version; the cards compare wOBA and xwOBA per PA |
| **House wOBA** | FanGraphs season weights over house PA (`get_stats`). Reached-on-error = 0 | MV-1: differs from Savant's `woba_value` |
| **Pitch group** | Fastball = FF/SI/FC · Breaking = SL/ST/CU/KC/SV · Offspeed = CH/FS | A proxy for Sale's four pitches, labelled as one |
