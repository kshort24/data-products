# 00 — DPO Delivery Spine
## UC #28 · `uc-pos-007` · `dp_uc27` — Phillies hitters at loanDepot park (venue split + Alcantara lens)

**Orchestrator:** `data-product-owner`
**Value stream:** Phillies Position Player / Offense (pos)
**Requested by:** Kellen Short (business user / human DPO)
**Request date:** 2026-07-27
**Target event:** PHI @ MIA, 2026-07-28, 6:40 pm ET — Sandy Alcantara (RHP) vs Aaron Nola (RHP)
**Data plane:** `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB`
**Governance plane:** `Agents for Data Products` (this repo)
**Publish recommendation:** **PUBLISH — internal, with three standing caveats** (see §6)

---

## 1. Ledger claim

| Field | Value |
|---|---|
| UC number | **28** |
| Use-case id | `uc-pos-007` |
| Build id | `dp_uc27` |
| Prior UC | #27 / `uc-pps-022` / `dp_uc26` — Brian Keller LHV 2026, delivered 2026-07-24 |
| Next available after this | **UC #29 / `dp_uc28`** (`uc-pos-008` / `uc-pps-023`) |

> **Ledger action required.** The installed `pitcher-scouting-report` skill's
> `references/uc-ledger.md` still reads "Next available: UC #12" and is now ~16 use cases
> stale. This row must be appended by hand:
>
> `| 28 | uc-pos-007 | Phillies hitters at loanDepot park + Alcantara lens | Delivered | data-products/uc-pos-007-loandepot-venue-split-001/ — first venue-cohort UC; PROVISIONAL VD-1/VD-2 |`

---

## 2. Use case as received

> Examine the performance of Phillies batters against their historical careers at loanDepot
> park in Miami — compare batting performance in Miami against performance in all other
> parks. A code snippet supplies the hitter list and the venue-flag approach; add Derek Hill
> and Edmundo Sosa; skip Bryan De La Cruz (no parquet pulled). The `nphl` frame carries
> minor-league rows for players like Rincones and Crawford — handle that. Preview the
> offensive performance for the July 28 game, started by Alcantara in Miami, in the context
> of performance vs RHP in other parks against performance in Miami vs RHP. Then, as a
> different perspective, compare to Sandy Alcantara. Identify players to watch, potential
> actions for Phillies personas, and any trends. Deliver a PDF.

**DPO scope decisions taken at intake** (confirmed with the human DPO before Layer 1):

| Decision | Choice | Consequence |
|---|---|---|
| Alcantara packaging | **Second perspective inside one UC**, not a separate `uc-pps` | One coherent game preview; the Alcantara lens is scoped to head-to-head and arsenal-vs-this-roster, not a full advance scout of the pitcher |
| Roster scope | **The nine names in the requester's snippet + Hill + Sosa**; De La Cruz excluded | 11-hitter entity lock; Rincones Jr. carried through the pipeline despite zero Miami PA so the absence is documented rather than silent |
| Sample handling | **Report below-gate hitters under a banner rather than drop them** | Sosa (25 PA) and Crawford (10 PA) appear in tables, are excluded from every pooled figure and every conclusion |
| Deliverable depth | **Full governance package** + PDF report + persona card + verification harness | Four Layer-4 artifacts |

---

## 3. Agent sequencing and gate results

### Layer 1 — Intake & Discovery

| Agent | Output | Gate |
|---|---|---|
| `use-case-validator` | 7 gaps: **1 blocking** (venue cohort undefined — `home_team` is a proxy, not a venue id), 6 non-blocking. Blocking gap resolved at intake by DPO ruling (§4 of `01_`) | **PASS after resolution** |
| `source-system-profiler` | 30 parquet sources scanned; 11 entity-locked hitters; naive-union inflation quantified per hitter (6–18%); MiLB contamination quantified (Rincones 45%, Crawford 33% of non-Miami pitches) | **PASS with findings** |
| `domain-steward-proxy` | Three domain rules surfaced that no agent could have inferred: the Realmuto/Hill Marlins-tenure confound, the 2017 Irma relocation, the loanDepot park-configuration changes | **PASS — materially changed the design** |
| `business-glossary-agent` | 2 new CDEs required (Venue Cohort, Competition Level); 2 new candidate KPI terms (VD-1, VD-2) routed to ratification as PROVISIONAL | **PASS with condition** |

