# BID: Trea Turner 2026 season recap, "Sounding the Alarm"

**Status:** FILED 2026-10-23 20:49 ET · **AWARDED by RFP rule (treat as winner)** · **DELIVERED 2026-10-23 21:27 ET in a new chat (Tier A); actuals in `07` §5.** Original hold note follows. The client asked for a hard stop at this BID so he can choose between continuing in this chat and opening a new one. Nothing past T0 has run. Actuals will be reconciled in `07_platform_marketing.md` §3 once the build runs.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-23 (T0 wall clock 20:40 → 20:49 ET)
**ID reservation:** UC **#57** · contract `uc-pos-022` · build artifact `dp_uc57` · control-plane folder `uc-pos-022-turner-2026-recap-001`
**Collision check (bid time):** no `dp_uc57*` in the MLB root, `out/` or the control plane. `uc-pos-022` and `dp_uc57` appear only as "next available" in the UC56 ledger patch and UC56 `07`. The repo ledger's own "Next available" line (UC52) is stale; the UC52–UC56 patches are still pending paste.

**Prior Turner work (inherited, not redone):** this is the **fourth Turner product of 2026** and the one that closes the season.
| UC | Contract | Delivered | What it settled | What this bid takes from it |
|---|---|---|---|---|
| UC25 | `uc-pos-006` (`dp_uc24`) | 2026-07-21 | First below-average season; shape (pulled air .117) and swing decisions; July "real-but-young" uptick | The client's "Midseason Review" bullets are this product's findings |
| UC40 / UC40a | `uc-pos-014` (`dp_uc40`, `dp_uc40a` v1.1.0) | 2026-09-03 | Uptick resolved against him; popup rate 15.2% (z 4.12); **bat-path addendum**: tilt 27.9° → 25.5°, flattest of 11 Phillies, contact 1.35″ further from the body, breaking-ball popups 3.9% → 12.1% | **K40a** (sha `807986c0…`) bat-path conventions C1–C8, BP-0/BP-1/BP-2, PU-1/PU-2, PB-1; O-15 |
| UC42 | `uc-pos-016` (`dp_uc42a` v1.1.0) | 2026-09-10 | "Pulling OOZ too often" not supported; real shift is in-zone (pull 47.5% → 40.1%) | In-zone directional frame; PM-1 attack-stability control |

**Working title:** "Sounding the Alarm", from the client's first line ("sounding major alarm bells to me"). The DPO can rename it.
**Fourth pos-side season recap** (after UC54 Crawford, UC55 Stott, UC56 Sosa). It inherits the K55 recap shape (C-7). It is also the first recap whose subject has a **completed in-season bat-path product**, so the swing-path chapter is a full-season close-out of UC40a rather than a first look.

---

## Audit counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Turn start (this RFP) | 15,000,000 | — | 0 |
| C1 | Two-repo recon: control-plane CLAUDE.md, ledger tail + 20 patches, UC56 BID/00/01, UC25/UC40/UC40a/UC42 READMEs, 03a conventions, K55 surface, scouting-report skill, prior-chat bat-tracking CDE read | 14,944,295 | 55.7k | 55.7k |
| C2 | Lineage 14/14, data profile, EDA to file, 2 web searches + 2 reads, log reconcile | 14,917,245 | 27.1k | 82.8k |
| C3 | BID, `00`, `01` written and copied | 14,899,460 | 17.8k | **100.5k** |

**Counter caveat (read before comparing to UC56).** This RFP ran in a chat that already held an unrelated build (the Single-Swing Pilot). The counter above moved 100.5k for T0, against UC56's 241.4k and UC55's 250.3k. Part of that gap is real: Turner has three prior products whose READMEs answered most recon questions. Part is instrument: the counter does not show the cost of re-sending this chat's long history on every call. Price the build on the phase table below, not on the T0 line.

## The ask (as submitted)
A notebook export (`9c281fb3-attachment.txt`, "Trea Turner") rated **7** ("An atrocious year … sounding major alarm bells"). It restates the midseason review, adds new findings by pitcher hand and pitch group, and asks the machines to take over the swing-path visualization and data exploration, "build[ing] off the previous data products as well as the conversation I started last night." It includes the client's KPI panel code (`nresults` + `whiff_rate` + `chase_rate` + `hard_hit_rate` + `barrel_rate` + in-zone/out-of-zone splits + `bb_type_by_level` popups, by `game_year × stand × p_throws × pitch_group`, plus a `velo_segment` cut at 94.9 mph) and the pilot-export cell.

