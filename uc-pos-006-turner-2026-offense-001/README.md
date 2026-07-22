# uc-pos-006 · Trea Turner 2026 Offense — Governance Package

**UC #25 · contract `uc-pos-006` · build `dp_uc24` · v1.0.0 · 2026-07-21 · Owner: Kellen Short**
Phillies position-player (pos) value stream. Status: **Build complete — Certification READY (33/33 verified) — pending DPO publish sign-off + ledger update.**

## What this is
A full governed data product answering: *why is Trea Turner's 2026 offense down, is the recent uptick real, and what can each persona do about it?* Headline: first below-average offensive season of his career (.691 OPS, wOBA .303, wRAA −4.8), process-backed (xwOBA .295), driven by shape (pulled-air .117, a Phillies-era low) and swing decisions, with a real-but-young July recovery (.980 OPS / 62 PA).

## Control plane (this folder)
| File | Agent role | Contents |
|---|---|---|
| `00_dpo_delivery_spine.md` | data-product-owner | sequencing, numbering, guardrails, escalations |
| `01_intake_gap_report.md` | use-case-validator | 4 non-blocking gaps, resolved |
| `02_source_profile_and_fitness.md` | source-system-profiler | entity lock, coverage, freshness, fitness |
| `03_glossary_and_kpi_specs.md` | business-glossary + kpi-calculator | mapping + RF-1/RF-2 specs |
| `04_model_and_lineage.md` | data-architect + technical-lineage-builder | grain, joins, column lineage |
| `05_dq_scorecard.md` | data-quality-engineer | scorecard + the caught "career-low" correction |
| `06_certification_readiness.md` | certification-agent | artifact audit + 33/33 + READY |
| `07_consumption_and_observability.md` | analytics-enabler + onboarding + observability | how-to, personas, monitoring |

## Runtime plane (MLB repo `C:\...\Python Scripts\MLB`)
- Build: `dp_uc24_turner_2026_review.py` · PDF builder: `dp_uc24_build_pdf.py` · Verifier: `dp_uc24_verification.py`
- Report: `dp_uc24_turner_2026_review_report.md` / `.pdf`
- Consumables: `dp_uc24_turner_2026_review_interactive.html`, `dp_uc24_turner_2026_persona_card.pdf`
- Receipts: `out/dp_uc24_turner_2026_review_*.csv` (16) + `*_fig{1..5}_*.png` (5)
- Contract: `uc-pos-006-Trea Turner 2026 Offense 20260721.md` · Ledger patch: `uc_ledger_AI_PATCH_uc-pos-006-turner.md`

## Pattern lineage
uc-pos-004/dp_uc20 (Schwarber first-half hitter kernel) · uc-pos-marsh-breakout-001/dp_uc18 (hitter retrospective + persona narrative) · uc-pos-005/dp_uc22 (interactive.html consumable) · UC11 (locked-KPI inheritance, evidence tiers).

## Open items for DPO
1. Publish sign-off. 2. Ledger append (bump to UC #26 / dp_uc25). 3. Promote RF-1/RF-2 from provisional. 4. Schedule August backtest.
