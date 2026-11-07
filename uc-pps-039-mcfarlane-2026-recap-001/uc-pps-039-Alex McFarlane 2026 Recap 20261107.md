# Use Case uc-pps-039 — Alex McFarlane 2026 Recap ("Nasty Stuff, Outlier Heater")

```yml
# Identity
name: Alex McFarlane 2026 Recap 20261107
id: uc-pps-039-Alex McFarlane 2026 Recap 20261107
description: >
  Governed 2026 season recap of RHP Alex McFarlane, told in the client's own narrative (CL-1) with every claim graded on bars filed before
  grading. Reproduces the client frame (333 pitches, 21 outings incl. 2 Wild Card), ranks the four-seam on velocity and spin (FO-1), counts
  bridge-to-Duran outings (BD-1), and pairs his first 21 outings with Orion Kerkering's (S-1 stretch). Ships PDF, dashboard and a Claude Design slide kit.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL (C1-C5), awaiting DPO sign-off
priority: Medium

# People
personas: Front Office, Pitching Coach, Bullpen / Manager, Content, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: client notebook code + narrative (intake/client_prompt_2026-11-07.md); recap shape UC48-UC62; kit pattern UC61; FF population floor UC47
sub_use_cases: []

# Metadata
uc_number: 63
build: dp_uc63 v1.0.0
kernel: dp_uc63_kernel.py (imports dp_uc62_kernel 2adc6005..., 11 pins)
entity_lock: pitcher == 686934 (Duran 661395, Kerkering 689147)
window: client frame = Phillies pitching, all game types (313 R + 20 F); context = regular season 2015-2026; anchor 2026-10-01
kpis_inherited: nresults, whiff_rate, chase_rate, putaway_rate, hard_hit_rate, pitch_mix, lhb/rhb_pitch_mix, barrel_rate (BR-1), xwoba_pa (XW-1), woba_statcast (WB-1), house_percentile (KP-1), arsenal_table, house_pitcher_seasons (RP-1)
kpis_new: FO-1, BD-1, ST-1, FN-1 (provisional); BS-1r (generalization); CL-1 copy rule
deliverables:
  - dp_uc63_mcfarlane_2026_recap_report.pdf (10 pp)
  - dp_uc63_mcfarlane_2026_dashboard.html (+ Artifact "Alex McFarlane 2026")
  - out/dp_uc63_design_kit/ (13-slide content, brief, registry, data, refs)
  - out/dp_uc63_* (52 receipts)
verification: harness 45/45 · DQ 10/6/0 · V1-V7 8/8
trail: Agents for Data Products/data-products/uc-pps-039-mcfarlane-2026-recap-001/
```
