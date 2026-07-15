# uc-pos-004 · Kyle Schwarber First-Half 2026 (All-Star / Derby Runner-Up) · UC #21 / dp_uc20

**Delivered 2026-07-14 · Certification: READY (06) · Verification: 18/18 PASS · v1.0.0**

One-line: Schwarber's 32-HR, .391-wOBA half is selective aggression, not new strength — career-high in-zone swing and pulled-air conversion on a flat-bat-speed engine, damage front-loaded before two strikes, with the walk rate kept intact and a career-worst K rate accepted as the price.

## Folder map
| File | What it is |
|---|---|
| `00_dpo_delivery_spine.md` | Orchestration record, numbering decision, guardrails, escalations |
| `01_intake_gap_report.md` | Use-case validation (GO; 3 non-blocking gaps) |
| `02_source_profile_and_fitness.md` | Source coverage, CDE fitness, data quirks |
| `03_glossary_and_kpi_specs.md` | User-KPI → glossary map; NEW SC-1 wRC + SC-2 P/PA specs |
| `04_model_and_lineage.md` | Grain, entity lock, receipt-level lineage |
| `05_dq_scorecard.md` | 10 rules + 2 warnings, all PASS |
| `06_certification_readiness.md` | READY, 3 conditions (ledger row, SC promotion, staleness) |
| `07_consumption_and_observability.md` | Persona cards, second-half watch rules, versioning |
| `dp_uc20_schwarber_first_half.py` | Build script (copy; canonical at MLB repo root) |
| `dp_uc20_schwarber_first_half_report.md/.pdf` | Reader report (copy; canonical at MLB repo root) |
| `dp_uc20_verification.py` | Independent recompute harness (18/18) |
| `telemetry/` | **Token-economist pilot**: run economics ledger + calibration report |

Receipts (17 CSV + 3 PNG + buildlog): `MLB/out/dp_uc20_schwarber_first_half_*`
Contract: `MLB/uc-pos-004-Kyle Schwarber ASG 20260714.md`
Lineage: UC3 → UC8 → UC11 → UC18 (Marsh, pos kernel) → UC19/20 (ASG shape) → **this**.