**Gate 1 verdict:** cleared 2026-07-27. See `01_`, `02_`.

### Layer 2 — Design

| Agent | Output | Gate |
|---|---|---|
| `data-architect` | Single-grain pitch-level model, union-then-dedup topology, three published cohort frames (all-rows, visitors-only, Alcantara) | **PASS** |
| `kpi-calculator` | 18 locked KPIs inherited verbatim from `dp_uc24`; 2 PROVISIONAL specced in full (`04_ §3`) | **PASS with condition** |
| `eda-agent` | Distribution pass surfaced the home-club confound as the dominant variance source — became the report spine | **PASS** |
| `join-validator` | **Found the defect that drove the build.** The requester's `pd.concat([pos, nphl])` produces 6–18% row duplication per hitter because the same pitch is carried by up to six source parquets. Fan-out quantified, dedup key proven sufficient | **PASS after remediation** |
| `dq-rule-definer` | 16 rules across 6 dimensions, 9 blocking | **PASS** |
| `metadata-mapper` | 31 physical columns → glossary terms; 0 unmapped; 1 ambiguous (`home_team` as venue proxy) escalated and resolved | **PASS** |
| `data-dictionary` | Published column/table descriptions for 24 CSV receipts | **PASS** |
| `data-tagger` | Sensitivity: PUBLIC-DERIVED. Domain: Offense. No PII | **PASS** |

**Gate 2 verdict:** cleared. See `03_`, `04_`, `05_`.

### Layer 3 — Build

| Agent | Output | Gate |
|---|---|---|
| `technical-lineage-builder` | Column-level source→target for every published number, including the four-step governance filter chain | **PASS** |
| `data-engineer` | `dp_uc27_phillies_at_loandepot.py` — 24 CSV receipts + 5 figures, ~12s runtime | **PASS** |
| `data-quality-engineer` | 16-check scorecard: 14 PASS / 2 WARN / 0 FAIL; all 9 blocking checks PASS | **PASS** |
| `machine-learning-engineer` | **Not invoked** — no prediction or forecast in scope | n/a |

**Gate 3 verdict:** cleared. See `06_`, `07_`.

### Layer 4 — Certify & Publish

| Agent | Output | Gate |
|---|---|---|
| `certification-agent` | Artifact package complete and internally consistent; independent recompute 256/256 | **READY** |
| `privacy-watchdog` | No PII; player performance data is public-derived; no quasi-identifier risk | **PASS** |
| `analytics-enabler` | Reader report (`.md` + `.pdf`, 9 pp) | **Delivered** |
| `consumer-onboarding-agent` | Hitting-coach card (`.pdf`, 1 p) | **Delivered** |
| `query-builder` | Consumption patterns documented in `07_ §4` | **Delivered** |
| `version-controller` | v1.0.0 — new product, no breaking changes | **PASS** |
| `data-observability` | Refresh triggers + drift watches defined in `07_ §5` | **PASS** |
| `cost-watchdog` | 30 parquet reads, ~150k rows pre-filter, <15s single-threaded. One finding: the full-column read of every opponents parquet is wasteful (see `07_ §6`) | **PASS — 1 low-priority finding** |

---

## 4. Governance principle compliance

| # | Principle | Status |
|---|---|---|
| 1 | No CDE inference | **HELD.** Two CDEs the pipeline needed (Venue Cohort, Competition Level) had no approved definition. Neither was silently invented by a downstream agent — both were routed to `business-glossary-agent`, defined in `02_`, and the one genuinely ambiguous case (`home_team` standing in for a venue id) was escalated to the human DPO and resolved by explicit ruling |
| 2 | No pipeline build without approved specs | **HELD.** Build followed `04_` and `06_`; the locked KPI kernel was copied verbatim from `dp_uc24`, not re-derived |
| 3 | No publish without certification | **HELD.** `certification-agent` returned READY before this spine was signed |
| 4 | No breaking changes without notice | **HELD.** v1.0.0, new product. VD-1 and VD-2 are explicitly non-inheritable, so no downstream UC can be broken by a later ratification decision |
| 5 | Privacy flags block external publish | **HELD.** No flags raised; internal distribution only |

---

## 5. What this product answers

