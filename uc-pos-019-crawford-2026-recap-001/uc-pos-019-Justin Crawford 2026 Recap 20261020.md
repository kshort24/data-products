```yml
# Identity
name: Justin Crawford 2026 Exactly as Advertised 20261020
id: uc-pos-019-Justin Crawford Exactly as Advertised 20261020
description: >
  Season recap of Justin Crawford (CF, bats L, MLBAM 702222), rookie year 2026: cumulative results vs Phillies
  centre-field seasons, a pre-registered test of "better from June 1", approach, ground balls, chase cost,
  RHP breaking balls (AAA 2025 vs MLB 2026), and centre-field defense (client method + sector proxy).
  Driven by the client notebook export "Justin Crawford" (a4523113-attachment.txt).
  Forms: PDF report (10 pp), interactive dashboard (7 chapters) + Artifact.

# Classification
value_stream: Phillies Offense
value_stream_code: pos
status: Build Complete — READY-CONDITIONAL, 5 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (player-facing excerpt limited to chapters 3-5; external publish only after DPO + privacy review)

# People
personas: Front office, player development, hitting and outfield coaches, analysts
owner: Kellen Short

# Relationships
parent_use_case: uc-pos-011 (Crawford YTD, dp_uc34: CX-1, CR-1/CR-2) ; uc-pos-014 (K40 pos spine) ; human parent notebook export "Justin Crawford"
related: uc-pos-005 (OZ attack regions) ; uc-pos-017 (DR-1 directional) ; UC48-53 season recaps (comparison profile) ; UC4 (outfield proxy precedent)
supersedes: nothing (uc-pos-011 stays the mid-season read)
sub_use_cases: []
closure: tripwires T-1..T-5 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 54
created: 2026-10-20
last_updated: 2026-10-20
anchor: phils_2026.parquet max game_date 2026-10-01 (regular season ends 2026-09-27)
build_artifact: dp_uc54_crawford_recap.py
kernel: dp_uc54_kernel.py (imports dp_uc40_kernel.py 895c0edc…, dp_uc34_kernel.py 263e57d1…, dp_uc53_kernel.py 03d7e380…, cumulative_metric.py a2888740…; IX-1 from dp_uc22 530d05cd… and Baseball Functions.ipynb)
report: dp_uc54_crawford_2026_recap_report.md / .pdf
dashboard: dp_uc54_crawford_2026_dashboard.html ; Artifact "Crawford 2026 Recap"
verification: dp_uc54_verification.py — 157/157
dq: 12 PASS / 4 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pos-019-crawford-2026-recap-001/

# Data References
kpis: [nresults_unrounded, risp_rows, swing_rate, chase_rate_g, whiff_rate_fix, ooz_whiff_rate, hard_hit_rate_fix, barrel_rate_g, battedball_profile (CR-1), xwoba_pa (XW-1), bat_tracking (BT-1), rolling_form (RF-2), breakpoint_scan (RC-5), cf_context_pool (CX-1), cumulative_frame (CM-1), tag_regions (OZ), hit_direction (DR-1), find_similar_hits (XO-1), TR-1 (NEW), CC-1 (NEW), XO-2 (NEW)]
data_domains: At-Bat Outcomes, Plate Discipline, Batted Ball, Outfield Defense (proxy), Minor-League Supporting Tier, Roster Context (carry-ins)
defects_found: [SF-1 K40 sac-fly DP denominators, TP-1 K40 truncated_pa, CM-D2 cumulative hard-hit nullable EV, ENT-2 wrong-Crawford file, SRC-2 duplicate MLB rows in an opponent file, ENV-3 pip TMPDIR]
```

# Justin Crawford 2026 Recap: "Exactly as Advertised"

> **Document status:** Build complete. Deliverables: `dp_uc54_crawford_2026_recap_report.pdf`, `dp_uc54_crawford_2026_dashboard.html` (Artifact "Crawford 2026 Recap").
> Receipts: `out/dp_uc54_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pos-019-crawford-2026-recap-001/`.

## Business Context
### Problem Statement
Crawford's rookie season is over. Player development and the front office need a governed answer to how he performed, whether he improved in-season, what his approach is, and where 2027 gains should come from, at the plate and in centre field.
### Questions answered
1. How did he perform in his rookie year? (cumulative BA, wOBA, OPS; RISP BA; GB rate; hard-hit rate) (report §2)
2. How did his performance evolve; was he better from ~June 1? (§3, pre-registered)
3. What was his approach? (§4)
4. How should he improve (walks, OBP, strikeouts)? (§6 walks, §7 righty spin)
5. How was his defense? (§8)
6. How was his ground-ball rate? (§5)
7. Were the notebook's claims right? (§9)
### Out of scope
2027 projection · MLB-wide ranks · fielding metrics the log lacks (shown only as carry-ins) · causal claims about platooning · contract or option valuation.

## Acceptance criteria
- Entity locked by MLBAM id with the batting role; regular season for rates; postseason separate — **met**
- Every superlative names its population and n — **met**
- Every published number reconciles to a receipt — **met** (harness F 39/39)
- Carry-ins labelled and never computed on — **met** (harness G 7/7)
- Turn test registered before any split was computed — **met** (BID 23:18 ET; harness A)
- Cleaner versions of the client's plots plus cumulative line graphs — **met** (F1, F6 cumulative; F7–F9 rebuilt from the client's charts)
- 00–07 receipts and a bid with token and time estimates — **met**
