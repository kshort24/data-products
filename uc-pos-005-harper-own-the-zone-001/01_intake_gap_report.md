# 01 — Intake Gap Report · uc-pos-005 (dp_uc22)

**Agent role:** use-case-validator · **Verdict: GO** — 0 blocking, 2 non-blocking gaps (both resolved by DPO decision at intake)

## Use case as received
DPO prompt (2026-07-15) with working plotly exploration attached. Ask: Harper's ability to **take** pitches around the edge of the zone while **punishing** pitches that get too close; explicit pivot to takes-first. Named KPIs: barrel rate ("as well as he ever has during his Phillies tenure?"), pitch-group/pitch-type barreling by year, platoon splits. Narrative anchors supplied: "own the moment" mantra, walks/chase intent, Dombrowski "elite" discourse, 9th ASG (Manfred add; Marsh fan-voted starter), contract facts, Wheeler teaser for the next UC.

## Completeness check
| Element | Status | Note |
|---|---|---|
| Business question | PRESENT | Edge discipline + edge punishment + barrel tenure trend + platoon |
| Entity | PRESENT | Harper; resolved to 547180 in 02 |
| Window | PRESENT (implied) | First half 2026; tenure 2019–2026 as benchmark — DPO answer at intake confirmed |
| KPIs | PARTIAL | Barrel/platoon explicit; edge KPIs needed definition → 03 (OZ family) |
| Personas | INFERRED from pos pattern | Manager, Hitting Dept, Player, DPO/Content — non-blocking |
| Deliverable | CONFIRMED at intake | Governed md report + interactive HTML (AskUserQuestion, 2026-07-15) |
| Geometry constant | PRESENT in DPO code | `ball_width = 0.25` ft — adopted as the shadow-band width |

## Gaps
1. **NON-BLOCKING — edge KPI definition.** DPO's exploration used the bottom rail only (`sz_bot ± 0.25`). Generalized in design to all four zone edges (shadow_in / shadow_out / heart / waste). Resolution: kpi-calculator spec in 03; DPO's 0.25 ft constant retained.
2. **NON-BLOCKING — "punished" definition.** Resolved as damage on shadow-in swings (OZ-4: xwOBAcon, barrel%, hard-hit%) plus heart-zone damage as supporting view, rather than hits-only (DPO's `events.isin(hits)` draft filter), so takes and swings share a denominator framework.

## Scope classification
Full governed run confirmed by DPO (run scope question, 2026-07-15). All four KPI families in scope: edge discipline, edge damage, barrel trends, platoon splits.
