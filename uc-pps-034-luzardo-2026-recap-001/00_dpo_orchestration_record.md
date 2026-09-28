# 00 · DPO Orchestration Record: `uc-pps-034-luzardo-2026-recap-001`

**UC #49 · contract `uc-pps-034` · build `dp_uc49` · v1.0.0 · delivered 2026-09-27 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **226 / 226** · DQ **21 PASS / 2 WARN / 0 FAIL** · brand 9 / 9 figures pass

---

## 1 · The ask and how we framed it

Two cells in `September 2026.ipynb`. Cell 118 is the analysis: a 14-KPI career recap, three scatters over *Phillies pitcher-seasons, min 150 pitches* (whiff × chase, the same by handedness, walk rate × in-zone rate with an OLS trendline) and a 2026 pitch map. Cell 51 is the narrative: the Labor Day shutout, the first All-Star selection, the extension, and a thesis, *"2026 could be the season to celebrate, forever … For Jesús Luzardo, it could be."* The instructions: let the narrative drive the use case, explore **different types of data products** that could tell it, keep it about storytelling rather than business, keep it grounded, and govern the visuals.

The organization read it as **four jobs**:

1. **Find the spine in the data before writing a word.** The spine turned out to be the notebook's own first comment: *he does not need to be in the strike zone.* It is the one 2025 → 2026 change that is statistically settled (in-zone 50.5% → 46.5%, p = 0.002), and it leads to a finding stronger than the client asked for: the highest whiff rate of any Phillies starter season since 2015 (CX-1b).
2. **Scope product forms against the story, not the other way round.** Eight forms were scoped (BID, "Product types explored"). Each had to own a part of the story no other form could tell. Seven were built; the Dombrowski acquisitions board was not, because "acquired by" cannot be keyed from either repo.
3. **Make the ending falsifiable.** A recap cannot know October. It can register, before October, what a *defining* October would look like in this pitcher's own data (OC-1), and publish its own calibration so nobody reads it as a prediction.
4. **Reproduce the parent before improving it.** The client's frame, scatters and pitch map were rebuilt by his method and by the governed one; every difference is explained (HP-01…HP-13). `uc-pps-017`'s published first-half figures were recomputed 4/4 before anything new was layered on.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 7 gaps (2 blocking, resolved from the repo and carry-in research); graded 13 client claims/chart choices |
| | `source-system-profiler` | Id-column scan of all 128 opponent files: Luzardo's pitches sit in **21**, not the 1 a name filter sees. Found the `nphl` keep-first dedup trap (O-26) and the byte-search defect (BS-1) |
| | `domain-steward-proxy` | Researched 7 carry-ins (trade, extension, All-Star, Labor Day box, Pitcher of the Month, scratch/IL, Game 162). One superseded the prompt's premise: the season stopped on 9/7 |
| | `business-glossary-agent` | Glossed "runs on watch" (house `runs_created`, not ERA), "starter workload", "on-script"; kept Game Score as *GS-1, log-derived* to avoid colliding with the published stat |
| Engineering Design | `data-architect` | One pitch-grain career frame (CF-2) with a four-source precedence dedup; every table a groupby of it |
| | `eda-agent` | Found the in-zone drop, the starter-workload whiff #1, the second-half turn, the Labor Day changeup spike, the 8/26 velocity dip |
| | `join-validator` | Only merges are 1:1 on level keys; the harness rebuilds the frame without the kernel |
| | `metadata-mapper` | `player_name` is the batter in batter-keyed pulls → entity lock by id only |
| | `dashboard-specifier` | Eight chapters, drill-through, pitch-by-pitch stepper, October card, theme toggle (`02` §5) |
| Governance | `kpi-calculator` | CF-2, CX-1/1b, GS-1, OU-1, VB-1, OC-1, NF-1, BN-1, US-1b specified before code (`03` §2) |
| | `technical-lineage-builder` | Column-level lineage for every published number (`03` §3) |
| | `privacy-watchdog` / `data-tagger` | Public performance data; carry-ins are published reporting. The shoulder is named only as reported, never modeled. Tagged **Internal** |
| | `version-controller` | v1.0.0; anchor-pinned 2026-09-26; OC-1 registered 2026-09-27 |
| Engineering Build | `data-engineer` | Kernel + build run **on the laptop VM** (first time: pyarrow/scipy/plotly installed to `/tmp`); 40 CSV/JSON receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 23 rules, 0 FAIL, 2 designed WARNs |
| | `certification-agent` | Harness A–G, 226 checks, independent code path |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | Reader paths, dashboard walkthrough, the narrative |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, calibration, tripwires |

