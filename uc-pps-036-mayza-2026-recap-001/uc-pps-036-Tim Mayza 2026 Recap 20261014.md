```yml
# Identity
name: Tim Mayza 2026 Recap 20261014
id: uc-pps-036-Tim Mayza 2026 Recap 20261014
description: >
  Season recap of LHP reliever Tim Mayza's 2026 (MLBAM 641835): results, contact and sustainability, platoon,
  stuff and delivery, the bullet slider, the Mayza Success Rate (QA-1), and delivery comps among Phillies LHP.
  Human parent: client notebook export + July 2026.ipynb cell 137. Forms: PDF report + interactive dashboard.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL, 5 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (external publish permissible after DPO review)

# People
personas: Pitching department, bullpen staff, front office
owner: Kellen Short

# Relationships
parent_use_case: UC51 uc-pps-035 (kernel by import; IX-1 second use) ; human parent: notebook export + July 2026.ipynb cell 137
related: uc-pps-033 (Bowlan recap), uc-pps-034 (Luzardo recap), uc-pps-035 (Wheeler recap)
supersedes: nothing
sub_use_cases: []
closure: tripwires T-1..T-4 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 52
created: 2026-10-14
last_updated: 2026-10-14
anchor: phils_2026.parquet max game_date 2026-10-01 (last RS appearance 2026-09-25)
build_artifact: dp_uc52_mayza_recap.py
kernel: dp_uc52_kernel.py (imports dp_uc51_kernel.py sha256 4845bae22861…)
report: dp_uc52_mayza_2026_recap_report.md / .pdf
dashboard: dp_uc52_mayza_2026_dashboard.html ; Artifact "The Sheriff of the Phillies Bullpen"
verification: dp_uc52_verification.py — 74/74
dq: 12 PASS / 0 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-036-mayza-2026-recap-001/

# Data References
kpis: [nresults (house wOBA), runs_created, house_percentile KP-1, XW-1, BR-1, hard_hit_rate, whiff/chase/putaway, QA-1 (NEW), BS-1 (NEW), DS-1 (NEW), RP-1 (NEW classifier), WB-1 (NEW basis companion)]
data_domains: At-Bat Outcomes, Batted-Ball Quality, Pitch Profile, Release/Delivery
defects_found: [EN-2 CF-2 projection gaps, HX-1 NF-1 drops launch_speed_angle, WB-1 wOBA basis mismatch, DEF-1 client success-rate pre-pitch count, RQ-1 kaleido string-x, RQ-2 '<' swallows PDF sections, RQ-3 pipe splits table]
```

# Tim Mayza 2026 Recap: "The Sheriff of the Phillies Bullpen"

> **Document status:** Build complete. Deliverables: `dp_uc52_mayza_2026_recap_report.pdf` (9 pp), `dp_uc52_mayza_2026_dashboard.html` (8 chapters; Artifact).
> Receipts: `out/dp_uc52_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pps-036-mayza-2026-recap-001/`.

## Business Context
### Problem Statement
Mayza was one of the Phillies' most dependable relievers in 2026. The client wants to know what he did well, whether it was sustainable, what is distinctive about his stuff and delivery, and how he compares with his own history and with Phillies LHP relievers. The output must stay comparable with the UC48, UC49 and UC51 recaps.
### Questions answered
1. What did he do well? (report §1–2)
2. Was it sustainable? (§3)
3. How were his platoon splits? (§4)
4. Is his stuff or release point exceptional? (§5)
5. Which pitch is his weapon against each side? (§6)
6. Does the Mayza Success Rate hold up? (§7)
7. Which Phillies LHP is most similar? Is he "Alvarado lite"? (§8)
8. Were the notebook's claims right? (§9)
### Out of scope
ERA as computed (runs on watch instead) · medical inference · MLB-wide ranks · 2027 projection · mound-position claims · video.

## Acceptance criteria
- Entity locked by MLBAM id; regular season for rates; postseason separate — **met**
- Every superlative names its population and n — **met**
- Every published number reconciles to a receipt — **met** (harness F 16/16)
- Carry-ins labelled and never computed on — **met** (harness G 4/4)
- Comparison-profile cap (≤10 pp / ≤9 sections · ≤8 chapters · ≤10 figures · ≤3 new KPIs) — **met** (9 pp / 9 · 8 · 10 · 3)
- 00–07 receipts and a bid with token and time estimates — **met**
