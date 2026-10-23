# BID: Edmundo Sosa 2026 season recap, "We Really Do Love Sosa"

**Status:** FILED 2026-10-23 14:04 ET · **AWARDED 2026-10-23 14:04 ET (Tier A)**. The RFP says to treat this bid as the winner, so the build continues in the same turn. Actuals are reconciled in `07_platform_marketing.md` §3.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-23 (T0 wall clock 13:52 → 14:04 ET)
**ID reservation:** UC **#56** · contract `uc-pos-021` · build artifact `dp_uc56` · control-plane folder `uc-pos-021-sosa-2026-recap-001`
**Collision check (bid time):** no `dp_uc56*` in the MLB root, `out/`, `eda/` or the control plane; `uc-pos-021` appears only as "pos next" in the UC55 ledger patch and `07`.

**Prior Sosa work (inherited, not redone):** `uc-pos-003` (Sosa vs power RHP, 2-out RISP composite) is a Layer-1 **NO-GO** intake, blocked on four DPO decisions. Its open item "career scope: Cardinals years vs Phillies-only" is a data-fitness question this bid settles (below). Nothing else was built.

**Working title:** "We Really Do Love Sosa", the client's own first line. The DPO can rename it.
**Third pos-side season recap.** It inherits the K55 recap shape (C-7) and, like UC53 Alvarado, is written as a possible **end-of-tenure** recap: Sosa is a free agent and 2026 may close a five-season run, not just a season.

---

## Audit counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Session start (this turn) | 15,000,000 | — | 0 |
| C1 | Two-repo recon: README, CLAUDE.md ×2, UC55 BID/00/04/07/ledger, K54/K55 surfaces, K46 Rule-1 hit, uc-pos-003 | 14,815,359 | 184.6k | 184.6k |
| C2 | ENV-3 (4th occurrence) render stack, selftest 3/3, data profile, 8 web carry-in reads | 14,758,629 | 56.7k | 241.4k |
| C3 | BID filed | read in `07` | | |

## The ask (as submitted)
A notebook export (`acd30523-attachment.txt`, "Edmundo Sosa") with a thesis line ("We really do Love Sosa"), five asks, client code (season KPI panel; Phillies-RHB swing-rate × wOBA scatter) and one note ("I would need to rely on Claude going out to the web to determine this contractual value stuff"). RFP instructions:
- (a) Work **inside the MLB repository (data plane)**; the control plane supplies the org.
- (b) Governed, documented output with **00–07 receipts in a `data-products/` subfolder**, inspired by the scouting-report skill and similar MLB outputs; data-plane coding standards apply.
- (c) **All output and governance in the control-plane subfolder** (code, `out/`, EDA, report, dashboard). The data plane is read, not written. This differs from UC55 (code at MLB root) and matches UC53/UC54.
- (d) Token and time estimate framed as a competitive bid; treat it as the winner.

### Client questions → report sections
| Q | Client ask | § | Primary figure |
|---|---|---|---|
| Q1 | Top-line: "should be below his results from prior years with the Phillies"; "several lines showing cumulative wOBA or OPS and highlighting 2026 as a down year" | §2 | F1 cumulative wOBA/OPS, 2026 red over 2022–25 · F2 season card |
| Q2 | "Can we see an uptick in performance throughout the year?" | §3 | F3 2026 form: rolling wOBA/xwOBA, ER-1 segments, All-Star-break TR-1 |
| Q3 | Batted-ball indicators of sustained performance (Barrel, HH, muEV, EV50, EV90, maxEV, Pull AIR%) | §4 | F4 over-the-hump panel (adds bat speed 2024–26) |
| Q4 | High-chase / high-contact approach: chase, contact, OOZ contact, OOZ BA — "are those sustainable?" | §5 | F5 OZ-1 (OOZ BA vs xBA) + chase × OOZ contact among Phillies RHB |
| Q5 | Pitch types: "fallen off against velocity", "previously strong against breaking balls but not so much now" | §6 | F6 pitch group × season |
| Q6 | The client's scatter: wOBA as a function of swing rate, Phillies RHB since 2022 | §5 | F7 rebuilt (house pool, Sosa seasons connected) |
| Q7 | "Over-the-hump, or still value as a utility infielder off the bench?" + five-season tenure | §7 | F8 tenure and versatility (games by position, Phillies career line) |
| Q8 | "Define a walkaway number for his contract" (web carry-ins) | §8 | F9 walkaway ladder (comps + salary history + WA-1 band) |

