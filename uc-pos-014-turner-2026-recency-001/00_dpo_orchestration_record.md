# 00 · DPO Orchestration Record — `uc-pos-014-turner-2026-recency-001`

**UC #40 · contract `uc-pos-014` · build `dp_uc40` · Phillies Offense (`pos`) value stream**
**Requested and delivered 2026-09-03 · data as of 2026-09-02 · Human DPO: Kellen Short**
**Status: CERTIFICATION READY · v1.0.0 verification 711/711 · v1.1.0 addendum 180/180 · conventions 12/12
· DQ 22/3/0 + 10/3/0**
**v1.1.0 bat-path addendum delivered 2026-09-03 — see `ADDENDUM_v1.1.0_bat_path.md`, `03a`, `05a`.**

---

## 1 · The ask, and how it was framed

A business-user prompt in one paragraph: *what is going on with Trea Turner recently, and this year in
general* — plus seven sub-questions and an explicit delegation of direction to the `data-product-owner`.
The prompt also asked that the bid be treated as a competitive RFP submission, priced, and — for this
exercise — considered won.

**The material fact the DPO acted on at intake:** this organization had already delivered a Trea Turner
2026 offense review — **UC #25 / `uc-pos-006` / `dp_uc24`, 2026-07-21** — which closed with an open,
unresolved call: *"July .980 OPS / 62 PA recovery real-but-young."* Six weeks of new data now exist.

The DPO therefore scoped this as a **parent-extension UC**, not a fresh study, and committed to the
standing **parent-reproduction check** before any new claim could be made. That decision is what the bid
was priced on and it is the single largest source of the organization's competitive advantage here.

## 2 · Delivery plan and sequencing

