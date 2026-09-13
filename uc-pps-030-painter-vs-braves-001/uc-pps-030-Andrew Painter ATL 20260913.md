```yml
# Identity
name: Andrew Painter Game 3 Advance 20260913 ATL (Away)
id: uc-pps-030-Andrew Painter ATL 20260913
description: >
  Game 3 advance on Andrew Painter at Truist Park, 2026-09-13, opposite RHP Grant
  Holmes, with top-wild-card-seed stakes. Built around a client-sketched index card
  whose three claims were reconciled against the log before anything was built on
  them. Deep-dive angles: arsenal turnover across the option date (the splitter is
  gone, a changeup replaced it), the four-seam elevation trade, the flipped platoon,
  and a new 20-80 scouting-grade KPI family. Opponent bounded rather than descoped —
  Atlanta hitters reconstructed from Phillies pitching rows, Holmes available only
  against Philadelphia.

# Classification
value_stream: Phillies Pitching
value_stream_code: pps
status: Build Complete — READY-CONDITIONAL, 6 conditions — Ready for DPO Sign-off
priority: High
classification: Internal — Restricted (external publish blocked)

# People
personas: Manager, Pitching Coach, Pitching Analyst, Pitcher, Catcher
owner: Kellen Short

# Relationships
parent_use_case: UC#3 -> UC#8 -> UC#11 -> UC#29 (uc-pps-023, Painter return) -> UC#44 (this)
supersedes: nothing
sub_use_cases: []
closure: post-game backtest, 8 checks (07_platform_marketing.md §6)

# Metadata
ledger_uc: 44
created: 2026-09-13
last_updated: 2026-09-13
build_artifact: dp_uc44_painter_vs_braves.py
kernel: dp_uc44_kernel.py
report: dp_uc44_painter_vs_braves_report.md / .pdf (10 pp)
dashboard: dp_uc44_painter_scouting_card.html (self-contained, no CDN)
notecard: out/dp_uc44_fig1_notecard.png
verification: dp_uc44_verification.py — 247/247 passed, 7 families
governance_trail: >
  Agents for Data Products/data-products/uc-pps-030-painter-vs-braves-001/ (00-07 + BID + README)

# Data References
entity_lock: pitcher == 691725 (MLBAM)
opponent_starter_lock: pitcher == 656550 (Grant Holmes, externally confirmed)
grading_window: 2026-07-31 -> 2026-09-08 (8 starts, 720 pitches, 185 PA)
anchor_game_date: 2026-09-12
kpis:
  - nresults / get_stats        # LOCKED — verbatim from Baseball Functions.ipynb
  - whiff_rate                  # LOCKED
  - chase_rate                  # LOCKED
  - putaway_rate                # LOCKED
  - first_pitch_strike_rate     # LOCKED
  - hard_hit_rate               # LOCKED
  - two_prop_z                  # LOCKED (dp_uc42)
  - scouting_grade_20_80        # NEW — SG-1, provisional
  - benchmark_population        # NEW — SG-2, provisional
  - grade_divergence_flag       # NEW — SG-3, provisional
  - pitch_grade                 # NEW — SG-4, provisional
  - grade_label                 # NEW — SG-5, provisional
  - arsenal_turnover_index      # NEW — AR-1, provisional (requires tag-drift control)
  - pitch_map_centroid          # NEW — PM-1, provisional
data_domains:
  - Pitch Profile
  - Pitch Outcomes
  - Strike Zone
  - At-Bat Outcomes
  - Batted Ball Profile (tracked-BIP only)
  - Opponent Lineup (reconstructed)
descoped:
  - Release Mechanics / arm slot — arm_angle 54% null (DQ-6 FAIL)
  - Holmes season profile — repo holds him only vs Philadelphia
```

# Andrew Painter — Game 3 Advance vs ATL, 2026-09-13

> **Document status:** the full contract, business context and answered business questions live in the
> governance trail at
> `Agents for Data Products/data-products/uc-pps-030-painter-vs-braves-001/`.
> This file is the repo-side registry entry so the `uc-pps-NNN` naming convention stays intact.

## Sources

