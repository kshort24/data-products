# 05 · Quality & Certification: `uc-pps-035`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed; `out/dp_uc51_dq_scorecard.csv`) — **26 PASS / 4 WARN / 0 FAIL**

| Rule | Dimension | Rule (grain) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate pitch key in CF-2b (pitch) | PASS | 0 |
| DQ-02 | consistency | entity lock: every row pitcher == 554430 (pitch) | PASS | [554430] |
| DQ-03 | validity | regular season only in the rate frame (pitch) | PASS | R |
| DQ-04 | timeliness | Phillies log current through the pinned anchor, Game 162 (file) | PASS | 2026-09-27 |
| DQ-05 | validity | p_throws == R (pitch) | PASS | R |
| DQ-06 | validity | MI-1: both clubs MLB on every row (game) | PASS | 148 AAA rows excluded (3 games) |
| DQ-07 | consistency | 28 appearances == carry-in 28 GS (season) | PASS | 28 |
| DQ-08 | timeliness | 2026 window 4/25 .. 9/27 (season) | PASS | 2026-04-25 .. 2026-09-27 |
| DQ-09 | consistency | Phillies-era rows all from the house log (pitch) | PASS | PHI 17,973 |
| DQ-10 | completeness | EN-1: woba_denom on ≥99% of PA-ending rows, each season (pitch) | PASS | 0.993–1.000 |
| DQ-11 | consistency | client frame − its postseason rows == CF-2b, every season (pitch) | PASS | 19,038 − 1,065 = 17,973 |
| DQ-12 | validity | OU-1: no inning credits > 3 outs (game-inning) | PASS | — |
| DQ-13 | consistency | every 2026 appearance is a start (game) | PASS | 28 |
| DQ-14 | validity | RHP arm-side FF pfx_x < 0, catcher view (pitch) | PASS | −0.945 ft |
| DQ-15 | consistency | uc-pps-020 first-half figures reproduced (season) | PASS | 6/6 |
| DQ-16 | consistency | strikeouts == carry-in 193 (season) | PASS | 193 |
| DQ-17 | consistency | walks + IBB == carry-in 47 (season) | PASS | 47 + 0 |
| DQ-18 | consistency | OU-2 outs == carry-in 162.0 IP; OU-1 beside it (season) | PASS | OU-2 486 · OU-1 480 |
| DQ-19 | consistency | Game 162 == 6 IP, 1 run (game) | PASS | 6.0 IP, 1 R |
| DQ-20 | consistency | WC G3 == 4 IP, 2 R, Albies HR in the 4th (game) | PASS | 4.0 IP, 2 R, Albies, 4th |
| DQ-21 | completeness | 2026 swings with a tracked intercept ≥ 90% (pitch) | PASS | 0.979 |
| DQ-22 | completeness | NULL zone share (pitch) | PASS | 0.0 |
| DQ-23 | completeness | FF arm_angle coverage 2026 (pitch) | **WARN** | 0.56 — arm angle not tested |
| DQ-24 | comparability | KP-1 / CX-1b / tied-up populations Phillies-only (**permanent**) | **WARN** | 198 / 41 / 45 |
| DQ-25 | validity | spring and exhibition rows excluded (pitch) | PASS | 0 (no spring outings; rehab) |
| DQ-26 | consistency | 5 modules + 6 IX-1 segments sha256-pinned (file) | PASS | 5 / 6 |
| DQ-27 | validity | postseason never enters a rate (pitch) | PASS | 1,065 pitches, 13 games |
| DQ-28 | consistency | MI-1 exposure in the client's zw frame (pitch) | **WARN** | 148 |
| DQ-29 | consistency | O-26 exposure in the client's nphl filter (pitch) | **WARN** | 283 |
| DQ-30 | consistency | SR-2: one six-start window reconciles to 8.51, and it is 7/27–8/24 (window) | PASS | 23 R / 73 outs |

## 2 · Brand and palette compliance

- **13 / 13 figures pass** the in-process brand checks (Arial, title, subtitle, axis titles on every visible axis, colours ⊂ house set): `out/dp_uc51_brand_compliance.csv`. The brand center MCP was not attached; the same rules ran locally.
- **PL-2 six-pitch palette** (FF `#D22D49`, FS `#3B6FD8`, SI `#C77800`, ST `#16945A`, FC `#6250D6`, CU `#D55181`, usage order) **passes all six dataviz checks** on light and on the dark surface, with one adjacent pair (SI/ST, protan ΔE 6.1) in the 6–8 floor band; every pitch mark carries its code as a direct label (the required secondary encoding). Two earlier orders failed (FF/FS red-green deutan ΔE 3.1; FC/ST violet-blue ΔE 3.0) and were rejected. Receipt: `out/dp_uc51_palette_validation.txt`.