1. **Do Phillies hitters perform differently at loanDepot park?** In the results, yes — `.720` OPS / `.311` wOBA vs `.804` / `.345` elsewhere across 1,901 Miami PA. In the causes, mostly no. The expected gap is `−.014` xwOBA against a `−.034` wOBA gap, and **45% of the Miami cohort is supplied by two hitters who were employed by the Marlins at the time** (Realmuto 783 PA, Hill 80 PA). Restricted to visiting-club rows, the gap falls to `−.008` wOBA and *inverts* on expected quality: `.391` xwOBA in Miami vs `.376` baseline, with higher hard-hit (44.8% vs 43.7%) and barrel (11.0% vs 9.4%) rates.

2. **What does that mean for July 28?** The venue is not a lineup input. Two hitters have a process-backed Miami lift (Stott +.056 wOBA on 96 PA, Marsh +.072 on 74 PA); two have positive process and negative results (Harper, Schwarber) and are the "owed runs" cases; Turner's `−.046` results gap sits on a `−.004` expected gap and is noise.

3. **How has this roster fared against Alcantara?** 309 career PA, `.353` wOBA on `.388` xwOBA — under-rewarded. In Miami against him: 163 PA, `.354` wOBA, **`.423` xwOBA**, 47.5% hard-hit, 3.7% HR rate. The slider is the exploitable pitch (`.496` xwOBA, 55.2% hard-hit, 27.7% chase); the curveball has beaten them (`.123` wOBA) and its usage has risen from 4.6% to 11.6% in the 2025–26 window while four-seam usage fell from 24.6% to 16.2%.

4. **What it does not answer.** Whether loanDepot suppresses offense *in general* — there is no league-wide park baseline in the local cache. And nothing about Alcantara's 2026 league-wide form; his own parquet ends 2025-04-12.

---

## 6. Publish decision and standing caveats

**PUBLISH — internal distribution, v1.0.0.** Signed by the orchestrating `data-product-owner`
on the strength of a READY certification, a 16-check DQ scorecard with zero blocking failures,
and a 256-check independent recompute with zero mismatches.

Three caveats travel with the product and are reproduced on the report's first page:

1. **Alcantara's 2026 form is not in the product.** His parquet ends 2025-04-12; the only 2026
   evidence is 103 pitches from one start (2026-06-17). Any statement about his current stuff
   is directional. A fresh pull before first pitch would materially improve §3 of the report.
2. **VD-1 and VD-2 are PROVISIONAL.** Their scaling divisors and classification boundaries are
   house conventions, not fitted values. They may appear in this report and may not be inherited
   by any downstream UC until ratified.
3. **The venue cohort is a proxy.** `home_team == 'MIA'` is the only venue signal in the pitch
   log. It was hand-corrected for the one known relocation; it would miss any other.

**Escalations returned to the human DPO — none blocking.** Two items for a future decision:
whether to promote VD-1/VD-2 to the glossary, and whether to commission a league-wide park-factor
baseline that would let venue studies benchmark against something other than the roster itself.

---

## 7. File map

| File | Layer | Contents |
|---|---|---|
| `00_DPO_delivery_spine.md` | Orchestration | This document |
| `01_intake_validation_and_source_profile.md` | 1 | Gap report, source fitness, entity lock, domain steward findings |
| `02_business_glossary_and_domains.md` | 1 | CDE definitions, new terms, domain rules |
| `03_data_dictionary.md` | 2 | Column and table descriptions for all receipts |
| `04_architecture_and_kpi_specs.md` | 2 | Model blueprint, locked KPI inventory, VD-1/VD-2 specs |
| `05_dq_rules_and_join_validation.md` | 2 | 16 DQ rules, join/fan-out validation report |
| `06_technical_lineage.md` | 3 | Column-level source→target lineage |
| `07_dq_scorecard_and_certification.md` | 3–4 | Scorecard results, certification verdict, consumption, observability, cost |
| `README.md` | Catalog | One-page catalog card |
| `dp_uc27_phillies_at_loandepot.py` | Receipt | Build script |
| `dp_uc27_verification.py` | Receipt | Independent recompute harness (256 checks) |
| `dp_uc27_build_pdf.py` / `dp_uc27_build_persona_card.py` | Receipt | Deliverable builders |
| `dp_uc27_phillies_at_loandepot_report.md` / `.pdf` | Deliverable | Reader report (9 pp) |
| `dp_uc27_hitting_coach_card.pdf` | Deliverable | One-page persona card |
| `out/` | Receipt | 24 CSVs + 5 figures + verification results |
