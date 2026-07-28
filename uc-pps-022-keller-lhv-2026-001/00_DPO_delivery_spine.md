# 00 — DPO Delivery Spine
## UC #27 · `uc-pps-022` · `dp_uc26` — Brian Keller (RHP), Lehigh Valley 2026

**Orchestrator:** `data-product-owner`
**Value stream:** Phillies Pitching & Defense (pps)
**Requested by:** Kellen Short (business user / human DPO)
**Request date:** 2026-07-24
**Data plane:** `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB`
**Governance plane:** `Agents for Data Products` (this repo)
**Publish recommendation:** **PUBLISH — internal, with two standing caveats** (see §6)

---

## 1. Ledger claim

| Field | Value |
|---|---|
| UC number | **27** |
| Use-case id | `uc-pps-022` |
| Build id | `dp_uc26` |
| Prior UC | #26 / `uc-pps-021` / `dp_uc25` — Nola vs Dodgers, delivered 2026-07-22 |
| Next available after this | **UC #28 / `dp_uc27`** (`uc-pps-023` / `uc-pos-007`) |

> **Ledger action required.** The installed `pitcher-scouting-report` skill's
> `references/uc-ledger.md` still reads "Next available: UC #12" and is ~15 use cases
> stale. This row must be appended by hand:
>
> `| 27 | uc-pps-022 | Brian Keller LHV/AAA 2026 | Delivered | data-products/uc-pps-022-keller-lhv-2026-001/ — first AAA-primary UC; PROVISIONAL SR-M1 |`

---

## 2. Use case as received

> Analyze Brian Keller's pitching performance for the Lehigh Valley IronPigs in 2026. He
> appears in the opponents dataframe. Start with high-level results — expect good
> performance in a limited sample. Then dive into the underlying indicators explaining
> those results. Tie these to plausible actions for Phillies personas: Keller himself, the
> manager, the pitching staff, and J.T. Realmuto as catcher. Part of the report should
> inform his gameplan — how should he call the game? Deliver a PDF report. Also take the
> supplied `tm_success_rate` function and prep it for ratification.

**DPO scope decisions taken at intake** (confirmed with the human DPO before Layer 1):

| Decision | Choice | Consequence |
|---|---|---|
| Gameplan frame | **Projected MLB call-up / debut** | Realmuto persona is in scope; an explicit AAA→MLB translation caveat becomes a blocking documentation requirement |
| SR-M1 handling | **Provisional — computed, published under banner, ratification packet produced** | SR-M1 appears in the report but is not inheritable by any downstream UC |
| Extra artifacts | **Realmuto game-calling card + independent verification harness** | Two additional Layer-4 deliverables |

---

## 3. Agent sequencing and gate results

### Layer 1 — Intake & Discovery

| Agent | Output | Gate |
|---|---|---|
| `use-case-validator` | 5 gaps: 0 blocking, 5 non-blocking | **PASS — proceed** |
| `source-system-profiler` | `lhvp26.parquet` slice, 533 pitches / 146 BF / 8 starts, fitness by CDE | **PASS** |
| `domain-steward-proxy` | Level-translation rules, AAA tracking-fidelity notes, the Brad Keller trap | **PASS** |
| `business-glossary-agent` | 0 new CDEs required; 1 new *candidate* term (SR-M1) routed to ratification | **PASS with condition** |

**Gate 1 verdict:** cleared 2026-07-24. See `01_`, `02_`.

### Layer 2 — Design

| Agent | Output | Gate |
|---|---|---|
| `data-architect` | Single-grain pitch-level model, no joins beyond the wOBA-constants dimension | **PASS** |
| `kpi-calculator` | 11 locked KPIs inherited verbatim; 1 PROVISIONAL (SR-M1) specced | **PASS with condition** |
| `eda-agent` | Distribution/outlier pass; surfaced the recency inflection that became the report spine | **PASS** |
| `join-validator` | Only join is `game_year → Season`; no fan-out possible | **PASS** |
| `dq-rule-definer` | 16 rules across 6 dimensions | **PASS** |
| `metadata-mapper` | 34 physical columns → glossary terms; 0 unmapped, 0 ambiguous | **PASS** |
| `data-dictionary` | Published column/table descriptions | **PASS** |
| `data-tagger` | Sensitivity: PUBLIC-DERIVED. Domain: Pitching. No PII | **PASS** |

