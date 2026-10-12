# 00 · DPO Orchestration Record: `uc-pps-035-wheeler-2026-recap-001`

**UC #51 · contract `uc-pps-035` · build `dp_uc51` · v1.0.0 · delivered 2026-10-12 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **204 / 204** · DQ **26 PASS / 4 WARN / 0 FAIL** · brand 13 / 13 figures pass

---

## 1 · The ask and how we framed it

`October 2026.ipynb` cells 16 and 21–23. Cell 16 holds the thesis in one line: *"One more year left on his deal, he started to show some signs of slowing down in the second half but for now he is still Zack Wheeler."* Cell 21 lists the KPIs (tied-up rate, pitch map, pitch plot, wOBA/OPS/K%/BB%, HH%/barrel/LD, edge rate, xwOBA .263), the code that builds them, and three claims: the walk rate was a Phillies-tenure high (7.6%) and the theme of August; the contact numbers are noise; lefties did more damage. Cell 23 is the jam-rate development that became the library's `jam_rate` on 10/9. Instruction: recap the season, use prior work where it helps, stand alone.

The organization read it as **four jobs**:

1. **Test the thesis, both halves.** "Still Zack Wheeler" needed a population and a rank (CX-1b: #6 of 41 starter seasons, six of the top ten his). "Slowing down in the second half" needed a decomposition: the second half is one six-start slide plus a strong finish, and the slowing is a multi-year velocity trend, not an in-season one.
2. **Find the slide by reconciliation, not by eye.** Reporting gave a number (8.51 ERA over six post-break starts). Exactly one six-start window in the log reproduces it (DQ-30). That window, not "August", is the unit of analysis.
3. **Say what the log can and cannot see about the reported cause.** The reported fix was mechanical (glove, rotation). The log shows release point (unchanged) and miss direction (arm side during the slide, back after). It cannot show a glove.
4. **Reproduce the parent and the client before improving either.** `uc-pps-020`'s six first-half figures were recomputed (6/6). Every client claim and chart choice is graded beside its governed value (HP-01…HP-18).

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 8 gaps (2 blocking, resolved: "slowing down" metric, the stretch window); graded 18 client items |
| | `source-system-profiler` | Id scan: Wheeler's pitches in **24** opponent files; `lhvp26.parquet` carries **148 AAA rehab pitches tagged `R`** (MI-1). wheeler.parquet holds Mets 2017–19 only |
| | `domain-steward-proxy` | 6 carry-ins researched (injury/surgery, extension, season line, the slide and its reported cause, Game 162, WC G3) |
| | `business-glossary-agent` | "Tied-up rate" adopted over "jam rate" (client); ST-1 centered/flail named; "the slide" defined by SR-2; "runs on watch" inherited |
| Engineering Design | `data-architect` | One pitch-grain frame (CF-2b) + the full defensive log for outs; every table a groupby |
| | `eda-agent` | Found the slide, the arm-side miss shift, the in-zone collapse, the flat edge rate, the platoon contact gap, the 8.51 window |
| | `join-validator` | Enrichment join is 1:1 on (pitcher, pitch key); DQ-09/10/11 |
| | `metadata-mapper` | `player_name` is the batter in `pos` and batter-keyed pulls → the client's jam population mixes roles (HP-13) |
| | `dashboard-specifier` | Eight chapters, start drill (select + click-through from the slide chart), theme bar (`02` §5) |
| Governance | `kpi-calculator` | CF-2b, OU-2, GS-1b, ST-1, NC-1, MX-1, SR-2, IX-1 specified (`03` §2) |
| | `technical-lineage-builder` | Column-level lineage for every published number (`03` §3) |
| | `privacy-watchdog` / `data-tagger` | Public performance data; the 2025 surgery named only as reported. Tagged **Internal** |
| | `version-controller` | v1.0.0; anchor 2026-09-27 + WC; card registered 2026-10-12 |
| Engineering Build | `data-engineer` | Kernel + build + harness on the laptop VM; render in the cloud from receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 30 rules, 0 FAIL, 4 designed WARNs |
| | `certification-agent` | Harness A–G, 204 checks, independent code path |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` / `product-narrator` | Reader paths, dashboard walkthrough, the report |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, calibration, tripwires |

**Not engaged:** `machine-learning-engineer` (no model), `semantic-modeler` (no cross-UC metric layer change), `data-observability` (point-in-time recap; tripwires in `07`).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id, MLB games only | **PASS**: 554430; 148 AAA rows excluded (DQ-06). The name filter is used only to reproduce the client's frames |
| G2 · Rule-1 search before declaring anything new | **PASS**: edge rate (UC8), jam rate (library), xwOBA (UC50 XW-1), release consistency (UC28), October card (UC49), recap (SR-1) all found and inherited. New: OU-2, ST-1, NC-1, MX-1, SR-2, IX-1 |
| G3 · Locked KPIs inherited, not re-derived | **PASS**: 5 modules sha256-pinned by import; 6 segments sha256-pinned by IX-1 extraction (`lineage_pins.csv`) |
| G4 · No re-derivation of existing work | **PASS**: `uc-pps-020` first-half figures recomputed 6/6; OC-1 used verbatim (second use) |
| G5 · Small samples print denominators | **PASS**: the slide (6 starts, 119 PA), the opener (1 start), WC G3 (17 PA), arm angle (n published) |
| G6 · Superlatives name their population | **PASS**: every rank names "Phillies pitcher-seasons" and n; "highest/lowest of his Phillies years" names the seven seasons |
| G7 · Carry-ins labelled, sourced, never computed on | **PASS**: 6 carry-in sources in the freshness manifest; harness G (15 checks) |
| G8 · Windows identified by reconciliation, not selection | **PASS**: SR-2 window is the unique 8.51 match (DQ-30, harness D) |
| G9 · Every published number reconciles to a receipt | **PASS**: harness F, 45 report/dashboard strings |
| G10 · Client claims graded, not overwritten | **PASS**: 18 HP rows with the client's words beside the governed value |
| G11 · Anchor pinned | **PASS**: build refuses any regular-season anchor other than 2026-09-27 |
| G12 · No medical or mechanical inference | **PASS**: the log is described (release point, misses); the glove and the surgery appear only as reported; harness G bans causal language |

## 4 · Capability fulfilment

| Asked for | Delivered as | Where |
|---|---|---|
| "Recap his 2026 season" | Report (10 sections) + dashboard (8 chapters) | `dp_uc51_wheeler_2026_recap_report.pdf`, `dp_uc51_wheeler_2026_dashboard.html` |
| Tied-up rate | JR-1 (library) + ST-1 buckets + population board + sinker detail | figs 7–8, report §5 |
| Pitch map / pitch plot | PM-1 centroids by side; movement plot with means | figs 10–11 |
| Top-level results | SR-1-style season table + small multiples | fig 2, report §1 |
| Contact quality | HH / barrel / LD vs his baseline, with tests | fig 6, `rate_tests.csv` |
| Edge rate, zone expansion | ER-1 (UC8) + in-zone/chase; Savant 42.4% reconciled as a definition difference | fig 3, report §3, HP-06/07 |
| xwOBA .263 | XW-1 = .263; house percentile and starter rank | fig 1, HP-05 |
| Platoon splits | governed version of the client's scatter + tests | fig 9, report §6 |
| "Consider previous work" | `uc-pps-020` reproduced 6/6; OC-1 reused; edge/jam/xwOBA/RCI inherited | `parent_reproduction.csv`, `lineage_pins.csv` |
| PDF report | Branded weasyprint PDF, 16 pp | MLB root + this folder |
| Interactive dashboard | Offline HTML + published Artifact "Still Zack Wheeler" | MLB root + this folder |
| Receipts 00–07 + bid with token/time estimate | This folder | here |

## 5 · The finding, in the DPO's words

He is still Zack Wheeler: a .263 xwOBA, sixth of 41 Phillies starter seasons since 2015, and six of the top ten are his. The walk rate is real and it is one stretch. For six starts from late July to late August he walked 13% of hitters and allowed 8.51 runs per nine; his misses drifted to the arm side while his release point stayed put; then he walked 6% and allowed 1.67 runs per 27 outs the rest of the way. The bigger change was where he pitched. He threw the fewest pitches in the zone of his Phillies career and got the most chases, and the splitter became his second pitch. The slowing is real too, but it is across years (97.2 mph in 2021, 95.2 now), and the 2027 card writes down how far it can go before he stops being this pitcher.

## 6 · Where the organization argued with itself

**"August" or "the slide"?** `product-narrator` wanted the chapter called *August*. `eda-agent`: the reported 8.51 matches 7/27–8/24 only; the August month (6 starts, 8/2–8/30) gives 6.26. **Resolution:** the unit is the reconciled window; the dashboard calls it "the six-start slide" and the report prints all eight candidate windows.

**Is the arm-side miss shift a finding?** `certification-agent`: p = .033 on pitch-level counts that cluster within starts. `eda-agent`: it reverses after the slide (12% in the finish), which is the pattern the reported fix predicts. **Resolution:** published as "consistent with, cannot prove", with the clustering caveat in report §10. The walk rate (p = .004) is the firm result.

**Can we say anything about the glove?** `domain-steward-proxy` supplied the Inquirer quote. `privacy-watchdog` and `certification-agent` objected to any sentence that reads as confirmation. **Resolution:** the glove appears only as a tagged carry-in; harness G checks every glove sentence for a tag or a negation.

**OU-1 or OU-2?** The first build failed DQ-18: OU-1 (the UC49 event map) gave 480 outs against the published 162.0 IP. Six outs were base-running outs on singles, a walk and a force play. **Resolution:** OU-2 (outs sequence of the full defensive log) gives 486 exactly; GS-1b re-scores games on it; OU-1 is kept beside it in the receipts and flagged upstream (E-3).

**Edge rate: whose number?** The client quoted Savant's 42.4%; ER-1 gives 36.0%. `business-glossary-agent` declined to rename ER-1 "edge%". **Resolution:** ER-1 is published under its own name; 42.4% is a carry-in; the finding (edge did not move) holds on ER-1.

**Dark or light** (E-5, carried). Print follows the brand center; the dashboard matches the viewer's system and offers *Notebook dark*.

## 7 · Escalations to the human DPO

1. **E-1 · Ratify OC-1** (second clean use, unchanged code). Recommend ratification as a subject-agnostic "season card" with a `reference_window` parameter.
2. **E-2 · Fix CF-2 (`dp_uc49_kernel`, v1.0.1)**: (a) **MI-1** it admits minor-league games through `lhvp26` and any other pitcher-keyed AAA pull; (b) **NM-1** it stamps UC49's `SUBJECT_NAME` on every frame. CF-2b carries both fixes; promote it.
3. **E-3 · Retire OU-1 for innings** (`dp_uc49_kernel`). It misses outs on base-running plays (6 of 486 for Wheeler). Back-check uc-pps-034's Game Score ranks under OU-2 (Labor Day stays 27 outs; other starts may move by 2 GS points per missed out).
4. **E-4 · IX-1 as a house mechanism.** Source-pinned extraction let this build inherit `edge_rate` from a build script and `jam_rate` from the notebook without running either. Recommend moving ER-1, JR-1 and RCI into a kernel so the next UC can import them.
5. **E-5 · Brand standard** (carried).
6. **E-6 · Ledger.** Rows #25–#51 are pending pastes into `uc_ledger_AI.md`.
7. **E-7 · ST-1 flail boundary.** 41 in is the client's histogram line. Confirm or replace before ST-1 is ratified.
8. **E-8 · Contract-value board (P8).** Needs salary and WAR sources; proposed as a follow-on.

## 8 · Publish recommendation

**READY-CONDITIONAL. Internal: pitching department, front office, broadcast/content.**

- **C1** Ranks and percentiles are Phillies-frame (2015–2026), not MLB-wide.
- **C2** Carry-ins (2025 injury and surgery, extension, season line, the slide's ERA and reported cause, WC box) are reported facts, never computed on.
- **C3** The mechanical story is not modeled. Report §4 and dashboard chapter 4 stay descriptive.
- **C4** The Still-Wheeler card is a definition registered 2026-10-12; it grades 2027 in v1.1.0 and predicts nothing.
- **C5** Tied-up rate is a public-data proxy; centered/flail (ST-1) are provisional.
- **C6** New objects are provisional; OC-1 is recommended for ratification.

External publication: permissible after DPO review (public performance data; other Phillies pitchers appear as context points named in hovers; no other club's players are ranked).
