# 00 — DPO Delivery Spine

**Agent:** `data-product-owner` (orchestrator) · **Use case:** `uc-pos-009-schwarber-swing-decay-001`
**Value stream:** `pos` (Phillies position players)
**Ledger IDs:** UC **#33** · contract `uc-pos-009` · build artifact `dp_uc32`
**Human DPO:** Kellen Short · **Date:** 2026-08-08
**Recommendation:** ✅ **Ready to publish** — Internal — Restricted. 8 open items, **none blocking**.

This is the spine: the sequenced delivery plan, the governance gates checked at each handoff, and the publish recommendation. Department detail lives in 01–07.

---

## The ask, in one line

> *"I am concerned about the state of Kyle Schwarber's swing. He has lost some pop in his bat as the season has progressed. How do these underlying indicators inform decisions that can be made against this use case? Provide an assessment on the state of things then consider personas within the value stream and the types of actions they can take to drive better expected outcomes."*
>
> Plus: a working KPI block at `player_name × game_year × stand`; a stated concern about **mean-imputing bat-speed NULLs**; a request for **sweet spot / ideal launch angle** and **anything about swing path**; PDF required; dashboard if sensible.

**One consumer, one player, one diagnostic question — and a governance question smuggled inside it.** The deliverable is a state-of-play assessment plus persona actions. It is not a scouting report and not a projection.

---

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 1 — Intake & Discovery | Strategy & Intake ∥ Governance | ✅ complete (**GO**, 0 blocking, 8 non-blocking gaps) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ complete — 9 new KPIs specified before use |
| 3 — Build | Engineering (Build) | ✅ complete — 24 CSV receipts, 5 figures, 24/24 DQ |
| 4 — Certify | Quality | ✅ **READY** — 59/59 independent verification, 0 FAIL |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ branded PDF (500 KB) + interactive dashboard (104 KB) + markdown source |
| 6 — Operations | Platform (persistent) | ✅ monitoring rules + runbook + closure step defined |

**Front door:** `visual-intake-agent` skipped — the request arrived as written prose with an embedded code block from the human DPO. Sequence started at `use-case-validator`.

**Pattern inheritance.** UC#21 / dp_uc20 (Schwarber first-half — same entity, locked KPI kernel) → UC#25 / dp_uc24 (Turner down-year diagnosis — *is it decline or variance*, the closest structural analogue) → UC#31 / dp_uc30 (Raley — population benchmark, proxy-ships-with-calibration) → UC#32 / dp_uc31 (Arraez — receipt naming, DQ shape, dashboard architecture) → **UC#33 (this one).**

---

## What is genuinely new in this UC

**1. The first governance decision that changed a finding.** The DPO asked whether mean-imputing bat-speed NULLs was sound. It was not. Nine of twelve seasons have **zero** coverage; imputation would have fabricated **7,021 swings — 67.7% of the career series** — at a single value with zero variance, drawing a flat nine-season bat-speed line that was never measured. The rejected policy is quantified in a receipt (`x1_imputation_harm`) and rendered as a figure, so the *cost of the alternative* is itself a published artefact rather than an assertion. **New house rule proposed (OI-1):** missing-because-the-instrument-did-not-exist is **out-of-scope data**, not missing data.

**2. A requested KPI was found to be actively misleading, and the product said so.** The DPO asked for sweet-spot %. Sweet-spot % **rose** (40.8% → 43.4%) across a phase in which slugging fell 27.2%. So did hard-hit rate and squared-up rate. The 8–32° band scores an 8° line drive and a 30° fly ball identically, which is fatal for a hitter whose value lives in the top third of it. The product delivers the metric, demonstrates the failure, and proposes replacements (SW-2, SW-8). **New house rule: when a requested KPI fails on the delivered data, ship it with the demonstration of failure — do not substitute silently.**

**3. The supplied grain could not answer the supplied question.** `game_year` is annual; "as the season has progressed" is intra-annual. The architect replaced it with a **data-driven phase split at the chronological midpoint of balls in play** (equal evidence weight, 120 vs 122) plus rolling 60-BIP windows. A calendar split at the All-Star break would have been 156 vs 86 and the delta would have been partly a denominator artefact. **New house rule: intra-season splits are balanced on evidence, not on time.**