## 3 · Verification harness: **204 / 204 PASS** (`dp_uc51_verification.py`, `out/dp_uc51_verification_log.csv`)

The harness imports no build kernel for computation. It re-reads the parquet with pyarrow and re-implements every KPI from its definition.

| Family | What it recomputes | Checks |
|---|---|---|
| A · lineage | 5 module hashes; the 6 IX-1 segments re-parsed and re-hashed independently; anchor; DQ 0 FAIL | 13 |
| B · frame | 2026 pitches/games/window; era frame size; 24-file id scan; MI-1 (148 rows, 3 games, all `R`); NM-1 (static); client frame = governed + 1,065 postseason | 10 |
| C · season rates | 7 seasons × 13 KPIs (PA, K, BB, wOBA, xwOBA, in-zone, chase, edge, HH, barrel, LD, whiff, FF velo) + tied-up 2025/26; tenure highs/lows; xwOBA = .263; K/BB carry-ins; the 2026-vs-baseline tests | 102 |
| D · outs and the slide | OU-2 = 486; the unique 8.51 window; slide BB 13.4% vs 5.9% (p = .004); K not different; finish; arm-side misses (p = .033); release point flat; Game 162; WC G3 | 9 |
| E · context and card | starter board #6 of 41, 6 of top 10, K-BB #6; tied-up #11 of 45 and #6 of 14; sinker 124/55/14; platoon; card bars recomputed from quantiles; 20 on / 8 off; finish 6/6; uc-pps-020 reproduction | 10 |
| F · published numbers | 26 report strings and 12 dashboard strings, each formatted from a harness value; 13 figures shipped; banned superlatives; 18 HP rows | 45 |
| G · carry-in discipline | 7 carry-ins present in the manifest; ERA only as carry-in; 6 causal-injury phrases absent; every glove sentence tagged or negated | 15 |

## 4 · What the build and the harness caught

| # | Caught | By | Fix |
|---|---|---|---|
| 1 | OU-1 found 480 outs against the published 162.0 IP | DQ-18 FAIL on the first run | OU-2 from the outs sequence; 486 exactly; GS-1b; E-3 upstream |
| 2 | "The stretch" defined as the first six post-break starts gave 5.60 runs per 27 outs, not the reported 8.51 | EDA against the carry-in | SR-2 reconciliation; DQ-30 asserts uniqueness |
| 3 | CF-2 would have counted 148 AAA rehab pitches as 2026 MLB pitches | id-scan profile | CF-2b MLB filter (MI-1); DQ-06 |
| 4 | CF-2 labels every subject "Luzardo, Jesús" | first build run | CF-2b stamps the subject name (NM-1) |
| 5 | Sinker tied-up count included a foul bunt (125 vs 124) and called type-S pitches "fouls" | harness E | build uses JR-1's swing list; "not in play" label; HP-10 rewritten |
| 6 | Report sentence "relieved Aaron Nola" (Mayza pitched between them) | prose review against the WC log | "entered in the 3rd after Nola's early exit" |
| 7 | `SWN.first` resolved to the DataFrame method, not the column | first build run | bracket access |
| 8 | Notecard x-axis parsed "MM-DD" strings as dates (2005–2009) | render QA | category axis |
| 9 | Dashboard: plotly titles duplicated the HTML headings; phone nav links overlapped; a 25 px horizontal scroll at 390 px (unbreakable file names in the product cards) | headless render (1280 light/dark, 390 phone) | strip plot titles in the page; `flex:0 0 auto` on nav links; `overflow-wrap:anywhere` on cards |
| 10 | Two palette orders failed CVD checks | validator | PL-2 order |

## 5 · Certification

**READY-CONDITIONAL** (conditions C1–C6 in `00` §8). Lineage complete (`03` §3), glossary entries recorded (`03` §1), KPI specs precede code (`03` §2), DQ 0 FAIL, harness 204/204, brand 13/13, privacy CLEAR, anchor pinned. The four WARNs are designed and disclosed.