### Client claims to be graded (HP rows, client's frame first)
The client frame is `pd.concat([nphl[nphl.player_name == pn], pos[pos.player_name == pn]])` with no `game_type` filter. Reproduced with the client's functions (K44 + `barrel_rate.py` + `inds` by IX-1) before any governed restatement.

| HP | Claim |
|---|---|
| HP-01 | 2026 top-line "should be below his results from prior years with the Phillies" |
| HP-02 | "2026 as a down year overall" on cumulative wOBA/OPS |
| HP-03 | "An uptick in performance throughout the year" |
| HP-04 | "A high-chase and high-contact guy" |
| HP-05 | OOZ contact and OOZ BA — "are those sustainable?" |
| HP-06 | "Has he fallen off against velocity" |
| HP-07 | "Previously strong against breaking balls but not so much now" |
| HP-08 | "Edmundo swung the bat and had high wOBAs among Phillies RHB" |
| HP-09 | "The Phillies put a premium on right handed hitters who swing the bat" |
| HP-10 | "Reliable bench player going back to 2022 … a true positive force" |
| HP-11 | "The Phillies should not pay him like an everyday player" |

## Why this shop wins this RFP
### 1. We inherit instead of re-deriving.
- **Spine K55** (`dp_uc55_kernel.py`, sha `9bdcce59…`, MLB root) → K54 → K40/K53 chain and K40a: 14 pins re-assert at import. It brings slash/wOBA/xwOBA, chase/whiff/swing/HH/barrel fixes, CR-1, XW-1, RF-2/RF-2x, KP-1, PA-1, `two_prop_z`, CM-1 cumulative frames, **CC-1 chase cost** and **`ooz_whiff_rate`** (K54), BP-1 bat speed (K40), and **ER-1** form eras (K55).
- **TR-1** (`tr1_ledger`, K54) answers "uptick" at a calendar date chosen before looking.
- **K46** (`dp_uc46_kernel.py`, sha `a45ac9a7…`, uc-pos-017, CONDITIONALLY CERTIFIED): `pull_air_rate` and `build_bip` — the client's commented-out `pull_air_rate` is the patched v1.1.0 function (O-7 closed there), so we use it, not the notebook cell.
- **EV90** has a house precedent (UC27 `ev90`, 0.90 quantile of BIP `launch_speed`); we reuse the definition.

### 2. We checked the premise before bidding (carry-ins are sourced and never computed on).
- **CI-1** 2026 line: .247/.283/.429, 9 HR, 250 PA, 84 G, 89 OPS+, 1.0 bWAR (Baseball-Reference). **Reconciles to the log at bid time:** 250 regular-season PA, .247/.283/.429.
  - NBC Sports Philadelphia (2026-10-02) printed .242/.280/.410 and 8 HR — pre-finale. We quote B-Ref and the log.
