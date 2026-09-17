```yml
# Identity
name: Cristopher Sanchez Command Diagnosis 20260916
id: uc-pps-031-Cristopher Sanchez Command 20260916
description: >
  Diagnoses Cristopher Sánchez's 2026 command against 2021-2025. Tests four client premises (walks, zone,
  chase, ahead-in-count) at season and in-season grain; inherits the governed Edge Rate; introduces the Shadow
  Zone family (zone grown by one baseball) and proves the diagnosis with chase on pitches that miss the shadow.
  Controls for the 2026 strike-zone rail redefinition (O-18).

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — Ready for DPO Sign-off (READY-CONDITIONAL, 436/436 verified)
priority: High

# People
personas: Pitching Coach, Pitching Analyst, Catcher, Manager, Pitcher
owner: Kellen Short

# Relationships
parent_use_case: uc-pps-019 (Sánchez first-half ASG) · pattern UC8 -> uc-pps-017 -> uc-pos-014 -> uc-pps-030
sub_use_cases: []

# Metadata
created: 2026-09-16
last_updated: 2026-09-16
build_artifact: dp_uc45_sanchez_command.py (kernel dp_uc45_kernel.py)
governance_trail: Agents for Data Products/data-products/uc-pps-031-sanchez-command-diagnosis-001/

# Data References
kpis:
  - bbrate (locked)
  - in_zone_rate, chase_rate (locked)
  - First Pitch Strike Rate (locked)
  - whiff_rate, barrel_rate, hard_hit_rate (locked)
  - edge_rate (governed, UC8, Register P16 = A)
  - count_leverage / pitch_share_ahead (CL-1 = PD-7 promoted)
  - shadow_region, shadow_zone_rate, shadow_miss_rate, beyond_shadow_chase_rate, edge_out_chase_rate, shadow_miss_direction (NEW SZ-0..SZ-5, provisional)
  - peer_delta_pitcher (NEW PN-1, provisional)
  - common_rail_rescore (NEW ZC-1, provisional)
data_domains: At-Bat Outcomes, Pitch Outcomes, Strike Zone, Count State
```

# Cristopher Sánchez — is he near the zone?

> **Document status:** deliverable `dp_uc45_sanchez_command_report.pdf` + `dp_uc45_command_dashboard.html` ·
> trail `00`–`07` in the control-plane folder · receipts `out/dp_uc45_*`

## Business Context

### Problem Statement
Sánchez is struggling with his command in 2026. We need to know whether the walks and bad counts come from being
*around* the zone and not getting the swings, or from missing the zone's shadow altogether, and we need the
answer on a definition of "edge" and "shadow" that matches what the repo already governs.

### Business Questions — Answered
1. *Is his walk rate up?* Not for the season (.054 → .055). Yes since the break (.048 → .068, directional).
2. *Is he in the zone less?* Yes (.519 → .465), but a third of that is the 2026 zone redefinition. On common rails, half is his own.
3. *Is he getting less chase?* Not for the season (up, .316 → .362). Yes since the break (.386 → .320, p = .008).
4. *Is he getting ahead less?* Not for the season (.311 → .313). Yes since the break (.333 → .278, p = .002).
5. *Is he near the zone?* Near the edge as often (Edge Rate .365 → .358). Missing the one-ball shadow more (.344 → .407, +.038 his own).
6. *Proof?* Chase on pitches beyond the shadow fell from .333 to .260 after the break (p = .008) while the league held at .274 → .276. The leak is the changeup to RHB.

### Actions
- **Pitching coach:** target the shadow on the changeup to RHB, not the heart. Track SZ-2 on that pitch (2H .621).
- **Catcher:** when ahead against RHB, set the chase target inside the shadow.
- **Analyst:** put every 2025↔2026 zone comparison through ZC-1.
- **Manager:** this is one pitch against one side of the plate, not a general decline (xwOBA .279 → .286).

## Data Specification (summary)
Grain: pitch. Entity: `pitcher == 650911`. Source: `phils_2021…2026.parquet`, regular season, deduplicated,
through 2026-09-15. 2021-22 combined. 2026 halves cut at 07-13. Geometry: `PLATE_HALF = 0.83`,
`BALL_FT = 2.94/12`, per-pitch rails. Known gap: 2026 rails are a per-batter constant (O-18), controlled with
ZC-1/PN-1. `arm_angle` not used (77.7% complete).
