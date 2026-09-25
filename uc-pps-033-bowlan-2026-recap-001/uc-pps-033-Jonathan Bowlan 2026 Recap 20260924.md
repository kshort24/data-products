```yml
# Identity
name: Jonathan Bowlan 2026 Season Recap 20260924
id: uc-pps-033-Jonathan Bowlan 2026 Recap 20260924
description: >
  Season recap of Jonathan Bowlan's 2026 (59 appearances, RHP reliever) built from the client's
  September 2026 notebook cells 115–117. It functionalizes the recap table, grades the client's
  22 claims and the Gemini cell, explains the uc-pps-032 archetype flip (RESULTS-ONLY 2025 →
  ELITE 2026) through the +1.5 mph velocity gain, and ties each result to hypotheses about actions
  in the pitching value stream, each with its data signature. Primary consumable is an
  interactive narrative dashboard with a persona lens and a pitch-type drill-through.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL, 6 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (external publish permissible after DPO review)

# People
personas: Front Office, Pitching Coach, Pitching Analyst, Catcher, Manager, Pitcher
owner: Kellen Short

# Relationships
parent_use_case: uc-pps-032 (UC#47, four-seam grades inherited) ; human parent September 2026.ipynb cells 115-117
related: uc-pps-012 (bullpen relievers), uc-pps-029 (bullpen script), uc-pos-012 (runs_created / rc_per_pa)
supersedes: nothing (supersedes the uc-pps-032 carry-in "suspected oblique" → reported right groin strain, no IL)
sub_use_cases: []
closure: tripwires T-1..T-5 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 48
created: 2026-09-24
last_updated: 2026-09-25
anchor: phils_2026.parquet max regular-season game_date 2026-09-23
build_artifact: dp_uc48_bowlan_recap.py
kernel: dp_uc48_kernel.py (imports dp_uc44_kernel.py, sha256 a2c119096db2…)
report: dp_uc48_bowlan_2026_recap_report.md / .pdf
dashboard: dp_uc48_bowlan_2026_dashboard.html (self-contained, offline)
verification: dp_uc48_verification.py — 153/153
dq: 16 PASS / 3 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-033-bowlan-2026-recap-001/

# Data References
kpis: [pitches, plate_apps, ba, obp, slg, ops, woba, krate, bbrate, hr_rate, runs_created, games, rc_per_pa,
       rc_per_gm (NEW), ff_vert, ff_velo, ff_spin, whiff_rate_breaking (NEW), whiff_rate_iz_ff (NEW),
       KP-1 house_percentile (NEW), AR-2 arsenal (NEW), CS-1 count_state (NEW), US-1 usage (NEW),
       VE-1 velo_by_outing (NEW), PA-1 persona signatures (NEW), rv100 (uc-pps-032, 2nd use), xwobacon (inherited)]
data_domains: At-Bat Outcomes, Batted Ball Profile, Pitch Profile, Pitch Outcomes, Strike Zone, Usage
defects_found: [O-25 pitch_mix pfx rounding, B-1 GroupBy.first non-null, HP-18 leaked loop state]
```

# Jonathan Bowlan 2026 Recap: "The Tick and a Half"

> **Document status:** Build complete. Deliverables: `dp_uc48_bowlan_2026_dashboard.html` (primary), `dp_uc48_bowlan_2026_recap_report.pdf`.
> Receipts: `out/dp_uc48_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pps-033-bowlan-2026-recap-001/`.

## Business Context

### Problem Statement
Bowlan came over from Kansas City for Matt Strahm, pitched in 59 games, and finished the season as the only elite right-handed four-seam on the staff. My notebook shows he threw harder and spun it more. It doesn't show *why that mattered*, whether the K and BB gains are real, or what the people around him did that the data can actually see. It also needs to be a function, so the next recap (Luzardo, Nola, Painter, Wheeler) doesn't start from a copied cell.

### Business Questions — Answered
1. **What changed between 2025 and 2026?** Velocity: 95.5 → 97.0 mph (+1.51, p < .001), from the first pitch of every outing. Ride held (17.7 → 18.0 in). The velocity grade moving 50 → 60 flipped the four-seam from RESULTS-ONLY (#20) to ELITE (#2 of 405).
2. **Is the K rate elite?** 31.5% is the 92nd percentile of 198 Phillies pitcher-seasons since 2015 (≥100 PA), second on the 2026 staff to Duran. The 25.4% → 31.5% jump is not statistically settled (p = 0.18).
3. **How was he used differently?** One late inning (multi-inning 47% → 10%; 41 of 59 entries in the 7th or 8th). The four-seam was called at two strikes (35% → 52%) and when behind (33% → 52%), both p < .01. Platoon arsenal: FF + CH to lefties (58% → 82%), a new sweeper to righties (16%), the curveball shelved.
4. **Which of my notebook claims held?** 17 of 22 held, 4 partly, 1 notebook-state hazard. The "xxth Percentile" is the 92nd.
5. **Was there a warning before 9/17?** No. His last five outings averaged 96.9 mph against 97.0 for the season.

### Actions
- **Pitching coach:** the sinker (whiff .176 → .055, xwOBAcon .187 → .393) is the first spring item. Keep whatever produced the whole-arsenal velocity gain.
- **Pitching analyst:** give the sweeper a real sample before judging it (−6.1 RV/100 on 77 pitches). Fix `pitch_mix` rounding (O-25) before the next shape comparison.
- **Catcher / manager:** the two-strike four-seam plan worked. Workload risk is frequency (6 back-to-backs, median 2 days' rest), not length.
- **Front office:** the acquisition thesis (buy plus ride and whiff before the run prevention shows) has STRONG signatures. The confirming evidence is the pro-scouting file.

## Data Specification (summary)
- **Grain:** pitch (CF-1 career frame) → pitcher-season, appearance, count state, pitch-of-outing bucket.
- **Entity key:** `pitcher == 680742`. Regular season only; 47 spring rows and 19 cross-source duplicates removed.
- **Populations:** KP-1, Phillies pitcher-seasons 2015–26 ≥100 PA (198). Staff four-seams, Phillies RHP 2015–26 excluding 2017 (132 seasons ≥100 FF). Four-seam grades inherited from uc-pps-032 (405).
- **Known gaps:** percentiles are not MLB-wide. Persona actions are hypotheses. The trade and the injury are carry-ins.
