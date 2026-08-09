# uc-pos-009 — Kyle Schwarber Swing Decay

**UC #33** · build `dp_uc32` · value stream `pos` · delivered 2026-08-08
**Status:** ✅ Certified — 24/24 DQ, 59/59 verification · **Internal — Restricted**
**Entity lock:** `batter == 656941` · **Evidence window:** 2026-03-26 → 2026-08-07 (T-1), career backfill to 2015

---

## Start here

| If you want… | Open |
|---|---|
| **The answer, formatted** | `dp_uc32_schwarber_swing_decay_report.pdf` |
| **The answer, sliceable** | `dp_uc32_schwarber_swing_decay_dashboard.html` |
| **The answer, editable** | `dp_uc32_schwarber_swing_decay_report.md` |
| **The orchestration record** | `00_DPO_delivery_spine.md` |
| **How to query this yourself** | `06_consumer_success.md` §5 |
| **The raw numbers** | `out/dp_uc32_*.csv` — 24 receipts |

---

## The finding in three lines

**The bat is fine. The decisions are not.**

Bat speed is **74.2 mph** in both 2025 and 2026; the 90th-percentile swing is 81.0 mph in both halves of this season; swing shape is unchanged. What moved is **chase rate (25.5%, a nine-year high)**, **strikeout rate (34.8%, a career high)**, and the **launch-angle distribution** — contact in his 20–32° home-run band fell from 21.7% to 14.9% of balls in play while sweet-spot %, hard-hit % and squared-up % all *rose*.

He is still hitting it hard. He is hitting it hard at the wrong angle.

---

## Two things this product establishes beyond the player

**1. A NULL-handling standard.** The DPO asked whether mean-imputing bat-speed NULLs was sound. It was not — nine of twelve seasons have zero coverage, and imputation would have fabricated 7,021 swings (67.7% of the career series) at a single value with zero variance. The rejected policy is quantified in a receipt and rendered as a figure. Proposed rule: *missing-because-the-instrument-did-not-exist is out-of-scope data, not missing data.* (OI-1)

**2. A requested KPI shown to fail, in public.** Sweet-spot % rose 6.4% while slugging fell 27.2%. The 8–32° band scores an 8° line drive and a 30° fly ball identically. The product ships the metric *with the demonstration of its failure* and proposes SW-2 and SW-8 as replacements, rather than substituting silently. (OI-2)

---

## Contents

### Governance trail
| File | Department | Contents |
|---|---|---|
| `00_DPO_delivery_spine.md` | Orchestration | Delivery plan, governance gates, agent sequence, open items, publish recommendation |
| `01_intake_validation_and_source_profile.md` | Strategy & Intake | Gap report (0 blocking / 8 non-blocking), entity lock, **three-window sensor finding**, domain rules & quirks |
| `02_business_glossary_and_domains.md` | Governance | SW-1…SW-9 definitions, evidence-window vocabulary, tagging, privacy assessment |
| `03_data_dictionary_and_technical_lineage.md` | Governance ∥ Design | Metadata mapping, output dictionary, 6-hop column-level lineage |
| `04_architecture_and_kpi_specs.md` | Engineering (Design) | Model, grain decision, EDA findings, all nine KPI specs, explicit non-goals |
| `05_dq_rules_and_join_validation.md` | Quality ∥ Build | 24 DQ rules, scorecard, join validation, build defects fixed |
| `06_consumer_success.md` | Consumer Success | Semantic layer, usage guide, interpretation traps, 7 persona guides, dashboard spec, query templates |
| `07_certification_and_publish_readiness.md` | Quality | Artefact audit, 59-check verification, open items, versioning, monitoring, cost |

### Code
| File | Purpose |
|---|---|
| `dp_uc32_schwarber_swing_decay.py` | **The build.** Every published number originates here. Exits non-zero on any DQ failure |
| `dp_uc32_verification.py` | Independent harness — reloads from parquet by a separate code path and audits the report's prose |
| `dp_uc32_build_pdf.py` | markdown → HTML → weasyprint, Phillies-branded |
| `dp_uc32_build_dashboard.py` | Receipts → self-contained HTML. Computes nothing |

### Deliverables
| File | Size |
|---|---|
| `dp_uc32_schwarber_swing_decay_report.pdf` | 500 KB, 10 sections |
| `dp_uc32_schwarber_swing_decay_dashboard.html` | 104 KB, 8 tabs, offline-capable |
| `dp_uc32_schwarber_swing_decay_report.md` | markdown source |
| `out/` | 24 CSV receipts, 5 PNG figures, headline JSON, verification results |

---

## Re-running

Order is mandatory — the PDF and dashboard builders trust that the harnesses ran green.

```bash
python dp_uc32_schwarber_swing_decay.py    # 24 receipts, 5 figures, DQ gate
python dp_uc32_verification.py             # 59 independent checks
python dp_uc32_build_pdf.py
python dp_uc32_build_dashboard.py
```

Data root resolves from `$DP_MLB_ROOT` → relative path → the Windows absolute path → the sandbox mount. Set `DP_MLB_ROOT` if none of those apply.

**If `DQ-08` or `DQ-09` fails**, an upstream backfill has added pre-sensor bat-tracking values. Do not override — the evidence-window architecture is invalidated and the UC must be re-designed, not re-run.

---

## Closure

Re-read at **150 additional plate appearances** (~2026-09-10) against three falsifiable projections:

1. Bat speed holds at 74 ± 0.5 mph.
2. Damage-Band Rate (20–32°) recovers above 18%.
3. Chase rate falls below 24%.

**If (1) fails, supersede this UC rather than amend it.**

---

## Ledger

| | |
|---|---|
| UC number | **#33** |
| Contract | `uc-pos-009` |
| Build artifact | `dp_uc32` |
| Next available | **#34** / `dp_uc33` (`uc-pos-010` / `uc-pps-026`) |
| Inherits from | UC#21 `dp_uc20` (Schwarber), UC#25 `dp_uc24` (Turner diagnosis), UC#32 `dp_uc31` (Arraez, package shape) |
| New KPIs | SW-1 … SW-9 (**provisional**) |
| Opens | OI-1 … OI-8 |
| Closes | none |