RFP instructions:
- (a) Work **inside the MLB repository (data plane)**; the control plane supplies the org.
- (b) Governed, documented output with **00–07 receipts in a `data-products/` subfolder**, inspired by the scouting-report skill and similar MLB outputs; data-plane coding standards apply.
- (c) **Code and outputs at the MLB root** (`dp_uc57_*`, `out/dp_uc57_*`, `eda/dp_uc57/`), the receipts in the control-plane folder. This matches UC55, not UC56 (whose RFP put everything in the control plane).
- (d) Token and time estimate framed as a competitive bid; treat it as the winner.
- (e) **Hard stop at the BID** (this turn only).

### Client questions → report sections
| Q | Client ask | § | Primary figure |
|---|---|---|---|
| Q1 | "An atrocious year … sounding major alarm bells" | §2 | F1 cumulative wOBA by PA, 2026 red over 2023–25 PHI, with the 2016–22 career band · F2 season card |
| Q2 | "Does that start with pitch recognition? Making contact with those types of pitches (breaking balls) when they are in the zone versus out of the zone?" | §3 | F3 decision map: in-zone and out-of-zone swing and contact, hand × pitch group, 2023–25 → 2026 |
| Q3 | vs RHP: "expanding the zone … really cannot make contact when he expands the zone on righty breaking balls" | §3 | F4 RHP breaking balls: chase location and OOZ contact |
| Q4 | vs LHP: "could take offspeed pitches when he connected but he whiffed more and popped them up too much" | §4 | F5 LHP offspeed: whiff, contact quality, popups (n printed) |
| Q5 | Fastballs both hands: "chase a touch less and do more damage in the zone"; "more popups" | §5 | F6 fastball damage in-zone vs chase, by hand |
| Q6 | "My man needs to do damage on slow lefty fastballs" (velo segment, < 95 vs ≥ 95) | §5 | F7 LHP fastballs by velo segment: xwOBA on contact, popup share |
| Q7 | "Flat bat path through contact, especially against breaking balls lead to an increase in pop-ups"; "If he can resolve the path of his barrel through the zone" | §6 | F8 swing-path panel: tilt × attack angle by pitch group, 2025 vs 2026, peer-netted · F9 contact-point map (lateral × depth) for breaking-ball popups vs hard contact |
| Q8 | "Move off of shortstop … second base or the outfield. Perhaps playing a different position improves his offense" ("don't want to worry about defense too much") | §7 | No figure. A sourced carry-in box (CI-2) and an HP grade |

### Client claims to be graded (HP rows, client's frame first)
The client frame is `pd.concat([nphl[nphl.player_name == pn], pos[pos.player_name == pn]])` with no `game_type` filter, and every table filters `game_year > 2022`. It is reproduced with the client's functions (by IX-1 extraction from `Baseball Functions.ipynb`) before any governed restatement.

| HP | Claim | Source |
|---|---|---|
| HP-01 | "An atrocious year" | notebook |
| HP-02 | "Weakness against offspeed likely drove underperformance against Lefties" | midseason review (UC25) |
| HP-03 | "In-Zone Swing was down and chase was up" | midseason review |
| HP-04 | "Almost no pulls or pull-AIRs" | midseason review |
| HP-05 | "Flat bat path through contact, especially against breaking balls lead to an increase in pop-ups" | midseason review (UC40a) |
| HP-06 | vs RHP: "expanding the zone … really cannot make contact when he expands the zone on righty breaking balls" | notebook |
| HP-07 | vs LHP: "could take offspeed pitches when he connected but he whiffed more and popped them up too much" | notebook |
| HP-08 | FB vs RHP: "could stand to chase a touch less and do more damage in the zone" | notebook |
| HP-09 | FB vs LHP: "more popups … needs to swing at fastballs in the zone and chase less" | notebook |
| HP-10 | "Needs to do damage on slow lefty fastballs" | notebook |
| HP-11 | "If he can resolve the path of his barrel through the zone, I think he can get back to doing damage" | midseason review |
| HP-12 | "Perhaps playing a different position improves his offense" | notebook. **Pre-graded NOT TESTABLE**: he played shortstop all season, so the log holds no position-change contrast for him. The grade says so; we do not build a proxy |

