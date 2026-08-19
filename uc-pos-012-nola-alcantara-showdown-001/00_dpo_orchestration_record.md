# 00 · DPO Orchestration Record
**UC #36 · `uc-pos-012-nola-alcantara-showdown-001` · `dp_uc35` · delivered 2026-08-19**
<br>Value stream: Phillies Offense (`pos`) · DPO: Kellen Short · Data window: 2015 → **2026-08-17** · Game context: Nola vs Alcantara, CBP, 2026-08-19 18:05 ET

---
## Delivery plan — layer status

| Layer | Status | Evidence |
|---|---|---|
| 1 — Intake & Discovery | ✅ complete | `01_strategy_intake.md` — validator pass 1 GO with 5 conditions; PA-floor question escalated to the human DPO and ruled at intake |
| 2 — Design | ✅ complete | `02_engineering_design.md`, `03_governance.md` |
| 3 — Build | ✅ complete | `04_engineering_build.md`; `dp_uc35_kernel.py`, `dp_uc35_nola_alcantara.py`, figure/pdf/dashboard builders |
| 4 — Certify & Publish | ✅ complete | `05_quality_certification.md` — **79/79 PASS** independent verification |

## Human-DPO decision log (this UC)

| # | Decision point | Ruling | Where applied |
|---|---|---|---|
| HD-1 | Comparison PA floor: submitted code said `> 15`, house standard is 50 | **"It is about Aaron Nola, use his minimum plate_apps in the dataset"** (intake, 2026-08-18) | Derived, not hand-keyed: **27 PA** season grain, **11 (L) / 12 (R)** stand grain — `out/dp_uc35_floor_derivation*.csv` |
| HD-2 | Box-plot design: per-season Nola points → career **constants** for Nola and Wheeler; highlight real Harper vs MIA | As submitted | Fig 1 + `SB-1 synthetic_batter` + `boxplot_population.csv` |
| HD-3 | Deliverable tier | Full governed package + PDF report + interactive dashboard | This folder |

## Capability fulfilment

| Capability | Satisfied by | Status |
|---|---|---|
| RC-1 premises tested before they are explained | Report §2 — five verdicts (P1–P5) ahead of any narrative | ✅ |
| RC-2 the submitted KPI family at one grain | `KF-1 kpi_family()` — slash, wOBA, K, whiff, chase, hard-hit, barrel, RC, RC/PA in one frame | ✅ |
| RC-3 denominator beside every rate | `plate_apps`, `pitches`, `swings`, `ooz`, `bips` shipped on every receipt row | ✅ |
| RC-4 the box-plot redesign (constants + Harper highlight) | Fig 1; constants annotated with their PA | ✅ |
| RC-5 stand-faceted season scatter with Nola highlighted | Fig 2 + dashboard tab 2; per-stand floors derived per HD-1 | ✅ |
| RC-6 the Alcantara flip side generated as BI, not prose | Exposure ranking, Harper book, 7/28 duel receipt — each premise priced (P2–P4) | ✅ |
| RC-7 every number traceable to a governed KPI | `04_engineering_build.md` lineage; 79/79 verification | ✅ |

## Governance gate checks

| Gate | Result |
|---|---|
| Validator go/no-go cleared before build | ✅ **GO.** Layer-1 repo search run first — `nresults`, `whiff_rate`, `chase_rate`, `hard_hit_rate`, `barrel_rate`, `runs_created` all exist and are governed; consumed, not rebuilt |
| Independent verification | ✅ **79 PASS / 0 FAIL**, no kernel import for the arithmetic checks |
| New KPIs registered as provisional | ✅ KF-1 (composition), SB-1 (synthetic batter) — see `03_governance.md` |
| Approved terms consumed, not forked | ✅ `runs_created` transcribed **verbatim** with its notebook glossary + lineage; SWINGS/WHIFFS/NON_PA inherited |
| D1–D5 defect register carried, no silent patches | ✅ `_fix` variants beside originals; **no new defects opened this build** |
| Entity locks on MLBAM id, never name | ✅ 605400 / 645261 / 554430 / 547180, each asserted against its authority |
| Floor deviation from house standard governed | ✅ HD-1 logged here, derivation receipted, `below_house_floor` flag on every hitter-season row |
| Vendor-don't-CDN (dashboard) | ✅ Chart.js 4.4.1 inlined; `chart()` helper degrades to placeholder (uc-pos-011 rule) |

## Premise verdicts (the BI the prose asked for)

| # | Premise | Verdict |
|---|---|---|
| P1 | Constants + Harper highlight redesign | Implemented — Noles 0.090 RC/PA (696 PA), Wheeler 0.084 (593 PA) |
| P2 | Alcantara #1 in pitches to PHI, Statcast era | **Falsified as posed** — #2 (2,278) behind Scherzer (3,137) |
| P3 | Harper faced Alcantara 3rd-most since 2015 | **Not reproducible in-plane** (pos = PHI batting only); **#1 in-frame** at 54 PA |
| P4 | Scherzer-teammate / deGrom-injury context | Consistent, partly out of plane; disclosed |
| P5 | Nola faced MIA every year | Falsified — 11 of 12 seasons, no 2025 meeting |

## Open items carried

| ID | Issue | Requires | Status |
|---|---|---|---|
| O-2 | D1–D3 zero-numerator drops in governed originals | DPO | open — repo-wide, inherited |
| O-3 | `nresults` 3dp rounding (D4) | DPO | open — inherited; unrounded kernel used |
| O-7 | `pull_air_rate` cannot execute (`loc_x/loc_y` absent) | DPO | open — inherited, not triggered here |
| O-8 | `hard_hit_rate` denominator counts untracked BIP | DPO | open — inherited; disclosed on every hard-hit figure |
| **O-10** | **NEW.** Pitcher display names have no local authority on the `pos` frame (`player_name` = the Phillie). Top-10 exposure ids ship as `MLBAM <id>`; Scherzer/deGrom names are logged manual carry-ins | DPO | **open — new this build.** Fast-follow offered: an id→name lookup table as a governed reference asset |
| O-11 | KF-1 / SB-1 provisional pending ratification | DPO | open |

## Publish recommendation

**APPROVE for internal Phillies staff distribution ahead of the 2026-08-19 game.** Every headline
independently verified on a separate code path; all five intake premises adjudicated in §2 of the
report rather than silently corrected.

Interpretive risks stated up front: (1) the ruling floor (27/11/12 PA) is far below the house 50 —
sub-50 cells are flagged and barred from rankings; (2) the "Noles" composite pools eleven Marlins
rosters and answers *what Nola allows*, not *how any Marlin hits*; (3) career-grain wOBA uses 2026
constants (kernel behavior, disclosed since dp_uc34).

**Not approved for external/media distribution** without stripping the manual name carry-ins (O-10)
and the sub-floor season cells (Harper-vs-Alcantara seasons are all <15 PA).
