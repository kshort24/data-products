# 00 · DPO Orchestration Record: `uc-pos-022-turner-2026-recap-001`

**UC #57 · contract `uc-pos-022` · build `dp_uc57` · BID filed 2026-10-23 20:49 ET**
Value stream: Phillies Offense (`pos`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-10-23 21:27 ET · READY-CONDITIONAL (C1–C6, `05`) · harness 34/34 · DQ 10/3/0.** T0 in the bidding chat; T1–T6 in a new chat (DPO choice), Tier A, G2 taken as the BID default.
Run: single turn, stopped by instruction after the BID. **Fourth Turner product of 2026** (after UC25, UC40/UC40a, UC42) and the **fourth pos-side season recap** (after UC54–UC56). Code and outputs will live at the MLB root; this folder holds the receipts.

---

## 1 · The ask and how we framed it
The client submitted a notebook export (`9c281fb3-attachment.txt`, "Trea Turner", rated 7: "An atrocious year … sounding major alarm bells"). It:
- restates the midseason review (offspeed vs LHP, in-zone swing down and chase up, almost no pulls or pull-air, flat bat path into popups);
- adds new reads by pitcher hand and pitch group (RHP breaking-ball expansion, LHP offspeed whiffs and popups, fastballs by hand, slow lefty fastballs);
- hands the swing-path visualization and exploration to the machines, building on prior products and "the conversation I started last night";
- raises a move off shortstop, but asks not to "worry about defense too much."

The organization read this as **five jobs**:
1. **Answer in the client's order**, one chapter each, ending on the notebook graded.
2. **Inherit, don't re-derive.** Spine K55 → K54 → K40 chain; K40a for bat path (UC40a's open finding is closed out on the full season); UC42's in-zone direction frame.
3. **Pre-register the recognition test** (PR-1, change bars, small-cell rule) before any split is computed, because the client's theory can be confirmed by choosing splits after looking.
4. **Keep the swing path observed.** Tier A uses the six bat-path fields as measured. The reconstructed 3D swing from this afternoon's pilot is a modeled product with its Gate 2 open, so it is a separately priced Tier B, not a default.
5. **Say what can't be answered.** "A different position improves his offense" is untestable on his data and is graded so, with sourced carry-ins in place of a model.

## 2 · Delivery plan (departments to be engaged after award)
| Phase | Departments | Output |
|---|---|---|
| T0 (done) | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | `01`, this record, BID |
| T1 | data-architect, kpi-calculator, eda-agent, data-engineer | `02`, `03`, `04`; `dp_uc57_kernel.py`, build, HP reproduction |
| T2–T4 | dashboard-specifier, analytics-enabler | figures, dashboard, report, PDF |
| T5 | data-quality-engineer, certification-agent | `05`; definition-first harness |
| T6 | consumer-onboarding-agent, version-controller, privacy-watchdog, data-observability | `06`, `07`, README, contract, ledger patch |

Receipts `02`–`07` written by the phases that produced their content.

## 3 · Governance gate checks (at bid time)
| Gate | Status |
|---|---|
| Use case validated (0 blocking gaps) | PASS (`01` §2) |
| Entity lock by MLBAM id | PASS (607208, one name, 0 duplicate keys) |
| Inherited lineage pins | PASS (K55 `assert_lineage()` 14/14) |
| No CDE inference | PASS (bat-path definitions consumed from K40a `03a`; one new KPI spec'd in the BID before any code) |
| Data anchor pinned | PASS (2026-10-01, unchanged despite the 19:53 file rewrite) |
| Build started | YES, new chat, 2026-10-23 21:01 ET (Tier A) |
| Harness | PASS 34/34 (`05` §2) |
| Certification | READY-CONDITIONAL (`05` §3) |

## 4 · Arguments the organization had (and how they were settled)
- **Ship the 3D pilot swing in Tier A?** The dashboard-specifier wanted it, since the client asked for "swing path visualization". The certification-agent refused: the pilot is DRAFT with Gate 2 open, and in this data plane its azimuth ignores O-15. **Settled:** Tier B, conditional on the DPO closing the pilot's Gate 2.
- **Answer the position question with a proxy?** A position-switch pool of Phillies hitters was floated. **Rejected:** a handful of different players, a different question, and the client asked to keep defense light. Carry-ins only.
- **Where does the code go?** UC56's RFP put everything in the control plane; this RFP says to work inside the MLB repo. **Settled:** UC55 pattern (code and outputs at the MLB root, receipts here).

## 5 · Escalations to the human DPO
1. **Go / no-go and where:** continue in this chat or open a new one. The BID's price note says a new chat adds ≈ 35k in and 3 minutes to T1.
2. **G2:** confirm that "the conversation I started last night" means the 2026-10-22 bat-tracking CDE read.
3. **Tier choice:** A (recommended) or B. B needs the pilot's Gate 2 closed first (A1–A6, thresholds, bounds, and the v0.4 bat-head decision).
4. **PL-1 (for the pilot's own trail):** re-point `phillies_dp.swing_pilot` to the house log for the intercept fields, and apply O-15 to `attack_direction`.
5. **Ledger:** UC52–UC56 patches are still pending paste, oldest first; UC57 will add one more.

## 6 · Certification conditions
Assessed in `05` §3 (C1–C6). The four expected at bid time all held:
- the bat-path window covers 2025–26 only (G7);
- small cells (SM-1);
- HP-12 is not testable (G3);
- the inherited pooled-season wOBA workaround (UC56 `00` §5).

## 7 · Delivery summary (added at T6)
- **What the build found** (against the client's theory): the recognition break is on **fastballs** (in-zone takes), not breaking balls; the process decline is **against righties**; popups and the flat path are both real but PP-1 grades the link **PARTLY**.
- **HP grades:** 2 SUPPORTED (HP-01, HP-10) · 8 PARTLY · 1 PLAUSIBLE, NOT PROVEN (HP-11) · 1 NOT TESTABLE (HP-12).
- **Escalations still open:** G2 confirmation; Tier B (pilot Gate 2 + PL-1); ledger paste order (UC52–UC57).
- **Bid vs actual:** `07` §5 (≈513k across two chats vs 471k new-chat-adjusted bid; ≈35 min build vs ≈41 bid).