**4. The premise was inverted, and the product priced both readings.** The consumer's model was "he has lost pop" — implying physical decline. Bat speed is **74.2 mph in 2025 and 2026**, 90th percentile 81.0 in both halves of 2026, swing shape unchanged. The decline is real but its mechanism is a **launch-angle redistribution** plus a nine-year-high chase rate. The report neither accepts the premise nor dismisses the concern: §1 prices the baseline honestly (2026 is a *normal* Schwarber season; 2025 was his career best), §2 confirms the within-season decline is real and steep, §3 identifies the mechanism.

**5. An honest caveat reversed a tempting conclusion.** Contact depth fell 33.79 → 32.03 inches across the split — which reads as lost extension. But his **2025 season mean was 31.98**. Phase B is his normal; **Phase A was the anomaly.** This is stated in the report, encoded as an interpretation rule in the SW-6 spec, and pinned by verification checks V-46 and V-47. **Verification checks now guard the report's humility, not only its findings.**

---

## Evidence-window decision (DPO, 2026-08-08)

The DPO was offered four comparison frames and chose **within-2026 time trend as primary**. Career and peer framings ship as secondary context.

Three evidence windows coexist in one table, and every KPI declares which it lives in:

| Window | Span | Fields | Role |
|---|---|---|---|
| **Full career** | 2015 → 2026-08-07 | results, EV, LA, barrel, sweet spot, discipline | Baseline pricing (§1) |
| **Bat tracking** | 2024 → 2026 | `bat_speed`, `swing_length` | **Carries the central claim.** 3 seasons |
| **Swing path** | 2025 → 2026 | `attack_angle`, `attack_direction`, `swing_path_tilt`, `intercept_*` | Corroboration only. **1 comparison season** |

**Consequence accepted by the DPO:** swing-path claims are year-over-year checks, not trends; the phase split is 120/122 BIP, which is thin. Mitigation: sample size printed on every row of every split, thin cells (< 15 BIP) flagged programmatically, and the report's §10 states the magnitude will regress even though the direction is corroborated by four independent measures.

---

## Governance gates checked at handoff

| Gate (CLAUDE.md governance principle) | Where enforced | Result |
|---|---|---|
| **1. No CDE inference** | 02 glossary | ✅ Nine report-local terms (SW-1…SW-9), each composed from existing physical CDEs or a published Statcast definition with the source named. Zero business meanings invented; all returned as promotion candidates |
| **2. No pipeline build without approved specs** | 04 §3 → build | ✅ All nine written to spec (plain language + formula + grain + population + CDEs + edge cases) **before** appearing in any output. SW-8 emerged from analysis and was specified before publication |
| **3. No publish without certification** | 07 | ✅ `certification-agent` returns READY; 59/59 independent verification, 24/24 build DQ |
| **4. No breaking changes without notice** | 07 §5 | ✅ n/a — new product, no consumers. Locked kernel inherited byte-identical from `Baseball Functions.ipynb` |
| **5. Privacy flags block external publish** | 02 §6 | ✅ **Internal — Restricted.** PW-2 (the opposing-scout mirror view is a live vulnerability disclosure) blocks external publication |

---

## Agent sequence and handoffs

| # | Agent | Consumed | Produced | Gate |
|---|---|---|---|---|
| 1 | `use-case-validator` | DPO prose + code block | gap report: 0 blocking, 8 non-blocking | **GO** |
| 2 | `source-system-profiler` | `phils_*.parquet`, `schwarber.parquet` | entity lock, **three-window sensor finding**, 2023-coverage correction | ✅ |
| 3 | `domain-steward-proxy` | repo history, prior UCs | 7 rules, 6 quirks, O2/O4/O5 carry-forwards | ✅ |
| 4 | `business-glossary-agent` | CDE list | SW-1…SW-9 + the evidence-window vocabulary; 0 inferred definitions | ✅ |
| 5 | `eda-agent` | locked frame | 8 findings — E-4 (the dissociation) and E-5 (the sweet-spot paradox) redirected the whole product | ✅ |
| 6 | `data-architect` | profile + glossary + EDA | single-grain model, data-driven phase split, coverage-gate enforcement | ✅ |
| 7 | `kpi-calculator` | business questions | SW-1…SW-9 specs | ✅ |
| 8 | `metadata-mapper` ∥ `data-dictionary` | physical schema | 30 exact / 1 fuzzy / 1 unmapped; full output dictionary | ✅ |
| 9 | `technical-lineage-builder` | model + specs | 6-hop lineage, column-level, incl. the deliberate-null step | ✅ |
| 10 | `dq-rule-definer` | KPI specs | 24 rules across 6 dimensions; **4 enforce the NULL policy** | ✅ |
| 11 | `join-validator` | model | 7 operations, **0 exceptions** — no-join design | ✅ |
| 12 | `data-engineer` | specs | build script, 24 receipts, 5 figures; 3 defects fixed at build time | ✅ |
| 13 | `data-quality-engineer` | build | 24/24 DQ scorecard | ✅ |
| 14 | `certification-agent` | everything | 59/59 verification; **READY** | ✅ |
| 15 | `semantic-modeler` | KPI register | aggregation constraints + 7 binding consumption rules | ✅ |
| 16 | `analytics-enabler` ∥ `consumer-onboarding-agent` ∥ `dashboard-specifier` ∥ `query-builder` | certified receipts | PDF, dashboard, 7 persona guides, 6 query templates + 1 anti-pattern | ✅ |
| 17 | `data-tagger` ∥ `privacy-watchdog` | all outputs | tagging proposal; Internal — Restricted, external blocked | ✅ |
| 18 | `version-controller` ∥ `data-observability` ∥ `cost-watchdog` | build + register | v1.0.0; 7 monitoring rules + runbook; 4 ranked cost findings | ✅ |

