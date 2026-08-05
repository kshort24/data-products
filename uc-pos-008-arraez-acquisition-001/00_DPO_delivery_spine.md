# 00 — DPO Delivery Spine

**Agent:** `data-product-owner` (orchestrator) · **Use case:** `uc-pos-008-arraez-acquisition-001`
**Value stream:** `pos` (Phillies position players)
**Ledger IDs:** UC **#32** · contract `uc-pos-008` · build artifact `dp_uc31`
**Human DPO:** Kellen Short · **Date:** 2026-08-04
**Recommendation:** ✅ **Ready to publish** — pending human acknowledgment of 6 open items, one of which is **blocking for circulation** (OI-1).

This is the spine: the sequenced delivery plan, the governance gates checked at each handoff, and the publish recommendation. Department detail lives in 01–07.

---

## The ask, in one line

> *"Luis Arraez — the headline deadline acquisition, a three-time batting champion who has reshuffled the infield and pushed Harper back to the outfield. Analyse his top-line results then the underlying indicators. I want to see his proclivity to collect hits with two strikes, the pitch groups and handedness he can slug, and his performance with runners in scoring position. Consider actions for personas in the batting department, though I expect his approach needs little guidance. The decision that interests me is where to hit him: Mattingly has him at cleanup because that spot sees the most men on base — but would the top of the order make more sense? Maybe swap him and Schwarber. And as a stretch: can we model his impact on run creation by lineup slot?"*

**One consumer, one decision, one player the organisation has never employed.** The deliverable is an onboarding dossier plus a decision model — not an opponent attack plan and not a performance review.

---

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 1 — Intake & Discovery | Strategy & Intake | ✅ complete (**GO**, 0 blocking, 7 non-blocking gaps) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ complete — 7 new KPIs specified before use |
| 3 — Build | Engineering (Build) | ✅ complete — 30 CSV receipts, 6 figures, 24/24 DQ |
| 4 — Certify | Quality | ✅ **READY** — 368/368 independent checks, 0 FAIL |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ branded PDF (12pp) + interactive dashboard + markdown source |
| 6 — Operations | Platform (persistent) | ✅ closure step defined (re-read at 150 PA in a Phillies uniform) |

**Front door:** `visual-intake-agent` skipped — the request arrived as written prose from the human DPO. Sequence started at `use-case-validator`.

**Pattern inheritance.** UC#21 / dp_uc20 (Schwarber — hitter retrospective, locked KPI kernel) → UC#25 / dp_uc24 (Turner — hitter diagnosis, RF-1/RF-2 trajectory KPIs, interactive consumable) → UC#30 / dp_uc29 (Kilian — first acquisition-onboarding variant) → UC#31 / dp_uc30 (Raley — population-benchmark pattern, proxy-ships-with-calibration rule) → **UC#32 (this one).**

---

## What is genuinely new in this UC

**1. The first decision model in either value stream.** Every prior UC in this repo describes. This one is asked to *choose* — where does the player bat. AR-6 Slot-Projected Run Contribution answers it by composing two independently observed quantities (a slot's opportunity mix; a hitter's context-specific run-expectancy contribution) with no simulation and no assumed transition matrix. **New house rule established: a decision model must be decomposable into separately observable, separately receipted components, and must publish the specific second-order effect it does not capture.** Here that effect is the feedback of re-ordering on the opportunity weights themselves, stated in the report body and in §4 of the architecture doc.

**2. First position-player acquisition-onboarding variant.** UC#30 and UC#31 established the shape for pitchers. This transfers it to hitters and adds the "who bats behind him" dimension that has no pitcher analogue (AR-7 Table-Setting Value).

**3. A consumer premise was contradicted by the data and the product priced both readings rather than choosing.** The request states Schwarber is the leadoff hitter; the log says Turner (399 PA vs 95). Rather than silently correcting the consumer or silently accepting the premise, the build prices **both framings** and escalates the conflict as **OI-1**. This is now the standard response to a manual carry-in that contradicts the pitch log: *price both, escalate, do not choose.*

**4. A units defect was caught and corrected during build, not after.** The first AR-7 implementation multiplied a count of baserunners by a per-plate-appearance rate, producing a column with no coherent unit. It was reworked onto a per-runner conversion basis, explicitly labelled an upper bound, and flagged as non-additive with AR-6 to prevent double-counting. See 05 §4.

**5. Two verification failures were investigated to root cause rather than tolerated.** The first harness run returned 330/351 with 21 failures. Both failure classes were real and both were benign; neither was silenced. See 07 §3.

---

## Evidence-window decision (DPO, 2026-08-04)

The human DPO was offered three windows and chose: **2026 only as primary, prior seasons as shadow.**

| Tier | Window | Volume | Role in the deliverable |
|---|---|---|---|
| **Primary** | 2026-03-26 → 2026-08-02 | 1,727 pitches / 464 PA | **Carries every forward-looking claim.** All benchmarking, all model inputs |
| **Shadow** | 2019-05-18 → 2025-09-28 | 13,501 pitches / 3,533 PA | Stability backdrop only. Proves the profile is durable; carries no forward-looking claim |

**Consequence accepted by the DPO:** the RISP cut (89 PA) and the group × hand cuts (one cell at 4 balls in play) are thin. Mitigation: sample size is printed on every row of every split table, thin cells are flagged programmatically at <15 BIP, and the report states the stability range from the shadow tier wherever a thin primary number carries weight.

---

## Governance gates checked at handoff

