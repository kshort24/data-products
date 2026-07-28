# uc-pps-022 — Brian Keller (RHP), Lehigh Valley IronPigs 2026

**UC #27 · `uc-pps-022` · build `dp_uc26` · Phillies Pitching (pps) value stream**
**Delivered 2026-07-25 · Certification: READY · Publish: internal · v1.0.0**

---

## What this answers

A player report on a pitcher with no major-league book: what Brian Keller's 2026 Triple-A
results are, what is actually driving them, where the exposure is, and how a Phillies battery
should call his game if he is called up.

**Business questions, answered inline:**

| Question | Answer |
|---|---|
| Are the results as good as they look? | Yes as results — **.268 wOBA allowed vs a .343 staff baseline**. Only partly as process — **xwOBAcon .348 vs .358** is roughly average. The surplus is strike-throwing, not barrel suppression |
| What explains them? | A mid-June pitch-mix change. **Four-seam 51.4% → 35.5%, sinker 11.7% → 24.3%**, and walk rate, chase, hard-hit and xwOBAcon all moved with it |
| Where is the risk? | **Left-handed hitters, second time through, elevated four-seam** — the three overlap and account for all five home runs |
| How should the game be called? | Cutter to start, sinker at the knees, slider to finish — **especially to lefties, where the four-seam takes 58% of two-strike calls at an 18.2% whiff rate** |

---

## The read

Keller is a 32-year-old strike-thrower whose Triple-A line is better than his contact profile,
who fixed his own biggest problem in mid-June by throwing fewer four-seams, and whose remaining
exposure is almost entirely against left-handed hitters the second time through a lineup. The
largest available gain is a game-calling change, not a mechanical one: he owns a plus slider he
barely uses against lefties, and he buries his best contact-suppression pitch below the zone.

**Deliberately not answered:** whether he should be called up. That requires roster, options,
and medical information this data product does not contain.

---

## File map

| File | Layer | Contents |
|---|---|---|
| `00_DPO_delivery_spine.md` | Orchestration | Ledger claim, agent sequencing, gate results, governance-principle compliance, publish decision |
| `01_intake_validation_and_source_profile.md` | Intake & Discovery | Gap report, source fitness by CDE, entity lock, comparison-population design, domain steward notes |
| `02_business_glossary_and_domains.md` | Intake & Discovery | 16 inherited terms; SR-M1 routed as a candidate, not defined; terms deliberately not created |
| `03_data_dictionary.md` | Design | 34 physical columns → glossary CDEs, output table catalog, tagging proposal |
| `04_architecture_and_kpi_specs.md` | Design | Model blueprint, EDA findings that shaped it, locked KPI register, **§SR-M1 ratification packet** |
| `05_dq_rules_and_join_validation.md` | Design | 16 DQ rule specs across 6 dimensions (14 execute as scorecard rows, 3 as harness assertions), rules deliberately not written, join + grain assertions |
| `06_technical_lineage.md` | Build | Column-level source→target for every published number, including figure lineage |
| `07_dq_scorecard_and_certification.md` | Certify | Executed DQ scorecard, verification summary, privacy, versioning, observability runbook, escalations, certification verdict |
| **`SR-M1_ratification_packet.md`** | — | **Standalone.** Everything needed to ratify the Mayza success-rate KPI, including a hardened drop-in function. Pull this into your function-ratification session |
| `dp_uc26_keller_lhv_2026.py` | Receipt | Build script — 25 CSV receipts + 4 figures |
| `dp_uc26_verification.py` | Receipt | Independent recompute harness — **107/107 checks pass** |
| `dp_uc26_build_pdf.py` | Receipt | Branded markdown → PDF builder |
| `dp_uc26_build_persona_card.py` | Receipt | Game-calling card builder; reads receipts, hard-codes nothing |
| `dp_uc26_keller_lhv_2026_report.md` / `.pdf` | Deliverable | The reader report, 12 pages |
| `dp_uc26_keller_realmuto_card.pdf` | Deliverable | One-page dugout card for Realmuto |
| `out/dp_uc26_*.csv` | Receipt | 25 CSVs — every table in the report |
| `out/dp_uc26_fig*.png` | Receipt | 4 figures, all traceable to CSVs |
| `out/dp_uc26_verification_ledger.csv` | Receipt | 107-row reconciliation ledger |

