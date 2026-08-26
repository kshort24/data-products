---
use_case_id: uc-pps-027
ledger_uc: 38
build_artifact: dp_uc38
title: The Nola–Stubbs Battery — Game-Planning Under a Changed Catcher
value_stream: Phillies Pitching (pps)
status: DELIVERED — certify-ready · 117/117 verification PASS (run 2, 2026-08-26)
created: 2026-08-25
reopened: 2026-08-26 (data plane granted; build executed; premise revised)
trigger: Scheduled task uc-pps-027-nola-battery-advance-scout-sea-20260825-001
game_context: PHI @ SEA, T-Mobile Park, 2026-08-26, Stubbs catching (DPO carry-in; date corrected from 08-25 in run 2)
persona: Pitching Coach · Catching Coordinator · Pitcher · Catcher · Advance Group
delivery_format: Governed report (md + pdf) + build script + receipts + governance spine
grain: pitcher × catcher (`fielder_2`) × {career | season | recency window}
data_domains: Statcast pitch-level (pps), Phillies batting frame (pos, for catcher name resolution)
entity_lock: pitcher == 605400 (Aaron Nola)
---

## 1 · Business context

Aaron Nola starts tonight in Seattle with Garrett Stubbs catching. He has pitched well over
his last several starts and has been paired with Stubbs more regularly. 2026 has been a
rollercoaster season for a career Phillie, and the advance file already carries three prior
reads on him. The question is whether the recent improvement has a **game-planning
mechanism** attached to it, or whether the battery change is coincident with — rather than
causal of — the better results.

## 2 · Questions

| # | Question | Answerable? | How |
|---|---|---|---|
| Q1 | How has the game planning been different with Stubbs back there recently? | **Yes** | BAT-1…BAT-9 at `catcher × window` grain, benchmarked against Nola's own all-catcher mean |
| Q2 | Are there actions they've made (Nola calls his own via PitchCom) driving the positive outcomes? | **Yes, further than expected** | The **adjustment-travel test (TR-1)** asks whether each approach change appears in the non-Stubbs starts too. **10 of 12 do** ⇒ pitcher-level, not battery-specific. Pitch-call attribution is still NOT in the data (AT-1); the design bounds the question rather than reading a field |
| Q3 | How does that compare to prior work with Stubbs and other catchers? | **Yes** | Career `Nola × catcher` panel: Stubbs-now / Stubbs-then / Realmuto / others |
| Q4 | Frame against the pitcher–catcher relationship product | **Yes** | Inherits the `uc-cat-001` strength-vs-weakness philosophy axis; ships three of its ten KPIs for the first time |

## 3 · Acceptance criteria

| # | Criterion | Status |
|---|---|---|
| AC-1 | Every published number traces to a CSV receipt written by `dp_uc38_*.py` this session | ✅ **MET** — 43 receipts written 2026-08-26; 0 `«FILL»` tokens remain |
| AC-2 | Outcome-layer KPIs inherited verbatim from the locked UC8→UC25 line; zero re-derivation | **MET** |
| AC-3 | Every NEW KPI carries a kpi-calculator spec, a glossary entry, and a lineage row before it appears in the report | **MET** (BAT-1…BAT-9, CS-1) |
| AC-4 | Entity locked to MLBAM 605400; no name filters anywhere | **MET** (asserted in build + DQ scorecard) |
| AC-5 | Small samples print their PA/pitch counts; floors are flags, not silent filters | **MET** |
| AC-6 | Catcher splits ship with a confound panel; no causal language without it | **MET** |
| AC-7 | Pitch-call attribution limit stated up front, not in a footnote | **MET** (report §front-matter, §9; `dp_uc38_attribution_guard.csv`) |
| AC-8 | Window choice is disclosed and sensitivity-tested | **MET** (3/5/8-start variants) |
| AC-9 | Independent verification recomputes published numbers by a second path | ✅ **MET** — **117/117 PASS** (48 primary + 69 addendum), incl. the DPO's own merge skeleton reconciled cell-for-cell |
| AC-10 | A competitive bid with token and time estimates ships with the product | **MET** |

## 4 · SLA / refresh

One-shot advance product tied to a specific start. Closure step is the **post-game
backtest**: projected approach vs actual pitch mix and results, using tonight's game once it
lands in the cache. Offered, not scheduled.

## 5 · Governance guardrails invoked

| ID | Guardrail | Source |
|---|---|---|
| G1 | Entity lock on MLBAM id, never a name filter | `pitcher-scouting-report` skill |
| G2 | Regular season only; dedup on `game_pk+at_bat_number+pitch_number` | house standard |
| G3 | Catcher assignment is non-random; confound panel mandatory | **NEW this UC** |
| G4 / AT-1 | Pitch-call attribution not observable; no person-level attribution | **NEW this UC** |
| G5 | Sample floors are flags, not filters | `uc-pos-012` HD-1 precedent |
| CLAUDE.md #1 | No CDE inference — definitions come from the glossary agent | project |
| CLAUDE.md #3 | No publish without certification | project |
| Skill NN-1 | Never publish a number the build didn't compute this session | `pitcher-scouting-report` |

## 6 · Scope boundaries

**In:** Nola's career pitch log; catcher dimension via `fielder_2`; game-plan composition,
sequencing, zone attack, and the locked outcome layer; recency windows; confound panel.

**Out (each with a reason):** catcher framing/blocking/throwing models (no model in this data
plane); Seattle lineup advance (priced as a bid option, not taken); the remaining seven
`uc-cat-001` KPIs staff-wide (offered as fast-follow); any causal estimate of catcher effect
(design cannot support it).

---

## 7 · Delivery record

| Run | Date | Outcome |
|---|---|---|
| 1 | 2026-08-25 | Scheduled, non-interactive. Layers 1/2/4 delivered; **Layer 3 blocked** (data plane unmounted). Harness shipped explicitly unfilled — no number invented |
| 2 | 2026-08-26 | Interactive. Data plane granted on request. **Build executed · 43 receipts · 0 DQ FAIL · 117/117 verification PASS · CERTIFY-READY** |

**What changed between the runs, beyond numbers.** The harness was built to characterise how
the game plan differs with Stubbs catching. Live data showed the same approach change in the
starts Stubbs did not catch, so under **G7** the harness could not be filled as written. Run 2
added the design that separates the two hypotheses — **TR-1** adjustment-travel test, **TR-2**
breakpoint scan, **OC-1** opponent-quality control — and the report's headline inverted:
*the pitcher changed the plan; the battery carries the most extreme version of it.*

New governance this UC: **G3** confound panel · **G4/AT-1** attribution not observable ·
**G6** breakpoint is a degree of freedom · **G7** single-stratum delta is a hypothesis.
New method family pending ratification: **TR-1, TR-2, OC-1, LH-1, CH-1** (E-2).
Defect closed: **O-12** accent-insensitive id→name cross-check.
