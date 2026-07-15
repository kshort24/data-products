# 00 — DPO Delivery Spine · uc-pos-005 (dp_uc22) · Bryce Harper "Own the Zone" First-Half 2026

**Use case:** First-half 2026 read on Bryce Harper's stated approach — take pitches around the edge of the strike zone, punish the ones that creep in. Takes-first analysis (pivot from swings-first, per DPO's own exploration), plus barrel-rate trend across the PHI tenure, pitch-group/pitch-type barreling, and platoon splits. Framed against the offseason "elite" discourse (Dombrowski) and the 9th All-Star selection.
**Requested by / DPO:** Kellen Short, 2026-07-15 · **Depth:** full governance package (DPO-confirmed at intake) · **Deliverables:** governed markdown report + interactive HTML consumable + receipts + trail.

## Sequencing & numbering decision
- Ledger (`uc_ledger_AI.md`, verified 2026-07-15) showed Next available **UC #23 / dp_uc22** (pos next: **uc-pos-005**). No collision with root files, `out/` receipts, or control-plane folders.
- Claimed: **UC ordinal #23 · contract id `uc-pos-005` · build prefix `dp_uc22`.**
- Ledger row appended and "Next available" bumped to UC #24 / dp_uc23 (pos next: uc-pos-006) — done this session, directly in `uc_ledger_AI.md`.

## Layer sequencing (all gates passed in order)
| Layer | Agent role | Artifact | Status |
|---|---|---|---|
| 1 Intake | use-case-validator | 01 | PASS (2 non-blocking gaps, resolved by DPO decision) |
| 1 Intake | source-system-profiler | 02 | PASS (full PHI tenure 2019–2026; entity lock 547180) |
| 1 Intake | business-glossary | 03 | PASS (4 new terms: OZ-1..OZ-4 — provisional) |
| 2 Design | data-architect + kpi-calculator | 04 / 03 | PASS (grain locked; kernel inherited verbatim from dp_uc18/dp_uc20; 4 new KPI specs + region geometry) |
| 3 Build | data-engineer | `dp_uc22_harper_own_the_zone.py` | PASS (run 2026-07-15; 16 CSV + 4 PNG receipts + buildlog) |
| 3 Build | data-quality-engineer | 05 + `out/dp_uc22_*_dq_receipts.csv` | PASS structural checks |
| 4 Certify | certification-agent + verification | 06 + `dp_uc22_verification.py` | READY — **18/18 independent recompute PASS** |
| 4 Publish | consumption docs + observability | 07 + interactive HTML | Delivered |

## Governance guardrails honored
1. **No CDE inference** — locked dp_uc18/dp_uc20 kernel inherited verbatim; the four NEW KPIs (OZ-1..OZ-4) carry full kpi-calculator specs in 03 and are flagged provisional pending glossary approval. The shadow-band constant (ball_width = 0.25 ft) is DPO-provided at intake, not inferred.
2. **No build without specs** — build script implements 03/04 only; consumable (interactive HTML) reads certified receipts, never raw data.
3. **No publish without certification** — 06 returned READY (18/18 verification) before the report and HTML were presented.
4. **Manual carry-ins** (DPO-provided at intake, 2026-07-15; never computed): 9th All-Star selection (Commissioner add, not fan vote); Marsh fan-voted starter; Dombrowski offseason "elite" discourse; contract facts (13 yr / $330M / 2019 / no opt-outs / full NMC). Narrative only.
5. **Privacy:** public MLB performance data, no PII beyond public player identity — privacy-watchdog pass trivial, noted in 06.
6. **Cross-plane contract:** ledger row carries the `use_case_id` crosswalk per the 2026-07-02 rule; runtime artifacts at MLB root, trail here.

## Escalations to human DPO
- OZ-1..OZ-4 glossary promotion from provisional → **open** (recommend approve; geometry is DPO's own definition, damage mechanics are the locked kernel at region grain).
- Second-half re-run trigger: end of regular season (observability spec in 07).
- LHP contact-quality flag (88.0 avg EV, tenure low) surfaced as a business finding, not a data issue.
