# BID: Bryson Stott 2026 season recap, "Another Level?"

**Status:** FILED 2026-10-22 19:27 ET · **AWARDED 2026-10-22 19:27 ET (Tier A)**. The RFP says to treat this bid as the winner, so the build continues in the same turn without a stop. Actuals are reconciled in `07_platform_marketing.md` §3.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-22 (T0 wall clock 19:17 → 19:27 ET)
**ID reservation:**
- UC **#55**
- contract `uc-pos-020`
- build artifact `dp_uc55`
- control-plane folder `uc-pos-020-stott-2026-recap-001`

**Collision check (bid time):** No `dp_uc55*` exists at the MLB root, in `out/`, in `eda/` or in the control plane. `uc-pos-020` appears only as "pos next" in the UC54 ledger patch and in `07`.

**Prior Stott work.** It is inherited, not redone:
- **`uc-pos-010` / dp_uc33** (UC #34, read through 2026-08-13). Approach-change read: chase 33.8% → 21.5% and first-pitch swing 24.0% → 7.1%. It also found that first-pitch strike rate against him collapsed 67.1% → 41.1%, and put OBP:K at the 83rd percentile.
- **`uc-pos-stott-qab-001`**: quality-at-bat intake, gap report only.

**Working title:** "Another Level?", from the client's own first line. The DPO can rename it.
**Second pos-side season recap.** It inherits the K54 recap shape (C-7: "Bohm, Stott, Marsh … get the same seven chapters in one constants change").

---

## Audit counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Session start (turn 1: data-dictionary interpretation) | 15,000,000 | — | 0 |
| C0' | Start of this turn, after the tool-schema load | 14,989,939 | 10.1k | 10.1k |
| C1 | Two-repo recon: UC54 card, BID, 00/04/07; data-products README | 14,940,921 | 49.0k | 59.1k |
| C2 | Env (ENV-3 third occurrence), K54 import and lineage, data profile, Rule-1 (K40a bat path, UC5, K44), carry-ins (6 web reads), house skills | 14,848,830 | 92.1k | 151.2k |
| C3 | BID filed | read in `07` | | |

## The ask (as submitted)
A notebook export (`d8b91d3b-attachment.txt`, "Bryson Stott") with a thesis ("Is there another level to unlock for him? I don't believe it"), four questions, code, and two notes for the org. Instructions from the RFP:
- (a) Evolve the notebook into a use case, then into a data product, **built iteratively**.
- (b) Work **inside the MLB data plane**. The control plane holds the org that drives the build. Output is governed and documented with **00–07 receipts in a `data-products/` subfolder**. Take inspiration from the scouting-report skill and similar MLB outputs, and follow data-plane coding standards.
- (c) Include a token and time estimate, framed as a competitive bid, and treat it as the winner.
- (d) The session opened with the client's data-dictionary card for six bat-path / delivery CDEs. Those CDEs are in scope wherever they inform the questions.

### Client questions → report sections
| Q | Client question | § | Primary figure |
|---|---|---|---|
| Q1 | "Show me his wOBA and OPS accumulating across a season" + the KPI panel by season | §2 | F1 cumulative wOBA/OPS, 2026 vs 2022–25 (house cumulative-chart skill) · F2 season card |
| Q2 | What does "Good" look like? Early 2023, 2025 second half, summer 2026, plus "a better way to determine timeframes" | §3 | F3 form-era timeline (ER-1) with the client's eras marked |
| Q3 | Good vs Bad A/B test ("pretty much the same hitter") | §4 | F4 GS-1 signature dumbbell, client eras and ER-1 eras |
| Q4 | "Is he hitting the ball the other way? Using all fields?" | §5 | F5 spray on a drawn CBP field + direction shares by era |
| Q5 | "Line drives or flyballs?" | §5 | F5 + F6 bat path (attack angle × attack direction, the client's scatter rebuilt) |
| Q6 | "Better against lefties? Righties? Pitch types?" Velocity | §6 | F7 hand × pitch-group grid by era · F8 ≥95 mph fastballs |
| Q7 | "Chasing less, taking walks?" | §2, §4, §6 | F2, F4 |
| Q8 | Defense: 2B vs prior years ("might have been a down year"); 3B "good enough … full time"; "limited thump if so" | §7 | F9 IO-1 by season and position, with OAA/DRS carry-ins · F10 opportunity map |
| Q9 | "Is there another level?" | §1, §8 | (synthesis) |

### Client claims to be graded
HP rows are reproduced on the client's own frame (`pos[pos.player_name == pn]`, no game-type filter) with the client's functions (IX-1 from `Baseball Functions.ipynb` + K44) before any governed restatement.

| HP | Claim |
|---|---|
| HP-01 | 2026 "very good … nearly in line with 2023 or better in some ways" |
| HP-02 | "He is barreling the ball better nowadays" |
| HP-03 | "Walked more than ever this year" |
| HP-04 | "Pretty consistent K rate" |
| HP-05 | "Line drives up to 2023 levels" |
| HP-06 | "Chased more than ever" |
| HP-07 | Good vs Bad: "barely barrels more, does walk more and hit more line drives … pretty much the same hitter" |
| HP-08 | Platoon: no noticeable Good/Bad difference vs LHP or RHP |
| HP-09 | "It might be velocity?" |
| HP-10 | Attack direction "middle 65%" band is −18° to +13° (the client's `add_hrect`) |
| HP-11 | 2B 2026 "might have been a down year" |
| HP-12 | 3B "good enough … to potentially move there full time" |
| HP-13 | "This team has limited thump if so" |
| HP-14 | Thesis: "I don't believe" there is another level |

## Why this shop wins this RFP
### 1. We inherit instead of re-deriving.
- The recap spine is **K54** (`dp_uc54_kernel.py`, sha `1a31b30a…`): K40 → K34 → K53 → K52 → K51/K50/K48/K44, CM-1, OZ, PA-1 and `two_prop_z`. Its 12 pins re-assert at import.
- The bat-path family is **K40a** (`dp_uc40a_kernel.py`, sha `807986c0…`). It brings:
  - BP-0 population, which excludes bunts and degenerate swings
  - BP-1 `swing_path_profile`
  - `assert_conventions` C1–C8
  - `peer_delta`
- **K40a already answers the governance questions raised on the client's data-dictionary card earlier in this session:**
  - `attack_direction` is **stand-normalised and PULL-NEGATIVE** in this data plane. That is the inverse of the published glossary (O-15).
  - `intercept_y` is the **depth** axis (C2).
  - Bat path ships from **2025**, bat speed from 2024.
  - The tilt fell team-wide by ~1.1° from 2025 to 2026 (O-16), so year-over-year tilt is peer-netted or not published.
  - We inherit these conclusions rather than re-proving them, and re-run `assert_conventions` as a build gate.
- **DR-1** `hit_direction` and **CR-1** `battedball_profile` come from K40, **RF-2** rolling form and **RC-5** breakpoint scan are reused, and **XO-2** machinery (`xo2_score`) is generalized for infield (IO-1).
- **UC34's Stott findings are carried forward,** not recomputed: the approach-change read and first-pitch-strike collapse are cited with their dp_uc33 receipts.

### 2. We checked the premise before bidding. Carry-ins are sourced and never computed on.
- **CI-1:** On the 2026 line (thatballsouttahere, 2026-10-22): .256, 10 HR, **62 BB (career high)**, 155 G, 4.14 P/PA (21st in MLB). The log reconciles at bid time: 608 PA, .256, 10 HR, 62 BB.
- **CI-2** (On Pattison, 2026-10-18, after Dombrowski's year-end presser):
  - Mar–May .217; Jun–Aug .286 with 2.8 fWAR (13th among qualified); September .692 OPS
  - 27-for-27 SB
  - **2B 2026: +8 OAA, −9 DRS over 953⅓ inn**
  - 2025: .234/.637 OPS in the first half, then **.294/.855 after the All-Star break following a stance change under Kevin Long**
  - Dombrowski: "I don't know why he can't be *that* player all the time"
  - Free agent after 2027
- **CI-3:** Luis Arraez was acquired at the deadline (uc-pos-008, read 2026-08-04). **Stott moved 2B → 3B in August: +2 OAA, +3 DRS in 129 inn** as of 2026-08-19. Dombrowski: "I'm not looking at him as a third baseman for the long term" (Inquirer / Central Bucks News, 2026-08-19/20).
- **CI-4:** Career 2B **+33 OAA, +8 DRS** (as of 2026-08-22).
- **CI-5:** Bohm was in the final year of his contract in 2026 (NBC Sports Philadelphia, 2026-05-06).
- **CI-6:** 2023: a franchise-record 17-game hitting streak to open his season; .280/.329/.419 (Wikipedia; the log's K40 OBP reads .327, SF-1 convention).

### 3. We pre-register the argument.
The client's eras were chosen from memory of outcomes, so any test of "what was different when he was good" on those eras is outcome-selected. We make three commitments, all written before any era split is computed:
- **ER-1** is the governed era detector.
- **GS-1** is the signature ledger.
- Both are applied to **both** the client's eras and the ER-1 eras.

Disclosure: the bidder printed PA counts per client era at T0 (`Bad/Good` = 401/237, 313/249, 289/319 for 2023/25/26) and season-level slash/xwOBA lines, but no era-level rate.

### 4. We found the traps before the build.
- **SRC-4 (new): the client frame has no `game_type` filter.** `pos[pos.player_name == pn]` carries:
  - 2022: 11 D + 7 F + 15 L + 18 W postseason PA
  - 2023: 16 D + 8 F + 27 L
  - 2024: 13 D
  - 2025: 14 D
  - 2026: **37 spring (S) + 3 exhibition (E) + 13 Wild Card (F) PA**
  - So the client's 2026 "season" row includes spring training. Every HP row reports both frames.
- **SHIFT-1 (new, domain-steward):** infield positioning changed with the 2023 shift restrictions. The IO-1 comparator pool is therefore **2023–26 only**. Stott's 2022 2B (47 games) is shown and labelled pre-rule.
- **ERA-1:** the client's `hot_or_not` 2025 window is `month > 6`. That starts July 1, about two weeks before the All-Star break that CI-2 dates the stance change from.
- **CL-1 (client code):** in the attack-direction block, `std_ad = ('attack_direction','mean')` computes the mean, not a standard deviation. And `level = ['game_year','attack_direction']` groups on the value itself, so every group is one value. The "middle 65%" band (HP-10) therefore can't have come from that block. We recompute it governed.
- **ENV-3, third occurrence:** `/sessions` is at 100% on the laptop VM again. The render stack went to `/tmp/pyrender` with `TMPDIR=/tmp/uc55/tmp`. `phillies_dp.selftest` passes 3/3.

### 5. We build where the RFP says.
This RFP says "work inside the MLB repository", so:
- **Code and outputs live in the data plane:** `dp_uc55_*.py` at the MLB root and `out/dp_uc55_*`, matching UC48–UC51.
- **EDA** goes to `eda/dp_uc55/`.
- **The governance trail** (00–07, BID, README) plus delivered copies of the report and dashboard go to the control-plane folder.

This differs from UC53/UC54, which kept code in the control plane per their RFPs.

## Data position (verified at bid time)
| Check | Result |
|---|---|
| House log | `phils_2015..2026.parquet`, 556,863 rows; max `game_date` **2026-10-01** (pinned anchor, same as UC54) |
| Entity lock | MLBAM **681082**, bats L, `phillies_role == 'batting'`; 0 duplicate pitch keys; one name |
| Regular-season PA | 2022 466 · 2023 638 · 2024 569 · 2025 562 · **2026 608** (154 games with a PA) |
| 2026 monthly PA | Mar 13 · Apr 82 · May 104 · Jun 107 · Jul 96 · Aug 116 · Sep 90 |
| 2026 PA by hand | vs RHP 463 · vs LHP 145 |
| Bat tracking (swings) | bat speed 2024 960 · 2025 980 · 2026 1,024; bat path 2025 980 · 2026 1,024; none before 2024 |
| Defense, regular season | games at 2B (`fielder_4`): 2022 47 · 2023 149 · 2024 137 · 2025 135 · 2026 116 · games at 3B (`fielder_5`): 2022 2 · **2026 43** · SS 2022 83, 2024 14, 2025 13 |
| Defensive BIP fielded at his position | 2B: 120 / 434 / 382 / 371 / 307 · 3B 2026: 98 |
| Postseason | own ledger line, never in a rate |

## Rule-1 search (full table goes to `03` §0)
| Need | Hits | Disposition |
|---|---|---|
| Slash line, wOBA, xwOBA, chase/whiff/swing, HH/barrel, CR-1, DR-1, RF-2, RC-5, KP-1, PA-1, two-prop z, CM-1 | **K54 → K40/K53 chain** | **Inherit** (pinned) |
| Bat path (attack angle/direction, tilt, intercepts, BP-0 population, conventions) | **K40a** | **Inherit** (pin `807986c0…`) |
| Client functions (`nresults`, `chase_rate`, `whiff_rate`, `hard_hit_rate`, `bb_type_by_level`) | K44 (Baseball Functions verbatim) | Inherit |
| Client `inds`, `barrel_rate` | `Baseball Functions.ipynb` / `barrel_rate.py` | IX-1 extraction / K54 chain |
| Stott approach-change history | UC34 / dp_uc33 receipts | Cite |
| Era detection ("a better way to determine timeframes") | RC-5 scans requester dates only; TR-1 tests one requester date | **New, provisional ER-1** |
| Good-vs-Bad signature test | TR-1 (pre/post one date) | **New, provisional GS-1** (TR-1 generalized to labelled eras, same PA-1 rule) |
| Infield expected outs | UC5 left-side conversion (proxy, Bohm at 3B, 2026 to June); XO-2 (CF) | **New, provisional IO-1** (XO-2 machinery on infield sectors; UC5 hit-location credit as the method check) |

## Pre-registered: ER-1 "form eras" (set 2026-10-22 19:27 ET)
- **Atom:** per-PA wOBA contribution (house weights, K40 numerator and denominator) in PA order within each regular season 2022–26. A second basis, **ER-1x**, uses XW-1's per-PA expected atom (RF-2x).
- **Segmentation:** binary segmentation on the PA sequence.
  - The split point maximizes the reduction in weighted squared error.
  - A split is accepted only if it beats **500 within-segment PA-order permutations at α = 0.10**. The seed is 55.
  - Each segment must be ≥ **100 PA**, with at most **3 segments per season**.
  - If no split survives, the season is one segment. That is a finding, not a failure.
- **Labels:** each segment is compared with his **career** regular-season wOBA (2022–26, same basis):
  - **Good** if ≥ career + .020
  - **Bad** if ≤ career − .020
  - **Par** otherwise
- **Robustness, reported beside the result:** agreement (share of PA) between ER-1 and the client's eras, ER-1 vs ER-1x, and the RF-2 rolling-100 view.

## Pre-registered: GS-1 good-era signatures (Good minus Bad)
Each signature is scored with PA-1 `signature_verdict`. Proportions take a `two_prop_z` p-value; xwOBA runs without a test.

| Sig | Metric | Direction | Bar | Test |
|---|---|---|---|---|
| S1 | xwOBA | + | .025 | — |
| S2 | BB% | + | .015 | z |
| S3 | K% | − | .030 | z |
| S4 | chase rate | − | .030 | z |
| S5 | whiff rate | − | .030 | z |
| S6 | hard-hit rate | + | .040 | z |
| S7 | barrel rate (per BIP) | + | .020 | z |
| S8 | line-drive rate | + | .030 | z |
| S9 | opposite-field share of BIP (DR-1) | + | .030 | z |
| S10 | fly-ball rate | + | .030 | z |

- **Reported, not scored:** wOBA, BA and BABIP (the eras are built on results, so they are circular). Bat path (2025–26 only) is reported with its tracked-swing n.
- **Call:**
  - process roll-up STRONG or SUPPORTED → **DIFFERENT HITTER**
  - MIXED → **PARTLY DIFFERENT**
  - UNSUPPORTED → **SAME HITTER, RESULTS RAN AHEAD**
- The call is computed twice: on the client's eras (grades HP-07) and on the ER-1 eras.

## Pre-registered: IO-1 infield sector expected outs (proxy)
- **Opportunity:** a regular-season ground ball (no bunts) in the position's spray sector while the subject is at that position.
  - **Sector rule (disclosed, fixed before scoring):** the contiguous spray band in which that position records ≥ 50% of the outs, over the 2023–26 pool with any fielder there.
- **Expected out:** the out share among **other fielders'** pool grounders in that sector (2023–26, SHIFT-1) within **EV ±3 mph, LA ±4°, spray ±5°**, with ≥ **10 neighbours**.
  - Coverage must be ≥ 90%. If not, widen in disclosed order: (4, 5, 6) → (5, 6, 8).
- **Outs** are outs on the play: `field_out`, `force_out`, `grounded_into_double_play`, `double_play`, `fielders_choice_out`, `triple_play`. Errors are not outs.
- **Published** as outs above expected per season × position, and per 100 opportunities. The OAA/DRS carry-ins sit **beside** it, never blended. It is labelled a **proxy** (the log has no catch or arm data and no starting position).
- **Method check:** the UC5 hit-location credit (balls he fielded, and how many he converted) is reported for the same rows.

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤10 pp, 8 sections) | All nine questions, HP grades, caveats | **Build (hero)** |
| P2 | Interactive dashboard (≤8 chapters) + Artifact | Cumulative lines, era timeline with hover, spray and bat-path scatter, defense map | **Build** |
| P3 | "Another level" development card for staff (one page) | Three repeatable traits of his good eras | **Folded into report §8 and dashboard ch. 8**; no separate form |
| P4 | 2027 projection / extension valuation | | **Not bid**: no projection model in the house; contract valuation is out of profile |
| P5 | Notebook cell patch (ER-1 replacing `hot_or_not`) | Gives the client the better timeframe tool in his own notebook | **Bid as a receipt** (`out/dp_uc55_er1_notebook_cell.md`), not applied to `.ipynb` |

## Scope tiers
Comparison-profile cap for every tier: report ≤10 pp · dashboard ≤8 chapters · ≤10 figures · ≤3 new KPIs.

### Tier A: Comparison profile (recommended, AWARDED)
**Report, 8 sections:**
1. Bottom line: another level?
2. The 2026 line (Q1, Q7)
3. What "Good" looks like: ER-1 eras vs the client's eras (Q2)
4. The A/B test, done properly (Q3: GS-1)
5. Direction, contact and bat path (Q4, Q5)
6. Platoon, pitch types and velocity (Q6)
7. Defense: second, third and the thump question (Q8)
8. Your notebook graded + caveats

**Figures (10):**
- F1 cumulative wOBA and OPS by PA, 2026 red over 2022–25 (CM-1; endpoints reconciled to K40)
- F2 season card: KPI × season with house percentile
- F3 form-era timeline 2022–26: rolling 100-PA wOBA, ER-1 segments shaded, client eras bracketed
- F4 GS-1 dumbbell (client eras | ER-1 eras)
- F5 spray chart on a drawn CBP field, Good vs Bad, with direction shares
- F6 the client's attack-angle × attack-direction scatter, rebuilt: Phillies density, Stott's era means, governed middle-65% band, 2025 H1/H2 stance change
- F7 hand × pitch-group grid by era (xwOBA, whiff, chase)
- F8 ≥95 mph fastballs by era and hand
- F9 IO-1 by season and position with OAA/DRS carry-ins
- F10 infield opportunity map (2B and 3B 2026)

**New KPIs (3):** ER-1 · GS-1 · IO-1.

### Tier B: Tier A + extras (≈ +80k, +7 min)
Adds a separate staff development card (PDF), a postseason ledger page, and a 27-for-27 baserunning page. It breaks comparability (+2 pp).

### Tier C: Lean (≈ −140k, −14 min)
PDF only; 6 figures (drops F2, F7, F8, F10); ER-1 + GS-1 only, with defense as carry-ins only.

## Deliverables (Tier A)
| # | Deliverable | Where |
|---|---|---|
| 1 | `dp_uc55_stott_2026_recap_report.pdf` (+ `.md`) | MLB root; copy in control plane |
| 2 | `dp_uc55_stott_2026_dashboard.html` (+ `_artifact.html`) + Artifact | MLB root; copy in control plane |
| 3 | `dp_uc55_kernel.py`, `_stott_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_report.py`, `_build_pdf.py`, `_build_dashboard.py`, `_verification.py` | MLB root (data plane) |
| 4 | `out/dp_uc55_*` (CSVs, figure JSON+PNG, `headlines.json`, DQ scorecard, verification log, HP grades, ER-1 notebook cell) | MLB `out/` |
| 5 | Receipts `00`–`07`, README, this BID, ledger patch, contract copy | Control plane (contract + ledger patch also at MLB root) |

**Explicitly not bid:**
- fielding metrics we don't have (OAA, DRS, arm, positioning; shown as carry-ins)
- MLB-wide ranks (house population rule)
- causal claims about the stance change
- projection
- any postseason or spring PA in a rate

## Price (Tier A)
**Basis:** UC54 Crawford actuals (≈576k, 46 min) with calibration C-7 (next pos recap: T0 −40k, T1 −10k).
- **Down:** the spine is known. K54 and K40a import in one line each, and T0 is already measured at 151k on the counter.
- **Up:** five seasons instead of one, and a permutation-tested segmentation (ER-1). IO-1 is a two-position adaptation with a sector-selection rule. GS-1 runs twice. The bat-path chapter crosses the earlier data-dictionary questions, and there are 14 HP rows.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, recon, carry-ins, env, profile, Rule-1 (**sunk: 151.2k at C2**) + this BID | ~155k | ~12k | 10 |
| T1 Kernel + build + HP reproduction + EDA to file | 75k | 22k | 11 |
| T2 Figures (10) + brand + render QA (C-8: 12k + 5k fix loop) | 55k | 18k | 8 |
| T3 Dashboard (8 chapters) + QA + Artifact | 38k | 14k | 6 |
| T4 Report + PDF (narrative module) | 12k | 8k | 3 |
| T5 Verification harness | 18k | 9k | 4 |
| T6 Governance 00–07, README, contract, ledger patch | 25k | 18k | 6 |
| D Defect discovery | 10k | 3k | 2 |
| Contingency 5% (unsunk) | 12k | 5k | 2 |
| **BID** | **~400k** | **~109k** | **~52 min** |

**Total ≈ 509k tokens, ≈ 52 minutes.**
- **Recap set for comparison:** 576k (UC54) / 518k / 469k / 681k / 545k / 530k.
- **Credits at list** ($10/M in, $50/M out): ≈ **$9.45**, band $8.00–10.90 (±15%). Cowork bills subscription usage, so read this as API-equivalent value.
- **Time cross-check:** 0.10 min per 1k × 0.85 (device build, foreground installs done) × 509k ≈ 43 min. We bid 52 because ER-1's permutation search and IO-1's two-sector scoring are new code paths on the device.

### Competitive position
A rival agentic org without this repo would have to:
- re-derive house wOBA, the `_fix` lineage and the CM-1 endpoint reconcile
- **discover O-15 on its own** (or, worse, read the glossary convention onto `attack_direction` and invert every pull/oppo conclusion in §5)
- hit SRC-4 (spring training inside the client's 2026 row), SHIFT-1 and CL-1 the hard way

We estimate that rival bid at **~0.95–1.15M tokens and 70–85 min** (+300k re-derivation, +120k bat-path conventions, +80k defect loops). It would have no 00–07 trail, no harness, and no way to grade the client's notebook on the client's own frame.

Our differentiators:
1. Pinned inheritance, so the numbers reconcile with UC34's August read and UC54's spine.
2. Eras detected by a pre-registered rule, so we're not testing a story fitted to remembered months.
3. Client claims graded, never overwritten.
4. A bid-vs-actual history (UC48–UC54 within −28% to +5%).

## Assumptions, exclusions, carry-ins
- Regular season for every rate. Postseason goes in its own ledger line; spring and exhibition are excluded and reported (SRC-4).
- The entity is locked by MLBAM 681082 + batting role, or `fielder_4`/`fielder_5` == 681082 on the defensive side. The name is used only to reproduce the client frame.
- **Populations:**
  - house hitter population: Phillies hitter-seasons 2015–26, ≥ 50 PA (K40/K54 pool)
  - bat-path peers: Phillies hitters with tracked swings, 2025–26 (K40a)
  - IO-1 pool: Phillies infield grounders 2023–26
- Rank and n are printed with every superlative.
- Carry-ins CI-1 to CI-6 are labelled at every use and never computed on.
- The 2025 stance change (CI-2) is a labelled date marker. Bat path is compared H1 vs H2 descriptively, and **no causal claim** is made.
