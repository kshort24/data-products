# Use Case Contract — uc-pos-009

```yaml
use_case_id: uc-pos-009-schwarber-swing-decay-001
ledger_number: 33
build_artifact: dp_uc32
value_stream: pos
title: "Kyle Schwarber — state of the swing"
requested_by: Kellen Short (human Data Product Owner)
requested_date: 2026-08-08
delivered_date: 2026-08-08
status: certified
classification: Internal — Restricted
external_publication: BLOCKED (privacy-watchdog PW-2)

entity:
  subject: Kyle Schwarber
  lock: "batter == 656941"
  lock_type: MLBAM id
  handedness: L
  contamination_check: passed (name filter resolves to the same single id)

evidence_windows:
  full_career:   {span: "2015 → 2026-08-07", pitches: 24891, role: "baseline pricing"}
  bat_tracking:  {span: "2024 → 2026",       measured_swings: 3349, role: "carries the central claim"}
  swing_path:    {span: "2025 → 2026",       measured_swings: 2141, role: "corroboration only; 1 comparison season"}
  primary_frame: "within-2026 time trend (DPO decision)"
  as_of: 2026-08-07
  staleness: T-1

sources:
  - {path: "data/phillies/phils_2015..2026.parquet", filter: "phillies_role == 'batting'", role: primary}
  - {path: "data/opponents/schwarber.parquet",       span: "2015-2021",                    role: career backfill}
  filters_applied: ["batter == 656941", "game_type == 'R'", "dedup on game_pk × at_bat_number × pitch_number"]
  rows_dropped: {duplicates: 0, non_regular_season: 1275}
  manual_carry_ins: 0

business_questions:
  - "Has Schwarber lost power in 2026, and against which baseline?"
  - "Has it declined within the 2026 season, and when?"
  - "Is the cause physical (bat speed / mechanics) or behavioural (decisions / contact point)?"
  - "Which pitch types, velocities, counts and directions carry the loss?"
  - "What action can each persona in the value stream take?"
  - "How should sensor-era NULLs be handled, and what would imputation have cost?"

out_of_scope:
  - recovery projection / aging model
  - park adjustment
  - opponent-quality adjustment
  - causal claim linking chase rate to launch-angle drift
  - any health, injury, workload or fatigue inference (deliberate — see 02 §6 PW-3)

kpis_inherited_locked:
  [whiff_rate, chase_rate, in_zone_whiff_rate, barrel_rate, hard_hit_rate, ev90, inds, xwoba_on_contact]

kpis_new_provisional:
  SW-1: {name: Sweet-Spot Rate,           window: full_career,  status: "shipped WITH demonstrated failure mode"}
  SW-2: {name: Ideal-Contact Rate,        window: full_career,  status: "promotion candidate — strong"}
  SW-3: {name: Fast-Swing Rate,           window: bat_tracking, status: provisional}
  SW-4: {name: Squared-Up Rate,           window: bat_tracking, status: "provisional — OI-3"}
  SW-5: {name: Attack-Angle Fit Rate,     window: swing_path,   status: provisional}
  SW-6: {name: Contact Depth,             window: swing_path,   status: "provisional — carries an interpretation rule"}
  SW-7: {name: Bat-Tracking Coverage,     window: all,          status: "promotion candidate — strong (governance KPI)"}
  SW-8: {name: Damage-Band Rate,          window: full_career,  status: "promotion candidate — strong; band validated for 1 hitter"}
  SW-9: {name: Blast Rate,                window: bat_tracking, status: provisional}

governance_decisions:
  bat_speed_nulls:
    decision: "NO IMPUTATION + coverage gate"
    decided_by: human DPO
    decided_date: 2026-08-08
    enforced_by: [DQ-08, DQ-09, DQ-10, DQ-11, V-16, V-17, V-18, V-52]
    cost_of_rejected_alternative:
      seasons_with_zero_coverage: 9
      swings_that_would_be_fabricated: 7021
      share_of_career_swings: 0.677
      variance_destroyed: "sd 10.06 → 0 on filled seasons"
  intra_season_grain:
    decision: "data-driven phase split at the chronological BIP midpoint, not a calendar split"
    rationale: "equal evidence weight (120 vs 122 BIP); a break-based split would have been 156 vs 86"
  requested_kpi_failure:
    decision: "ship SW-1 with the demonstration of its failure; do not substitute silently"

acceptance_criteria:
  - "Every published number traces to a CSV receipt written by the build script"     # met, 24 receipts
  - "Zero imputed bat-tracking values in any deliverable, table or prose"            # met, V-16..18, V-52
  - "Sample size printed on every row of every split"                               # met
  - "Build DQ 100% pass"                                                            # met, 24/24
  - "Independent verification 100% pass"                                            # met, 59/59
  - "PDF deliverable"                                                               # met, 500 KB
  - "Interactive dashboard"                                                         # met, 104 KB offline
  - "Persona actions for the value stream"                                          # met, 7 personas

certification:
  dq_scorecard: {pass: 24, total: 24, fail: 0}
  verification:  {pass: 59, total: 59, fail: 0}
  receipts: 24
  figures: 5
  numbers_computed_outside_build: 0
  verdict: READY

headline_findings:
  - "Bat speed 74.2 mph in both 2025 and 2026; p90 81.0 in both 2026 phases — no physical decline"
  - "Barrel rate fell 24.2% → 9.8% across the phase split (−59.5%) while bat speed moved 0.006 mph"
  - "Damage band (20–32°) share fell 21.7% → 14.9%; the 8–20° band rose 18.3% → 27.3%"
  - "Sweet-spot %, hard-hit % and squared-up % ALL ROSE during the collapse"
  - "Chase rate 25.5% (nine-year high); strikeout rate 34.8% (career high)"
  - "2026 season line (.518 SLG / .276 ISO / 46-HR pace) is a normal Schwarber season; 2025 was his career best"
  - "Phase A exceeded his career-best 2025 — the A→B delta overstates the decline by roughly half"

open_items:
  OI-1: {item: "Promote the sensor-boundary NULL standard to CLAUDE.md", severity: non-blocking, value: high}
  OI-2: {item: "SW-1 warning label; ratify SW-2 / SW-7 / SW-8", severity: non-blocking}
  OI-3: {item: "SW-4 / SW-9 constants are published approximations", severity: non-blocking}
  OI-4: {item: "SW-8 band validated for one hitter only", severity: non-blocking}
  OI-5: {item: "O4 xwobacon size-semantics carry-forward", severity: non-blocking}
  OI-6: {item: "Nullable-dtype masking guidance for references/data-quality.md", severity: non-blocking}
  OI-7: {item: "No opponent-quality adjustment — largest unmodelled confounder", severity: non-blocking}
  OI-8: {item: "Intake note corrected — 2023 bat-speed coverage is 0.0%, not 'limited'", severity: informational}
blocking_items: 0

closure:
  trigger: "150 additional plate appearances (~2026-09-10)"
  projections:
    - "Bat speed holds at 74 ± 0.5 mph"
    - "Damage-Band Rate recovers above 18%"
    - "Chase rate falls below 24%"
  supersede_condition: "If bat speed drops below 73, supersede this UC rather than amend it"

ledger:
  inherits_from: [uc-pos-004 (dp_uc20), uc-pos-006 (dp_uc24), uc-pos-008 (dp_uc31)]
  next_available: {uc_number: 34, build: dp_uc33, contracts: [uc-pos-010, uc-pps-026]}
```