| Gate (CLAUDE.md governance principle) | Where enforced | Result |
|---|---|---|
| **1. No CDE inference** | 02 glossary | ✅ All terms locked-inherited or explicitly flagged report-local. Seven report-local terms (AR-1 … AR-7) defined from existing physical CDEs and returned to the DPO as promotion candidates — no business meaning invented |
| **2. No pipeline build without approved specs** | 04 → build | ✅ All seven new KPIs written to spec (plain language + formula + grain + population + CDEs + edge cases) **before** appearing in any output |
| **3. No publish without certification** | 07 | ✅ `certification-agent` returns READY; 368/368 independent verification, 24/24 build DQ |
| **4. No breaking changes without notice** | 07 §5 | ✅ n/a — new data product, no consumers to break. Locked KPI functions inherited byte-identical from `dp_uc24`; the `truncated_pa` fork is additive and documented, not a redefinition |
| **5. Privacy flags block external publish** | 02 §4 | ✅ No PII beyond public MLBAM identifiers. **Internal — Restricted:** contains acquisition-evaluation judgments and a regression forecast about a current employee |

---

## Agent sequence and handoffs

| # | Agent | Consumed | Produced | Gate |
|---|---|---|---|---|
| 1 | `use-case-validator` | DPO prose | gap report: 0 blocking, 7 non-blocking | **GO** |
| 2 | `source-system-profiler` | `arraez.parquet`, `phils_2026.parquet` | entity lock, window fitness, zero-Phillies-rows finding | ✅ |
| 3 | `domain-steward-proxy` | repo history, prior UCs | `truncated_pa` quirk, xwOBAcon O4 carry-forward, lineup-slot derivability | ✅ |
| 4 | `business-glossary-agent` | CDE list | 7 report-local terms; 0 inferred definitions | ✅ |
| 5 | `data-architect` | profile + glossary | PA-spine grain design, slot reconstruction method | ✅ |
| 6 | `kpi-calculator` | business questions | AR-1 … AR-7 specs | ✅ |
| 7 | `join-validator` | slot reconstruction | 111/112 clean; 1 exception root-caused to `truncated_pa` | ✅ |
| 8 | `dq-rule-definer` | KPI specs | 24 rules across 6 dimensions | ✅ |
| 9 | `data-engineer` | specs | `dp_uc31_arraez_acquisition_read.py`, 30 receipts, 6 figures | ✅ |
| 10 | `data-quality-engineer` | build | 24/24 DQ scorecard | ✅ |
| 11 | `certification-agent` | everything | 368/368 verification; READY | ✅ |
| 12 | `analytics-enabler` ∥ `dashboard-specifier` | certified receipts | 12pp PDF, interactive dashboard | ✅ |
| 13 | `privacy-watchdog` | all outputs | Internal — Restricted classification | ✅ |
| 14 | `version-controller` | KPI register | v1.0.0; 7 provisional KPIs pending ratification | ✅ |

---

## Open items for the human DPO

| # | Item | Severity | Ask |
|---|---|---|---|
| **OI-1** | **Leadoff premise conflict.** Request says Schwarber leads off; the log through 2026-08-02 says Turner (399 PA vs 95; Schwarber has not led off since June). Both framings priced; neither chosen | **BLOCKING for circulation** | Confirm the current lineup card before this goes to the manager or coaching staff. The recommendation differs by sign between framings (−2.58 vs +0.65 runs) |
| OI-2 | AR-1 … AR-7 are **provisional**. Seven new KPIs is the largest batch this repo has introduced in one UC | Non-blocking | Ratify or amend at glossary review. AR-1 (Two-Strike Survival) and AR-4 (Scoring-Position Conversion) are the strongest promotion candidates — both are roster-general, not Arraez-specific |
| OI-3 | **O4 carry-forward** (`xwobacon` `size` semantics, opened in `uc-pps-025`). Still unpatched; honest denominator published alongside as `xwoba_con_n` | Non-blocking | Schedule the coordinated version bump across `dp_uc28`/`dp_uc29`/`dp_uc30`/`dp_uc31` |
| OI-4 | **O5 (new): `truncated_pa` definitional fork.** Locked `get_stats` counts it as a PA; the new strict PA spine does not. Affects 2021 (1) and 2025 (2); **2026 primary window unaffected** | Non-blocking | Decide whether the locked kernel should be amended at the next version bump. Do not patch mid-build — it is shared with four prior UCs |
| OI-5 | **AR-6 holds opportunity weights fixed.** Re-ordering the lineup would change `W(s,c)` slightly; the model does not capture the feedback | Non-blocking | Accept as a stated limitation, or commission a Markov extension as a follow-on UC |
| OI-6 | **No Citizens Bank Park adjustment.** Everything is inferred from a Giants hitter in Giants parks | Non-blocking | The `uc-pos-007` loanDepot venue-split pattern could be applied as a follow-on if the DPO wants a park-adjusted read |

---

## Publish recommendation

**Ready to publish, with one gate.** The build is certified: 368/368 independent checks, 24/24 build DQ, every published number traced to a CSV receipt, no number computed outside the build script.

**OI-1 must be resolved before this reaches the manager or coaching staff**, because the lineup recommendation changes sign depending on which lineup is real. It does not block circulation to the analytics group, for whom both framings are informative.

Everything else is a disclosure, not a defect.

## Closure step

Re-read at **150 plate appearances in a Phillies uniform**, testing three specific projections made here:

1. wOBA regresses from .337 toward **.300–.310** (the xwOBA gap closes).
2. Production against left-handed pitching declines toward the **.256 xwOBA**, not the .441 SLG.
3. Two-strike survival rate holds **above .85** — the one skill claimed to be durable.

If (3) fails, the entire acquisition thesis needs revisiting and this UC should be superseded rather than amended.
