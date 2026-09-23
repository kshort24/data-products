```yml
# Identity
name: Elite RHP Four-Seam Archetype Gap 20260922
id: uc-pps-032-Elite RHP FF Archetype Gap 20260922
description: >
  Pilot of the Archetype Gap Analysis product: given the 2026 Phillies roster, which
  player archetype — and which player embodying it — would move the needle most if
  added? Pilot archetype = the elite right-handed four-seam fastball. Part A ranks a
  six-arm Phillies-affiliated cohort (Wheeler, Painter, McFarlane, Duran, Bowlan,
  Seranthony Domínguez); Part B grades every non-Phillies RHP in a bounded, governed
  house frame (Phillies logs + nphl, MiLB and duplicates removed) and measures how
  each would change the staff's elite-four-seam share. Part H reproduces and grades
  the client's own notebook claims.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
value_stream_scope_note: >
  DPO decision 9 (2026-09-22) — kept in pps rather than a new `rca` stream. pps now
  includes evaluating non-Phillies pitchers against a Phillies pitching need.
status: Build Complete — READY-CONDITIONAL, 6 conditions — Ready for DPO Sign-off
priority: High
classification: Internal — Restricted (external publish blocked)

# People
personas: DPO, Front Office, Pitching Coach, Pitching Analyst
owner: Kellen Short

# Relationships
parent_use_case: UC#44 (uc-pps-030, SG-1/SG-2 grading engine) -> UC#47 (this)
related: uc-pps-018 (Duran), uc-pps-020 (Wheeler), uc-pps-023 / uc-pps-030 (Painter), uc-pps-029 (Bowlan, McFarlane ids)
supersedes: nothing
sub_use_cases: [Part A cohort ranking, Part B external gap]
closure: tripwires T-1..T-5 (07_platform_marketing.md §1)

# Metadata
ledger_uc: 47
created: 2026-09-22
last_updated: 2026-09-22
anchor: phils_2026.parquet max game_date 2026-09-20
build_artifact: dp_uc47_archetype_gap.py
kernel: dp_uc47_kernel.py (imports dp_uc44_kernel.py, sha256 a2c119096db2…)
report: dp_uc47_elite_ff_archetype_gap_report.md / .pdf (10 pp)
dashboard: dp_uc47_archetype_explorer.html (self-contained, no CDN)
verification: dp_uc47_verification.py — 241/241
dq: 16 PASS / 3 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-032-elite-rhp-ff-archetype-gap-001/

# DPO decisions recorded (from September 2026.ipynb cell 101)
decisions:
  9: keep in pps with a scope note
  10: bounded population, "this era" -> 2018-2026, drift-adjusted to 2026
  11: nphl is non-Phillies but not MLB-wide -> profiled; frame governed by FR-1
  12: aspirational, open to suggestions -> EFS (AF-5) + needle swap (AF-6)

# Glossary / KPIs introduced (all provisional)
kpis: [FR-1, NR-1, AF-1, AF-2, AF-3, AF-4, AF-5, AF-6, SG-6, SG-7, CB-1]
flags: [ff_elite_shape_flag, ff_elite_results_flag, ff_elite_archetype_flag]
retired_alias: ff_elite_stuff_flag -> ff_elite_shape_flag (collision with SG-4 "Stuff grade")
ratification_recommended: [SG-1, SG-2]   # second independent use

# Conditions (00 §8)
conditions:
  C1: bounded, non-MLB-wide frame — any external use of a grade carries that sentence
  C2: aspirational only — no board row is a trade recommendation
  C3: Bowlan-out scenarios are client carry-ins
  C4: McFarlane and all watch-list arms are THIN
  C5: new objects provisional
  C6: anchored to 2026-09-20; a refresh is v1.1.0
```

## Headline

The Phillies own the #2 elite RHP four-seam in the frame (Bowlan 2026, 2nd of 405) and only one: the 2026
elite-four-seam share is 11.1%, all his. No external arm with ≥100 four-seams of evidence grades higher; the
lever is a starter's elite four-seam (669 pitches of volume vs a reliever's 241).