---

## Original request (verbatim, for the record)

> Work inside the `C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB` repository. This is the data plane. The Agents for Data Products repository this prompt connects to holds the agentic data product organization which provides the structure and engine to drive development of the data product against the use case I will provide. Output should be well-governed and documented including receipts following the standards of this repository, but it should also follow the scouting-report skill for inspiration and other similar outputs produced in the MLB repository. Coding standards and guidelines of the data plane are important for maintaining fidelity. I expect the receipts to be written in a subfolder of the data-products directory that is below the mounted repository for this prompt. It should follow the 00_ to 07_ format of the other receipts in that directory.
>
> I am concerned about the state of Kyle Schwarber's swing. He has lost some pop in his bat as the season has progressed. How do these underlying indicators that I have identified inform decisions that can be made against this use case. Provide an assessment on the state of things then consider personas within the value stream and the types of actions they can take to drive better expected outcomes.
>
> For context, I have also pulled all other Phillies LHB in the Statcast era and Schwarber's career history. Bat_speed is only available for 2024, 2025, and 2026 with very limited availability in 2023 as well. I had originally imputed Schwarber's mean bat speed for the missing values. I am not sure this is the best way to handle NULLs in general.
>
> I would like to include some data about ideal launch angle or sweet spot %, anything about the path of the swing could be interesting as well although data may be limited.
>
> [KPI code block — `barrel_rate` / `chase_rate` / `whiff_rate` / `whiff_rate_iz` / `inds` / `ev90` merged at `player_name × game_year × stand`, with a commented-out `.fillna()` on the career mean bat speed]
>
> I would like to see a pdf report as an output and expect a fully governed package to be delivered. If it makes sense, I would like to explore an interactive dashboard as a delivery method. Other output types are acceptable too. Any other additions to the data product can be driven by the data product organization.
>
> One more thing to consider — leverage the Brand Guidelines and brand-center-mcp folder in the data plane for sample graphs and formatting standards.

### Where the request was answered, corrected, or extended

| Request element | Disposition |
|---|---|
| Assessment of the swing | Report §1–4 |
| Persona actions | Report §8 — seven personas, including an opposing-scout mirror |
| Sweet spot % / ideal launch angle | Delivered as SW-1, **and shown to fail** — replaced by SW-2 and SW-8 (report §3) |
| Swing path | **Data exists.** `attack_angle`, `attack_direction`, `swing_path_tilt`, contact depth — report §4 |
| NULL handling question | Report §7, receipt `x1_imputation_harm`, Fig 4, and proposed as a repository standard (OI-1) |
| Phillies LHB context | Report §5 — demoted to secondary per the DPO's frame choice; `pool_n = 5` flagged |
| Supplied `game_year` grain | **Replaced** — could not answer an intra-season question (01 G-3, 04 §1.1) |
| Supplied query's missing dedup / `game_type` filter | **Corrected** in build; anti-pattern documented in 06 §5 |
| "2023 has very limited availability" | **Corrected** — coverage is 0.0% for this batter. Pinned by V-20 |
| PDF | ✅ 500 KB, Phillies-branded |
| Interactive dashboard | ✅ 104 KB, offline-capable, 8 tabs |
| Brand guidelines | Applied — `#E81828` / `#002D72` / `#7A99C2`, `plotly_white`-equivalent styling, title+subtitle pattern, rounding rules (three decimals no leading zero for rate stats; percentages to one decimal), **no pie charts** |
| "Other additions driven by the org" | Nine new KPIs, a coverage-gate governance control, an evidence-window vocabulary, seven monitoring rules, six query templates, and a proposed repository-wide NULL standard |
