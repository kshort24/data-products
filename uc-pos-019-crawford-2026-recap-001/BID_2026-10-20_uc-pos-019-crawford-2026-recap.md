# BID — Justin Crawford 2026 season recap (rookie year): "Exactly as Advertised"

**Status:** FILED 2026-10-20 23:18 ET · **AWARDED 2026-10-20 23:18 ET (Tier A)**. Per the RFP, the exercise treats this bid as the winner, so the build proceeds in the same turn without a stop. Actuals are reconciled in `07_platform_marketing.md` §3.
**Bidder:** the data product organization (`data-product-owner`, bidding for all seven departments)
**Human DPO:** Kellen Short · **Bid date:** 2026-10-20 (T0 wall clock 23:07→23:18 ET = 11 min)
**ID reservation:** UC **#54** · contract `uc-pos-019` · build artifact `dp_uc54` · folder `uc-pos-019-crawford-2026-recap-001`
**Collision check (bid time):** `dp_uc54*`: none at the MLB root, in `out/` or in the control plane. `uc-pos-019*`: no claim; it appears only as "pos next" in the ledger and the UC51–UC53 patches. Prior Crawford work: **`uc-pos-011` / dp_uc34** (YTD read through 2026-08-13). It is inherited, never redone: its CX-1 centre-field pool, CR-1/CR-2 contact functions and the "June 15 breakpoint is not robust" finding are carried forward.
**Working title:** "Exactly as Advertised", from the client's line "he pretty much was the hitter we expected him to be". The DPO can rename it.
**First pos-side season recap.** UC48–UC53 were all pitchers. This bid sets the pos recap shape.

---

## Audit Phase 2 counters (session token counter, tokens left)
| Mark | When | Counter | Δ | Cumulative |
|---|---|---|---|---|
| C0 | Session start | 15,000,000 | — | 0 |
| C0' | First visible reading (after first-turn load + tool-schema load) | 14,869,918 | 130.1k | 130.1k (first-turn load) |
| C1 | Two-repo recon, house card, UC53 README/BID, UC34 README/report, ledger tail | 14,814,000 (≈) | ≈56k | ≈186k |
| C2 | Env (ENV-3 again), id scan, data profile, kernel reads (K53/K40/K34/K44/K46/CM), carry-ins, skills | 14,722,304 | ≈92k | 277.7k |
| C3 | BID filed | read in `07` | | |

- **First-turn load ~130k** (system prompt, skill listings, the client notebook). Repo work in T0 net of it: **~148k**. That is above UC53 (~126k net) for two reasons. The pos spine had to be found: K40 → K34 lineage, which no pitcher recap used. And the defense question needed a Rule-1 sweep across UC4 and the client's `Baseball Functions.ipynb`. Per C-5, the kernel reads are priced into T0.
- **Kernels read by function excerpt only:** K53 (head, 150 lines), K52/K50/K48/K44/K51 (one function each), K40 (header + 4 functions), K34 (governed functions, ~380 lines), K46 (constants), UC22 `tag_regions`. No parent build script was opened in full.

## The ask (as submitted)
A notebook export (`a4523113-attachment.txt`, "Justin Crawford") with six questions and code. Instructions from the RFP:
- (a) Work inside the MLB data plane. The control-plane org drives the build; receipts follow the house 00–07 standard. Take inspiration from the scouting-report skill and from prior outputs.
- (b) **Good visuals.** That means line graphs of cumulative statistics and **cleaner versions of the client's own plots**: mean location by pitch group vs RHP, EV box by breaking-ball type, the hit pitch map faceted by year, and the spray chart. The RFP asks for these instead of "fairly lame bar charts and simple line graphs".
- (c) Receipts, outputs and artifacts go in a new control-plane `data-products/` folder.
- (d) Include a token and time estimate, framed as a competitive bid.

**The six client questions → report sections:**

