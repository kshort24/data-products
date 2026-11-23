# 00 · DPO Orchestration Record: `uc-pos-026-bohm-career-retrospective-001`

**UC #67 · contract `uc-pos-026` · build `dp_uc67` · v1.0.0 · delivered 2026-11-22 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short · Parent: uc-pos-013 (UC #38, `dp_uc37`)
Status: **READY-CONDITIONAL (C1–C7)** · harness **51 / 51** · DQ **11 PASS / 0 WARN / 0 FAIL** · visual audit **8 / 8** figures
Run: single session. The RFP said to treat the bid as won, so the BID was filed (13:30 ET) and awarded by rule, and the build continued without a stop. Scouting-report skill loaded at T0.

---

## 1 · The ask and how we framed it
One message: the client's notebook markdown (a Bohm 2026 recap that "morphs into a career retrospective", a continuation of uc-pos-013, written on the assumption he does not return; line drives, platoon, RHP breaking balls, luck; an LD spray chart *if* the LD angle is good, in the house field-outline style; run creation, RISP and the game-winning-runs cell) plus the standing RFP.

The organization read it as **five jobs**:
1. **Score the parent out of sample.** uc-pos-013 called the post-break surge "real and process-backed" on data to 2026-08-22. PR-1 H-F filed five signatures before anything after that date was computed.
2. **Let a rule decide the client's angle.** "If the line-drive deficiency is a good angle" became H-LD plus a pool relevance gate (G-LD), filed before either was computed. The gate failed; the spray chart moved to the dashboard as context, as the rule said.
3. **Grade the client and ourselves.** Eight notebook comments became HP-01..HP-08 with bars; HP-09 grades our own parent's career table.
4. **Give the client's favourite stat a governed definition.** The game-winning-runs cell became GW-1 (deciding run), computed for every Phillies win since 2015 so Bohm's count has a population.
5. **Close the career honestly.** RISP results are the best of his era; RS-1 says they are not a repeatable split. Both ship.

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 8 gaps, 0 blocking (`01` §2) |
| | `source-system-profiler` | id-locked frame 13,126 regular-season pitches 2020–26; 12 non-regular cells receipted and excluded |
| | `domain-steward-proxy` | 6 carry-ins (CI-1..CI-6); free agency confirmed (no qualifying offer) |
| | `business-glossary-agent` | GW-1, XC-1, G-LD, RS-1, W-3 windows, TP-1, runs on watch (scoped) |
| Engineering Design | `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier` | subject + pool + game-table model; EDA to file; GW-1 join asserted one-per-win; 8-tab spec + season inspector |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | Rule-1 table; specs in the BID before code; 4 new pins over the 23-pin K61 chain; privacy CLEAR internal; v1.0.0 |
| Engineering Build | `data-engineer` | 9 scripts in the MLB root; 43 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | DQ 11/0/0; harness 51/51 (families A–F); TP-1 found by family A |
| Consumer Success | `consumer-onboarding-agent` · `analytics-enabler` · `query-builder` | reading paths, personas, GW-1 snippet, FAQ (`06`) |
| Platform & Marketing | `cost-watchdog` · `token-economist` · `data-observability` | tripwires, cost, bid vs actual, calibration (`07`) |

**Not engaged:** `machine-learning-engineer` (nothing forecast; PR-1 grades the past) · `semantic-modeler` beyond the GW-1 / XC-1 specs. No Artifact was published (not requested; offered in the reply).

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 664761; name used only to reproduce the client cell |
| G2 · Rule-1 search before declaring anything new | PASS: `03` §0 (GW-1, XC-1, G-LD, RS-1, TP-1 new; 12 found and inherited) |
| G3 · Locked KPIs inherited, not re-derived | PASS: `dp_uc61_kernel` (23-pin chain) + K48 + K62 + parent K37, frozen in `dp_uc67_pins.json` at 13:32:24, after the BID |
| G4 · No inherited file edited | PASS: TP-1 is a frame rule in `dp_uc67_kernel.load_house`, not an edit to K57 `NON_PA` |
| G5 · Small samples print denominators | PASS: every window, cell and RISP figure prints PA; post-audit = 120 PA, its breaking cell 25 PA |
| G6 · Superlatives name their population | PASS: "of 220 Phillies hitter-seasons 2015–26 (≥50 PA)", "of 11 Phillies regulars 2020–26 (≥1,000 PA)", "122 hitter-seasons ≥200 PA" |
| G7 · Carry-ins labelled, never computed on | PASS: CI-1..CI-6; RBI appears only as a carry-in (harness F) |
| G8 · Pre-registration is not prediction | PASS: H-F grades 8/24–9/27 against the audited window; nothing forecast. Disclosure: 4 of 11 signatures client-seen |
| G9 · Every published number reconciles to a receipt | PASS: one narrative module; harness E (20 checks) |
| G10 · Client claims graded, not overwritten | PASS: 9 HP rows (8 client, 1 parent) |
| G11 · Anchor pinned | PASS: 2026-10-01 (last regular game 2026-09-27) |
| G12 · No medical inference | PASS: harness F regex |

