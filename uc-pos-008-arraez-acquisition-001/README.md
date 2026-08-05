# uc-pos-008-arraez-acquisition-001

**Luis Arraez — deadline acquisition read, 2026-08-04.**
UC **#32** · contract `uc-pos-008` · build artifact `dp_uc31` · value stream `pos`

Status: ✅ **Build complete — ready for human DPO sign-off.** Internal — Restricted.
⚠️ **One circulation gate: OI-1** (leadoff-hitter premise conflict) must be resolved before this reaches the manager or coaching staff.

---

## What this is

The first **position-player** acquisition-onboarding read, and the first product in either value stream that carries a **decision model**.

Arraez is the headline 2026 deadline addition. The organisation has never employed him — there are zero Phillies plate appearances in the data — so this is an intake dossier, not a review. Beyond the profile, one decision is live: **where does he bat?** Mattingly has him at cleanup; the consumer wanted to know whether the top of the order is better, and specifically whether to swap him with Schwarber.

**The short version.**

He is the player the consumer described, with **one correction** and **one warning**.

*The correction:* he is **not** a wild at-bat hitter. He sees 3.72 pitches per plate appearance — below average, and below his own 2019–2022 rate. The wildness lives in exactly one place: once he has two strikes he expands to a **56.3% chase rate**, swings at 73% of everything, fouls off 42% of it, and takes a called third strike **1.1%** of the time. The endings are wild; the beginnings are efficient.

*The warning:* 2026 is the **first season of his career** in which the results run meaningfully ahead of the contact. A .337 wOBA sits **33 points above** a .304 xwOBA, on a **0.7% barrel rate**, 86.0 mph exit velocity, and a fast-swing rate of **0.0%** — zero of 817 tracked swings reached 75 mph. Expect **.300–.310**, not .337.

*What is genuinely elite and durable:* **two-strike survival.** 90.1% of his two-strike plate appearances avoid a strikeout. The best Phillie is 67.0%; Schwarber is 43.0%. He is the only regular on the roster who is not a net negative with two strikes. Alongside it, the best scoring-position conversion rate on the team (34.3%) with **one strikeout in 89 RISP plate appearances**.

*On the lineup question:* **the entire decision is worth 3.95 runs per 162 games** — under half a win across all nine slots. The consumer's reasoning about cleanup is confirmed by the data (slot 4 leads the order at 47.8% men-on and 1.06 RISP plate appearances per game), and Mattingly's choice is the better of the two options discussed. Against the lineup that actually exists, the proposed swap **costs 2.6 runs**. The model's own preference is a third option: **bat him second** — not because of his own production, but because slots 2–3 hand their runners to better converters than slots 4–5 do.

---

## Deliverables

### Reader-facing

| File | What |
|---|---|
| `dp_uc31_arraez_acquisition_read_report.pdf` | **The report.** 12 pages, Phillies-branded, 13 tables, 6 figures |
| `dp_uc31_arraez_acquisition_dashboard.html` | **Interactive companion.** 7 tabs, 16 charts, a live lineup-swap explorer. Single file, works offline |
| `dp_uc31_arraez_acquisition_read_report.md` | Markdown source |
| `uc-pos-008-Luis Arraez PHI 20260804.md` | Use-case contract — problem, seven questions answered, actions, open items |

### Build & verification

| File | What |
|---|---|
| `dp_uc31_arraez_acquisition_read.py` | The build. **The only place a number is computed** |
| `dp_uc31_verification.py` | Independent recompute — **368/368 checks passed** |
| `dp_uc31_build_pdf.py` | Markdown → weasyprint renderer |
| `dp_uc31_build_dashboard.py` | Receipts → self-contained HTML |
| `out/` | 30 CSV receipts + 6 figures + DQ scorecard + freshness manifest + verification results |

### Governance trail

`00_DPO_delivery_spine.md` · `01_intake_validation_and_source_profile.md` · `02_business_glossary_and_domains.md` · `03_data_dictionary_and_technical_lineage.md` · `04_architecture_and_kpi_specs.md` · `05_dq_rules_and_join_validation.md` · `06_consumer_success.md` · `07_certification_and_publish_readiness.md`

---

## What's new in this UC

**A decision model, not a description.** Every prior UC in this repo describes; this one is asked to choose. **AR-6 Slot-Projected Run Contribution** composes two independently observed quantities — a slot's opportunity mix, and a hitter's run-expectancy contribution by base context — with no simulation and no assumed transition matrix. Both inputs ship as standalone receipts so the composition is auditable in halves.

