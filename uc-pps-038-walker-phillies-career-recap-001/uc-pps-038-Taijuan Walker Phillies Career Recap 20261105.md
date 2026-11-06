```yml
# Identity
name: Taijuan Walker Phillies Career Recap 20261105
id: uc-pps-038-Taijuan Walker Phillies Career Recap 20261105
description: >
  Governed Phillies career recap (2023-26) of RHP Taijuan Walker read against the 2015-22 career the club bought. Rebuilds the
  client's wOBA-vs-K% chart on the governed pool (KR-1), scores a pre-registered stuff / luck / residual ledger (PR-1), and prices
  the contract per inning and per batter on the AAV basis (CE-1). Ends with the 2026 release and Angels minor-league carry-ins.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL (C1-C6), awaiting DPO sign-off
priority: Medium

# People
personas: Front Office, Pro Scouting, Pitching Coach, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: client turn-1 code + KS Taijuan Walker Analysis.csv (graded, not inherited); recap shape UC48-UC53; trail layout UC61
sub_use_cases: []

# Metadata
uc_number: 62
build: dp_uc62 v1.0.0
kernel: dp_uc62_kernel.py (imports dp_uc53_kernel 03d7e380..., 10 pins)
entity_lock: pitcher == 592836
window: MLB regular season 2015-2026; house anchor 2026-10-01
kpis_inherited: nresults, whiff_rate, chase_rate, hard_hit_rate, barrel_rate, xwoba_pa (XW-1), woba_statcast (WB-1), runs_created, outs_by_pa (OU-2), game_score (GS-1), arsenal_table, house_pitcher_seasons (KP-1 / RP-1), PA-1
kpis_new: KR-1 (provisional), CE-1 (provisional), PR-1 ledger (provisional)
deliverables:
  - dp_uc62_walker_phillies_career_recap_report.pdf (8 pp)
  - dp_uc62_walker_phillies_career_dashboard.html (+ Artifact "Taijuan Walker, Phillie")
  - out/dp_uc62_* (38 receipts)
verification: harness 47/47 · DQ 15/0/0 · V1-V7 9/9
trail: Agents for Data Products/data-products/uc-pps-038-walker-phillies-career-recap-001/
```