**Gate 2 verdict:** cleared. See `03_`, `04_`, `05_`.

### Layer 3 — Build

| Agent | Output | Gate |
|---|---|---|
| `technical-lineage-builder` | Column-level source→target for every published number | **PASS** |
| `data-engineer` | `dp_uc26_keller_lhv_2026.py` — 25 CSV receipts + 4 figures | **PASS** |
| `data-quality-engineer` | 14-check scorecard: 10 PASS / 4 WARN / 0 FAIL; all 8 blocking PASS | **PASS** |
| `machine-learning-engineer` | **Not invoked** — no prediction/forecast in scope | n/a |

**Gate 3 verdict:** cleared. See `06_`, `07_`.

### Layer 4 — Certify & Publish

| Agent | Output | Gate |
|---|---|---|
| `certification-agent` | Artifact package complete and internally consistent | **READY** |
| `privacy-watchdog` | No PII; player performance data is public-derived | **PASS** |
| `analytics-enabler` | Reader report (`.md` + `.pdf`) | **Delivered** |
| `consumer-onboarding-agent` | Realmuto game-calling card (`.pdf`) | **Delivered** |
| `version-controller` | v1.0.0 — new product, no breaking changes | **PASS** |
| `data-observability` | Refresh triggers + drift watches defined in `07_` | **PASS** |
| `cost-watchdog` | Single-file read, ~15k rows, <10s runtime — nothing to optimize | **PASS — no findings** |

---

## 4. Governance principle compliance

| # | Principle | Status |
|---|---|---|
| 1 | No CDE inference | **HELD.** No agent defined a business meaning. SR-M1 — the one term without an approved definition — was *not* silently defined; the ambiguity was quantified and returned to the DPO (`04_ §SR-M1`) |
| 2 | No pipeline build without approved specs | **HELD.** Build followed `04_` and `06_`; locked KPI kernel copied verbatim from `dp_uc25`, not re-derived |
| 3 | No publish without certification | **HELD.** `certification-agent` returned READY before this spine was signed |
| 4 | No breaking changes without notice | **HELD.** v1.0.0, new product. SR-M1 is explicitly non-inheritable, so no downstream UC can be broken by a later ratification decision |
| 5 | Privacy flags block external publish | **HELD.** No flags raised; internal distribution only |

---

## 5. What this product answers

1. **Are the results real?** Yes as results, partly as process. `.268` wOBA allowed against a
   `.343` league-staff baseline is a top-of-staff line. But `xwOBAcon` of `.348` against a
   `.358` baseline says contact suppression is roughly *average* — the surplus is coming from
   walk avoidance, strikeouts, and some batted-ball fortune, not from missing barrels.
2. **What is driving it?** A mid-June approach change. Four-seam usage fell 51.4% → 35.5%,
   sinker usage rose 11.7% → 24.3%, and command, chase, and contact quality all moved with it.
3. **Where is the exposure?** Left-handed hitters, second time through the order, and the
   elevated four-seam — the three overlap and account for all five home runs allowed.
4. **What is the gameplan?** Cutter to start at-bats, sinker as a *strike* not a chase pitch,
   slider far more often with two strikes to both sides — see `07_` and the persona card.

---

## 6. Publish decision

**PUBLISH — internal (Phillies pitching, player development, advance scouting).**

Two caveats travel with every copy of this product and are printed on the report's first page:

1. **Level translation is unmodelled.** Every number is AAA. Keller has thrown zero MLB
   pitches. No AAA→MLB translation factor is applied because none is available in the repo.
   Directional conclusions transfer; magnitudes do not.
2. **SR-M1 is PROVISIONAL.** The Mayza Success Rate is published under a banner and is not
   ratified. `04_ §SR-M1` shows the as-written implementation returns `.411` while the
   literal reading of the stated business intent returns `.637`. **The DPO must ratify a
   variant before SR-M1 is cited outside this document or inherited by another UC.**

**Escalations to the human DPO:** 3 open items, listed in `07_ §5`.

**Signed:** `data-product-owner`, 2026-07-24.
