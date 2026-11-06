# 00 · DPO Orchestration Record: `uc-pps-038-walker-phillies-career-recap-001`

**UC #62 · contract `uc-pps-038` · build `dp_uc62` · v1.0.0 · delivered 2026-11-05 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL (C1–C6)** · harness **47 / 47** · DQ **15 PASS / 0 WARN / 0 FAIL** · visual audit 9 / 9 figures
Run: single session. The RFP said to treat the bid as won, so the BID was filed (20:19 ET) and awarded by rule, and the build continued without a stop. Scouting-report skill loaded at T0.

---

## 1 · The ask and how we framed it
Turn 1: "Tell me the story of Tai Walker. A guy who the Phillies paid nearly $18 million to this season to pitch in Angels minor league system," with the client's code: Walker's MLB seasons against every Phillies pitcher-season since 2015, wOBA as a function of K%, his career overall highlighted. This session answered it ungoverned. Turn 2 (the RFP) asked for the governed package in the data plane, receipts `00`–`07` here, a competitive bid, a **PDF**, and an **interactive dashboard** if it made sense.

The organization read it as **four jobs**:
1. **Reconcile before writing.** Every public number the story leans on (innings, games, starts, homers, the $18M) is checked against the log or labelled a carry-in. The innings reconcile to the out.
2. **Turn the client's chart into a measure.** "wOBA as a function of K%" becomes KR-1, the distance from the Phillies line. That gap is what the contract paid for.
3. **Make the ending falsifiable.** PR-1: ten signatures in three families (stuff, luck, residual), filed before the unseen ones were computed, scored by the inherited PA-1 rule.
4. **Grade the parent, including ourselves.** The client's CSV and this session's own turn-1 claims are HP rows with bars. One turn-1 claim is withdrawn (CR-4) and one is graded PARTLY for the wrong mechanism (HP-06).

