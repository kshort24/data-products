# Use Case uc-pps-040 — Aaron Nola 2026 Recap + Pitch Sequencing ("Better Process Than Results, and a Book Built on the Curve")

```yml
# Identity
name: Aaron Nola 2026 Recap 20261116
id: uc-pps-040-Aaron Nola 2026 Recap 20261116
description: >
  Governed 2026 season recap of RHP Aaron Nola read as a holistic arc (context vs 40 Phillies SP seasons, start-by-start, prior Nola products'
  tripwires re-read at season's end), plus the plane's first pitch-sequencing engine: the client's pitch_sequence() verbatim, 2-4 pitch windows
  inside PAs, count-adjusted setup lift, terminal endings scored on outs / K / poor contact / xwOBA, era drift on pre-registered bars,
  batterymate book divergence, and a predictability stretch. Ships PDF, interactive dashboard with a Sequence Explorer, and the 00-07 trail.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL (C1-C4), awaiting DPO sign-off
priority: Medium

# People
personas: Pitching Coach, Pitching Analyst, Catchers, Front Office
owner: Kellen Short

# Relationships
parent_use_case: client prompt + pitch_sequence() (intake/client_prompt_2026-11-16.md); recap shape UC48-UC63; Nola file uc-pps-008 / 014 / 021, uc-pos-012, uc-pps-027, uc-cat-002
sub_use_cases: []

# Metadata
uc_number: 64
build: dp_uc64 v1.0.0
kernel: dp_uc64_kernel.py (imports dp_uc63_kernel c4c0eea4..., 12 pins)
entity_lock: pitcher == 605400 (guard against 'Hoffman, Nolan' 676510)
window: regular season 2015-2026 (career sequencing pool, DPO ruling Q-C); 2026 highlight; WC Game 3 reported separately; anchor 2026-10-01
dpo_rulings: Q-A setup lift + endings · Q-B weak contact = Savant LSA 1-3 (PC-1) · Q-C career-wide, all lengths
kpis_inherited: nresults, whiff_rate, chase_rate, putaway_rate, fpsr, hard_hit_rate, csw, rv100, xwobacon, arsenal_table, house_percentile (KP-1), game_score (GS-1), outs_recorded (OU-1), xwoba_pa (XW-1), barrel_rate (BR-1), BAT-4
kpis_new: SQ-0 (client, verbatim), PT-H, SQ-1..SQ-6, SQ-5d, OUT-1, PC-1, PI-1 (provisional)
deliverables:
  - dp_uc64_nola_2026_recap_report.pdf (12 pp)
  - dp_uc64_nola_2026_dashboard.html (+ Artifact "Aaron Nola 2026")
  - out/dp_uc64_* (63 receipts)
verification: harness 43/43 · DQ 21 PASS / 3 WARN / 0 FAIL · V1-V7 10/10 (1 registered exception)
trail: Agents for Data Products/data-products/uc-pps-040-nola-2026-recap-sequencing-001/
```

## Acceptance criteria → status
| # | Criterion (BID) | Status |
|---|---|---|
| 1 | every number traces to an `out/dp_uc64_*` receipt computed this session | MET (report/dashboard generated from receipts; harness V45–V49) |
| 2 | entity lock + REC-1 reconcile | MET with dispositions (BB + IBB exact; outs −2 after reconstruction) |
| 3 | SQ bars unchanged after first compute | MET (additions classified non-breaking, `03` §2) |
| 4 | harness all PASS | MET 43/43 |
| 5 | V1–V7 on every figure | MET 10/10 (F5 registered V2 exception) |
| 6 | certification verdict in `05` | MET — READY-CONDITIONAL |
| 7 | bid vs actual in `07` | MET (≈300k / ≈62 min vs ≈545k / ≈68 min) |