## Why this shop wins this RFP
### 1. We inherit instead of re-deriving.
- **Spine K55** (`dp_uc55_kernel.py`, sha `9bdcce59…`, MLB root) → K54 → K40/K53 chain and K40a. **14 lineage pins re-asserted at bid time: 14/14 PASS.** It brings slash/wOBA/xwOBA, chase/whiff/swing/HH/barrel fixes, CR-1, XW-1, RF-2, KP-1, PA-1, `two_prop_z`, CM-1 cumulative frames, CC-1 chase cost, `ooz_whiff_rate`, and `PITCH_GROUP`.
- **K40a** (sha `807986c0…`, UC40 folder) is the swing-path engine: BP-0 tracked-swing population, BP-1 path profile, BP-2 path by pitch group, PU-1/PU-2 popup signature and rate, PB-1 peer-netted deltas, and the 12 proven conventions. The client's "flat bat path" claim was UC40a's finding at 2026-09-02; we close it out on the full season with the same code.
- **UC42's in-zone directional frame** answers HP-04 without new geometry.
- **The client's KPI panel** is reproduced as written (IX-1, source-pinned), then restated on governed functions. Every HP row shows both.

### 2. We checked the premise before bidding (carry-ins are sourced and never computed on).
- **CI-1** 2026 line (FanGraphs): 157 G, 700 PA, 19 HR, .242/.297/.378, wOBA .298, wRC+ 83, 1.1 WAR. **Reconciles to the log at bid time:** 157 games, 700 regular-season PA, 645 AB, 156 H, 19 HR, .242/.297/.378.
- **CI-2** NBC Sports Philadelphia (2026-10-15): Dombrowski, "If he plays shortstop like he did in '25, he can play shortstop. But if he plays it like he did in '26, he can't." Second base or the outfield are named as the alternatives. 2026 OAA −10 (2025 +17), DRS −17 (worst among MLB shortstops), 21 errors (tied for the MLB lead), 507 outs (most in MLB), K% 21% (2025 16.7%), AVG/OBP .304/.378 in 2025. Contract: seven years and $190M remaining, full no-trade clause.
- Both carry-ins are quoted in §2 and §7. None enters a calculation.

### 3. We pre-register the argument.
The client already believes the year was atrocious, that recognition of breaking balls is the root, and that the flat path causes the popups. Each of those can be confirmed by choosing splits after looking. So these rules are fixed now, before any split is computed:
- **Baseline:** "prior Phillies years" = **2023–25 regular season** (1,874 PA). 2026 = 700 PA. Career context = 2016–22 from `opponents/turner.parquet`, labelled, never pooled into the baseline.
- **Change test:** inherited `two_prop_z` on every rate in Q2–Q6, 2026 vs 2023–25. **|z| ≥ 1.96 → CHANGED; 1.00–1.96 → LEANS; < 1.00 → SAME.** Every cell prints its n. Cells under 30 BIP or 50 pitches print "too few to call" instead of a grade.
- **Swing path (Q7):** bat-path fields exist only for **2025 and 2026** (1,177 and 1,290 tracked swings), so the comparison is 2025 vs 2026, peer-netted by PB-1 against the same Phillies cohort UC40a used. No 2023–24 swing-path baseline exists, and none will be implied.
- **Path → popup link (Q7, HP-05):** on breaking balls, mean tilt and attack angle are compared for popups vs all other BIP, by season. The claim is graded **SUPPORTED** only if 2026 popups sit at least 2° flatter in tilt than 2026 non-popup BIP **and** the 2026 popup rate on breaking balls passes the change test. Otherwise it is **PARTLY** (one leg) or **NOT SUPPORTED**.

