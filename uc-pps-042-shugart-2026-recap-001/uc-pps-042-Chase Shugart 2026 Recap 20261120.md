# Use Case uc-pps-042 — Chase Shugart 2026 Recap ("A Solid Middle Reliever Who Rebuilt His Plan Against Lefties")

```yml
# Identity
name: Chase Shugart 2026 Recap 20261120
id: uc-pps-042-Chase Shugart 2026 Recap 20261120
description: >
  Governed 2026 season recap of RHP reliever Chase Shugart: high-level performance vs Phillies RHP relief seasons (CS-A), platoon split vs the
  righty-reliever norm, pitch plot and pitch map (every pitch + density), pitch x hand drivers vs CS-C, cumulative pitch usage (CU-1) and cumulative
  wOBA/xwOBA (CW-1) by batter hand, months, role (LC-1 vs the 2026 bullpen) and command by stint (S-1). The client's scratch claims graded on
  pre-registered bars. Redesigned recap visuals under VZ-1..VZ-6. Ships PDF, interactive dashboard, PNGs and the 00-07 trail.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL (C1-C4), awaiting DPO sign-off
priority: Medium

# People
personas: Pitching Coach, Pitching Analyst, Front Office, Content
owner: Kellen Short

# Relationships
parent_use_case: client prompt + scratch notebook (intake/client_prompt_2026-11-20.md, intake/client_scratch_shugart_2026.md); recap shape UC48-UC64
sub_use_cases: []

# Metadata
uc_number: 66
build: dp_uc66 v1.0.0
kernel: dp_uc66_kernel.py (imports dp_uc64_kernel 32a83b8491dd..., full chain asserted)
entity_lock: pitcher == 663767
window: regular season 2026 (871 pitches, 46 outings); context pools regular season 2015-26; anchor 2026-10-01; FR-1 client frame (944 incl. 73 spring) reconciled, not graded
comparison_sets: CS-A phi_rhp_relief_seasons (DRAFT) · CS-B phi_bullpen_2026 · CS-C phi_rhp_pitch_stand_seasons · own history NOT OBSERVABLE
kpis_inherited: nresults, whiff_rate, chase_rate, putaway_rate, fpsr, hard_hit_rate, pitch_mix, lhb/rhb_pitch_mix, rv100, house_percentile (KP-1), context_frame (CX-1), xwoba_pa (XW-1), barrel_rate (BR-1), RP-1, outing_ledger, FN-1, cumulative_frame
kpis_new: FR-1, CS-A, CS-B, CS-C, IN-1, LC-1 (= FN-1), CU-1, CW-1, S-1 (provisional) · visual rules VZ-1..VZ-6 (provisional)
deliverables:
  - dp_uc66_shugart_2026_recap_report.pdf (11 pp)
  - dp_uc66_shugart_2026_dashboard.html
  - out/dp_uc66_*.png (11 figures)
  - out/dp_uc66_* (64 receipts)
verification: harness 34/34 · DQ 12 PASS / 5 WARN / 0 FAIL · V1-V7 11/11 figures · HP 8 SUPPORTED / 3 PARTLY / 1 NOT
trail: Agents for Data Products/data-products/uc-pps-042-shugart-2026-recap-001/
```

## Acceptance criteria → status
| # | Criterion (BID) | Status |
|---|---|---|
| 1 | every number traces to an `out/dp_uc66_*` receipt computed this session | MET (report/dashboard generated from receipts; harness V25–V29) |
| 2 | FR-1 reconciles exactly | MET (.430 SLG / 10.0% barrel == regular-season frame) |
| 3 | HP bars unchanged after first compute | MET (`03` §6) |
| 4 | harness all PASS | MET 34/34 |
| 5 | V1–V7 + VZ recorded per figure | MET 11/11 (`05` §4) |
| 6 | certification verdict in `05` | MET — READY-CONDITIONAL |
| 7 | bid vs actual in `07` | MET (≈325k / ≈43 min vs ≈410k / ≈64 min) |
