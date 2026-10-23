```yml
# Identity
name: Bryson Stott 2026 Another Level 20261022
id: uc-pos-020-Bryson Stott Another Level 20261022
description: >
  Season recap of Bryson Stott (2B/3B, bats L, MLBAM 681082), 2026 in the context of 2022-25: cumulative results,
  a governed era detector (ER-1) replacing hand-set "Good/Bad" windows, a pre-registered Good-vs-Bad signature test (GS-1),
  direction / batted-ball / bat-path change around the 2025 stance change, platoon / pitch-type / velocity splits, and
  2B / 3B defense by an infield expected-outs proxy (IO-1) with the "thump" trade-off. Driven by the client notebook export
  "Bryson Stott" (d8b91d3b-attachment.txt) and the client's six-CDE data-dictionary card.
  Forms: PDF report (10 pp), interactive dashboard (7 chapters) + Artifact, ER-1 notebook cell.

# Classification
value_stream: Phillies Offense
value_stream_code: pos
status: Build Complete — READY-CONDITIONAL, 5 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (player-facing excerpt limited to chapters 1, 4, 5; teammate comparisons stay internal)

# People
personas: Front office, player development, hitting and infield coaches, analysts
owner: Kellen Short

# Relationships
parent_use_case: uc-pos-019 (K54 recap spine) ; uc-pos-014 v1.1.0 (K40a bat path, O-15) ; uc-pos-010 (Stott approach change, dp_uc33) ; human parent notebook export "Bryson Stott"
related: uc-pos-008 (Arraez acquisition) ; uc-pos-013 (Bohm) ; UC5 (left-side infield proxy) ; uc-pos-017 (DR-1 directional)
supersedes: nothing (uc-pos-010 stays the August approach read)
sub_use_cases: []
closure: tripwires T-1..T-6 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 55
created: 2026-10-22
last_updated: 2026-10-22
anchor: phils_2026.parquet max game_date 2026-10-01 (regular season ends 2026-09-27)
build_artifact: dp_uc55_stott_recap.py
kernel: dp_uc55_kernel.py (imports dp_uc54_kernel.py 1a31b30a…, dp_uc40a_kernel.py 807986c0…; 14 pins)
report: dp_uc55_stott_2026_recap_report.md / .pdf
dashboard: dp_uc55_stott_2026_dashboard.html ; Artifact "Stott 2026 Recap"
verification: dp_uc55_verification.py — 185/185
dq: 15 PASS / 5 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pos-020-stott-2026-recap-001/

# Data References
kpis: [nresults_unrounded, xwoba_pa (XW-1), chase_rate_g, whiff_rate_fix, hard_hit_rate_fix, barrel_rate_g, battedball_profile (CR-1), hit_direction (DR-1), rolling_form (RF-2/RF-2x), cumulative_frame (CM-1), swing_path_profile (BP-1), house_percentile (KP-1), signature_verdict (PA-1), ER-1 (NEW), GS-1 (NEW), IO-1 (NEW)]
data_domains: At-Bat Outcomes, Plate Discipline, Batted Ball, Bat Tracking, Infield Defense (proxy), Roster Context (carry-ins)
defects_found: [SRC-4 client frame game types, CL-1 client std-as-mean, ERA-1 2025 window pre-break, Q-1 F9 axis, Q-2 F7 overclaim, Q-3 harness O-8 denominator, J-1 JSON default, ENV-4 stale commits, ENV-5 Py3.10 f-strings]
```

# Bryson Stott 2026 Recap: "Another Level?"

> **Document status:** Build complete. Deliverables: `dp_uc55_stott_2026_recap_report.pdf`, `dp_uc55_stott_2026_dashboard.html` (Artifact "Stott 2026 Recap").
> Receipts: `out/dp_uc55_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pos-020-stott-2026-recap-001/`.

## Business Context
### Problem Statement
Stott's 2026 is over and he is under control through 2027. The front office and coaches need a governed answer to three things: whether there is "another level", what his successful stretches had in common, and where he should play.

### Questions answered
1. Cumulative wOBA/OPS across 2026 vs prior seasons; the season KPI panel (report §2)
2. What "Good" looks like, and a better way to set the timeframes (§3, ER-1)
3. Good vs Bad A/B test (§4, GS-1, pre-registered)
4. All fields? Line drives or fly balls? (§5, plus bat path)
5. Lefties, righties, pitch types, velocity (§6)
6. Chasing less, walking more (§2, §4)
7. 2B vs prior years; 3B full time; the thump trade-off (§7)
8. Is there another level? (§1, §8)

### Out of scope
2027 projection · contract/extension valuation · fielding metrics the log lacks (carry-ins only) · causal claims about the stance change · MLB-wide ranks.

## Acceptance criteria
- Entity locked by MLBAM id; regular season for rates; postseason and spring separate — **met**
- Every superlative names its population and n — **met**
- Every published number reconciles to a receipt — **met** (harness F)
- Carry-ins labelled and never computed on — **met** (harness G)
- Era rule and signature bars registered before any split was computed — **met** (BID 19:27 ET; harness A)
- Cumulative wOBA/OPS lines and cleaner versions of the client's plots — **met** (F1, F4, F6, F7, F8)
- 00–07 receipts and a bid with token and time estimates — **met**