| Layer | Department | Agents | Output |
|---|---|---|---|
| 1 | Strategy & Intake | `use-case-validator`, `source-system-profiler`, `domain-steward-proxy` | `01` — 8 questions, 3 premises, 0 blocking gaps, 3 non-blocking, 4 watch items |
| 2 | Engineering Design | `data-architect`, `eda-agent`, `join-validator`, `metadata-mapper` | `02` — model, 4 validated joins, 2 EDA-forced design changes |
| 2 | Governance | `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `data-tagger`, `privacy-watchdog` | `03` — Rule-1 grep, 4 KPI specs, column-level lineage, LOW–MODERATE privacy |
| 3 | Engineering Build | `data-engineer` | `04` — 5 scripts, 27 CSV receipts, 6 figures |
| 4 | Quality | `data-quality-engineer`, `certification-agent`, `version-controller` | `05` — 711 checks, DQ scorecard, defect register, READY |
| 5 | Consumer Success | `analytics-enabler`, `consumer-onboarding-agent`, `dashboard-specifier` | `06` — persona onboarding, query patterns, dashboard spec |
| 6 | Platform & Marketing | `data-observability`, `cost-watchdog`, `token-economist` | `07` — monitors, 6 tripwires, cost audit, bid-vs-actual |

## 3 · Governance gate checks

| Guardrail | Check | Result |
|---|---|---|
| No CDE inference | every term consumed from the glossary; **0 new business terms minted** | ✅ |
| No build without approved specs | `03` closed before `dp_uc40_turner_recency.py` was written | ✅ |
| No publish without certification | `certification-agent` READY, human DPO owns the publish decision | ✅ |
| No breaking change without notice | `version-controller` classified 5 changes; **1 is breaking for prior consumers** (D-7 `in_zone_rate`) and is raised explicitly | ⚠ raised |
| Privacy assessed before any external surface | LOW–MODERATE; no external surface proposed; player-facing brief scoped | ✅ |
| Rule-1 grep before declaring a KPI new | executed; found OZ-3 and 6 other inheritances | ✅ |
| Falsify before describe (C-1) | 3 premises adjudicated; **P3 came back split** (true vs his Phillies self, false vs his career) | ✅ |
| G8 — no superlative without a named metric and enumerated cohort | enforced; **verification caught one violation and it was corrected** | ✅ |
| Parent reproduction (extension UC) | **84/84 on the parent's own window and definitions; 0 definitional drift** | ✅ |
| Sensor-boundary NULLs never imputed | bat tracking pre-2024 and `attack_angle` pre-2025 left NULL and asserted | ✅ |
| Outcome-selected window → RC-5 scan | 10 candidate cuts published | ✅ |

## 4 · Capability fulfilment

| Requested capability | Fulfilled | Where |
|---|---|---|
| High-level performance, this year | ✅ | report §2, dashboard *Overview* |
| Where he has struggled | ✅ | §2–§4, §7 |
| What "good" looked like — Phillies and prior career | ✅ | §5, two baselines rather than one |
| Underlying indicators | ✅ | §4 + ST-1 uncertainty bands |
| Persona actions | ⚠ **partially — by design** | §8, as testable hypotheses; causation declared unidentifiable (gap G-1) |
| Has his approach changed | ✅ | §6, AD-1 |
| Pitches / pitch groups | ✅ | §7, dashboard *Pitches & platoon* |
| Lefty/righty trend | ✅ | §7 + PL-1 counterfactual |
| PDF report | ✅ | `dp_uc40_turner_recency_report.pdf`, 13 pp |
| Interactive dashboard | ✅ | `dp_uc40_turner_recency_dashboard.html`, self-contained, 6 tabs |
| Fully governed package | ✅ | `00`–`07` + README + BID + telemetry + 27 receipts + verification harness |
| Bid with token/time estimate, framed competitively | ✅ | `BID_2026-09-03_uc-pos-014-turner.md`, reconciled in `telemetry/` |

## 5 · The finding, in the DPO's words

Turner is having the lowest of his eleven qualified seasons on every rate metric, and the six weeks since
the parent product shipped are the worst stretch of it. **The parent's open call resolved against the
optimistic reading** — the rolling-form line peaked at .421 on 2026-07-21, the day `uc-pos-006` was
delivered, and now reads .238; the breakpoint scan flips sign on exactly that date.

The mechanism is **contact point, not bat speed**. He is getting under the ball: popup rate 15.2% of balls
in play against a 5.0% Phillies norm — the only measure in the product that clearly clears sampling noise
(z = 4.12) — with launch angle up and exit velocity down. His plate discipline is simultaneously the best
it has been all season (K% 19.4%, BB% 8.5% in the window). **This is a contact-quality problem wearing the
costume of a plate-discipline improvement.**

Two structural facts sit under the slump: **sweepers and sliders are 27.8% of everything he sees and he
posts .182 / .243 wOBA against them**, with breaking-ball usage against him rising 34.6% → 40.3%; and
**the left-handed edge that made him a matchup weapon in 2020–21 has not existed since 2022** — his
vs-RHP line is now the lowest of his qualified career, and right-handers are two-thirds of his PA.

## 6 · Where the organization argued with itself

Two moments are worth recording, because both changed what shipped:

1. **A plausible mechanism was killed by its own uncertainty receipt.** The first build supported "his bat
   slowed down" — August bat speed is 1.6 mph below July. ST-1 priced that against his own 2023–25 norm
   and found it **inside noise (z = −0.90)**. July was the spike, not August the decline. The product ships
   the weaker-sounding, correct mechanism and shows the working.
2. **Verification found a defect in the governed kernel, not in the build.** Two failing checks traced to
   `chase_rate_g` counting NULL-`zone` rows as in-zone. Logged as **D-7 / O-13**, remediated with an
   `in_zone_rate_fix` sibling, report re-cut onto the corrected values, governed original untouched.
   It affects every prior UC that published `in_zone_rate`.

## 7 · Escalations to the human DPO

| # | Item | Decision needed |
|---|---|---|
| E-1 | **D-7 / O-13** is breaking for prior consumers of `in_zone_rate` | Ratify the `_fix`, and decide whether prior UCs need a corrections note |
| E-2 | **AD-1, ST-1, BT-1** are NEW-PROVISIONAL | Ratify (or reject) before a third reuse |
| E-3 | **RF-2** is on its second reuse with a declared denominator change | Promote to APPROVED, or keep provisional |
| E-4 | **PA-L1 / PA-F1** (the O-7 pull-air remediation) still awaits ratification from `uc-pos-013` | Ratify — it has now shipped twice |
| E-5 | **O-5 and O-8 remain open** repo-wide | Schedule kernel maintenance outside a use-case build |
| E-6 | **F1** — third copy of the vendored Chart.js in `data-products/` | Approve a shared `_assets/` directory |
| E-7 | **Tripwires TT-1…TT-6** are armed | Approve a re-run trigger (suggest: after ~120 further PA, or season end) |
| **E-8** | **O-15 (v1.1.0)** — `attack_direction` is pull-**negative** in this data plane, the inverse of the published MLB glossary convention. Four independent anchors | Confirm against Savant methodology, then ratify the corrected `pull_direction` or a source-level fix. **Highest-priority item in this package** — it is wrong in the same direction for every future consumer |
| **E-9** | **O-16 (v1.1.0)** — `swing_path_tilt` drifted team-wide 2025→2026 | Make peer-netting (PB-1) a standing rule for every instrumented year-over-year bat-path claim (recommended) |
| **E-10** | **O-18 / BP-0** — bunt and checked-swing exclusion | Ratify the population rule. It changed a headline: it removed a 7 mph bat-speed "collapse" that was an artifact |
| **E-11** | **BP-0/1/2, PU-1/2, PB-1** provisional | Ratify before a third reuse |
| **E-12** | **O-17** — `hyper_speed` = `max(EV, 88)` | Add a deprecation note to the glossary |
| **E-13** | **The open-item register has no ID allocator.** A concurrent session claimed **O-14** for an unrelated `bbrate` defect while this addendum was in flight; these items were renumbered O-15…O-18 before publication | Adopt an allocator so two builds cannot claim the same ID |

## 7a · v1.1.0 addendum — what it added

The DPO asked what Statcast's bat-path columns say about **how** Turner is meeting the ball, and asked
that the `domain-steward-proxy` and `source-system-profiler` establish what the columns are before
anything was built. That sequencing was honoured: six sourced semantic definitions, twelve conventions
**proven against the data** (the build refuses to publish if one fails), a technical dictionary, KPI specs
and column-level lineage — all in `03a` — before a single number was produced.

**Finding.** Two measures changed and both clear the noise bar: the swing plane flattened
**27.9° → 25.5°** (peer-netted −1.20°, largest in an 8-hitter cohort; **the flattest of 11 Phillies**,
against an MLB average of ~32°) and the contact point moved **1.35″ further from his body**
(**+1.70″ on breaking balls**). Popup rate on **breaking balls 3.9% → 12.1%** while fastball and offspeed
were flat; he went from **rank 6 of 12 — exactly the peer median — to rank 1 of 10**. **Bat speed is up**,
so the v1.0.0 conclusion survives from a second, independent direction.

**And the governance argued with itself again.** An ungoverned swing population showed a 7 mph bat-speed
collapse on breaking-ball popups — the most quotable number in the addendum. The **BP-0** population rule
(O-18: exclude bunts, flag sub-25 mph checked swings) reduced it to −0.5 mph, inside noise. **In v1.0.0
ST-1 killed a bat-speed story; in v1.1.0 BP-0 killed a bat-speed story.** Both times the surviving finding
was geometric.

## 8 · Publish recommendation

**PUBLISH — internal, Baseball Operations.** Certification is READY; verification is 711/711; DQ carries 0 FAIL; the parent product is reproduced in full; every floor, defect, and structural limit is disclosed
on the consumable surfaces. The player-facing brief in `06` is the only surface scoped for the subject
himself, and it excludes the decline framing and the persona table. **No external publication surface is
proposed.** The publish decision belongs to the human Data Product Owner.
