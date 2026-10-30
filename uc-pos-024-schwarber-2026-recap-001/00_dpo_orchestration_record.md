# 00 · DPO Orchestration Record: `uc-pos-024-schwarber-2026-recap-001`

**UC #60 · contract `uc-pos-024` · build `dp_uc60` · BID filed 2026-10-29 20:14 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-10-29 ≈20:34 ET · READY-CONDITIONAL (C1–C6, `05`) · harness 28/28 · DQ 11/2/0 · Tier 3 audit 8/8.** Single chat, no hard stop (RFP rule). **Fourth and closing Schwarber product of 2026** (UC21, UC33, UC58). First UC built to the Tier 3 visual standard, and the builder of its shared dependencies.

---

## 1 · The ask and how we framed it
The client asked for the complete 2026 season recap, with a PDF (required), a dashboard (if it makes sense), a fully governed package, and "consider the Tier 3" of the Pitcher Recap Visual Redesign brief. The business questions are the ones UC58 parked: what happened, should we be concerned, was it his back, did he lose his pop.

Five jobs:
1. **Answer the four questions on pre-registered bars** (BK-1, POP-1, CN-1) and say plainly what the log cannot see (a back).
2. **Inherit, don't re-derive:** K57 recap spine, K58 career loader / DH-1 / HR quality, UC33's damage band and sensor boundary, `cumulative_metric`, RC-5 scans.
3. **Build Tier 3's shared dependencies once**, as house assets: SD-1 comparison sets, SD-2 eras, SD-3 helpers plus a V1–V7 machine audit.
4. **Hold every figure to V1–V7** and ship the audit.
5. **Keep the 13 pitcher redesign items out of this UC.** Each has to trace to the pps UC it modifies. Tier B.

## 2 · Delivery plan (all phases ran)
| Phase | Departments | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | BID, `01`, `intake/` |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer | SD-1/2/3, kernel, build, `02`, `04` |
| T2 | dashboard-specifier | F1–F8, Tier 3 audit, season card |
| T3–T4 | analytics-enabler | narrative, report, PDF, dashboard |
| T5 | data-quality-engineer, certification-agent | harness, `05` |
| T6 | metadata-mapper, data-dictionary, data-tagger, consumer-onboarding-agent, query-builder, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

## 3 · Governance gates
| Gate | Status |
|---|---|
| Use case validated (0 blocking) | PASS (9 non-blocking, `01` §2) |
| Entity lock | PASS (656941, both sources) |
| Lineage | PASS (22 pins) |
| No CDE inference | PASS (all metrics consumed; three grade rules pre-registered) |
| Anchor | PASS (2026-10-01, sha `be5d313d…`) |
| Tier 3 visual standard | PASS (8/8, `visual_audit.csv`) |
| Harness | PASS 28/28 |
| Certification | READY-CONDITIONAL (C1–C6) |
| Privacy | Clear |
| Publish | **DPO decision** |

## 4 · Arguments the organization had
- **Run the 13 pitcher redesigns here?** The dashboard-specifier was ready to. The certification-agent refused: the brief requires each redesign to trace to the UC it modifies, with a DPO review gate per prototype. **Settled:** this UC builds the shared parts and is the first adopter; the items are Tier B.
- **Use BP-0 or K40 tracked swings for BK-1?** The BID named "bat speed" without a population. **Settled:** BK-1 runs on K40 `bat_tracking`, the recap spine's governed field. F4 draws BP-0 and prints both means; both are verified (V08), and neither shows a drop.
- **Keep F7 with R² ≈ 0?** The analytics-enabler wanted to drop it. The domain-steward-proxy argued the near-zero fit is itself the finding: chase doesn't drive his strikeouts, so chase is a separate lever. **Kept.** V4 forces the R² onto the page.
- **Say "the back caused the slump"?** Never. The bars were set before the data was looked at, and the grade is "not visible in the log".

## 5 · Escalations to the human DPO
1. **Publish** the PDF / dashboard externally (privacy clear).
2. **Ratify SD-1 DRAFT entries** (Phillies SP seasons: workload cut ≥ 2000 pitches vs a role cut; LHP relief: RP-1) before the pitcher redesign starts.
3. **Adopt SD-2 `asb_2026`** as the single ASB definition (retire the three kernel constants on next touch).
4. **Tier B go / no-go:** pitcher redesign items 1–4 (Alvarado, Wheeler) on the new helpers.
5. **Ledger:** paste UC52–UC60 patches, oldest first.
6. **Carry-over from UC58:** the `cumulative_metric` v1.1 (DH-1 `order=`, PA-X1 default) decision is still open; this UC wraps it again.

## 6 · Delivery summary
- **Findings:**
  - A top-decile Phillies hitter season (90th percentile wOBA) that turned in July.
  - The back is not visible in the swing: bat speed flat, the biggest break 33 games before the scratch.
  - The pop thinned after the break (barrels 19.3% → 10.6%) without leaving his range for the year.
  - One real flag: chase (26.1%, z 4.1), plus the righty-fastball leak (.495 → .386 xwOBA).
- **HP:** 5 SUPPORTED (one "stronger") · 1 PARTLY · 1 NOT VISIBLE · 1 NOT SUPPORTED. The concern question is graded NOT SUPPORTED, which is not the same as "no concern".
- **Bid vs actual:** ≈240k / ≈28 min vs ≈478k / 54 min (`07` §5).
