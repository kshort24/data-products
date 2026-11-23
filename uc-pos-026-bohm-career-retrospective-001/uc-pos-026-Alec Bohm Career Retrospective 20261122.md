```yml
# Identity
name: Alec Bohm Career Retrospective 20261122
id: uc-pos-026-Alec Bohm Career Retrospective 20261122
description: >
  Governed 2026 recap of 3B/1B Alec Bohm that continues uc-pos-013 out of sample (PR-1 H-F on the 8/24-9/27 window) and closes his
  Phillies career (2020-26) on the assumption that he does not return. Grades the client's line-drive, platoon, RHP-breaking-ball and
  luck claims; decides the line-drive angle by a filed pool gate (G-LD, failed); defines deciding runs (GW-1) over every Phillies win
  since 2015; reports RISP results with a repeatability rule (RS-1). Finds and fixes a house PA defect (TP-1, truncated_pa).

# Classification
value_stream: Phillies Offense
value_stream_code: pos
status: Build Complete — READY-CONDITIONAL (C1-C7), awaiting DPO sign-off
priority: Medium

# People
personas: Front Office, Hitting Coach, Pro Scouting, Analyst
owner: Kellen Short

# Relationships
parent_use_case: uc-pos-013 (UC #38, dp_uc37) - inherited by import (risp_rows, BREAK), graded (HP-09) and scored out of sample (PR-1 H-F)
sub_use_cases: []

# Metadata
uc_number: 67
build: dp_uc67 v1.0.0
kernel: dp_uc67_kernel.py (imports dp_uc61_kernel 0466c66e..., dp_uc48_kernel 0f63857a..., dp_uc62_kernel 2adc6005..., dp_uc37_kernel 396c4600...; + K61's 23 pins)
entity_lock: batter == 664761
window: MLB regular season 2020-2026; house anchor 2026-10-01
kpis_inherited: nresults_unrounded (WB-2), xwoba_pa (XW-1), woba_statcast (WB-1), cell_panel, season_panel, battedball_profile (CR-1), pull_air (K46), hit_direction (DR-1), derive_loc (PA-L1), hitter_seasons + house_percentile (KP-1), runs_created (runs on watch), risp_rows, wall_outline, PA-1
kpis_new: GW-1 (provisional), XC-1 (provisional), G-LD gate (provisional), RS-1 (provisional), TP-1 frame rule
deliverables:
  - dp_uc67_bohm_career_retrospective_report.pdf (7 pp)
  - dp_uc67_bohm_career_retrospective_dashboard.html
  - out/dp_uc67_* (43 receipts)
verification: harness 51/51 · DQ 11/0/0 · V1-V7 8/8
trail: Agents for Data Products/data-products/uc-pos-026-bohm-career-retrospective-001/
```