> **New house rule.** *A decision model must be decomposable into separately observable, separately receipted components, and must publish the specific second-order effect it does not capture.* Here that effect is the feedback of re-ordering on the opportunity weights themselves — stated in the report body, the architecture doc, and every place AR-6 appears.

**A contested consumer premise, priced both ways rather than resolved.** The request states Schwarber is the leadoff hitter. The log through 2026-08-02 says **Turner** (399 PA to Schwarber's 95; Schwarber has not led off since June). Rather than silently correcting the consumer or silently accepting the premise, the build prices **both framings** — and they disagree in sign (−2.58 vs +0.65 runs).

> **New house rule.** *When a manual carry-in contradicts the pitch log: price both, escalate, do not choose.*

**A units defect caught during build.** The first AR-7 implementation multiplied a count of baserunners by a per-plate-appearance rate — a quantity with no coherent unit. It was reworked onto a per-runner conversion basis, labelled an upper bound, and flagged **non-additive** with AR-6 to prevent double-counting.

**Two verification failure classes, both root-caused rather than tolerated.** The harness returned 330/351 on first run. Neither failure was a data defect and neither was silenced:

- **`truncated_pa` definitional fork.** The locked `get_stats` counts it as a plate appearance; the new strict PA spine does not. The gap is exactly 1 PA in 2021 and 2 in 2025. **The locked kernel was not edited** — it is shared with four delivered UCs. The harness now asserts the *reconciliation*, plus two new checks proving the 2026 primary window contains **zero** occurrences, so no forward-looking number is touched. Logged as open item **O5**.
- **Rounding-chain drift.** Reconstructing AR-6 from published 4-dp inputs drifts ≤0.015 runs per 162. The tolerance was widened *and documented with its reason*; the raw-path check carries the real burden and passes at 1e-4.

**Seven report claims are enforced as verification assertions**, so the prose cannot drift from the data — including "Arraez has the best two-strike survival rate on the roster" and "Schwarber outproduces Arraez in every slot."

**Batting-order slot reconstructed from the pitch log.** Statcast has no lineup-slot field. It is recoverable exactly, because a batting order cycles strictly and substitutions inherit the slot they replace. Validated at 112/112 games after the `truncated_pa` fix — the single failing game was root-caused, not tolerated.

---

## Pattern inheritance

UC#21 / `dp_uc20` (Schwarber — hitter retrospective, locked KPI kernel) → UC#25 / `dp_uc24` (Turner — hitter diagnosis, trajectory KPIs, interactive consumable) → UC#30 / `dp_uc29` (Kilian — first acquisition-onboarding variant) → UC#31 / `dp_uc30` (Raley — population benchmark, proxy-ships-with-calibration) → **UC#32 (this one).**

**Reusable assets for the next UC.** The slot-reconstruction method and AR-5/AR-6 generalise to any lineup-construction question for any team-season in this repo. AR-1 and AR-4 are roster-general and are the strongest glossary-promotion candidates.

---

## Quality

| Gate | Result |
|---|---|
| Build DQ scorecard | **24 / 24 PASS** |
| Independent verification | **368 / 368 PASS · 0 FAIL** |
| Locked KPI functions modified | **0** |
| New KPIs specified before use | **7 / 7** |
| Published numbers traced to a receipt | **all** |
| Privacy | Internal — Restricted; no PII beyond public identifiers |

---

## Reproducing

```bash
python dp_uc31_arraez_acquisition_read.py     # ~15 s  → out/
python dp_uc31_verification.py                # must report 0 FAIL
python dp_uc31_build_pdf.py                   # → report.pdf
python dp_uc31_build_dashboard.py             # → dashboard.html
```

Data root resolves via `MLB_DATA_ROOT`, `argv[1]`, or a portable candidate list. The build **refuses to run without a reachable data root** rather than emitting an unfilled harness — the `uc-pps-010` failure mode.

---

## Closure

Re-read at **150 plate appearances in a Phillies uniform**, testing three falsifiable projections:

1. wOBA regresses from .337 toward **.300–.310**.
2. Production against left-handed pitching declines toward the **.256 xwOBA**.
3. **Two-strike survival holds above .85.**

If (3) fails, supersede this UC rather than amend it — the acquisition thesis rests on it.

---

## Ledger

**Next available: UC #33 / `dp_uc32`** (`pos` next: `uc-pos-009` · `pps` next: `uc-pps-026`).

> `uc_ledger_AI.md` in the MLB repo is stale at UC #25. UCs #26–#32 need appending. Flagged to the human DPO.