---

## Open items for the human DPO

| # | Item | Severity | Ask |
|---|---|---|---|
| **OI-1** | **Sensor-boundary NULL standard.** Enforced here by four DQ rules and quantified by a receipt | Non-blocking, **high value** | **Promote to a repository-wide governance principle in `CLAUDE.md`.** Generalises past baseball to any sensor-era field in any data product |
| **OI-2** | **SW-1 Sweet-Spot Rate is unsafe alone for power hitters.** Rose 6.4% while SLG fell 27.2% | Non-blocking | Ratify SW-2, SW-7, SW-8 for promotion (all roster-general). Decide whether SW-1 carries a standing warning label |
| **OI-3** | **SW-4 / SW-9 provisional** — Statcast's 1.23 / 0.2306 constants are published approximations (the plate-speed derivation is exact) | Non-blocking | Ratify as directional, or commission a calibration |
| **OI-4** | **SW-8 band validated for one hitter.** 20–32° is where *Schwarber's* value concentrates | Non-blocking | Validate per-archetype before roster-wide use |
| **OI-5** | **O4 carry-forward** (`xwobacon` `size` semantics) still unpatched repo-wide | Non-blocking | This build avoids it; schedule the coordinated version bump |
| **OI-6** | **Nullable-dtype masking defect** will hit any future agent masking a Statcast numeric column | Non-blocking | Add `coerce_numeric` guidance to `references/data-quality.md` |
| **OI-7** | **No opponent-quality adjustment** — the largest unmodelled confounder behind the breaking-ball finding | Non-blocking | Accept as stated, or commission a follow-on |
| **OI-8** | **Intake note corrected** — 2023 bat-speed coverage is 0.0%, not "very limited" | Informational | Acknowledge; pinned by V-20 |

---

## Publish recommendation

**Ready to publish, internally.** The build is certified: 59/59 independent verification, 24/24 build DQ, 24 receipts, **zero manual carry-ins**, and no number in any deliverable computed outside the build script.

**Blocked for external publication** — §8.7 of the report enumerates three exploitable weaknesses. That section is the point of the product internally and a self-inflicted wound externally.

**One distribution control:** §8.5 (Front Office) contains contract and valuation language about a current player. It should not circulate to the clubhouse alongside §8.1 and §8.2, which are written for the coaching staff and the player.

Everything else is a disclosure, not a defect.

---

## Closure step

Re-read at **150 additional plate appearances** (approximately 2026-09-10), testing three falsifiable projections:

1. **Bat speed holds at 74 ± 0.5 mph.** If it drops below 73, the central claim of this report is wrong and the aging interpretation returns.
2. **Damage-Band Rate (SW-8, 20–32°) recovers above 18%.** If it stays below 15% with bat speed intact, the problem is durable mechanical timing rather than a slump, and the hitting-coach action set in §8.1 needs rewriting.
3. **Chase rate falls below 24%.** If it does not, the decision-making explanation hardens and the intervention shifts entirely to approach.

**If (1) fails, supersede this UC rather than amend it.** The whole product is built on the premise that the engine is intact.
