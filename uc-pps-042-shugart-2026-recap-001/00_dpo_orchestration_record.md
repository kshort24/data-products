# 00 · DPO Orchestration Record: `uc-pps-042-shugart-2026-recap-001`

**UC #66 · contract `uc-pps-042` · build `dp_uc66` v1.0.0 · BID filed 2026-11-20 14:12 ET · awarded by RFP rule, accepted 14:13 ET**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **DELIVERED 2026-11-20 ≈14:45 ET · READY-CONDITIONAL (C1–C4, `05`) · harness 34/34 · DQ 12 PASS / 5 WARN / 0 FAIL · V1–V7 11/11 figures (0 FAIL) · HP 8 SUPPORTED / 3 PARTLY / 1 NOT.**
First pitcher recap built on an explicit **visual rule set (VZ-1…VZ-6)** answering the client's complaint about the last recaps' visuals, and the first
in which the org — not the client — chose and defended the comparison sets.

## 1 · The ask and how we framed it
A 2026 recap of RHP Chase Shugart (acquired 2026-01-13 from PIT) that starts high and drills down to the indicators behind the outcomes, built
on the client's scratch notebook, with better visuals (pitch plot, pitch map, cumulative usage, cumulative wOBA), and with the comparison set
delegated to the org. Four jobs:
1. **Grade the scratch work, don't restate it.** Twelve claims in the client's notes became HP-01…HP-12 with bars filed before compute.
2. **Choose the context and say why** (CS-A righty relievers, CS-B 2026 bullpen, CS-C pitch × hand cells; own history not observable).
3. **Fix the visuals with rules** (VZ-1…VZ-6 on top of V1–V7), two eyeball-QA rounds, every figure re-audited.
4. **Keep it governed:** K64 pinned import, receipts for every number, independent harness, 00–07.

## 2 · Delivery plan (all phases ran)
| Phase | Departments (agents) | Output |
|---|---|---|
| T0 | use-case-validator, source-system-profiler, domain-steward-proxy, business-glossary-agent, token-economist | recon of both planes + 3 prior recaps' figures, entity lock, frame + history profile, carry-ins (web), comparison-set decision, BID + acceptance, `intake/` |
| T1 | data-architect, kpi-calculator, eda-agent, join-validator, data-engineer | `dp_uc66_kernel.py` (K64 pinned), `dp_uc66_shugart_recap.py`, `dp_uc66_hp.py`, 64 receipts, `eda/dp_uc66/` |
| T2 | dashboard-specifier | F1–F9 + S1 (11 figures), VZ rules, V1–V7 audit, two eyeball-QA rounds |
| T3 | analytics-enabler | `dp_uc66_build_report.py` → report `.md` + `.pdf` (11 pp), fact-check pass |
| T4 | consumer-onboarding-agent, query-builder | dashboard `.html` with Pitch × Hand Explorer (JS syntax-checked) |
| T5 | data-quality-engineer, certification-agent | DQ scorecard, independent harness 34/34, `05` |
| T6 | metadata-mapper, data-dictionary, data-tagger, version-controller, privacy-watchdog, data-observability, cost-watchdog | `03`, `06`, `07`, README, contract, ledger patch |

## 3 · Governance gates
| Gate | Status |
|---|---|
| Use case validated (0 blocking) | PASS (4 non-blocking gaps, `01` §2) |
| Entity lock | PASS (663767; name rows == id rows, 944 == 944) |
| No CDE inference | PASS — every new object (CS-A/B/C, IN-1, LC-1 reuse, CU-1, CW-1, S-1) specified in the BID before code; no business meaning inferred |
| Lineage | PASS (`dp_uc64_kernel` pinned `32a83b84…`; full K64 chain asserted at every run) |
| Anchor | PASS (house max 2026-10-01) |
| Pre-registration | PASS (HP bars filed 14:12 ET; unchanged after compute) |
| FR-1 reconciliation | PASS (client .430 SLG / 10.0% barrel == regular-season frame; all-types frame would print .422) |
| Visual standard V1–V7 | PASS 11/11 figures, 0 FAIL |
| Harness | PASS 34/34 |
| Certification | READY-CONDITIONAL (C1–C4) |
| Privacy | Clear (public-figure performance data; no PII) |
| Publish | **DPO decision** |

