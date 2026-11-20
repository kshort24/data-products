# 05 · Quality & Certification
Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc66_dq_scorecard.csv`): **12 PASS / 5 WARN / 0 FAIL**
| Rule | Check | Result | Evidence |
|---|---|---|---|
| DQ-01 | entity lock: id rows == name rows (O-26) | PASS | 944 == 944 (asserted in K64.subject_frame) |
| DQ-02 | dedup key unique in client frame | PASS | 0 dupes |
| DQ-03 | FR-1 client frame game types | WARN | {'R': 871, 'S': 73} - spring rows excluded from every grade |
| DQ-04 | anchor: max game_date <= 2026-10-01 | PASS | 2026-10-01 |
| DQ-05 | pitch_type non-null | WARN | 4 null |
| DQ-06 | pfx / plate location non-null | WARN | 16 |
| DQ-07 | zone non-null (chase / in-zone denominators, D-7) | WARN | 4 |
| DQ-08 | BIP launch_speed tracked (O-8) | PASS | 0 of 140 untracked |
| DQ-09 | wOBA weights joined for 2026 | PASS | Season 2026 row |
| DQ-10 | subject in CS-A (RP-1 reliever, >= 150 pitches) | PASS | starts 0 of 46 games |
| DQ-11 | CW-1 endpoints == house nresults / XW-1 (all + by stand) | PASS | asserted in cumulative_frame(reconcile=, tol=1e-9) |
| DQ-12 | CU-1 final shares == pitch_type value_counts | PASS | final appearance |
| DQ-13 | D-1/D-2 whiff inner join (zero-whiff cells drop to NaN) | PASS | 0 stand x pitch cells |
| DQ-14 | AAA tier kept separate (no blend) | PASS | 115 AAA rows in headlines only |
| DQ-15 | CS-C excludes subject from its own pool | PASS | is_subject filtered before percentile |
| DQ-16 | house PA rule (events not null, not pickoff_1b; IBB = PA not walk) | PASS | IBB in frame: 1 |
| DQ-17 | AB-1 automatic-ball rows (no pitch thrown; pitch_type and zone null) | WARN | 4 rows = a 4-pitch intentional walk on 2026-06-22; K44 chase_rate counts them in-zone (D-7, June zone +1.0 pt); excluded from CU-1 and pitch-type cells; K44 pitch_mix usage keeps them in its denominator |

WARNs are disclosures, not defects: the spring rows in the client frame (DQ-03, excluded from every grade) and one 4-pitch intentional walk whose automatic balls carry no pitch type, location or zone (DQ-05/06/07/17).

## 2 · Independent harness (`dp_uc66_verification.py` → `out/dp_uc66_verification.csv`): **34 / 34 PASS**
Recomputes from raw parquet with plain pandas (own swing/whiff lists, own wOBA from the constants CSV, own RP-1 for the CS-A count, own stint split); never imports the kernel's KPI functions.

| ID | Check | Recomputed | Published | Status |
|---|---|---|---|---|
| V01 | pitches (regular season, id-locked) | 871.0000 | 871.0000 | PASS |
| V02 | outings | 46.0000 | 46.0000 | PASS |
| V03 | PA | 223.0000 | 223.0000 | PASS |
| V04 | wOBA (FanGraphs weights / PA) | 0.3124 | 0.3120 | PASS |
| V05 | SLG | 0.4301 | 0.4300 | PASS |
| V06 | K% | 0.2646 | 0.2650 | PASS |
| V07 | BB% (IBB excluded from walks) | 0.0852 | 0.0850 | PASS |
| V08 | whiff% (whiffs / swings) | 0.2343 | 0.2343 | PASS |
| V09 | chase% (swings out of zone / pitches out of zone) | 0.2568 | 0.2570 | PASS |
| V10 | barrel% (launch_speed_angle == 6 / BIP) | 0.1000 | 0.1000 | PASS |
| V11 | hard-hit% (EV >= 95 / BIP) | 0.3357 | 0.3357 | PASS |
| V12L | wOBA vs LHB | 0.3094 | 0.3090 | PASS |
| V13L | K% vs LHB | 0.2857 | 0.2860 | PASS |
| V12R | wOBA vs RHB | 0.3152 | 0.3150 | PASS |
| V13R | K% vs RHB | 0.2458 | 0.2460 | PASS |
| V14 | SI share of strikeouts (HP-07) | 0.5085 | 0.5085 | PASS |
| V15 | FC to LHB on inner third (plate_x >= 0.277) (HP-05) | 0.4173 | 0.4173 | PASS |
| V16 | June wOBA (HP-08) | 0.4405 | 0.4410 | PASS |
| V17 | June zone rate (pitches minus OOZ / pitches, K44 D-7 rule) | 0.5208 | 0.5210 | PASS |
| V18 | Sep FC share (HP-09) | 0.3840 | 0.3840 | PASS |
| V19 | Sep ST share vs RHB (HP-09) | 0.2241 | 0.2241 | PASS |
| V20 | ST share vs LHB, April (report §6) | 0.2500 | 0.2500 | PASS |
| V21-1 | stint 1 first-pitch strike% | 0.5440 | 0.5440 | PASS |
| V21-2 | stint 2 first-pitch strike% | 0.6429 | 0.6429 | PASS |
| V22 | CW-1 final wOBA (All) == headline | 0.3124 | 0.3120 | PASS |
| V23 | CU-1 final ST share vs LHB == raw share | 0.1531 | 0.1531 | PASS |
| V24 | CS-A size excluding subject (independent RP-1) | 114.0000 | 114.0000 | PASS |
| V25 | report prints '.312 wOBA' | True | True | PASS |
| V26 | report prints '26.5%' | True | True | PASS |
| V27 | report prints '10.0%' | True | True | PASS |
| V28 | report prints '.441' | True | True | PASS |
| V29 | report prints '6 of 46' | True | True | PASS |
| V30 | 12 HP rows graded | 12.0000 | 12.0000 | PASS |
| V31 | visual audits: 11 figures, no V-standard FAIL | 11.0000 | 11.0000 | PASS |

Harness findings during build (both fixed before publish): V17 first failed because pandas nullable `zone` drops NA from `.mean()` while K44 `chase_rate` counts null-zone pitches in-zone (D-7) — the harness now applies the house rule and the report text was corrected (June ties September for his best zone rate); V23 first failed because CU-1 excludes automatic balls from its denominator — the harness now matches the CU-1 spec (`03` §2).

## 3 · HP grades (`out/dp_uc66_hp_grades.csv`) — bars from the BID, unchanged after compute
| HP | Legs | Verdict |
|---|---|---|
| HP-01 | gap +0.006; xgap +0.003 | **SUPPORTED** |
| HP-02 | wOBA 56th, xwOBA 65th | **SUPPORTED** |
| HP-03 | K% L>R Y, BB% L<R Y, whiff L>R Y, SLG L>R Y, BA R>L Y, OBP R>L Y | **SUPPORTED** |
| HP-04 | RHB Y, LHB Y | **SUPPORTED** |
| HP-05 | 58/139 = 41.7% | **PARTLY** |
| HP-06 | 100th of 32 | **SUPPORTED** |
| HP-07 | 30/59 = 50.8% | **SUPPORTED** |
| HP-08 | wOBA Y, command N | **PARTLY** |
| HP-09 | FC N, ST N, finish Y | **NOT** |
| HP-10 | REC PASS (0.430); pct 44 | **SUPPORTED** |
| HP-11 | REC PASS (10.0%); pct 18 | **SUPPORTED** |
| HP-12 | share 13.0% (N), below p75 56.5% (Y) | **PARTLY** |

## 4 · Visual audit (V1–V7, `recap_viz.audit`; VZ-5 contrast)
| Figure | V1 | V2 | V3 | V4 | V5 | V6 | V7 | min contrast |
|---|---|---|---|---|---|---|---|---|
| f1_context | PASS | PASS | PASS | N-A | PASS | PASS | PASS | 3.03 |
| f2_platoon | PASS | PASS | PASS | N-A | PASS | PASS | PASS | 3.03 |
| f3_pitch_plot | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f4a_pitch_map | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f4b_pitch_density | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f5_cumulative_usage | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f6_cumulative_woba | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f7_months | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| f8_pitch_scorecard | PASS | PASS | PASS | N-A | PASS | PASS | PASS | 3.03 |
| f9_role | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |
| s1_stints | PASS | PASS | N-A | N-A | PASS | PASS | PASS | 3.03 |

Two eyeball-QA rounds (dashboard-specifier): round 1 found clipped titles, legends colliding with axis titles, F1 outliers compressing every row, F4b's
claim "cutters climb in on lefties" not supported by its own density, F5 labels colliding with panel titles; round 2 found F6's band not rendering and
S1 duplicate tick labels. All fixed; titles rewritten to state what the figure shows.

## 5 · Certification verdict (`certification-agent`): **READY-CONDITIONAL**
| # | Condition | Owner |
|---|---|---|
| C1 | Small samples: 223 PA season, 12–47 PA per pitch × hand cell, 35 PA in September — caveats printed on page 1 and in §Caveats | reader |
| C2 | CS-A `phi_rhp_relief_seasons` and CS-C are DRAFT comparison sets until the DPO ratifies them | DPO |
| C3 | VZ-1…VZ-6 are provisional rules (machine-checked only for VZ-5; the rest by eyeball QA) | DPO |
| C4 | Thin CS-C pools for FC × RHB (9 seasons) and ST × LHB (3 seasons) — those percentiles are directional | reader |
Artifacts present and consistent: BID + acceptance, 00–07, README, contract, receipts (64), harness 34/34, DQ 0 FAIL, lineage asserted, privacy clear.
