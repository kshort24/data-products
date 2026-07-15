# 01 — Strategy & Intake
## uc-pps-019 · Sánchez first-half 2026 · use-case-validator + source-system-profiler

## A. Use-case-validator gap report

**Verdict: GO.** No blocking gaps.

| # | Gap | Class | Resolution |
|---|---|---|---|
| 1 | "Phillies record" scoreless-streak claim not derivable from local data | Non-blocking | Treated as manual carry-in; streak length recomputed from log (SL-1) as a consistency check, record status not asserted from data |
| 2 | "Pitching department emphasizes early PA resolution" is unverified institutional context | Non-blocking | Report frames QR findings as *consistent/inconsistent with* the stated emphasis, not proof of it |
| 3 | Official ERA not computable from pitch log | Non-blocking | RA9 from score deltas + FIP, per dp_uc17 precedent; caveat printed in report warning box |
| 4 | "Rough outing in Kansas City" — date not given | Non-blocking | Located in start log (KC opponent row); confirmed present |
| 5 | Persona actions are not observable in Statcast | Non-blocking | §6 persona narratives labeled *inference consistent with the data* (house rule from uc-pps-017) |

Acceptance criteria: (i) results-first structure; (ii) persona-action section; (iii) QR-1 trend answered 2025 vs 2026 and month-by-month 2026; (iv) all numbers receipt-traceable; (v) certification-style verification pass before publish.

## B. Source profile & fitness-for-purpose

Profiled this session (2026-07-14), sandbox mount of the MLB repo data layer.

| Item | Finding |
|---|---|
| Source | `data/phillies/phils_2026.parquet` + `phils_2025.parquet`, `phillies_role=='pitching'`, `game_type=='R'` |
| Entity lock | `pitcher == 650911` — unique modal id for "Sánchez, Cristopher"; no name-collision contamination (checked all `*nchez*` pitcher rows: single id) |
| 2026 window | 2026-03-26 .. 2026-07-11 · **20 starts · 1,903 pitches · 525 PA** · cache fresh through 2026-07-12 (T-2 vs today; Sánchez has not pitched since 07-11) |
| 2025 baseline | Full season: 32 starts · 2,896 pitches (2025-03-31 .. 2025-09-28) |
| Dedup | `game_pk + at_bat_number + pitch_number` unique after standard dedup |
| `pitch_number` | 0 nulls in 2026 entity-locked frame → **QR-1 is computable at full population** (fitness: PASS for the new KPI) |
| Arsenal fields | `pitch_name` populated: Sinker / Changeup / Slider (3-pitch mix, no four-seam) — supports the changeup/slider narrative |
| TTO / battery | `n_thruorder_pitcher`, `fielder_2` present (dp_uc17 precedent) |
| Feasibility probe | Raw QR-1 2026 ≈ 0.503 (build script recomputes authoritatively) |

**Fitness verdict:** FIT for all requested panels. Sample-size flags to print in report: July 2026 monthly split will be small (~2 starts); battery splits below 100-BF convention are directional only.