### 4. We found the traps before the build.
- **SRC-4 (repeat): the client frame carries spring, exhibition and postseason rows.** In 2026 that is 153 spring + 15 exhibition + 46 Wild Card pitches; 2023 adds 208 postseason pitches, 2024 and 2025 add 78 and 72. Every HP row reports both frames.
- **SRC-5 (repeat): the client frame is two teams, and it uses a name filter.** `nphl` contributes `opponents/turner.parquet` (WSH/LAD 2015–22). The `game_year > 2022` filter keeps those rows out of the client's tables, so it does no harm there, but the governed build locks by **MLBAM 607208 + batting role**. The name resolves to that one id in the house log (checked).
- **VS-1 (new, glossary): the client's velo segment** puts `release_speed > 94.9` in "High Velo" and everything else, **nulls included (`fillna(0)`)**, in "Less than 95 mph". In 2026 there are 0 null-velo LHP fastballs, so the client and governed frames agree this year. The rule is still disclosed.
- **SM-1 (new): the slow-lefty-fastball question is small.** 2026 LHP fastballs: 476 pitches, **107 at ≥ 95 mph with 22 BIP**; 369 under 95. "Damage on slow lefty fastballs" can be graded. The ≥ 95 bucket prints "too few to call" on contact-quality rates.
- **O-15 (inherited): `attack_direction` is pull-negative and stand-normalised in this data plane**, the inverse of the published glossary. Any pull-side swing direction is `−attack_direction`.
- **PL-1 (new, cross-product): the Single-Swing Pilot** (`phillies_dp.swing_pilot`, built this afternoon in this chat) **does not apply O-15** and halts for want of intercept columns that the **house log already carries for that exact swing** (game_pk 824932, at-bat 18: intercept_y 23.46 in). Both are fixable, but they belong to the pilot, not to this recap. See Tier B.
- **WB-x (inherited from UC56 `00` §5): pooled-season wOBA uses 2026 constants for every season.** This build pools 2023–25 for the baseline, so it applies UC56's workaround (season-wise wOBA, then PA-weighted) and states it.
- **Popups are a small count.** 2026 breaking-ball popups: 15 of 125 BIP vs RHP, 5 of 47 vs LHP. Rates print their numerator.
- **ENV-3 (fifth occurrence):** device `/sessions` at 100%. The render stack runs from `/tmp/pyrender`.

### 5. We build where the RFP says.
Code (`dp_uc57_*.py`), `out/dp_uc57_*`, EDA (`eda/dp_uc57/`, via `phillies_dp.eda.to_file`), report, dashboard, contract and ledger patch at the **MLB root**. The 00–07 trail, this BID, README and copies of the report, dashboard, contract and ledger patch go in the control-plane folder. Inherited kernels are imported by pinned hash and never edited.

## Data position (verified at bid time)
| Check | Result |
|---|---|
| House log | `phils_2015..2026.parquet`. `phils_2026` was rewritten 2026-10-23 19:53 (sha `be5d313d…`), but the max `game_date` is unchanged at **2026-10-01** (Wild Card), with the regular season ending 09-27. The anchor is pinned at 2026-10-01, the same as UC54–UC56 |
| Entity lock | MLBAM **607208**, bats R, `phillies_role == 'batting'`; 0 duplicate pitch keys; one name (`Turner, Trea`) |
| Regular-season PA (PHI) | 2023 692 · 2024 541 · 2025 641 · **2026 700** |
| 2026 PA by hand | vs RHP 465 · vs LHP 235 |
| 2026 pitches, hand × group | RHP: fastball 899 · breaking 677 · offspeed 150 · LHP: fastball 476 · breaking 270 · offspeed 177 |
| 2026 BIP, hand × group | RHP: 174 / 125 / 30 · LHP: 94 / 47 / 31 |
| Tracked swings (BP-0 gate) | 2023 0 · 2024 0 · **2025 1,177 · 2026 1,290** (≈96% of swings) |
| Unmapped pitch types (2023–26) | EP 4 · FA 3 · null 4 (excluded from pitch-group cells, counted in totals) |
| EDA | `eda/dp_uc57/turner_reg_2023_26.md` (9,778 rows × 42 columns) |

