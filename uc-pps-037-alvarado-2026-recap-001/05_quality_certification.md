# 05 · Quality & Certification: `uc-pps-037`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed; `out/dp_uc53_dq_scorecard.csv`) — **11 PASS / 2 WARN / 0 FAIL**
| Rule | Dimension | Rule (grain) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate pitch key in the tenure frame (pitch) | PASS | 0 |
| DQ-02 | consistency | entity lock: every tenure row pitcher == 621237 (pitch) | PASS | 1 id |
| DQ-03 | validity | regular season only in the rate frames (pitch) | PASS | R |
| DQ-04 | timeliness | phils_2026 file current through the anchor; regular season ends before it (file) | PASS | file 2026-10-01, regular 2026-09-27 |
| DQ-05 | consistency | ENT-1: no pitching-role rows before 2021; raw 2018 rows exist under another name | PASS | raw 9, in frame 0 |
| DQ-06 | completeness | release_speed non-null on every thrown pitch (tenure) | PASS | 0 null |
| DQ-07 | validity | AB-1: every row without pitch_type is an automatic ball/strike | PASS | 16 rows, all 2026 |
| DQ-08 | validity | zone null on tenure rows (K44 D-7 counts them in-zone) | **WARN (designed)** | 16; thrown-pitch zone .414 |
| DQ-09 | consistency | tenure frame == house log pitch counts by year | PASS | 6/6 |
| DQ-10 | consistency | CM-1a endpoints == WB-1 by year | PASS | tol 1e-9 |
| DQ-11 | consistency | OD-1 bands partition appearances; appearances == games | PASS | 6/6 |
| DQ-12 | consistency | carry-in CI-7 (68 G, 70 K) reconciles to the log | PASS | 68 G, 70 K |
| DQ-13 | accuracy | CM-D1 exposure (PA ends, value > 0, denom 0) | **WARN (designed)** | 9 rows |

## 2 · Brand and palette compliance
- **10 / 10 figures pass** the in-process brand checks: `out/dp_uc53_brand_checks.csv`.
- Pitch palette (SI `#C77800`, FC `#6250D6`) validated light **and** dark with the dataviz validator: ALL PASS, CVD ΔE 31.3 (`out/dp_uc53_palette_validation.txt`).
- A gray categorical trial for OD-1 failed the chroma floor and was rejected; the bands use a sequential red ramp with direct count labels.
- Render QA, headless at 1280 light / 1280 dark / 390 phone: 10/10 plots drawn in each, 0 console errors, no horizontal overflow. The PDF was rasterized and inspected (10 pages).

## 3 · Verification harness: **163 / 163** (`dp_uc53_verification.py`, `out/dp_uc53_verification_log.csv`)
Definition-first: it imports no `dp_uc*` kernel or house module. It re-reads the parquet with its own projection and filters (`phillies_role`, `game_type`, its own dedup) and re-implements each KPI from `03` §2 and the K44/K48/K50 definitions.

| Family | What it recomputes | Checks |
|---|---|---|
| A · lineage | pins, anchor, DQ 0 FAIL, DB-1 registration note, 8 bars vs `03` spec | 13 |
| B · frame | pitches by year, ENT-1, spring, dedup, dates, AB-1, 15 season rates, 12 velocities | 35 |
| C · context | leaderboard rank/n/PA, RP-1t relievers above, games rank, putaway rank (all + 300+), whiff ranks + n, RP population | 9 |
| D/E · story | OD-1 bands + damage ×6 seasons, monthly velocity/xwOBA/BB%, CM-1a endpoints ×6, share above prior, floor claim, DB-1 values/verdicts ×8, roll-up, sensitivity | 38 |
| F · published numbers | 27 strings formatted from harness values, checked in report and dashboard; banned phrases; 10 HP rows | 59 |
| G · carry-in discipline | 6 sources labelled in both forms; ERA only as carry-in; no causal injury language; $9M only beside its source | 9 |

## 4 · What the build and the harness caught
| # | Caught | By | Fix | Intake could have caught |
|---|---|---|---|---|
| 1 | ENT-1: 2018 rows with his id under a batter's name | T0 profile | pitching role; DQ-05 | Y (caught) |
| 2 | SRC-1: client frame mixes 53 spring + 335 postseason pitches | T0 profile | HP on client frame, restated | Y (caught) |
| 3 | DEF-1: whiff `hline` hard-coded at 0.39 | T0 read | computed (.391); the typed value happened to be right | Y (caught) |
| 4 | ENV-3: pip ENOSPC from TMPDIR | T0 env | `TMPDIR=/tmp` | Y (caught) |
| 5 | CM-D1: house cumulative wOBA counts IBB/sac-bunt `woba_value` | T1 reconciliation | CM-1a spec + reconcile assert; E-2 | N |
| 6 | HP-06 note "best in the house at his volume" was false (a combo with 3,149 two-strike pitches ranks above) | T1 (computing the note instead of typing it) | rank among 300+ (#9 of 58) | N |
| 7 | HP-02/04/05 notes overstated gaps (~1,400 OOZ is right) | T1 | notes computed | N |
| 8 | Prose: "bridge-to-Duran role he held in 2022–24" is wrong (Duran arrived 2025); "contact best of his tenure" overreached | T3 fact-check | rewritten; "bridge-to-Duran" is a banned phrase in harness F | N |
| 9 | Render: log-axis tick clutter, subplot titles colliding with subtitles, clipped labels, F10 labels clipped on the dashboard | render QA | tickvals, margins, ranges, short labels, `automargin` | N |
| 10 | F9 title claim ("for most of the year") asserted only the endpoint | T2 review | assert share > 50% (75%) | N |
| 11 | DQ-04 as first written compared the regular-season max (09-27) with the file anchor (10-01) | DQ run | rule restated at file level | N |
| 12 | **AB-1:** 16 automatic balls/strikes with no pitch in 2026 | DQ-06/07 | rule + thrown-pitch zone rate; E-3 | N |
| 13 | **RK-2:** K−BB from rounded rates published 15.6% (true 15.7%) | harness F | from counts; E-4 | N |
| 14 | Whiff population count included a zero-whiff group with no rate (898 vs 897) | harness C | excluded and disclosed (D-1) | N |
| 15 | Harness-side: putaway rank compared against a rounded value; cumulative used the wrong PA rule | harness self-review | harness fixed (build rank #39 unchanged) | — |

## 5 · Certification
**READY-CONDITIONAL** (conditions C1–C6 in `00` §8). Lineage complete, glossary recorded, KPI specs precede code (DB-1 registered before 2026 rates), DQ 0 FAIL, harness 163/163, brand 10/10, privacy CLEAR, anchor pinned. The two WARNs are designed and disclosed.
