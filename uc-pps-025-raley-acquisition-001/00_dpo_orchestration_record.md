# 00 — DPO Orchestration Record

**Agent:** `data-product-owner` (orchestrator) · **Use Case:** `uc-pps-raley-acquisition-001` · **Value stream:** `pps`
**Ledger IDs:** UC **#31** · contract `uc-pps-025` · build artifact `dp_uc30`
**Human DPO:** Kellen Short · **Date:** 2026-08-04
**Recommendation:** ✅ **Ready to publish** — pending human acknowledgment of 5 non-blocking open items.

This is the spine of the package: the sequenced delivery plan, the governance gates checked at each handoff, and the publish recommendation. Department detail lives in files 01–07.

---

## The ask, in one line

> *"Brooks Raley — a wily veteran who I'm guessing provides a funky look from the left-hand side. Analyze his top-line results, then the underlying indicators, and set expectations. Summarize his approach against lefties and righties. In particular, analyse his release point against other LHPs in my historical Phillies dataset — does it impact how batters track the ball out of his hand? Then: what can the pitching department do with him, what should the battery call, and how should the manager use him out of the bullpen?"*

**Four named personas, four different decisions, one pitcher the organization has never worked with.** The deliverable is an onboarding dossier, not an opponent attack plan.

---

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 1 — Intake & Discovery | Strategy & Intake | ✅ complete (**GO**, 0 blocking, 6 non-blocking gaps) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ complete — 4 new KPIs specified before use |
| 3 — Build | Engineering (Build) | ✅ complete — 21 CSV receipts, 5 figures, 38/38 DQ |
| 4 — Certify | Quality | ✅ **READY** — 661/661 independent checks, 0 FAIL |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ artifacts staged (branded PDF, 11pp + markdown source) |
| 6 — Operations | Platform (persistent) | ✅ closure step defined (re-read at 100 BF in a Phillies uniform) |

**Front door:** `visual-intake-agent` skipped — the request arrived as written prose from the human DPO. Sequence started at `use-case-validator`.

**Pattern inheritance.** UC#3 (Luzardo deep dive) → UC#8 (Nola vs WAS, canonical flat-file) → UC#11 (Rangel, multi-level evidence) → UC#29 (Painter, first self-scout variant) → UC#30 (Kilian, first acquisition-onboarding variant) → **UC#31 (this one, second acquisition-onboarding variant)**.

---

## What is genuinely new in this UC

UC#30 established the acquisition-onboarding shape. This UC inherits it wholesale and adds two things the next three deadline reads should reuse:

1. **A benchmarked release-point study.** UC#30 asked "what did the role change do to him." This one asks "why is this look hard to pick up, and who does it play against." The answer required scoring the subject against a **population** — all 28 Phillies left-handers with ≥300 pitches since 2015 — rather than against his own history. That population-benchmark pattern generalizes to any "is this pitcher's X unusual?" question and is the reusable asset here.

2. **A proxy KPI with a published calibration.** The native `arm_angle` field exists in this repo's Phillies files only from 2025. The benchmark the consumer asked for spans 2015–2026. Rather than silently truncate the population or silently substitute a proxy, the build **derives** Release Slot Angle from release coordinates, **calibrates** it against native `arm_angle` on the 10-pitcher overlap (r = 0.831), publishes the residuals, and labels RSA a proxy everywhere it appears. **A derived metric that stands in for a missing field must ship with its calibration.** That is now the house rule.

3. **A negative result was published rather than dropped.** The Release Distinctiveness Index — one of the four new KPIs — does *not* support the report's headline (Raley scores 1.26 against a population mean of 1.20, i.e. unremarkable). It is reported as a negative finding in the report body with an explanation of why (RDI is a distance and ignores direction). Suppressing it would have made the report more persuasive and less true.

---

## Era design decision (DPO, 2026-08-04)

The human DPO was offered three evidence windows and chose: **full history, split into pre-TJ and post-TJ segments, never blended.**

| Tier | Window | Volume | Role in the deliverable |
|---|---|---|---|
| **Pre-TJ** | 2020-07-24 → 2024-04-19 | 3,162 pitches / 770 BF / 213 outings | "What he was." Sizes the delta; carries no forward-looking claim |
| *(rehab gap)* | 2024-04-20 → 2025-07-18 | — | **True gap. Never interpolated.** Asserted as 0 rows in DQ |
| **Post-TJ** | 2025-07-19 → 2026-08-02 | 1,022 pitches / 269 BF / 75 outings | "What the Phillies acquired." Carries every forward-looking claim |

The boundary is the last outing before surgery and the first outing after return — both derived from the data, not assumed.

---

## Governance gates checked at handoff

