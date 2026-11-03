# 00 · DPO Orchestration Record: `uc-pos-025-harper-2026-recap-001`

**UC #61 · contract `uc-pos-025` · build `dp_uc61` · BID filed 2026-11-02 18:05 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-11-02 ≈18:22 ET · READY-CONDITIONAL (C1–C6, `05`) · harness 25/25 · DQ 14/0/0 · V1–V7 audit 3/3.** Single chat, no hard stop (RFP rule). Second governed Harper product of 2026 (UC #23 "Own the Zone", first half) and the one that closes his season. First UC whose primary consumable is a **design kit** for Claude Design rather than a PDF or dashboard.

---

## 1 · The ask and how we framed it
The client asked for a Harper 2026 recap built as one notecard: headline "Bryce Harper | 3 | {one line}", executive bullets, a cumulative wOBA chart against his career (other slash metrics available), a pitch map split by pitcher hand, and a spray chart with batted-ball KPIs. **Pieces, not a poster**: the client will assemble and animate in Claude Design. "Focus on getting the data right."

Five jobs:
1. **Reconcile before writing a word.** The 2026 line ties to MLB.com exactly (693 PA, .269/.380/.485, 29 HR, 162 G).
2. **Inherit, don't re-derive:** the K60 → K58 → K57 recap chain, SD-1/2/3, and UC #23's OZ geometry (pinned, imported).
3. **Generalize twice, non-breaking:** a subject-parameterized career loader (K58 hard-binds Schwarber) and CM-2, the whole slash line by PA (the client wants OPS/OBP/SLG/BA/HR switchable).
4. **Grade the public narrative** ("approach held, hard contact faded", ".997 vs .657", the June "owning the edge" read) on bars set before the grades.
5. **Ship pieces Claude Design can't get wrong:** every printed number registered to a headline key (NC-1), every chart audited (V1–V7), a brief with non-negotiables.

## 2 · Delivery plan (all phases ran)
| Phase | Departments | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | BID, `01`, `intake/` |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer | kernel, T1 build, 30+ receipts, `02`, `04` |
| T2 | dashboard-specifier | F1–F3, V1–V7 audit, reference notecard |
| T3 | analytics-enabler | HP grades, headline, bullets, callouts (`notecard_copy.json`) |
| T4 | consumer-onboarding-agent, query-builder | Claude Design brief + kit (16 files, sha manifest) |
| T5 | data-quality-engineer, certification-agent | harness 25/25, `05` |
| T6 | metadata-mapper, data-dictionary, data-tagger, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

## 3 · Governance gates
| Gate | Status |
|---|---|
| Use case validated (0 blocking) | PASS (7 non-blocking, `01` §2) |
| Entity lock | PASS (547180, both sources, 0 duplicate keys) |
| Lineage | PASS (23 pins) |
| No CDE inference | PASS (all metrics consumed; AP-1 / HC-1 / OZ-H pre-registered) |
| Anchor | PASS (2026 max game_date 9/27 ≤ 10/01) |
| Visual standard V1–V7 | PASS (3/3, `visual_audit.csv`) + eyeball QA, 2 rounds |
| NC-1 notecard copy rule | PASS (87 registered numbers, 0 unregistered on the card) |
| Harness | PASS 25/25 |
| Certification | READY-CONDITIONAL (C1–C6) |
| Privacy | Clear |
| Publish | **DPO decision** |

## 4 · Arguments the organization had
- **Use the ad-hoc `harper_2026_visuals.py` (Oct 12) as the base?** The dashboard-specifier wanted its spray and wall functions. The certification-agent refused: notebook scope, no pins, `-i` namespace dependencies. **Settled:** governed parts only (PA-L1, DR-1, house `wall_outline`); the script is cited as prior art.
- **Draw every pitch to scale (UC58 rule)?** With 2,734 pitches a to-scale map is a solid blob. **Settled:** location marks (not to scale) for every pitch; damage and HR marks on top; the brief states it. UC58's to-scale rule stays for HR-only maps.
- **"Lefties were bad luck"?** The June ad-hoc `harper_vs_lhp_report.md` called his vs-LHP slump small-sample luck (.303 wOBA vs .383 xwOBA in 95 PA). The domain-steward-proxy asked for the full-season test before any copy: xwOBA vs LHP finished **.314**. **Settled:** the card says the results were mostly earned and prints both numbers.
- **Headline "the eye carried a softer bat"**: the analytics-enabler checked it is a both-legs claim: AP-1 SUPPORTED (eye) and HC-1 SUPPORTED (softer), with the H2 OPS held flat by walks (.862 → .868) while H2 hard-hit fell (46.2% → 37.4%).

## 5 · Escalations to the human DPO
1. **Publish** the notecard / kit externally (privacy clear).
2. **Ratify** AP-1, HC-1, OZ-H (grade rules), NC-1 (copy rule), CM-2 (`cum_slash`), DH-2 (sourced doubleheader-order override). All first use.
3. **`cumulative_metric` v1.1** (open since UC58): CM-2 is the candidate for the slash-line metrics; fold it in or keep it kernel-local.
4. **Tier B** (offered, not built): PDF report + multi-chapter dashboard on the same receipts.
5. **Ledger:** paste UC52–UC61 patches, oldest first.

## 6 · Delivery summary
- **Headline:** "Bryce Harper | 3 | The Eye Carried a Softer Bat".
- **Findings:**
  - .375 wOBA: best among the 10 Phillies with 200+ PA, 94th percentile of 122 Phillies hitter seasons; all 162 games.
  - BB% 15.4% (best since 2020) and a .380 OBP. Chase, K% and edge-takes all held (AP-1, OZ-H).
  - Hard-hit 42.8%, barrels 10.3%, EV p90 106.3 and SLG .485 are all Phillies-tenure lows (HC-1). Pulled 49.9% of balls in play; oppo 25.6% (tenure low).
  - Platoon: .997 OPS / 25 HR vs RHP, .657 / 4 HR vs LHP (worst of 12 Statcast seasons). Lefty fastballs .320 xwOBA vs .410 in 2019–25; lefties lived low-away (32% of pitches, 60% whiffs).
- **HP:** 6 / 6 SUPPORTED (3 exact reconciliations, AP-1, HC-1, OZ-H HELD).
- **Bid vs actual:** ≈183k / ≈28 min vs ≈410k / 57 min (`07` §5).
