```yml
# Identity
name: José Alvarado 2026 The Full Ride 20261018
id: uc-pps-037-José Alvarado The Full Ride 20261018
description: >
  Season recap of José Alvarado (LHP, MLBAM 621237) with a Phillies-tenure lens (2021-26): results vs his own
  seasons and Phillies relievers, the cutter, velocity, command, outing volatility, and a pre-registered
  decline-or-blip verdict. Driven by the client notebook export "Jose Alvarado" (c9ed969a-attachment.txt).
  Forms: PDF report (10 pp), interactive dashboard (7 chapters) + Artifact.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL, 6 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (external publish permissible after DPO review)

# People
personas: Front office, pitching department, bullpen staff
owner: Kellen Short

# Relationships
parent_use_case: UC52 uc-pps-036 (kernel, WB-1 second use, RP-1 second use) ; human parent notebook export "Jose Alvarado"
related: uc-pps-016 (Alvarado multi-stint flag, MLBAM id) ; UC48/49/51/52 season recaps (comparison profile)
supersedes: nothing
sub_use_cases: []
closure: tripwires T-1..T-5 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 53
created: 2026-10-18
last_updated: 2026-10-18
anchor: phils_2026.parquet max game_date 2026-10-01 (regular season ends 2026-09-27)
build_artifact: dp_uc53_alvarado_recap.py
kernel: dp_uc53_kernel.py (imports dp_uc52_kernel.py sha256 3667f8028acd… and cumulative_metric.py a28887406d98…)
report: dp_uc53_alvarado_2026_recap_report.md / .pdf
dashboard: dp_uc53_alvarado_2026_dashboard.html ; Artifact "The Full Ride"
verification: dp_uc53_verification.py — 163/163
dq: 11 PASS / 2 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-037-alvarado-2026-recap-001/

# Data References
kpis: [nresults, whiff_rate, chase_rate, putaway_rate, hard_hit_rate, barrel_rate, runs_created, xwoba_pa (XW-1), woba_statcast (WB-1), csw (locked), game_score (GS-1), signature_verdict (PA-1), cumulative_frame (CM-1/CM-1a), OD-1 (NEW), DB-1 (NEW)]
data_domains: At-Bat Outcomes, Pitch Profile, Appearance Log, Roster Context (carry-ins)
defects_found: [CM-D1 cumulative wOBA numerator, AB-1 automatic pitches, RK-2 K-BB rounding, ENT-1 id under batter name, ENV-3 pip TMPDIR]
```

# José Alvarado 2026 Recap: "The Full Ride"

> **Document status:** Build complete. Deliverables: `dp_uc53_alvarado_2026_recap_report.pdf`, `dp_uc53_alvarado_2026_dashboard.html` (Artifact "The Full Ride").
> Receipts: `out/dp_uc53_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pps-037-alvarado-2026-recap-001/`.

## Business Context
### Problem Statement
2026 is most likely Alvarado's last season with the Phillies (free agent; CI-2). The front office needs his tenure in context, an account of how 2026 declined, and a defensible answer to "move on, or was it a blip?"
### Questions answered
1. How much did the Phillies lean on him, and how good was his peak? (report §2)
2. How did 2026 compare with his own standard? (§3)
3. What happened to the cutter, the velocity and the strike zone? (§4–§6)
4. Was 2026 inconsistent, and how? (§7)
5. Move on, or a blip? (§8, pre-registered)
6. Were the notebook's claims right? (§9)
### Out of scope
ERA as computed (runs on watch instead) · medical inference · inference about the 2025 suspension · MLB-wide ranks · 2027 projection · contract terms.

## Acceptance criteria
- Entity locked by MLBAM id with the pitching role; regular season for rates; postseason separate — **met**
- Every superlative names its population and n — **met**
- Every published number reconciles to a receipt — **met** (harness F 59/59)
- Carry-ins labelled and never computed on — **met** (harness G 9/9; DQ-12)
- Verdict rule registered before 2026 rates were read — **met** (kernel note; harness A)
- 00–07 receipts and a bid with token and time estimates — **met**