| Gate (CLAUDE.md governance principle) | Where enforced | Result |
|---|---|---|
| **1. No CDE inference** | 03 glossary | ✅ All terms locked-inherited or explicitly flagged report-local. Four report-local terms (`release_slot_angle`, `release_distinctiveness_index`, `sightline_offset`, `release_tipping_delta`) defined from existing physical CDEs, returned to DPO as promotion candidates — not invented business meaning |
| **2. No pipeline build without approved specs** | 02 → 04 | ✅ Build implements the 02 KPI specs; all four new KPIs written to spec (plain language + formula + grain + population + CDEs + edge cases) **before** appearing in any output |
| **3. No publish without certification** | 05 | ✅ `certification-agent` returns READY; 661/661 independent verification, 38/38 build DQ |
| **4. No breaking changes without notice** | 07 | ✅ n/a — new data product, no consumers to break. Locked KPI functions inherited byte-identical from `dp_uc29` |
| **5. Privacy flags block external publish** | 03 | ✅ No PII beyond public MLBAM player identifiers. **Internal use only** — contains acquisition-evaluation judgments about a current employee |

---

## Agent sequence and handoffs

| # | Agent | Consumed | Produced | Gate |
|---|---|---|---|---|
| 1 | `use-case-validator` | DPO prose | gap report: 0 blocking, 6 non-blocking | **GO** |
| 2 | `source-system-profiler` | `raley.parquet`, `phils_*.parquet` | entity lock, era boundary, benchmark scope, fitness | ✅ |
| 3 | `domain-steward-proxy` | repo history, prior UCs | TJ context, KBO gap, `arm_angle` availability quirk | ✅ |
| 4 | `business-glossary-agent` | prior glossaries | 4 report-local terms, 0 inferred CDEs | ✅ |
| 5 | `data-architect` | profile + glossary | pitch-level grain, era partition, benchmark join | ✅ |
| 6 | `kpi-calculator` | model | 8 locked KPIs inherited verbatim; 4 new specs | ✅ |
| 7 | `join-validator` | model | benchmark join is a scoring comparison, not a row join — no fan-out risk | ✅ |
| 8 | `dq-rule-definer` | CDE list | 38 rules incl. coordinate-convention assertions | ✅ |
| 9 | `technical-lineage-builder` | specs | column-level lineage, source → receipt | ✅ |
| 10 | `data-engineer` | lineage + model | `dp_uc30_..._read.py`; 21 receipts, 5 figures | ✅ |
| 11 | `data-quality-engineer` | rules + build | scorecard **38/38 PASS** | ✅ |
| 12 | `certification-agent` | all artifacts | **READY**; 661/661 independent recompute | ✅ |
| 13 | `analytics-enabler` / `consumer-onboarding-agent` | report | 3 persona sections (dept / battery / manager) | ✅ |
| 14 | `privacy-watchdog` | element list | no PII beyond public identifiers; internal-only | ✅ |
| 15 | `data-observability` | build | closure trigger + monitoring rules | ✅ |

**Not invoked and why:** `machine-learning-engineer` (no prediction task — the ask is descriptive and prescriptive), `dashboard-specifier` (single-read dossier, no recurring surface), `version-controller` (no prior version), `cost-watchdog` (local parquet, negligible cost).

---

## Open items for human DPO acknowledgment

| # | Item | Severity | Disposition |
|---|---|---|---|
| **O1** | 269 post-TJ BF. Clears the 100-BF threshold; below what stabilizes rate stats. vs-LHH split is 100 BF | Non-blocking | Every rate in the report ships with its n. Closure re-read at 100 Phillies BF |
| **O2** | Zero Phillies rows — no in-org baseline, no assigned role | Non-blocking | Structural to the acquisition variant. Opponent dimension deferred until a role exists |
| **O3** | RSA is a proxy with r = 0.831 and residuals to ±14° | Non-blocking | Calibration published; RSA labelled a proxy everywhere; native `arm_angle` preferred where present |
| **O4** | **Found by the verification harness during this build.** The inherited `xwobacon()` reports its BIP count via `.agg(..., "size")`, counting balls in play with no tracked xwOBA estimate. Means are correct; published *n* is inflated (178 vs 176 post-TJ; 462 vs 457 pre-TJ) | Non-blocking | Locked function **not edited**. Discrepancy asserted in the harness and disclosed in the report caveats. Fix belongs in the next KPI-function revision, alongside uc-pps-021 O1 |
| **O5** | Bat-tracking fields (`bat_speed`, `swing_length`) begin 2023, so pre-TJ tracking rows cover 222 of 1,450 swings | Non-blocking | Pre/post tracking comparisons labelled indicative only |

**None of these block publication.** All five are disclosed in the report's caveats section.

---

## Publish recommendation

✅ **Ready to publish, internal only.**

The build computes every published number this session against a live data layer; the independent harness reproduces all 661 of them through a different code path; the DQ scorecard is clean; the four new KPIs carry full specs and, where a proxy is involved, a published calibration; and one of the four is reported as a negative result. The three persona sections answer the four questions the human DPO asked, in the order asked.

**Closure step:** re-read at 100 batters faced in a Phillies uniform — the first genuine test of whether the sequencing recommendation (cutter over sweeper to RHH with two strikes) was adopted and whether it moved the contact-quality split.