## 4 · Arguments the organization had
- **Which context?** The eda-agent proposed "all Phillies RHP" (largest pool). The domain-steward-proxy objected: starters' K and platoon profiles are
  shaped by times through the order; a reliever ranked against them flatters or punishes him for role, not skill. **Settled:** CS-A RHP relief
  seasons (mirrors the registered `phi_lhp_relief_seasons`); "middle reliever" treated as a usage role inside CS-B, not a population cut.
- **League context from `nphl`?** The source-system-profiler showed `nphl` is 132 hand-picked opponent files — not a sampling frame. **Settled:** rejected; disclosed.
- **Own history.** The client asked for it. The profiler found 77 scattered 2025 MLB pitches. **Settled:** NOT OBSERVABLE; no comparison drawn.
- **The spring-training rows.** The house projection of the client's `pps` carries 73 spring pitches. The kpi-calculator wanted to grade on the
  client frame; the certification-agent showed the client's own printed .430 / 10% only reproduce on the regular-season frame. **Settled:** governed frame = regular season; FR-1 disclosed.
- **Visuals.** The dashboard-specifier listed what the last recaps did wrong (mixed-scale rates on one axis, mean-location bubbles, colliding labels,
  low-contrast gold). **Settled:** VZ-1…VZ-6; F1 rebuilt as per-metric small multiples, F4 split into an every-pitch map (client's view) and a density grid.
- **June "lost command".** First draft said June had his "highest zone rate". The harness (V17) disagreed until the house rule was matched: a 4-pitch
  intentional walk on Jun 22 (null zone) is counted in-zone by K44 `chase_rate` (D-7). **Settled:** text says June ties September for his best zone rate
  (52.1% house rule; 51.1% on tracked pitches); DQ-17 added. HP-08 verdict unaffected (PARTLY).
- **Sweeper to righties.** The client's monthly chart read "backed off his sweeper" to righties. CU-1 split by hand put the change against lefties
  (25% → 4%). **Settled:** HP-09 NOT on its pre-registered bar; the report credits the strong finish and relocates the mix change.

## 5 · Escalations to the human DPO
1. **Publish** the report / dashboard (privacy clear).
2. **Ratify** CS-A `phi_rhp_relief_seasons` into `data/_schema/comparison_sets.json` (DRAFT), and VZ-1…VZ-6 as recap-wide visual rules (proposed additive module `phillies_dp/recap_viz` VZ checks).
3. **Render env:** the device VM session disk was full; stack installed to `/tmp/pylib` (RN-3). Staged-file commits can deliver a stale copy when the staged path is reused (RN-4) — commit under a fresh staged name and verify md5.
4. **Ledger:** paste UC52–UC66 patches, oldest first.
5. **Next UC candidate:** a 2027 spring check-in on Shugart's cutter location to righties and first-pitch strike rate (the two indicators in §11 of the report).

## 6 · Delivery summary
- **Headline:** "Chase Shugart | 2026 | A Solid Middle Reliever Who Rebuilt His Plan Against Lefties".
- **Season:** .312 wOBA (56th pct of 114 Phillies RHP relief seasons) on .300 xwOBA (65th); K 26.5% (71st); barrel 10.0% (18th); chase 25.7% (21st).
- **Platoon:** .309 vs LHB / .315 vs RHB — reverse by .006 where the CS-A median runs .028 the other way; 6/6 legs of the client's read hold.
- **Drivers:** FC .289 wOBA vs LHB / .439 vs RHB (lives middle-away to righties); SI 51% of strikeouts; ST vs LHB .545 and shelved (25% → 4%).
- **Arc:** June .441 wOBA = contact (17% barrels), not walks; after the July recall first-pitch strikes 54% → 64%, wOBA .352 → .262.
- **Role:** 6 of 46 outings late & close (rank 10 of 13); entered behind 30 times.
- **Bid vs actual:** ≈410k / ≈64 min bid vs ≈330k (est.) / ≈46 min actual (`07` §5).