**Not engaged:** `machine-learning-engineer` (no model), `semantic-modeler` (no cross-UC metric layer), `data-observability` (point-in-time recap; tripwires in `07`).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | **PASS**: 666200. The accented name filter is used only to reproduce the client frame (HP-08) |
| G2 · Rule-1 search before declaring anything new | **PASS**: Game Score, first-N velocity, October card, starter-workload cut: 0 hits. `edge_rate` found (UC8) → the client's unfinished function is redirected (HP-13). `season_recap` found (UC48) → **second use** |
| G3 · Locked KPIs inherited, not re-derived | **PASS**: `dp_uc48_kernel` imported (sha256 `0f63857a…`), `dp_uc44_kernel` through it (`a2c11909…`); both asserted at build and in the harness |
| G4 · No re-derivation of existing work | **PASS**: `uc-pps-017` first-half figures recomputed and matched 4/4 instead of redone; its sweeper-first finding is cited, not rediscovered |
| G5 · Small samples print denominators | **PASS**: 2019 (46 PA) and 2024 (274 PA) flagged; postseason lines print outs, H, R, BB, K; the changeup spike prints its 8 pitches |
| G6 · Superlatives name their population | **PASS**: every rank carries "Phillies pitcher-seasons 2015–2026" and its n; "best starter" carries the ≥2,000-pitch cut and its sensitivity (1,500 / 2,500) |
| G7 · Carry-ins labelled, sourced, never computed on | **PASS**: 7 carry-ins in the freshness manifest; harness G |
| G8 · Pre-registration is not prediction | **PASS**: OC-1 publishes its backtest (off-script starts allowed fewer runs) in the report, the dashboard and `05` |
| G9 · Every published number reconciles to a receipt | **PASS**: family F, 96 report/dashboard assertions |
| G10 · Client claims graded, not overwritten | **PASS**: 13 HP rows keep the client's words beside the governed value |
| G11 · Anchor pinned | **PASS**: the build refuses any regular-season anchor other than 2026-09-26 |
| G12 · No medical inference | **PASS**: chapter 7 / report §6 state what the log shows (velocity, workload) and stop; harness G checks the language |

## 4 · Capability fulfilment

| Asked for | Delivered as | Where |
|---|---|---|
| "Let this narrative drive the use case" | Eight chapters, arrival → October, each anchored to one data finding | dashboard, report §1–8 |
| "Explore different types of data products" | 8 forms scoped, 7 built, 1 declined with reason | BID, dashboard appendix, `06` §1 |
| Well-labelled, curated, governed visuals | 9 figures; each asserts its subtitle before writing; PL-1 palette validated light + dark; brand 9/9 | `out/dp_uc49_fig*`, `05` §2 |
| The recap table (cell 118) | SR-1 second use, governed + notebook-exact, reconciled | `out/dp_uc49_recap_*.csv`, report §1 |
| "Better than most pitchers in my dataset" | Ranked in the client's population and a starter cut | CX-1/1b, report §2 |
| The command scatter | One OLS per handedness; the per-color defect named | HP-10, fig 2 |
| Pitch map | PM-1 unrounded centroids, usage within batter side | fig 7 |
| Receipts `00`–`07` + bid | This folder | here |

## 5 · The finding, in the DPO's words

The notebook had the thesis in its first comment and did not know how strong it was. Luzardo stopped needing the zone: fewer pitches in it than in any season since 2021, the most chases of his career, and no extra walks. Among every Phillies season with a starter's workload since 2015, nobody got more swings and misses. The second half was a different pitcher (1.87 runs on watch per 27 outs), and Labor Day was the best start of his career by fourteen Game Score points: hitters chased almost half of what he threw out of the zone, the four-seam was faster in the ninth, and the changeup appeared the second time through. Then the log goes quiet. The story's last chapter is not written yet, so the product writes down, in advance, what it would take for October to be his.

## 6 · Where the organization argued with itself

