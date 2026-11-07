# 05 · Quality & Certification
Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc63_dq_scorecard.csv`): **10 PASS / 6 WARN / 0 FAIL**
| Rule | Check | Result | Evidence |
|---|---|---|---|
| DQ-01 | entity lock: id rows == name rows (O-26) | PASS | 333 == 333 |
| DQ-02 | dedup key unique in client frame | PASS | 0 dupes |
| DQ-03 | game types in client frame | PASS | F,R |
| DQ-04 | anchor: max game_date <= 2026-10-01 | PASS | 2026-10-01 |
| DQ-05 | pitch_type non-null (automatic balls/strikes excepted, AB-1) | WARN | 1 null, all automatic balls/strikes; kept (client frame counts them) |
| DQ-06 | release_speed / spin non-null | WARN | 2 |
| DQ-07 | pfx_x / pfx_z non-null | WARN | 2 |
| DQ-08 | zone non-null (chase / in-zone denominators, D-7) | WARN | 1 |
| DQ-09 | BIP launch_speed tracked (O-8) | PASS | 0 of 56 untracked |
| DQ-10 | arm_angle coverage (display only) | WARN | 157 of 333 |
| DQ-11 | wOBA weights joined for 2026 | PASS | Season 2026 row present |
| DQ-12 | AAA tier kept separate (no blend) | PASS | 73 AAA rows in separate receipts |
| DQ-13 | Kerkering id == name 1:1 | PASS | 3544 rows |
| DQ-14 | FO-1 pool deduped across pps/pos | PASS | 239 seasons |
| DQ-16 | EN-3: FO-1 names from pitching-role rows only (pos player_name is the batter) | PASS | 81 opponent seasons labelled by id |
| DQ-15 | AB-1 automatic ball/strike rows (no pitch thrown) | WARN | 1 row(s): counted in pitches (333) and as in-zone by K44 chase_rate (D-7); pitch_mix usage denominators include it (vs LHB shares sum to 99.4%) |

WARNs are disclosures, not defects: the AB-1 automatic ball (DQ-05/06/07/08/15, one row) and arm-angle coverage (DQ-10, display only).

## 2 · Independent harness (`dp_uc63_verification.py` → `out/dp_uc63_verification.csv`): **45 / 45 PASS**
Recomputes from raw parquet with plain pandas (own swing/whiff lists, own wOBA from the weights CSV, own FO-1 pool, own BD-1 logic); never imports the kernel.

| ID | Check | Recomputed | Published | Status |
|---|---|---|---|---|
| V01 | pitches (id frame, all game types) | 333 | 333 | PASS |
| V02 | outings | 21 | 21 | PASS |
| V03 | postseason games | 2 | 2 | PASS |
| V04 | name frame == id frame | 333 | 333 | PASS |
| V05 | overall woba | 0.2798 | 0.28 | PASS |
| V06 | overall ops | 0.633 | 0.633 | PASS |
| V07 | overall krate | 0.2588 | 0.259 | PASS |
| V08 | overall bbrate | 0.0824 | 0.082 | PASS |
| V09 | overall whiff_rate | 0.2911 | 0.2911392405063291 | PASS |
| V10 | overall chase_rate | 0.3353 | 0.335 | PASS |
| V11 | overall hard_hit_rate | 0.4107 | 0.4107142857142857 | PASS |
| V12 | overall barrel_rate | 0.0893 | 0.089 | PASS |
| V13 | overall ba | 0.2208 | 0.221 | PASS |
| V14 | K:BB counts | 22:7 | 22:7 | PASS |
| V15 | vs LHB K/BB/BA/HH/barrel | [np.float64(0.333), np.float64(0.026), np.float64(0.263), np.float64(0.4), np.float64(0.08)] | [0.333, 0.026, 0.263, 0.4, 0.08] | PASS |
| V16 | vs RHB K/BB/BA/HH/barrel | [np.float64(0.196), np.float64(0.13), np.float64(0.179), np.float64(0.419), np.float64(0.097)] | [0.196, 0.13, 0.179, 0.419, 0.097] | PASS |
| V17 | vs LHB usage (count / all pitches incl. AB-1 row) | {'FF': np.float64(63.4), 'SL': np.float64(27.5)} | {'FF': 63.4, 'SL': 27.5} | PASS |
| V18 | vs RHB usage (count / all pitches incl. AB-1 row) | {'SI': np.float64(45.6), 'FF': np.float64(25.0), 'SL': np.float64(15.6), 'ST': np.float64(13.9)} | {'SI': 45.6, 'FF': 25.0, 'SL': 15.6, 'ST': 13.9} | PASS |
| V19 | SL v LHB whiff | 0.381 | 0.381 | PASS |
| V20 | FF v RHB whiff | 0.32 | 0.32 | PASS |
| V21 | FF v LHB whiff | 0.333 | 0.333 | PASS |
| V22 | SL v LHB chase | 0.5 | 0.5 | PASS |
| V23 | FF IVB 10th/90th pct (in) | [np.float64(12.85), np.float64(16.55)] | [12.85, 16.55] | PASS |
| V24 | FF run median |HB| (in) | 9.48 | 9.48 | PASS |
| V25 | SI run 90th pct |HB| (in) | 18.61 | 18.61 | PASS |
| V26 | SL mean HB / IVB (BS-1r inputs) | [np.float64(4.7), np.float64(-2.02)] | [4.7, -2.02] | PASS |
| V27 | FO-1 pool size (others) | 238 | 238 | PASS |
| V28 | FO-1 velo / spin rank | [3, 6] | [3, 6] | PASS |
| V29 | FO-1 seasons at/above on both | 0 | 0 | PASS |
| V30 | FF mean velo / spin | [np.float64(99.42), np.float64(2543.9)] | [99.42, 2543.9] | PASS |
| V31 | BD-1 bridge outings | 4 | 4 | PASS |
| V32 | BD-1 first bridge date | 2026-08-31 | 2026-08-31 | PASS |
| V33 | AAA pitches / outings / K | [73, 4, 8] | [73, 4, 8] | PASS |
| V34 | Kerkering first 21: postseason outings / PA | [7, 85] | [7, 85] | PASS |
| V35 | Kerkering first 21: K% / HH% | [np.float64(0.235), np.float64(0.255)] | [0.235, 0.255] | PASS |
| V36 | whiff percentile vs CX-1 pool (±1, RK-3) | 73 | 73 | PASS |
| V37 | chase percentile vs CX-1 pool (±1, RK-3) | 75 | 74 | PASS |
| V38 | HP-09 verdict follows the filed bar | CONFIRMED | CONFIRMED | PASS |
| V39 | HP-10 verdict follows the filed bar | PARTLY | PARTLY | PASS |
| V40 | report body carries no uncorrected 'Central Florida' | False | False | PASS |
| V41 | report body carries the client's verbatim anchor sentence | True | True | PASS |
| V42 | dashboard loads plotly from the pinned CDN, not inline | True | True | PASS |
| V43 | V1-V7 audit (figures passing incl. 1 registered exception) | 8 | 8 | PASS |
| V44 | NC-1: every on-screen string is registered | True | True | PASS |
| V45 | design-kit manifest sha256 matches files | True | True | PASS |

## 3 · Visual standard (`out/dp_uc63_visual_audit.csv`)
8/8 figures pass `recap_viz.audit` V1–V7; F3 (pitch map, the client's chart form) carries a registered V2 exception (the strike zone is the reference).
Eyeball QA, two rounds: F3 SI/SL labels collided (moved by pitch); F5 marginal histograms had stray "share" titles and hairline bins (axes hidden, bins 25 rpm / 0.25 mph, axes clipped and stated); F5 annotation moved off the histogram; F6 shared-axis title missing (V6).

## 4 · Catches (with "intake could have caught")
| Catch | Where | Intake could have caught? |
|---|---|---|
| "Central Florida" → South Florida | carry-in check (web) | yes, and did (flagged in the BID) |
| Subtitle digits truncated (2.6 → "2", 41.9 → "41", 9.7 → "9") | HP-06/07 at printed precision | yes (flagged in the BID) |
| FF "run about a foot" is ≈ 9.5 in at the median | HP-05b | no (needed the shape receipt) |
| Opponent pitcher named "Harper, Bryce" in FO-1 | figure QA (EN-3) | no |
| Bullet slider misses the house line by 0.7 in | BS-1r | no |
| Chase percentile 74 vs 75 (RK-3) | harness V37 | no |

## 5 · Certification (`certification-agent`): **READY-CONDITIONAL**
| Artifact | Present | Consistent |
|---|---|---|
| BID + acceptance, `00`–`07`, README, contract, ledger patch | yes | yes |
| Lineage pins asserted | yes (11) | yes |
| DQ scorecard, 0 FAIL | yes | yes |
| Harness all PASS | yes (45/45) | yes |
| Report `.md` / `.pdf`, dashboard, slide kit read the same receipts | yes | yes (one narrative module) |
Conditions: **C1** DPO ratifies FO-1 / BD-1 / ST-1 / FN-1 / BS-1r / CL-1 · **C2** DPO accepts the five corrections to the narrative · **C3** small-sample label stays on every rate (85 PA) · **C4** AAA stays a separate tier in the Claude Design build · **C5** ledger patches UC52–UC63 pasted.