- **CI-2** NBC (2026-10-02): final 50 games .275/.313/.493, .806 OPS in 149 PA; .923 OPS with RISP (89th pct of 298); top 16% OAA and sprint speed; **2026 salary $4.4M**; free agent; CBA expires after 2026.
- **CI-3** Salary history (Spotrac; Wikipedia; MLB.com 2026-01-08): 2022 $715.6k · 2023 $950k · 2024 $1.7M · 2025 $3.0M · 2026 $4.4M (arbitration each year).
- **CI-4** bWAR by season (B-Ref): 2021 STL 3.2 · 2022 1.4 (PHI 0.8 in 59 PA) · 2023 0.6 · 2024 2.2 · 2025 2.3 · 2026 1.0. Positions 2026: LF 32 G, 3B 21, SS 18, 2B 14.
- **CI-5** Utility comps, 2025–26 offseason: Rosario 1/$2.5M (NYY), Rojas 1/$5.5M (LAD), Kiner-Falefa 1/$6.0M (BOS), Willi Castro 2/$12.8M (COL; value from the ESPN report headline).
- **CI-6** Born 1996-03-06 (Wikipedia): 2027 is his age-31 season. Acquired 2022-07-30 for JoJo Romero. Left groin injury, 2026-09-30, WC Game 2 (NBC).
- **CI-7** PhillyVoice (2026-10-09): Phillies career .260/.302/.444 over five seasons, 392 G; positive offensive WAR every Phillies season.

### 3. We pre-register the argument.
The client already believes 2026 was a down year and suspects an uptick late. Late-season splits picked after seeing the .806 OPS stretch are outcome-selected. So:
- **ER-1** (inherited, unchanged parameters: ≥100 PA segments, 500 permutations, α 0.10, seed 55) finds 2026 change points without our input.
- **TR-1** is run at one date fixed now: the first 2026 game after the All-Star break, derived from the house schedule gap (≥3 days), never hand-keyed.
- The "final 50 games" carry-in is quoted as the client's media frame, never tested as if it were pre-registered.

### 4. We found the traps before the build.
- **SRC-4 (repeat):** the client frame carries **19 spring + 7 Wild Card PA in 2026**, plus 2022–25 postseason PA. Every HP row reports both frames.
- **SRC-5 (new): the client frame is two teams.** `nphl` holds `opponents/edmundo.parquet` (STL 2018–22, 1,688 pitches, no bat-tracking columns, no 2026 rows). The client's "prior years" means Phillies years. Governed comparisons are **PHI 2022–26**; STL 2021–22 rows appear once, labelled, as career context. This answers uc-pos-003's open "career scope" item for this product only.
- **SRC-6 (new): 2022 PHI is 59 PA.** It is shown and labelled, never used as a baseline. The baseline for "prior Phillies years" is **2023–25** (836 PA).
- **GL-1 (new, glossary): EV50 is ambiguous.** The client's comment defines EV50 as the median exit velocity; Statcast's public "EV50" is the mean of a hitter's hardest 50% of batted balls. We use the client's definition (glossary agent may not infer) and disclose the difference.
- **ENV-3, fourth occurrence:** `/sessions` 100% full. Render stack to `/tmp/pyrender`, `TMPDIR=/tmp/uc56/tmp`. `phillies_dp.selftest` 3/3.

### 5. We build where the RFP says.
Code (`dp_uc56_*.py`), `out/dp_uc56_*`, EDA (`eda/dp_uc56/`, via `phillies_dp.eda.to_file(root=…)`), report, dashboard and the 00–07 trail all live in this control-plane folder. The data plane (`data/`, `phillies_dp`, K55, `barrel_rate.py`, `Baseball Functions.ipynb`) is read, never written.

