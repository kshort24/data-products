# 00 · DPO Orchestration Record: `uc-pps-040-nola-2026-recap-sequencing-001`

**UC #64 · contract `uc-pps-040` · build `dp_uc64` v1.0.0 · BID filed 2026-11-16 22:47 ET · awarded by RFP rule, accepted 22:48 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-11-16 ≈23:30 ET · READY-CONDITIONAL (C1–C4, `05`) · harness 43/43 · DQ 21 PASS / 3 WARN / 0 FAIL (5 INFO) · V1–V7 10/10 (1 registered exception).**
First product in the plane with a **pitch-sequencing engine** (SQ family) and the first recap whose intake ran a mid-flight **DPO ruling round** (Q-A/Q-B/Q-C) before the bid was priced.

## 1 · The ask and how we framed it
A 2026 season analysis of Aaron Nola that leans on the five prior Nola-touching products without "tying out narratives", plus a new capability:
how he sequences vs LHB and RHB, which sequences maximize run prevention (outs, strikeouts, weak contact), differences by batterymate, and drift
since his young years. The client flagged sequence length as the hard part and invited questions.

Four jobs:
1. **Recap the arc honestly** — 2026 against 40 Phillies starter seasons, start by start, and the prior products' tripwires re-read at season's end (PR-R), with no HP grading ledger (client: don't tie out narratives).
2. **Build the sequencing engine as a counterfactual, not a leaderboard** — a sequence earns credit only for what its follow-up pitch did *beyond* that pitch in that count (SQ-2).
3. **Let the client set the three judgment calls** that no agent may infer: credit rule, the weak-contact definition, window scope.
4. **Keep the claims inside the noise floor** — intervals on every lift, a calibration row, pre-registered era bars.

## 2 · Delivery plan (all phases ran)
| Phase | Departments (agents) | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | recon of both planes + 6 prior Nola products, sequence-length profile, **DPO ruling round** (Q-A/B/C), carry-ins (web), BID + acceptance, `intake/` |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer | `dp_uc64_kernel.py` (K63 pinned; SQ-0 verbatim; SQ-1..6, PC-1, OUT-1, PI-1), `dp_uc64_nola_recap.py`, 63 receipts, `eda/dp_uc64/` |
| T2 | dashboard-specifier | F1–F9, S1; V1–V7 audit; two eyeball-QA rounds (F6 interval display, F9 window, F4 labels, F8 title) |
| T3 | analytics-enabler | `dp_uc64_build_report.py` → report `.md` + `.pdf` (12 pp); hand-claim fact-check pass |
| T4 | consumer-onboarding-agent, query-builder | dashboard `.html` with Sequence Explorer + Artifact; headless-browser test |
| T5 | data-quality-engineer, certification-agent | DQ scorecard, independent harness 43/43, `05` |
| T6 | metadata-mapper, data-dictionary, data-tagger, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

## 3 · Governance gates
| Gate | Status |
|---|---|
| Use case validated (0 blocking) | PASS (3 non-blocking gaps, all closed by DPO ruling Q-A/B/C, `01` §2) |
| Entity lock | PASS (605400; name frame == id frame on pitching rows; 'Nola' substring also hits Nolan Hoffman 676510 — guarded) |
| No CDE inference | PASS — **PC-1 "weak contact" defined by the DPO (Q-B)**, not by an agent; all other metrics inherited or specified in the BID before code |
| Lineage | PASS (`dp_uc63_kernel` pinned `c4c0eea4…`; 12 files asserted at every build) |
| Anchor | PASS (house max 2026-10-01) |
| Pre-registration | PASS (SQ-4 floors, SQ-5 eras + FADED bar, SQ-6 test filed 22:47 ET; first compute after) |
| Reconciliation REC-1 | PASS-with-disposition (K exact; BB exact incl. 2 IBB; outs 524 vs 526 after reconstruction) |
| Visual standard V1–V7 | PASS 10/10 (F5 registered V2 exception: the comparison is inside the measure) |
| Harness | PASS 43/43 |
| Certification | READY-CONDITIONAL (C1–C4) |
| Privacy | Clear (public-figure performance data; no PII) |
| Publish | **DPO decision** |

## 4 · Arguments the organization had
- **Who defines "weak contact"?** The kpi-calculator proposed EV < 90 mph (simple, house-adjacent). The business-glossary-agent blocked it: no glossary term existed, and Principle 1 forbids inference. **Settled:** returned to the DPO as Q-B; the client chose Savant LSA 1–3 (PC-1).
- **Tiered windows vs "career-wide everything."** The org recommended tiered windows (2026 pairs, pooled triples). The client chose career-wide for all lengths. **Settled:** DPO ruling stands; 2026 shown as a highlight on the career baseline, and the report says plainly that no 2026 righty pair clears its interval.
- **Is "the sequence faded" the same as "the results faded"?** The eda-agent's first read of the young-era staples was "they stopped working". The kpi-calculator pointed out that SQ-5 scores each era against its own baselines, so a stuff decline cannot show up as a fade. **Settled:** add **SQ-5d** (raw = baseline part + lift) as a descriptive, non-breaking table; the bar itself unchanged. Answer: 0 FADED; the decline lives in the pitches (fastball RV/100).
- **Batterymate result vs G7.** SQ-6 returned DISTINCT BOOK vs LHB for Realmuto vs Stubbs (2023–26), but 2026 Stubbs starts cluster after the 7/05 pivot. **Settled:** G7 robustness run on 2023–25 only (p = 0.002, still distinct); 2026 alone is SAME BOOK (power). Shipped as "a real but small difference; who called it is unknowable (G4)".
- **F6 display.** First render plotted the *shrunk* lift with the *raw* lift's interval — points sat off-center. The dashboard-specifier caught it at eyeball QA. **Settled:** plot raw lift ± its interval, order by shrunk.
- **Hand-written claims.** The analytics-enabler's draft said THIN era cells were "mostly cutter sequences", K% was "career-low", the curve was thrown "more than ever". The certification-agent checked each against receipts: 9 of 81 THIN cells involve the cutter (corrected: short 2025–26 window), 2015's K% was lower, 2019's curve usage was higher. All three corrected before render.
- **Stretch choice.** S-1 predictability (PI-1) chosen over S-2 (count-conditioned next-pitch simulator): S-2 needs the machine-learning-engineer and a validation design; S-1 answers "is he tipping by pattern?" cheaply.

## 5 · Escalations to the human DPO
1. **Publish** the report / dashboard (privacy clear). The Artifact "Aaron Nola 2026" is private until shared.
2. **Ratify** the SQ family (SQ-0 … SQ-6), PT-H, OUT-1, PI-1 (provisional) and **PC-1** (your Q-B definition) as glossary terms.
3. **Watch item for 2027:** two straight curves to RHB — the one young-era staple whose lift turned negative (not beyond noise). Re-test with 2027 data.
4. **Ledger:** paste UC52–UC64 patches, oldest first.
5. **Next UC candidate:** feed SQ-2/SQ-3 into the next Nola advance scout (`uc-pps` pattern) as a pre-game sequencing card by opponent handedness mix.
6. **K44 note (not new, now quantified):** house `nresults` walks exclude IBB (`events == 'walk'`); public BB includes them (2 here). Disclose or generalize in a K44 successor.

## 6 · Delivery summary
- **Headline:** "Aaron Nola | 2026 | Better Process Than Results, and a Book Built on the Curve".
- **Season:** .343 wOBA (5th pct of 40 Phillies SP seasons) vs .315 xwOBA (27th); HR/PA 5.0% (last); whiff 65th, chase 77th, CSW 67th; 1H .355 → 2H .327 wOBA with xwOBA flat; pivot held (CH share 12.6% → 20.1%), CH vs LHB wOBA regressed .192 → .311.
- **Sequencing:** best ending two straight curves (.222 xwOBA vs LHB / .174 vs RHB); setups that add value: SI→CH (+3.2) and SI→FF (+2.3) vs RHB, CH→KC (+1.8) vs LHB; 28 of 176 rankable sequences clear their interval vs 17.6 by chance (p = .009); 0 of 43 testable sequences FADED; lefty book differs with Stubbs (p = .002); 2026 the least predictable mix of his career (2.17 bits).
- **Bid vs actual:** ≈545k / ≈68 min bid vs ≈300k (est.) / ≈60 min actual (`07` §5).
