```yml
# Identity
name: Zack Wheeler 2026 Season Recap 20261012
id: uc-pps-035-Zack Wheeler 2026 Recap 20261012
description: >
  Season recap of Zack Wheeler's 2026 (28 starts + Wild Card G3 relief, RHP), driven by the client's October 2026
  notebook cells 16 (thesis), 21 (KPI list, code, claims) and 23 (jam-rate development). Tests "still Zack Wheeler"
  against the Phillies starter population, decomposes "slowing down in the second half" into a reconciled six-start
  slide and a strong finish, describes what the log shows about the reported mechanical cause, and registers a 2027 card.
  Delivered as a feature report (PDF), a narrative dashboard (offline + Artifact), a notecard and receipts 00-07.

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
parent_use_case: uc-pps-020 (first-half figures reproduced 6/6) ; uc-pps-034 (CF-2 → CF-2b, OC-1 second use) ; human parent October 2026.ipynb cells 16, 21-23
related: uc-pps-008 (ER-1 edge_rate), uc-pos-018 (XW-1 xwoba_pa), uc-pps-023 (RCI), uc-pps-032 (velocity trend), Baseball Functions jam_rate (2026-10-09)
supersedes: nothing (flags CF-2 MI-1/NM-1 and OU-1 upstream)
sub_use_cases: []
closure: tripwires T-1..T-5 (07_platform_marketing.md §1); card graded in v1.1.0

# Metadata
ledger_uc: 51
created: 2026-10-12
last_updated: 2026-10-12
anchor: phils_2026.parquet max regular-season game_date 2026-09-27 (Wild Card rows through 2026-10-01)
build_artifact: dp_uc51_wheeler_recap.py
kernel: dp_uc51_kernel.py (imports dp_uc49_kernel a4ad5191…, dp_uc50_kernel 8084cb17…; IX-1 extracts edge_rate, jam_rate, release_consistency)
report: dp_uc51_wheeler_2026_recap_report.md / .pdf
dashboard: dp_uc51_wheeler_2026_dashboard.html (self-contained, offline) ; Artifact "Still Zack Wheeler"
verification: dp_uc51_verification.py — 204/204
dq: 26 PASS / 4 WARN / 0 FAIL
governance_trail: Agents for Data Products/data-products/uc-pps-035-wheeler-2026-recap-001/

# Data References
kpis: [pitches, plate_apps, games, ba, obp, slg, ops, woba, krate, bbrate, hard_hit_rate, barrel_rate, line_drive_rate,
       tied_up_rate (JR-1, inherited), whiff_rate, chase_rate, in_zone_rate (tracked), edge_rate (ER-1, inherited),
       xwoba (XW-1, inherited), runs on watch, ST-1 swing timing (NEW), NC-1 clear miss (NEW), MX-1 release by start (NEW),
       SR-2 slide window (NEW), OU-2 outs (NEW), GS-1b (NEW), OC-1 card (second use), KP-1, CX-1b, AR-2, PM-1]
data_domains: At-Bat Outcomes, Batted Ball Profile, Bat Tracking, Pitch Profile, Pitch Outcomes, Strike Zone, Release, Game Log
defects_found: [MI-1 CF-2 admits AAA games, NM-1 CF-2 subject-name stamp, OU1-1 OU-1 misses base-running outs,
                SJ-1 sinker tied-up count included a bunt (build-caught), HP-13 role-mixed player_name population]
```

# Zack Wheeler 2026 Recap: "Still Zack Wheeler"

> **Document status:** Build complete. Deliverables: `dp_uc51_wheeler_2026_recap_report.pdf` (primary), `dp_uc51_wheeler_2026_dashboard.html`.
> Receipts: `out/dp_uc51_*`. Governance trail (00–07 + BID): control plane `data-products/uc-pps-035-wheeler-2026-recap-001/`.

## Business Context

### Problem Statement
One year is left on the deal of a 36-year-old ace who came back from a rib resection. The notebook says he slowed in the second half and lost his command in August, and also that he is still Zack Wheeler. Both claims needed numbers, a population and a window before anyone acts on 2027.

### Questions answered
1. Is he still Zack Wheeler, and against whom? (report §2: #6 of 41 starter seasons by xwOBA; 6 of the top 10 his)
2. Where did the walks come from? (§4: one reconciled six-start slide, 13.4% vs 5.9%)
3. What does the log show about the reported mechanical cause? (§4: misses arm side, release point unchanged)
4. What changed beyond walks? (§3: in-zone 42.1%, chase 36.2%; §7: the splitter)
5. What does "still Zack Wheeler" have to look like in 2027? (§8: the card)

### Out of scope
ERA and IP as computed numbers; any medical or mechanical inference; MLB-wide ranks; contract value (no salary/WAR source); a 2027 projection.

## Acceptance criteria (met)
- Entity locked by MLBAM id, MLB games only; regular season for rates; postseason ledger separate — **met** (DQ-02/06/27)
- Every superlative names its population and n — **met** (G6)
- Every published number reconciles to a receipt — **met** (harness F, 45/45)
- Carry-ins labelled and never computed on — **met** (harness G)
- PDF report, interactive dashboard, 00–07 receipts and a bid with token and time estimates — **met**
