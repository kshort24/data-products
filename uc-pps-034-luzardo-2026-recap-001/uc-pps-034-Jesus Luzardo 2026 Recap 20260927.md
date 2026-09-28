```yml
# Identity
name: Jesus Luzardo 2026 Season Recap 20260927
id: uc-pps-034-Jesus Luzardo 2026 Recap 20260927
description: >
  Narrative season recap of Jesús Luzardo's 2026 (29 starts, LHP), driven by the client's September 2026
  notebook cells 51 (narrative) and 118 (analysis). Explores eight data-product forms for one story and builds
  seven: a chaptered narrative dashboard, a pitch-by-pitch game story of the Labor Day shutout, a pre-registered
  October card, a feature report, a governed context board (the client's three scatters), a notecard and a
  career postseason ledger. Grades the client's 13 claims and chart choices.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL, 6 conditions — Ready for DPO Sign-off
priority: Medium
classification: Internal (external publish permissible after DPO review)

# People
personas: Pitching department, Front office, Broadcast/content, Pitcher
owner: Kellen Short

# Relationships
parent_use_case: uc-pps-033 (SR-1 season_recap, second use) ; uc-pps-017 (first-half figures reproduced) ; human parent September 2026.ipynb cells 51, 118
related: uc-pps-028 (consistency audit), uc-pps-008 (edge rate, HP-13), uc-pos-012 (runs_created)
supersedes: nothing (closes uc-pps-033 V-3 by back-check)
sub_use_cases: []
closure: tripwires T-1..T-5 (07_platform_marketing.md §1); OC-1 graded in v1.1.0

# Metadata
ledger_uc: 49
created: 2026-09-27
last_updated: 2026-09-27
anchor: phils_2026.parquet max regular-season game_date 2026-09-26
build_artifact: dp_uc49_luzardo_recap.py
kernel: dp_uc49_kernel.py (imports dp_uc48_kernel.py sha256 0f63857a1032…, which imports dp_uc44_kernel.py a2c119096db2…)
report: dp_uc49_luzardo_2026_recap_report.md / .pdf
dashboard: dp_uc49_luzardo_2026_dashboard.html (self-contained, offline) ; Artifact "Luzardo's 2026 Chase"
verification: dp_uc49_verification.py — 226/226
dq: 21 PASS / 2 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-034-luzardo-2026-recap-001/

# Data References
kpis: [pitches, plate_apps, ba, obp, slg, ops, woba, krate, bbrate, hr_rate, whiff_rate, chase_rate,
       in_zone_rate (tracked denominator), First Pitch Strike Rate, runs_created ("runs on watch"),
       CX-1/CX-1b context ranks (NEW), GS-1 game score (NEW), OU-1 outs (NEW), VB-1 first-15 velocity (NEW),
       OC-1 October card (NEW), KP-1 house percentile (inherited), AR-2 arsenal (inherited), PM-1 pitch map (inherited)]
data_domains: At-Bat Outcomes, Pitch Profile, Pitch Outcomes, Strike Zone, Usage, Game Log
defects_found: [O-26 nphl keep-first dedup, BS-1 byte-search profiling, ENV-1 US-1 duplicate groupby key,
                E-7 PM-1 plate_x docstring sign, HP-10 per-color OLS trendline]
```

# Jesús Luzardo 2026 Recap: "The Chase"

> **Document status:** Build complete. Deliverables: `dp_uc49_luzardo_2026_dashboard.html` (primary), `dp_uc49_luzardo_2026_recap_report.pdf`.
> Receipts: `out/dp_uc49_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pps-034-luzardo-2026-recap-001/`.

## Business Context

### Problem Statement
The client's notebook holds a thesis (*he does not need to be in the strike zone*), three context scatters and a narrative (*2026 could be the season to celebrate, forever*). The ask: let that narrative drive the use case, explore the kinds of data products that could tell it, and ground every beat in governed data.

### Questions answered
1. How far did he step away from the zone, and did walks follow? (report §3)
2. Is he "better than most pitchers in my dataset"? By how much, in which population? (§2)
3. Was Labor Day the best start of his career, and by what measure? (§5)
4. What does the log show before the IL, and what does it not show? (§6)
5. What would a defining October look like in his own data? (§8, pre-registered)

### Out of scope
ERA and innings as computed numbers; any medical inference; MLB-wide ranks; "acquired by Dombrowski" (no transaction source); a 2027 projection.

## Acceptance criteria (met)
- Entity locked by MLBAM id; regular season for rates; postseason ledger separate — **met** (DQ-02/03/23)
- Every superlative names its population and n — **met** (G6)
- Every published number reconciles to a receipt — **met** (harness F, 96/96)
- Carry-ins labelled and never computed on — **met** (harness G)
- 00–07 receipts and a bid with token and time estimates — **met**