## Pre-registered (set 2026-10-23 20:49 ET, before any split or flag is computed)
### PR-1 pitch-recognition gap (new, provisional)
- **Grain:** batter × season × `p_throws` × pitch group, regular season.
- **Swing gap** = in-zone swing rate − out-of-zone swing rate (zone 1–9 vs 11–14). Higher means better discrimination.
- **Contact gap** = in-zone contact rate − out-of-zone contact rate, where contact = 1 − whiff/swing (`ooz_whiff_rate` from K54 for the OOZ leg).
- **Call** per cell, 2026 vs 2023–25, on the swing gap: CHANGED / LEANS / SAME per the change test in §3 above. HP-06 ("cannot make contact when he expands on righty breaking balls") is graded on the OOZ contact leg alone; HP-03 on the two swing legs.
- **Population for context:** Phillies hitter-seasons 2023–26 ≥ 200 PA (house pool rule, KP-1). Ranks, never MLB-wide.

### VS-1 velo segment (client definition, adopted for this product)
`High Velo` = `release_speed > 94.9`; `Less than 95 mph` otherwise. Governed frame excludes null velo (client frame keeps it; the difference is 0 pitches in 2026 vs LHP).

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤ 8 pp, 8 sections) | All eight questions, HP grades, caveats | **Build (hero)** |
| P2 | Interactive dashboard (≤ 7 chapters) + Artifact | Decision map by hand × group, swing-path panel with hover, contact-point map | **Build** |
| P3 | Reconstructed 3D swing animation (Single-Swing Pilot) | "Swing path visualization", one swing | **Tier B only**: needs the pilot's Gate 2 closed and PL-1 fixed first |
| P4 | Position-change projection | | **Not bid** (no position-change contrast in his data; carry-ins only) |

## Scope tiers (comparison-profile cap: report ≤ 8 pp · dashboard ≤ 7 chapters · ≤ 9 figures · ≤ 2 new KPIs)
### Tier A: Comparison profile (recommended, AWARDED)
Report: 1 Bottom line · 2 How bad was 2026? (Q1, CI-1) · 3 Recognition: in the zone vs out, by hand (Q2, Q3) · 4 Lefties and offspeed (Q4) · 5 Fastballs and the slow lefty fastball (Q5, Q6) · 6 The bat path, full season (Q7) · 7 Shortstop, second base, or the outfield (Q8, carry-ins only) · 8 The notebook graded (HP-01…HP-12) + caveats.
Figures F1–F9 as mapped above. New KPIs (1): **PR-1**. Glossary adoption (1): **VS-1**.
### Tier B: Tier A + the reconstructed swing (≈ +75k, +9 min)
Re-points the pilot to the house log (the intercept fields are there), applies O-15, reruns the pilot self-tests, and embeds one reconstructed swing (the 2026 Truist Park HR) next to one breaking-ball popup as chapter 7 of the dashboard. **Ships only if the DPO closes the pilot's Gate 2 first** (A1–A6, thresholds, bounds; and the v0.4 bat-head decision from this chat). Otherwise every frame carries the DRAFT label and the chapter is held back from the Artifact.
### Tier C: Lean (≈ −140k, −13 min)
PDF only, 6 figures (drops F2, F5, F9), no dashboard, no Artifact.

## Deliverables (Tier A)
| # | Deliverable | Where |
|---|---|---|
| 1 | `dp_uc57_turner_2026_recap_report.pdf` (+ `.md`) | MLB root (+ copy in this folder) |
| 2 | `dp_uc57_turner_2026_dashboard.html` (+ `_artifact.html`) + Artifact | MLB root (+ copy) |
| 3 | `dp_uc57_kernel.py`, `_turner_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py` | MLB root |
| 4 | `out/dp_uc57_*` (CSVs, figure JSON + PNG, `headlines.json`, DQ scorecard, verification log, HP grades) · `eda/dp_uc57/` | MLB root |
| 5 | Receipts `00`–`07`, README, this BID | this folder |
| 6 | Contract `uc-pos-022-Trea Turner 2026 Recap 20261023.md`, ledger patch `uc_ledger_AI_PATCH_uc-pos-022-turner-2026-recap.md` | MLB root (+ copy) |