**Reproduce:**

```bash
python dp_uc26_keller_lhv_2026.py     # receipts + figures
python dp_uc26_verification.py        # independent recompute; exits non-zero on blocking failure
python dp_uc26_build_pdf.py           # report PDF
python dp_uc26_build_persona_card.py  # Realmuto card
```

Data root resolves via `MLB_DATA_ROOT` → local `./data/opponents` → sandbox mount → absolute
Windows path. Deterministic; no sampling, no model fitting.

---

## What is new in this UC

**First AAA-primary use case in the pps value stream.** Every prior advance report had a
major-league tier as the primary evidence base. Keller has thrown zero MLB pitches, so the
Triple-A tier *is* the primary tier. Two governance consequences, both handled explicitly:

1. **A same-league comparison population is mandatory, not optional.** Every Keller rate is
   published beside the 2026 LHV staff excluding Keller (41 pitchers, 3,702 BF). A raw AAA
   number alone is uninterpretable, so `05_` makes "no rate without a benchmark" a **blocking
   DQ rule** rather than an editorial preference.
2. **The standing AAA-fidelity restriction was re-adjudicated, not ignored.** The
   `pitcher-scouting-report` skill restricts an AAA *supporting* tier to usage/velo/whiff/
   outcome counting. `01_ §B` rules that the restriction exists to stop AAA data corrupting
   MLB rates by blending — which cannot happen when there is no MLB tier — and admits EV/LA/
   xwOBA on two conditions: same-league benchmarking only, and `n` printed on every line.

**One PROVISIONAL KPI.** SR-M1 "Mayza Success Rate", supplied by the DPO. Computed, published
under a banner, and **not ratified**. The as-written implementation returns `.411`; the literal
reading of the stated intent returns `.637`. See `SR-M1_ratification_packet.md`.

---

## Governance snapshot

| | |
|---|---|
| DQ scorecard | **10 PASS · 4 WARN · 0 FAIL** — all 8 blocking checks pass |
| Independent verification | **107 / 107 pass**, 0 blocking failures |
| Governance principles 1-5 | All **HELD** — see `00_ §4` |
| Privacy | No PII, no flags. INTERNAL on competitive-sensitivity grounds |
| Certification | **READY**, conditional on two standing caveats |
| Locked KPIs re-derived | **0** — all 11 inherited verbatim from `dp_uc25` |
| New KPIs defined by an agent | **0** (SR-M1 was routed to the human DPO, not defined) |

**Two caveats travel with this product and are printed on the report's first page:**

1. **Level translation is unmodelled.** All AAA, zero MLB pitches, no translation factor
   available. Directions transfer; magnitudes do not.
2. **SR-M1 is provisional** and must not be cited outside this package or inherited by another
   use case until ratified.

---

## Open items for the human DPO

| # | Item | Where |
|---|---|---|
| **E1** | Ratify SR-M1 — six decisions R1-R6 | `SR-M1_ratification_packet.md` §5 |
| **E2** | UC ledger in the installed skill is ~15 use cases stale ("Next available: UC #12"). Row for this UC is drafted | `00_ §1` |
| **E3** | No AAA→MLB translation capability exists in the repo. Several LHV pitchers have MLB innings in the same season — the raw material for a translation study | `07_ §5` |

---

## Lineage

```
UC#3  Luzardo deep-dive        → the pitcher-side pattern
UC#8  Nola vs Nationals        → canonical flat-file pattern; edge/OOZ-CSR/air-GB KPIs
UC#11 Rangel vs Pirates        → "no MLB book" precedent; multi-level evidence tier
UC#26 Nola vs Dodgers          → locked-KPI kernel; xwOBAcon grain fix
UC#27 Keller LHV 2026 (this)   → first AAA-primary UC; provisional-KPI containment pattern
```

**Next available:** UC #28 / `dp_uc27` (`uc-pps-023` / `uc-pos-007`).