## 4 · Capability fulfilment
| Asked for | Delivered as | Where |
|---|---|---|
| 2026 recap continuing uc-pos-013 | §1 of the report: three windows, PR-1 H-F, F2 | report §1; dashboard "The 2026 finish" |
| 2026 against his Phillies career | season panel 2020–26 + KP-1 ranks + F1 | report §2 |
| Career retrospective, assuming he leaves | §5–§6, F7/F8, carry-ins CI-2/CI-3 | report §5–6 |
| LD angle, and the spray chart if it is good | H-LD + G-LD; **angle not good** by the filed rule → spray chart in the house outline ships as context in the dashboard; the report says why | report §3; dashboard "The line-drive question" |
| Run creation and RISP | runs on watch, GW-1 leaderboard, RISP by season, RS-1 | report §5 |
| Game-winning-runs cell | HP-01 reproduces it exactly; GW-1 governs it | `03` §2 |
| Receipts `00`–`07`, bid with tokens and time | this folder; `BID_…`, actuals in `07` §5 | here |
| Scouting-report voice | bottom line first, data-window box, PA on small lines, caveats last | report |

## 5 · The finding, in the DPO's words
Alec Bohm leaves as an average bat with an elite contact profile and the best run-scoring results of any Phillies regular of his era. uc-pos-013's surge did not survive September in the results: wOBA went .374 → .323 and the in-zone whiff came back (6.8% → 15.3%). But the contact quality held and rose: hard-hit 46.9% → 50.0%. The registered call is **"it held in the contact, not in the results."** 2026 finished at .308 wOBA, the Phillies median (110 of 220 hitter-seasons), and the season was lost in April. The line-drive dip was real (24.8%, his lowest of seven seasons), but LD share explains 0.7% of a Phillie's wOBA, so it is not the story. The righty problem was results, not contact: wOBA vs RHP breaking .301 → .237 with xwOBA flat. He drove the deciding run in 63 Phillies wins, second to Schwarber's 69, and his BA with runners in scoring position (.314) leads every Phillies regular since 2020. RS-1 says that last number is results, not a repeatable split.

## 6 · Where the organization argued with itself
**Should the spray chart lead the LD chapter anyway?** `product-narrator` argued the client asked for it and the picture is good. `kpi-calculator` pointed at the filed rule: H-LD SUPPORTED, G-LD failed (R² .007 vs .05). **Resolution:** the rule wins. The chart ships, in the house outline, as dashboard context. The report names the gate result and points to it.

**Was REC-1 a scoring change?** At T1 the slash line missed the public line by .002 on all three rates. `data-engineer` restated the rule as "+1 hit, official-scorer change" and it passed. `certification-agent` refused to certify on a restated rule, and the harness found the real cause. Three `truncated_pa` rows were being counted as PA and AB (TP-1). **Resolution:** TP-1 frame rule, REC-1 restored to its original exact rule and passing. The T1 diagnosis is withdrawn in `05` §4 and `07` §6.

**Does GW-1 flatter him?** `domain-steward-proxy` noted that any batter credited with the go-ahead run gets GW-1 even on an out (6 of 63) or an error (1). **Resolution:** the mechanism ships beside the count, and the count is ranked only against a population built with the same rule.

## 7 · Escalations to the human DPO
1. **E-1 · Ratify** GW-1, XC-1, G-LD and RS-1 (first use). Recommend GW-1 into the next pos kernel with the population as a parameter.
2. **E-2 · TP-1 (new, house-wide).** K57 `NON_PA` omits Statcast `truncated_pa`: 65 rows in the 2024–26 Phillies log are counted as PA/AB (both roles). Statcast introduced the event in 2024, so governed 2024–26 lines that include those rows can move at the third decimal (Bohm 2026: .247 → .249 BA). Recommend adding `truncated_pa` to `NON_PA` as a **breaking** change (`version-controller`), with a sweep of published lines.
3. **E-3 · Parent defects (uc-pos-013).** Its career table mixed postseason PA into 2022–25 (HP-09), and its pre-break window carries 3 TP-1 phantom PA (374 governed vs 377 printed). Its headline is unaffected (post-break window has none). Recommend a v1.0.1 errata note on uc-pos-013.
4. **E-4 · Withdrawn BID claim.** The BID's competitive section claimed the client's pitch-grain cell would credit mid-PA runs. For Bohm it never does (HP-01: 63 = 63). Withdrawn.
5. **E-5 · ENV-3 recurrence.** pip on the laptop VM still needs `TMPDIR` off the full `/sessions` volume (100% full). Fourth recurrence; add to the MLB `CLAUDE.md` setup line.
6. **E-6 · Ledger.** `uc_ledger_AI_PATCH_uc-pos-026-bohm-career-retrospective.md` is a **pending paste** (copies here and at the MLB root). UC52–UC66 patches are still pending.
7. **E-7 · Decision ownership.** No contract, market or roster recommendation is made. The departure is the client's assumption plus public carry-ins.
8. **E-8 · Commit.** Not made; not requested.

## 8 · Publish recommendation
**READY-CONDITIONAL. Internal audience (front office, hitting department, pro scouting).**
- **C1** Ranks are Phillies-frame (2015–26), never MLB-wide; populations named on every superlative.
- **C2** Carry-ins are reported facts, never computed on. RBI, OPS+, WAR and salary are carry-ins only.
- **C3** GW-1, XC-1, G-LD and RS-1 are provisional (first use). Changing a PR-1 bar is breaking.
- **C4** After-the-audit window = 120 PA; its breaking-ball cell = 25 PA. Read direction, not decimals.
- **C5** TP-1 is applied in this build only; inherited house numbers elsewhere still count `truncated_pa` (E-2).
- **C6** 4 of 11 PR-1 signatures were client-seen (disclosed in the BID).
- **C7** HP-03's grade is sensitive to TP-1: NOT CONFIRMED before the fix, PARTLY after (vs-LHP wOBA .3505 → .3524 against a .3510 bar).

External publication: after DPO review of C5 (it touches every published house slash line).