## 2 · Delivery plan (departments actually engaged)
| Layer | Agent / capability | What it did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 7 gaps, 0 blocking (`01` §2) |
| | `source-system-profiler` | id scan: `walker.parquet` + 662 rows in other files + 6,757 house rows; SRC-1 and O-26 surfaced |
| | `domain-steward-proxy` | 6 carry-ins, 2 conflicts resolved (4/22 bulk relief; Angels innings) |
| | `business-glossary-agent` | KR-1, CE-1, PR-1, luck gap, bulk relief, tenure, market years |
| Engineering Design | `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier` | CF-2d frame, pools, windows; EDA to file; OU-2 join reconciled; 8-tab spec + season inspector |
| Governance | `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` / `data-tagger` · `version-controller` | Rule-1 table; specs before code; 10-pin lineage; privacy CLEAR internal; v1.0.0 |
| Engineering Build | `data-engineer` | 9 scripts in the MLB root; 38 receipts in `out/` |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` · `certification-agent` | DQ 15/0/0; harness 47/47 (families A–F) |
| Consumer Success | `consumer-onboarding-agent` · `analytics-enabler` · `query-builder` | reading paths, persona notes, KR-1 snippet, FAQ (`06`) |
| Platform & Marketing | `cost-watchdog` · `token-economist` · `data-observability` | tripwires, cost, bid vs actual, calibration (`07`) |

**Not engaged:** `machine-learning-engineer` (no forecast; PR-1 grades the past) · `semantic-modeler` beyond the KR-1/CE-1 specs.

## 3 · Governance gate checks
| Gate | Result |
|---|---|
| G1 · Entity locked to MLBAM id | PASS: 592836; name used only to rebuild the client frame |
| G2 · Rule-1 search before declaring anything new | PASS: `03` §0 (KR-1, CE-1 new; 5 found and inherited) |
| G3 · Locked KPIs inherited, not re-derived | PASS: `dp_uc53_kernel` sha `03d7e380…` + chain (10 pins) |
| G4 · No re-derivation | PASS: nresults, whiff/chase, hard-hit, barrel, XW-1, WB-1, OU-2, GS-1, PA-1, arsenal, pools all imported |
| G5 · Small samples print denominators | PASS: 2026 = 115 PA on every 2026 line; < 100-PA seasons out of ranks and charts |
| G6 · Superlatives name their population | PASS: "of 198 Phillies pitcher-seasons (≥100 PA)", "of 199 Phillies pitchers", "among 18 Phillies splitter-seasons" |
| G7 · Carry-ins labelled, never computed on | PASS: CI-1..CI-6; DQ-06/07 reconcile to them |
| G8 · Pre-registration is not prediction | PASS: PR-1 grades 2023–26 against 2021–22; nothing forecast. Disclosure: 4 of 10 signatures were seen at T0 (client CSV) |
| G9 · Every published number reconciles to a receipt | PASS: one narrative module; harness E |
| G10 · Client claims graded, not overwritten | PASS: 7 HP rows |
| G11 · Anchor pinned | PASS: 2026-10-01 |
| G12 · No medical inference | PASS: harness F regex |

## 4 · Capability fulfilment
| Asked for | Delivered as | Where |
|---|---|---|
| "The story of Tai Walker" | 6-chapter PDF (8 pp) + 8-tab dashboard + Artifact "Taijuan Walker, Phillie" | MLB root; copies here |
| The client's chart with his career overall | F1 rebuilt on the governed pool with era totals; KR-1 | report §2; tab "What they bought" |
| $18M to pitch in the Angels system | CE-1 cost chapter + carry-in epilogue | report §5–6 |
| Governed package, receipts `00`–`07` | this folder | here |
| Bid with tokens and time | `BID_…`, actuals in `07` §5 | here |
| Dashboard "if it makes sense" | It did: the season inspector and tabs make 12 seasons × 15 KPIs navigable | MLB `dp_uc62_walker_phillies_career_dashboard.html` |
| Org-driven additions | PR-1 ledger; graded turn-1 claims; EV-1 defect; KR-1 reusable as a free-agent screen | `03` §4, `06` §3 |

## 5 · The finding, in the DPO's words
The Phillies bought a contact manager. In 2021–22 Walker allowed .296 wOBA at a 21.4% strikeout rate, .027 below what the Phillies line expects at that K%, and Statcast agreed it was mostly real contact quality, not luck. Over the contract the four-seamer lost 1.8 mph and then disappeared, the splitter's whiff rate fell from 28.2% to 21.6% (his 2023–25 splitters are the three lowest-whiff of 18 Phillies splitter-seasons since 2015), and contact got harder (xwOBA +.033). The favorable luck of the Mets years also went away, though his Phillies luck was ordinary for a Phillie. The registered call is **both, and the price was set on a residual**. He faced 1,772 batters (#8 among 199 Phillies pitchers since 2015) over 402.2 reconciled innings. 2023 sat near the Phillies median (.311 vs .318); 2024 and 2026 are the #3 and #1 worst of 198 Phillies pitcher-seasons. On the AAV basis the deal cost $179K per inning, and 2026 cost $794K per inning before his April 23 release and two minor-league stints with the Angels.

## 6 · Where the organization argued with itself
**Was it bad luck?** `product-narrator` wanted to lead with H-L STRONG (luck gap +.021 vs the Mets years). `kpi-calculator` pointed to the pool receipt: the Phillies median luck gap is +.019, so his tenure (+.013) is ordinary. **Resolution:** the registered verdict ships as scored; the pool comparison ships beside it, labelled post-hoc and ungraded. The copy says the luck "stopped being good", not that it turned bad, and names 2026 as the exception.

**What did the contract buy?** The draft headline said the Phillies "paid for a lucky stretch". R2 came back WEAK (luck gap −.008 at signing), so the gap they paid for was mostly real weak contact. **Resolution:** the headline became "the gap the strikeouts never explained", and Takeaway 1 says the skill was real but fragile.

**One career dot or two?** The client asked to "highlight his career overall". `data-architect` argued a single blended dot hides the story. **Resolution:** two era diamonds on F1 (2015–22, 2023–26), with the reason in `01` V-2.

## 7 · Escalations to the human DPO
1. **E-1 · Ratify** KR-1, CE-1 and PR-1 (first use). Recommend KR-1 into the next kernel as a reusable screen with the population as a parameter.
2. **E-2 · O-26 again.** The client's `nphl` name filter lost 483 of Walker's pitches. Recommend a `get_nphillies_data(pitcher_id=…)` path in `Baseball Functions` (second recurrence after UC49).
3. **E-3 · EV-1 (new).** `inds().ev_mu` mixes BIP and non-BIP readings and is not comparable across 2015 and later years. Recommend a BIP-only `ev_mu` or a footnote in the notebook.
4. **E-4 · ENV-3 again.** pip on the laptop VM still needs `TMPDIR` off the full volume. Add it to the MLB `CLAUDE.md` setup line (third recurrence).
5. **E-5 · Ledger.** `uc_ledger_AI_PATCH_uc-pps-038-walker-phillies-career-recap.md` is a **pending paste** (copies here and at the MLB root). UC52–UC61 patches are still pending too.
6. **E-6 · Decision ownership.** The report grades a finished contract; it makes no roster or contract recommendation beyond Takeaway 4's screening rule.
7. **E-7 · Commit.** Not made; not requested.

## 8 · Publish recommendation
**READY-CONDITIONAL. Internal audience (front office, pro scouting, pitching department).**
- **C1** Ranks are Phillies-frame (2015–26, ≥ 100 PA, n = 198), not MLB-wide.
- **C2** Carry-ins are reported facts, never computed on; contract figures per MLB Trade Rumors (CI-1, CI-2).
- **C3** KR-1, CE-1, PR-1 are provisional (first use). Changing a PR-1 bar is breaking.
- **C4** 2026 is 115 PA. Read direction, not decimals.
- **C5** Two wOBA bases, labelled; the luck-gap pool context is post-hoc and ungraded.
- **C6** Money is AAV basis only.

External publication: after DPO review of C2 and the cost chapter.