**"Most consistent" all over again.** `product-narrator` wanted the dek to read *"made hitters chase better than any Phillies pitcher."* `certification-agent`: he is #28 in chase across all pitcher-seasons and #8 among starters. The claim that survives is whiff among starters (#1, robust at 1,500 and 2,500 pitches). **Resolution:** the dek says *missed more bats than any Phillies starter of the Statcast era*, and the chase rank is printed as it is.

**"Lowest in-zone rate of his career."** The first dashboard draft said it. The harness family B found 2021 lower (45.5%). **Resolution:** "lowest since 2021" everywhere, and a family-F check that the phrase never returns.

**Should the October card exist?** `eda-agent` backtested it on his 29 starts and found the off-script starts allowed *fewer* runs. `data-product-owner` kept it, because the card was never meant to predict runs; it answers the narrative's real question (*is October Luzardo this season's Luzardo?*). **Resolution:** it ships as a *sameness card*, with the backtest printed beside it. A card that is only ever shown when it flatters is not evidence.

**The shoulder.** `domain-steward-proxy` supplied the IL facts; `eda-agent` found the 8/26 velocity dip (95.4). `privacy-watchdog` objected to placing the two side by side as cause and effect. **Resolution:** chapter 7 lists what the log shows, says in plain words that it does not show an injury, and harness G checks for causal language.

**Game Score's name.** `business-glossary-agent`: the published Game Score uses earned runs and official innings; ours uses event-coded outs and runs on watch. **Resolution:** GS-1, "Tango v2 form, log-derived", on first use and in every subtitle.

**Dark or light** (E-5, carried). Print follows the brand center; the dashboard matches the viewer's system and offers *Notebook dark*.

## 7 · Escalations to the human DPO

1. **E-1 · Ratify SR-1 `season_recap`.** Second clean use (cell 118 KPI set = SR-1's set + FPSR). Recommended for ratification with CF-2 as its frame loader.
2. **E-2 · Upstream fixes to `dp_uc48_kernel` (v1.0.1, non-breaking).** (a) US-1 `appearance_log` groups by `game_pk` twice; pandas 2.3 raises (ENV-1). (b) CF-1 hard-codes Bowlan's id/file; CF-2 generalizes it.
3. **E-3 · Fix O-26 in `mlb_data.get_nphillies_data()`?** Keep-first dedup across sorted files silently hands pitcher-keyed rows to batter-keyed files. For Luzardo it drops 230 regular-season pitches from any `nphl[player_name == …]` frame. Proposal: dedup with a pitcher-keyed-first precedence (breaking for any cached frame; version it).
4. **E-4 · Retire the byte search (BS-1).** It under-counts (2 files vs 21 by id). The back-check also **closes `uc-pps-033` V-3**: the notebook's ".269 / 60 G" for Bowlan is one Lehigh Valley appearance (2026-04-26, 16 pitches) that reaches the client frame through `lhvp26.parquet` in `nphl`.
5. **E-5 · Brand standard** (carried from uc-pps-032/033).
6. **E-6 · Ledger.** Rows #25–#49 are pending pastes into `uc_ledger_AI.md`.
7. **E-7 · PM-1 docstring** (`dp_uc44_kernel`) says `plate_x` + = third-base side. The data says + = first-base side (LHP arm-side FF pfx_x > 0; uc-pps-033 DQ-13 found RHP arm-side < 0). Numbers are unaffected; the text is wrong.
8. **E-8 · Acquisitions board (P8).** Needs a transaction source. Proposed as the next use case.

## 8 · Publish recommendation

**READY-CONDITIONAL. Internal: pitching department, front office, broadcast/content.**

- **C1** Ranks and percentiles are Phillies-frame (2015–2026), not MLB-wide.
- **C2** Carry-ins (trade, extension, All-Star, box time, Pitcher of the Month, IL, Game 162) are reported facts, never computed on.
- **C3** The shoulder is not modeled. Chapter 7 stays descriptive.
- **C4** OC-1 is a sameness card, registered 2026-09-27; it grades October in v1.1.0 and predicts nothing.
- **C5** GS-1 is log-derived and ranks his own starts; it is not the published Game Score.
- **C6** New objects are provisional; SR-1 is recommended for ratification.

External publication: permissible after DPO review (public performance data; other Phillies pitchers appear as context points, named in hovers and in the frontier receipt; no other club's players are ranked).
