# uc-pos-marsh-breakout-001 — Brandon Marsh 2026 First-Half Breakout (UC #18)

**Question:** What has Marsh done differently in 2026 — first All-Star nod — relative to the rest of his career? Has his approach changed?
**Answer in one line:** Same raw power, radically more aggressive early-count swing decisions (walks traded for damage), career-high pulled-air contact, and a removed platoon — with honest regression flags on the .304 average.

| File | What it is |
|---|---|
| `marsh_breakout_report.md` | **The production deliverable** — recap, indicators, persona narrative, watch items |
| `marsh_breakout_analysis.py` | Build script (run: `python marsh_breakout_analysis.py <MLB_repo> <out_dir>`) |
| `00_dpo_orchestration_record.md` | DPO spine: plan, gate checks, capability fulfillment, publish rec (READY) |
| `01_strategy_intake.md` | Validator gap report, source fitness, domain context |
| `02_engineering_design.md` | Locked-KPI inheritance + new indicator specs |
| `03_governance.md` | Glossary status, PD-1..PD-4 provisional definitions, tagging |
| `04_engineering_build.md` | Build record, lineage hops, output manifest |
| `05_quality_certification.md` | DQ scorecard + independent recomputation (PASS) |
| `06_consumer_success.md` | Usage guide + persona onboarding (coach / manager / analyst / player) |
| `07_platform_marketing.md` | Versioning, observability runbook, ledger crosswalk |

Data consumables (v1.1.0): 16 CSVs at `MLB/out/dp_uc18_marsh_breakout_*.csv`; runtime deliverables at MLB repo root: `dp_uc18_marsh_breakout.py` + `dp_uc18_marsh_breakout_report.md` + **`.pdf`** (Phillies-branded). Data window: 2021-07-18 → 2026-07-12 (complete first half), regular season, batter 669016. v1.0.0 receipts (`marsh_breakout_*`, window ≤07-11) retained.