| Tier | File | Filter | Rows | Window | Starts |
|---|---|---|---|---|---|
| MLB (subject) | `data/phillies/phils_2026.parquet` | `phillies_role=='pitching' & pitcher==691725 & game_type=='R'` | 1,861 | 2026-03-31 → 09-08 | 22 |
| — graded window | " | `& game_date >= '2026-07-31'` | 720 | 07-31 → 09-08 | 8 |
| MLB (benchmark) | `phils_2015..2026.parquet` | `game_type=='R' & p_throws=='R'`, both roles | 393,126 | 2015 → 2026 | — |
| AAA (supporting) | `data/opponents/lhvp26.parquet` | `pitcher==691725` | 396 | 2026-06-28 → 07-26 | 5 |
| Opponent hitters | `phils_2026.parquet` | pitching rows, 12 PHI–ATL `game_pk` | 1,660 | 04-17 → 09-12 | — |
| Opponent starter | `phils_2026.parquet` | batting rows, `pitcher==656550` | 260 | 04-19, 04-24, 09-07 | 3 |

52 spring-training pitches excluded. Cache current through 2026-09-12 (T-1). Target game D+1.

## The client's card, checked

| Claim | Claimed | Computed | Denominator | Verdict |
|---|---|---|---|---|
| High-Ride FF — 21% whiff | .210 | **.218** | 24/110 swings | Reconciles (2H cut) |
| High-Ride FF — 16.8" vert | 16.8" | **16.97"** | 218 pitches | Reconciles |
| Plus FS — 39.5% whiff to LHB | .395 | **.395** | 30/76 swings | Reconciles — **but stale**: 0 splitters since 2026-06-17 |
| Lands breaking balls — above-avg IZR | — | **.477** | 767 pitches | Confirmed: **grade 55**, 68th pctile |

## Findings in one table

| # | Finding | Key numbers |
|---|---|---|
| 1 | The card is right three times, and one of the three is about a pitcher who no longer exists | FS .395 to LHH on 76 swings, **all pre-option**; zero splitters in 8 starts back |
| 2 | A changeup replaced the splitter, and it is now his best pitch | 22.2% usage · 90.5 mph (+3.1) · 5.0" IVB (−3.1) · −12.8" HB (−3.0) · **xwOBA .160**, results grade **75**. Lefty whiff gap .395 → .301, z = 1.20, **p = 0.23**. League FS share 4.14% → 5.39% ⇒ **pitcher decision, not classifier drift** |
| 3 | The four-seam went up: a trade, not a decline | elevation .307 → **.349** vs pop mean .200 (grade **70**) · whiff .106 → **.218** (stuff 35 → 50) · in-zone .474 → **.422** (command **25**) · 90 pitches / 23 BF per start, while FPSR *rose* .612 → .638 |
| 4 | The platoon flipped, and Atlanta is built for the new weak side | whiff **.322 RHH / .238 LHH** (z = −1.78, **p = 0.075**) · K% **29.7 / 18.1** · **six of nine** most-used Atlanta bats hit left-handed |
| 5 | The leak is the sweeper to lefties; the head-to-head is unusable | ST vs LHH: 17.2% usage, **64.5% in zone**, .200 whiff, **.523 xwOBA on 9 tracked PA**. H2H = 47 PA, all April, **arsenal turnover 0.33** |
| 6 | Houston was a contact-quality start, not a command start | 27 BF, 6 K, 2 BB, CSW .276 (5th of 8) but **.438 xwOBA / .550 xwOBAcon**, 2 HR, 8 of 19 hard-hit. 4 of 5 post-option HR came in the 2 starts over .400 |
| 7 | Arsenal grade **50**, up from **45** on the arm that got optioned | covering 98% of post-option usage |

## The single attack rule

> **Changeup, not sweeper, to the left-handed hitters.** CH to LHH allows **.178** xwOBA on 31% usage; ST to
> LHH sits in the zone 64.5% of the time for a 20.0% whiff and **.523** xwOBA (9 tracked PA — a usage
> instruction, not a claim about the pitch).

## Certification

19 DQ checks: **17 PASS · 1 WARN · 1 FAIL** (`arm_angle` 54% null → arm-slot analysis **descoped with cause**;
the `uc-pps-023` arm-spread finding is **not** refreshed and must not be quoted as current).
Independent verification: **247/247** (`out/dp_uc44_verification_log.txt`), 7 families including 40
narrative-to-receipt reconciliations — which caught three real errors in the draft report.
Publish surface: **internal only**, need-to-know.

Six conditions on certification: C1 valid for this start only · C2 grades are Phillies-schedule, not league ·
C3 sweeper grades THIN · C4 platoon split is directional · C5 arm slot descoped · C6 all seven new objects
provisional. Full text: `05_quality_certification.md` §5.

## Closure

Post-game backtest — 8 checks at `07_platform_marketing.md` §6. B-8 is the one that matters: rerun SG-1
including this start and see whether a grade moves. A grading scheme that swings on 90 pitches is not
measuring what it claims to.
