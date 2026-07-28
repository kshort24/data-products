# uc-pos-007 · Phillies hitters at loanDepot park

**UC #28 · `uc-pos-007` · build `dp_uc27` · v1.0.0 · delivered 2026-07-27 · PUBLISH (internal)**
Value stream: Phillies Position Player / Offense (`pos`) · Target event: PHI @ MIA, 2026-07-28

---

## What it answers

Do Phillies hitters perform differently at loanDepot park than everywhere else — and what does that
mean for the July 28 series opener against Sandy Alcantara? Career vs RHP, MLB regular season,
11 hitters, 24,592 plate appearances.

## The read

**The Miami gap is a tenure artifact, not a park effect.** All-rows, the group hits `.720` OPS /
`.311` wOBA at loanDepot against `.804` / `.345` everywhere else. But 45% of those Miami plate
appearances belong to two hitters who were *playing for the Marlins at the time* — Realmuto (783 PA,
2015–18) and Derek Hill (80 PA, 2024–25). Restricted to visiting-club rows the gap nearly closes
(`.783` OPS / `.337` wOBA) and **inverts on expected quality: `.391` xwOBA in Miami vs `.376`
baseline**, with higher hard-hit (44.8% vs 43.7%) and barrel (11.0% vs 9.4%) rates and an identical
home-run rate.

**Against Alcantara they have hit, and hit hardest in Miami.** 309 career PA, `.353` wOBA on `.388`
xwOBA. In Miami against him: 163 PA, `.423` xwOBA, 47.5% hard-hit, a homer every 27 PA. The slider
is the pitch to hunt (`.496` xwOBA, 55.2% hard-hit, only 27.7% chase); the curveball has beaten them
(`.123` wOBA) and he has more than doubled its usage in the 2025–26 window while cutting four-seams
from 24.6% to 16.2%.

**Players to watch:** Harper (`.516` xwOBA vs Alcantara, highest in the file), Schwarber (`.402`
xwOBA vs him on a `.303` wOBA — owed runs), Stott (the only process-backed positive venue split),
Realmuto (read the visiting-club line, not the headline).

## Publish status

| Gate | Result |
|---|---|
| DQ scorecard | 16 checks · 14 PASS · 2 WARN · **0 FAIL** · all 9 blocking PASS |
| Independent recompute | **256 / 256** reconcile |
| Certification | **READY** |
| Privacy | PASS — no PII, public-derived |
| Version | v1.0.0, new product, no breaking changes |
| Standing caveats | Alcantara cache stale (2025-04-12) · VD-1/VD-2 PROVISIONAL · venue cohort is a `home_team` proxy |

## File map

| File | Layer | Contents |
|---|---|---|
| `00_DPO_delivery_spine.md` | Orchestration | Sequencing, gate results, governance compliance, publish decision |
| `01_intake_validation_and_source_profile.md` | 1 | Gap report, entity lock, source fitness, union-inflation and MiLB-contamination measurements, domain steward findings |
| `02_business_glossary_and_domains.md` | 1 | 3 new CDEs, 2 PROVISIONAL KPI terms, 5 registered domain rules |
| `03_data_dictionary.md` | 2 | 31 source columns, 7 derived columns, 24 receipts, 5 figures, classification tags |
| `04_architecture_and_kpi_specs.md` | 2 | Model blueprint, 18 locked KPIs, full VD-1 / VD-2 specs, EDA findings, acceptance criteria |
| `05_dq_rules_and_join_validation.md` | 2 | 16 DQ rules; the union fan-out defect found, quantified and remediated |
| `06_technical_lineage.md` | 3 | Nine-stage pipeline diagram, column-level lineage, cohort-to-claim map, reproduction commands |
| `07_dq_scorecard_and_certification.md` | 3–4 | Scorecard results, certification verdict, consumption guide + FAQ, observability runbook, cost audit, 6 open items |
| `dp_uc27_phillies_at_loandepot_report.pdf` | Deliverable | **Start here.** 9-page branded reader report |
| `dp_uc27_phillies_at_loandepot_report.md` | Deliverable | Same, markdown source |
| `dp_uc27_hitting_coach_card.pdf` | Deliverable | One-page dugout card, every number read from the CSVs at build time |
| `dp_uc27_phillies_at_loandepot.py` | Receipt | Build script — 24 CSV receipts + 5 figures |
| `dp_uc27_verification.py` | Receipt | Independent recompute harness, shares no code with the build |
| `dp_uc27_build_pdf.py` / `dp_uc27_build_persona_card.py` | Receipt | Deliverable builders |
| `out/` | Receipt | 24 CSVs, 5 PNGs, verification results |

## What is new in this package

* **First venue-cohort use case in the repo.** `VENUE_COHORT`, `COMPETITION_LEVEL` and
  `VENUE_TENURE_CONTEXT` are new inheritable CDEs.
* **The tenure confound is the transferable lesson.** A "park" cohort built from `home_team` silently
  mixes visiting performance with a player's own tenure at that club. Any future venue study in this
  repo should inherit CDE-3 rather than rediscover it.
* **The union fan-out fix.** `pd.concat([pos, nphl])` double-counts 6–18% of a hitter's rows because
  the same pitch is cached in up to six parquets. Dedup on the Statcast pitch key is now a blocking
  DQ rule.
* **VD-1 / VD-2** — provisional venue-delta and signal-classification KPIs, specced in full and
  routed to ratification.

## Reproduce

```bash
python dp_uc27_phillies_at_loandepot.py <MLB_DIR> <MLB_DIR>/out
python dp_uc27_verification.py           <MLB_DIR> <MLB_DIR>/out   # exits 0 on success
python dp_uc27_build_pdf.py              .
python dp_uc27_build_persona_card.py     .
```

Data plane: `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB`.
Build script and receipts also live there under `out/`; this package carries copies as the receipt
trail.