**Explicitly not bid:** fielding metrics we don't have (OAA, DRS, errors are carry-ins only) · any claim that a position change would change his hitting · MLB-wide ranks (house population rule) · 2023–24 swing-path baselines (the fields don't exist) · spring or postseason PA in any rate · the 3D reconstruction in Tier A.

## Price (Tier A)
**Basis:** UC56 Sosa actual (≈466k, 34 min; ≈225k after T0) and UC55 Stott actual (≈322k after T0, 44 min). **Down:** the swing-path engine is inherited whole (K40a), the in-zone direction frame is inherited (UC42), only one new KPI, the T0 recon was short. **Up:** twelve HP rows (UC56 had eleven), hand × pitch-group cells multiply the figure and harness work, and the client panel has to be reproduced by IX-1 across four seasons and two frames.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon, carry-ins, env, profile, Rule-1 (**sunk: 100.5k at C3, 9 min**) + this BID and `00`/`01` | ~85k | ~22k | 9 |
| T1 Kernel + build + HP reproduction (both frames) + EDA to file | 65k | 20k | 8 |
| T2 Figures (9) + brand + render QA | 55k | 18k | 7 |
| T3 Dashboard (7 chapters) + QA + Artifact | 35k | 12k | 6 |
| T4 Narrative + report + PDF | 12k | 8k | 3 |
| T5 Verification harness | 25k | 9k | 4 |
| T6 Governance 00–07, README, contract, ledger patch | 25k | 16k | 6 |
| D Defect discovery | 10k | 3k | 2 |
| Contingency 5% (unsunk) | 12k | 4k | 2 |
| **BID** | **~324k** | **~112k** | **~47 min** |

**Total ≈ 436k tokens, ≈ 47 minutes.**
- **Recap set for comparison (actuals):** 466k (UC56) / 485k (UC55) / 576k (UC54) / 518k / 469k / 681k.
- **Credits at list** ($10/M in, $50/M out): ≈ **$8.84**, band $7.50–10.15 (±15%). Cowork bills subscription usage; read this as API-equivalent value.
- **Honest note:** the T0 line is low because this chat already had Turner context and three prior products did most of the recon. If the build runs in a **new chat**, add ≈ 35k in and 3 minutes to T1 to re-read this BID, `01` and the K55/K40a surfaces. That is still cheaper than a fresh T0 (≈ 240k on the UC55/UC56 record).

### Competitive position
A rival agentic org without this repo would have to:
- re-derive house wOBA, and the bat-path conventions that took UC40a a full addendum to prove (O-15 alone inverts every pull/oppo claim);
- discover that the client frame mixes spring and postseason rows (SRC-4) and two teams (SRC-5);
- rebuild a chase-cost and out-of-zone framework that K54 already certifies.

We estimate that bid at **~0.8–1.0M tokens and 65–80 min**, with no 00–07 trail, no harness, and no way to grade the notebook on the client's own frame.

Our differentiators:
- pinned inheritance: the full-season swing-path numbers reconcile with UC40a's 2026-09-02 cut;
- a recognition test whose bars were set before looking;
- client claims graded, never overwritten;
- a position question answered honestly as untestable instead of with a proxy;
- bid-vs-actual history (UC48–UC56 within −28% to +5%).

## Assumptions, exclusions, carry-ins
- Regular season for every rate. Postseason in its own ledger line; spring and exhibition excluded and reported (SRC-4).
- Entity locked by MLBAM 607208 + batting role; the name is used only to reproduce the client frame.
- Populations: house hitter pool = Phillies hitter-seasons 2015–26 ≥ 50 PA (K40/K54, KP-1); PR-1 context pool = Phillies hitter-seasons 2023–26 ≥ 200 PA; bat path 2025–26 only, peer cohort as UC40a.
- Carry-ins CI-1 and CI-2 are labelled at every use and never computed on.
- "The conversation I started last night" is read as the 2026-10-22 bat-tracking CDE interpretation (carried forward in UC55 `01` §5). The DPO can point elsewhere (gap G2 in `01`).

---
**HARD STOP.** Per the client's instruction, the build does not start in this turn. To proceed, the DPO says "go" (this chat) or opens a new chat pointing at this folder; either path starts at T1 with the ID reservation, pre-registration and pins above unchanged.