## Data position (verified at bid time)
| Check | Result |
|---|---|
| House log | `phils_2015..2026.parquet`, max `game_date` **2026-10-01** (pinned anchor, same as UC54/UC55) |
| Entity lock | MLBAM **624641**, bats R, `phillies_role == 'batting'`; 0 duplicate pitch keys; one name |
| Regular-season PA (PHI) | 2022 59 · 2023 300 · 2024 275 · 2025 261 · **2026 250** |
| 2026 monthly PA | Mar 7 · Apr 37 · May 53 · Jun 48 · Jul 43 · Aug 29 · Sep 33 |
| 2026 PA by hand | vs LHP 138 · vs RHP 112 (platoon-heavy bench usage) |
| 2026 pitches by group | fastball 464 · breaking 288 · offspeed 146 |
| Out-of-zone pitches seen | 2023 561 · 2024 558 · 2025 492 · 2026 487 |
| STL context (other file) | 2021 324 PA (.271/.342/.389) · 2022 131 PA |
| Phillies RHB seasons ≥50 PA, 2022–26 | 43 (the client's scatter population) |

## Pre-registered (set 2026-10-23 14:04 ET, before any split or flag is computed)
### TR-1 at the 2026 All-Star break (inherited rule and bars, K54)
Pre = 2026 regular season before the first post-break game; Post = from it. K54 `TR_SIGNATURES` and `TR_RULE` unchanged (results + process families → EARNED / RESULTS / PROCESS / NO TURN).

### OZ-1 out-of-zone damage (new, provisional)
- **Population:** PAs that end on a pitch with `zone` 11–14 and a `pitch_type` (AB-1).
- **OZ-BA** = hits / at-bats on those PAs (the client's `ba_ooz`). **OZ-xBA** = mean `estimated_ba_using_speedangle` over the same at-bats (BIP expectation; strikeouts 0; BIP without an estimate fall back to the actual outcome, XW-1 style).
- **OZ contact** = 1 − `ooz_whiff_rate` (K54). **CC-1** chase cost per 100 chases (K54), vs the house.
- **Call per season:** `RAN HOT` if OZ-BA − OZ-xBA ≥ +.030; `RAN COLD` if ≤ −.030; else `EARNED`. "Sustainable" requires `EARNED` (or `RAN COLD`) **and** OZ contact at or above the Phillies-RHB 2022–26 median.

### WA-1 walkaway number (new, provisional; carry-in arithmetic, not a valuation model)
- **Band (carry-ins only):** floor = his 2026 salary ($4.4M); ceiling = the top AAV among CI-5 utility comps ($6.4M).
- **Decline flags (DF):** 2026 vs his 2023–25 PHI mean, each flagged if worse by more than the bar: bat speed (2024–25 mean) 1.0 mph · EV90 1.0 mph · hard-hit .040 · barrel/BIP .020 · xwOBA .020 · OZ contact .030.
- **Rule:** walkaway AAV = band ceiling, rounded down to $0.5M. Term ≤ **2 years** if DF ≤ 2; **1 year (+ club option)** if DF ≥ 3. Any offer above the walkaway (AAV or term) is "everyday money" → let him go.
- Not financial advice; a framework for the DPO, sourced at every number.

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤8 pp, 8 sections) | All eight questions, HP grades, walkaway | **Build (hero)** |
| P2 | Interactive dashboard (≤7 chapters) + Artifact | Cumulative lines, form timeline, scatter with hover | **Build** |
| P3 | One-page "front-office card" (walkaway) | WA-1 | **Folded into report §8 and dashboard ch. 7** |
| P4 | Projection / aging curve | | **Not bid** (no house projection model) |

## Scope tiers (comparison-profile cap: report ≤8 pp · dashboard ≤7 chapters · ≤9 figures · ≤2 new KPIs)
### Tier A: Comparison profile (recommended, AWARDED)
Report: 1 Bottom line · 2 The 2026 line (Q1) · 3 Was there an uptick? (Q2) · 4 Batted ball: over the hump? (Q3) · 5 The approach: chase, contact, swing (Q4, Q6) · 6 Velocity and breaking balls (Q5) · 7 Five seasons in red pinstripes (Q7) · 8 The walkaway number + notebook graded + caveats (Q8).
Figures F1–F9 as mapped above. New KPIs (2): **OZ-1**, **WA-1**.
### Tier B: Tier A + extras (≈ +70k, +6 min)
Adds a defensive chapter (house fielding-opportunity proxy by position) and an RISP page. Breaks comparability.
### Tier C: Lean (≈ −150k, −14 min)
PDF only, 6 figures (drops F2, F7, F8), no dashboard, no Artifact.

## Deliverables (Tier A), all in this folder
| # | Deliverable |
|---|---|
| 1 | `dp_uc56_sosa_2026_recap_report.pdf` (+ `.md`) |
| 2 | `dp_uc56_sosa_2026_dashboard.html` (+ `_artifact.html`) + Artifact |
| 3 | `dp_uc56_kernel.py`, `_sosa_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py` |
| 4 | `out/dp_uc56_*` (CSVs, figure JSON+PNG, `headlines.json`, DQ scorecard, verification log, HP grades) · `eda/dp_uc56/` |
| 5 | Receipts `00`–`07`, README, this BID, contract (`uc-pos-021-…md`), ledger patch |

**Explicitly not bid:** fielding metrics we don't have (OAA, DRS, arm; carry-ins only) · MLB-wide ranks (house population rule) · a contract valuation model or projection · any spring or postseason PA in a rate · causal claims about the groin injury.

## Price (Tier A)
**Basis:** UC55 Stott actuals (≈485k, 44 min) with C-7 (next pos recap cheaper), C-12 (harness 35k for multi-season). **Down:** no new segmentation or neighbour-scoring code (ER-1 inherited; no IO-1, no GS-1), smaller sample, fewer client questions. **Up:** T0 ran long (two-team source, uc-pos-003 read, 8 web reads for the walkaway); WA-1 is web-dependent; Artifact publish.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon, carry-ins, env, profile, Rule-1 (**sunk: 241.4k at C2**) + this BID | ~240k | ~12k | 12 |
| T1 Kernel + build + HP reproduction + EDA to file | 55k | 18k | 8 |
| T2 Figures (9) + brand + render QA | 45k | 15k | 7 |
| T3 Dashboard (7 chapters) + QA + Artifact | 32k | 12k | 6 |
| T4 Narrative + report + PDF | 10k | 8k | 3 |
| T5 Verification harness | 22k | 8k | 4 |
| T6 Governance 00–07, README, contract, ledger patch | 22k | 16k | 6 |
| D Defect discovery | 8k | 2k | 2 |
| Contingency 5% (unsunk) | 10k | 4k | 2 |
| **BID** | **~444k** | **~95k** | **~50 min** |

**Total ≈ 539k tokens, ≈ 50 minutes.**
- **Recap set for comparison:** 485k (UC55) / 576k (UC54) / 518k / 469k / 681k.
- **Credits at list** ($10/M in, $50/M out): ≈ **$9.19**, band $7.80–10.55 (±15%). Cowork bills subscription usage; read this as API-equivalent value.
- **Honest note:** this bid prices above UC55 despite a lighter product because T0 is sunk at 241k (vs 163k). Excluding T0, Tier A is priced at ≈286k vs UC55's ≈322k post-T0 actual (−11%).

### Competitive position
A rival agentic org without this repo would have to re-derive house wOBA and the CM-1 endpoint reconcile; discover that the client frame mixes two teams (SRC-5) and spring/postseason rows (SRC-4); rebuild a chase-cost and OOZ framework that K54 already certifies; and patch the notebook's `pull_air_rate` (which cannot execute: O-7) on its own. We estimate that bid at **~0.85–1.05M tokens and 65–80 min**, with no 00–07 trail, no harness and no way to grade the notebook on the client's own frame.
Our differentiators: pinned inheritance (numbers reconcile with UC55 and the K54 spine) · pre-registered uptick test (not a stretch chosen after seeing .806) · client claims graded, never overwritten · a walkaway rule whose inputs are sourced and whose data half is computed · bid-vs-actual history (UC48–UC55 within −28% to +5%).

## Assumptions, exclusions, carry-ins
- Regular season for every rate. Postseason in its own ledger line; spring excluded and reported (SRC-4).
- Entity locked by MLBAM 624641 + batting role; the name is used only to reproduce the client frame.
- Populations: house hitter pool = Phillies hitter-seasons 2015–26 ≥50 PA (K40/K54, KP-1); client scatter pool = Phillies RHB 2022–26 ≥50 PA; bat speed 2024–26 only.
- Carry-ins CI-1 to CI-7 are labelled at every use and never computed on (WA-1's band is arithmetic on carry-ins, disclosed as such).