| Q | Client question | Section | Primary figure |
|---|---|---|---|
| Q1 | Rookie line: cumulative BA, wOBA, OPS; final BA with RISP, GB rate, hard-hit rate | §2 | F1 cumulative ghost lines vs Phillies CF seasons |
| Q2 | Evolution: "better from ~June 1 on" | §3 | F2 rolling form + F3 TR-1 turn ledger |
| Q3 | Approach: high swing, high chase, low whiff | §4 | F4 percentile profile + F5 attack-region swing/take |
| Q4 | Improve: raise BB% and OBP, cut K% (the client's mechanism: chase less, esp. vs RHP; handle RHP spin; use the whole field) | §6–§7 | F7 chase map + CC-1 cost · F8 RHP breaking balls · F9 spray |
| Q5 | Defense | §8 | F10 CF opportunity map + outs vs expected |
| Q6 | Ground-ball rate | §5 | F6 cumulative GB% and HH% vs CF seasons, plus LA and bat path |

**Client claims to be graded (HP rows; reproduced on the client's own frame before any governed restatement):**
| HP | Claim |
|---|---|
| HP-01 | 17.3% K rate |
| HP-02 | 53.3% swing rate |
| HP-03 | 37.7% chase rate |
| HP-04 | 17.6% whiff rate |
| HP-05 | "only 35% hard hits" |
| HP-06 | BA .186 on pitches out of the zone |
| HP-07 | Out-of-zone contact is "pretty impressive" |
| HP-08 | He was better from ~June 1 on |
| HP-09 | "He chased too much against RHP" |
| HP-10 | He needs to do damage against RHP breaking balls |
| HP-11 | His AAA hits on RHP breaking balls came on hangers, which he doesn't get in MLB |
| HP-12 | He pulls RHP breaking balls; should use the whole field |
| HP-13 | Defense: "made all the plays I would have expected" (outs ≈ expected outs) |
| HP-14 | "Pretty much the hitter we expected" (framing; graded against the UC34 profile, not a number) |

## Why this shop wins this RFP
1. **We inherit instead of re-deriving.**
   - The pos-side spine is **K40** (`dp_uc40_kernel.py`, uc-pos-014, sha `895c0edc…`), the latest of the K33 → K34 → K37 → K40 `_fix` lineage. Through it come D4-corrected slash lines and wOBA, RISP rows, whiff/chase/swing/OOZ-whiff fixes, hard-hit and barrel fixes, CR-1 batted-ball profile, CR-2 xwOBAcon, PA-L1/DR-1 spray, RF-2 rolling form, RC-5 breakpoint scan, PL-1 platoon counterfactual, bat tracking, and the house percentile.
   - **K34** (`dp_uc34_kernel.py`, sha `263e57d1…`) supplies the CX-1 Phillies centre-field context pool, built for this player.
   - **K53** (sha `03d7e380…`) supplies the K52 → K51/K50/K48/K44 chain: XW-1 xwOBA, WB-1, KP-1 percentile, PA-1 verdict rule, IX-1 source extraction, brand, `two_prop_z`. It also brings the house cumulative module **CM-1** with K53's corrected wOBA spec **CM-1a**.
   - The attack-region geometry comes from **UC22 `tag_regions`** (OZ family) and the client's own `find_similar_hits` from `Baseball Functions.ipynb`. Both are extracted with IX-1, source-pinned and never copied.
2. **We checked the premise before bidding** (carry-ins, sourced, never computed on):
   - **CI-1:** debut 2026-03-26 as the starting CF vs TEX. Contract selected 2026-03-25 (Wikipedia).
   - **CI-2:** final line .264/.309/.353, 149 G, 3 HR, 17 SB in 21, OPS+ 78, −0.2 WAR, **−2 DRS, −8 OAA** in CF. Mostly platooned once Derek Hill emerged; mostly hit ninth (97.5 The Fanatic, 2026-10-14).
   - **CI-3:** OAA −3 in March/April (2nd-worst among MLB CFs), 0 in May. Sprint speed 97th percentile. Benched 2026-06-05 in a slump, .195 since May 1 (Inquirer, 2026-06-05).
   - **CI-4:** 2025 Triple-A Lehigh Valley: .334, 7 HR, 46 SB in 112 G (Wikipedia).
   - **CI-5:** Derek Hill's first PHI game was 2026-06-13 (derived in UC34; inherited).
   - The log reconciles to CI-2 at bid time: 465 PA, 112 H / 425 AB = **.264**. Every rate in the product is computed; CI-2's OAA and DRS are shown beside our proxy, never blended into it.
3. **We pre-register the argument.** "Better from June 1" is the client's hypothesis, and UC34 already showed a requester-chosen breakpoint can be outcome-selected. So the **TR-1 turn ledger** (below) is written into this BID **before** this UC computes any pre/post-June-1 rate. Disclosure: UC34 published one June-1 split through 2026-08-13 (+.019 wOBA), and this bidder read it at T0.
4. **We found the source traps before the build.**
   - **ENT-2 (new):** `data/opponents/crawford.parquet` is **J.P. Crawford** (641487, SEA 2019–23), not Justin. A name- or file-based lock gets the wrong player. The lock is MLBAM **702222** + `phillies_role == "batting"`.
   - **SRC-1:** the client frame `pd.concat([nphl[pn], pos[pn]])` has no `game_type` filter. Its 2026 group carries **125 spring and 25 Wild Card pitches**.
   - **SRC-2 (new):** `white-sox-of-25-26.parquet` holds **3 of Justin's 2026 MLB pitches**. They survive `nphl`'s own de-dupe and are double-counted once concatenated with `pos`.
   - **SRC-3:** the client's 2025 "year" is **Triple-A Lehigh Valley** (`lhvb25`, 1,938 pitches, 507 PA). It is a different level with weaker tracking: 25/356 BIP have no EV, and `woba_denom` is null on most rows. It gets a labelled "supporting tier", never blended (scouting-report skill rule).
   - **DEF-3:** the client's defense method only scores balls **Crawford fielded** (`hit_location == 8 & fielder_8 == rid`). Balls that fell in, or that he never reached, cannot be outs he missed. That is selection toward the made play, which matches the client's own note: "I have a tendency to overrate guys with this". CI-2's −8 OAA is the external check.
   - **ENV-3:** `/sessions` is 100% full on the laptop VM again. The render stack went to `/tmp/pyrender` with `TMPDIR=/tmp/uc54/tmp`.
5. **We build where the data lives.** Everything runs on the laptop VM against the parquet layer, with nothing staged. Outputs, code and receipts go to the control-plane folder (UC53 convention). The contract and ledger patch copies go to the MLB root.

## Data position (verified at bid time)
| Check | Result |
|---|---|
| Phillies 2026 log | `phils_2026.parquet`, 52,863 rows, max `game_date` **2026-10-01** (pinned anchor) |
| Entity lock | MLBAM **702222**, bats L. Regular season **1,681 pitches · 465 PA · 144 games with a PA** (CI-2's 149 G includes defensive/pinch appearances), 2026-03-26 → 2026-09-27. 0 duplicate pitch keys. 0 rows under his name with another id |
| Postseason | 3 Wild Card games, 25 pitches → own ledger line, never in a rate |
| Splits (counts only) | PA vs RHP 399 / LHP 66 · pre-June-1 182 / post 283 · monthly PA 13/86/83/79/59/84/61 |
| Tracking | 4 of 353 BIP without EV (O-8 exposure); 0 null zone/pitch type |
| CF defense | 146 regular-season games at `fielder_8`; 18,625 defensive pitches; 506 BIP with `hit_location == 8`; 1,649 air BIP with him in CF |
| AAA tier | `lhvb25.parquet`: 1,938 pitches, 507 PA, 2025-03-28 → 2025-09-03 |
| Environment | plotly 6.0.1 · pandas 2.2.3 · weasyprint 70.0 · pyarrow 24.0.0 in `/tmp/pyrender`; `phillies_dp.selftest` 3/3 |

## Rule-1 search (full table goes to `03` §0)
| Need | Hits | Disposition |
|---|---|---|
| Slash line, wOBA (house weights), RISP, whiff/chase/swing/OOZ fixes, CR-1, CR-2, spray, rolling, breakpoint scan, bat tracking, percentiles | **K40** | **Inherit** (pinned) |
| Phillies CF context pool | **K34 CX-1** | **Inherit** (pinned) |
| xwOBA (XW-1), WB-1, KP-1, PA-1, IX-1, brand, two-prop z | K53 → K52 → K51/K50/K48/K44 | **Inherit** (pinned chain) |
| Cumulative by PA | `cumulative_metric.py` CM-1 + CM-1a | **Inherit**. BA/OBP/SLG/GB%/HH% go in as spec dicts (supported API). Multi-panel ghost-line figure = **CM-1b** (non-breaking generalization: consumes CM-1 frames, adds named comps) |
| Attack regions (heart/shadow/chase/waste) | UC22 `tag_regions` (OZ, ±0.25 ft) | **Inherit by IX-1** (UC22 is a script that parses argv at import) |
| Run value per pitch | K47 convention (`delta_run_exp`, batting side +) | Inherit the convention |
| Chase cost | **0 hits** | **New, provisional CC-1** |
| Turn test | **0 hits** (DB-1 is decline-or-blip for pitchers) | **New, provisional TR-1** on PA-1 |
| Expected outs, client method | `Baseball Functions.ipynb` `find_similar_hits` | **XO-1 = IX-1 extraction** (client-authored) |
| Expected outs, governed | UC4 has run-value proxies only, no catch probability | **New, provisional XO-2** (sector-based opportunities) |

## Pre-registered: TR-1 "the June turn" ledger (bars set 2026-10-20 23:18 ET)
Windows: **pre** 2026-03-26 → 05-31 · **post** 06-01 → 09-27 · regular season only. Each signature is scored with PA-1 (`signature_verdict`). Proportions pass `two_prop_z` p to PA-1; wOBA/xwOBA/BA/SLG run without a test.
| Sig | Family | Metric | Direction | Bar |
|---|---|---|---|---|
| R1 | results | wOBA (house) | + | .030 |
| R2 | results | BA | + | .030 |
| R3 | results | OBP | + | .030 |
| R4 | results | SLG | + | .040 |
| P1 | process | xwOBA (XW-1) | + | .025 |
| P2 | process | K% | − | .030 |
| P3 | process | BB% | + | .015 |
| P4 | process | chase rate | − | .030 |
| P5 | process | hard-hit rate | + | .040 |
| P6 | process | whiff rate | − | .030 |

**Rule:**
- results SUPPORTED/STRONG and process SUPPORTED/STRONG → **EARNED TURN**
- results only → **RESULTS TURN** (not earned)
- process only → **PROCESS TURN** (results lag)
- neither → **NO TURN**

**Robustness, reported beside the verdict:** the RC-5 breakpoint scan on the 1st and 15th of each month (04-15 → 09-01), and sign stability across 05-15 / 06-01 / 06-15.

## Product types explored
| # | Form | The part of the story it owns | Bid |
|---|---|---|---|
| P1 | PDF recap report (≤10 pp, 9 sections) | All six questions, HP grades, caveats | **Build (hero)** |
| P2 | Interactive dashboard (≤8 chapters) + Artifact | Cumulative lines, chase map, spray, CF opportunity map with hover | **Build** |
| P3 | Player-facing development card | "Three things for 2027", scoped per UC34 privacy ruling | **Folded into report §6 / dashboard ch. 6 as a scoped panel**; not a separate form |
| P4 | 2027 projection | Bounce-back odds | **Not bid**: no projection model in the house |
| P5 | Video clips (chases, CF misreads) | | **Not bid**: out of profile; clip tooling exists (`kr3_clip_acquisition.py`), priced for v1.1 |

## Scope tiers
Comparison profile cap for every tier: report ≤10 pp / ≤9 sections · dashboard ≤8 chapters · ≤10 figures · ≤3 new KPIs.

**Tier A — Comparison profile (recommended, AWARDED).**
- **Report, 9 sections:**
  1. Bottom line
  2. The rookie line (Q1)
  3. The June turn (Q2)
  4. The approach (Q3)
  5. Ground balls (Q6)
  6. Where the walks are (Q4: CC-1)
  7. Righty spin (Q4: the client's breaking-ball study, cleaned)
  8. Centre field (Q5)
  9. Your notebook graded + caveats
- **10 figures:**
  - F1: cumulative BA / OPS / wOBA vs Phillies CF seasons (3-panel ghost lines, CM-1b)
  - F2: rolling 100-PA wOBA vs xwOBA with June 1 and the breakpoint scan
  - F3: TR-1 ledger (dumbbell)
  - F4: percentile profile vs Phillies hitter-seasons (Savant-style beads)
  - F5: swing/take by attack region vs the house
  - F6: cumulative GB% and HH% vs CF seasons
  - F7: chase map vs RHP by pitch group (cleaner version of the client's mean-location scatter) + CC-1 cost
  - F8: RHP breaking balls, EV by pitch type AAA 2025 vs MLB 2026 plus hit locations (cleaner version of the client's box and pitch map)
  - F9: spray chart on a drawn field, AAA vs MLB (cleaner version of the client's spray)
  - F10: CF opportunity map + running outs vs expected (XO-2), with CI-2 OAA beside it
- **New KPIs (3):** TR-1 · CC-1 · XO-2.

**Tier B — Tier A + extras (≈ +90k, +7 min).** A separate player development card (PDF), a postseason ledger page, and a Derek Hill platoon-deployment page (PL-1 rerun on the full season). Breaks comparability (+2 pages, +2 figures).

**Tier C — Lean (≈ −150k, −12 min).** PDF only; 6 figures (drops F3, F5, F7, F9); TR-1 only.

**Deferred: priced, not built:** player card (~35k) · Hill deployment page (~20k; PL-1 re-run is cheap, but the narrative isn't) · MLB-wide context (not bid: house population rule) · clips (~40k).

## Deliverables bid (Tier A)
| # | Deliverable | Notes |
|---|---|---|
| 1 | `dp_uc54_crawford_2026_recap_report.pdf` (+ `.md`) | ≤10 pp, 9 sections |
| 2 | `dp_uc54_crawford_2026_dashboard.html` (+ `_artifact.html`) + Artifact | ≤8 chapters; plotly via `phillies_dp.render.plotly_script_tag()` |
| 3 | `dp_uc54_kernel.py`, `_crawford_recap.py`, `_hp.py`, `_build_figs.py`, `_narrative.py`, `_build_dashboard.py`, `_build_report.py`, `_build_pdf.py`, `_verification.py` | Control-plane folder; MLB kernels imported by path, sha-pinned |
| 4 | `out/dp_uc54_*`: CSVs, fig JSON+PNG, `headlines.json`, `dq_scorecard.csv`, `verification_log.csv`, `hp_grades.csv` | Every narrative number comes from `headlines.json` |
| 5 | Receipts `00`–`07`, README, this BID, contract, ledger patch | Control-plane folder (contract + ledger patch copies at MLB root) |

**Explicitly not bid:** fielding metrics we do not have (OAA, catch probability, jumps; CI-2/CI-3 shown labelled) · any rate blending AAA and MLB · postseason in any rate · MLB-wide ranks · causal claims about platooning · medical inference (none known).

## Price (Tier A)
**Basis:** UC53 Alvarado actuals (≈518k, 41 min), adjusted by the house calibration rules:
- **C-2:** T1 −15k · T5 −10k · T6 −10k · contingency 5%.
- **C-4:** single turn, no second T0.
- **C-5:** kernel reads in T0.
- **C-6:** D ~13k.

**Up** for: the first pos-side recap shape, two new families (CC-1 and XO-2 with a neighbour search), the AAA supporting tier, 14 HP rows, and three "cleaner version of the client's plot" rebuilds that need a drawn field and strike zones. **Down** for: one season (not six), and inherited cumulative, rolling and breakpoint machinery.

| Phase | Tokens in | Tokens out | Minutes |
|---|---|---|---|
| T0 Intake, two-repo recon, house format, carry-ins, env, data profile, Rule-1 (**sunk: 277.7k at C2, gross**) + filing this BID | ~278k | ~12k | 13 |
| T1 Kernel + build + HP reproduction + EDA to file | 68k | 17k | 9 |
| T2 Figures (10) + dataviz skill + brand + render QA | 46k | 14k | 7 |
| T3 Dashboard (8 chapters) + headless QA + Artifact | 33k | 12k | 5 |
| T4 Report + PDF (narrative module) | 8k | 6k | 2 |
| T5 Verification harness (families A–G + TR-1/CC-1/XO-2) | 21k | 9k | 4 |
| T6 Governance 00–07, README, contract, ledger patch | 27k | 18k | 6 |
| D Defect discovery | 10k | 3k | 2 |
| Contingency 5% (on unsunk work) | 12k | 4k | 2 |
| **BID** | **~503k** | **~95k** | **~50 min** |

**Total ≈ 598k**, against 518k (UC53) / 469k / 530k / 545k / 681k for the recap set.
- **Time cross-check:** 0.10 min per 1k × 0.7 (device build) × 598k ≈ 42 min. We bid 50 because this is the first pos recap on device, with a neighbour search in T1.
- **Token credits** at list ($10/M in, $50/M out) ≈ **$9.80**, band **$8.30–11.30** (±15%). Cowork bills subscription usage; read this as API-equivalent value.

### Competitive position
A rival agentic org without this repo would have to re-derive several things:
- the house wOBA weights and the D1–D6 `_fix` lineage
- the CF context pool
- the attack-region geometry
- the cumulative module, with its endpoint reconciliation

It would also meet ENT-2 (the wrong Crawford), SRC-1/2/3 and DEF-3 the hard way, and could not grade the client's notebook on the client's own frame. Our estimate of that rival bid is **~1.0–1.2M tokens and 65–80 min** (+350k re-derivation, +100k defect loops, +50k pos-shape discovery), with no 00–07 trail and no independent harness. Our differentiators:
1. Pinned inheritance, so the numbers reconcile with UC34's August read.
2. A pre-registered turn test, not a narrative fitted to a chosen date.
3. Client claims graded, never overwritten.
4. A public bid-vs-actual history (UC48–UC53 within −28% to +5%).

## Assumptions, exclusions, carry-ins
- Regular season for every rate; the Wild Card goes in its own ledger line.
- Entity lock by MLBAM 702222 + batting role. Names are used only to reproduce the client frame.
- Population claims: the house hitter population is Phillies hitter-seasons 2015–26 with ≥50 PA (K40 pool, UC34 precedent); the CF context pool is CX-1. Rank and n are printed with every superlative.
- The AAA 2025 tier is labelled at every use. AAA tracking-dependent stats (EV, LA, xwOBA) are reported with their own tracked-n and never compared as levels to MLB without the caveat.
- Carry-ins CI-1 to CI-5 are labelled at every use and never computed on.
