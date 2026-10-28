# 05 · Quality & Certification
**data-quality-engineer · certification-agent**
`uc-pos-023-schwarber-2026-hr-animation-001` · UC #58 · `dp_uc58` v1.0.0

## 1 · DQ scorecard (`out/dp_uc58_dq_scorecard.csv`): 10 PASS · 3 WARN · 0 FAIL
| Rule | Status | Detail |
|---|---|---|
| DQ-01 uniqueness | PASS | 0 duplicate `PITCH_KEY` across house log + opponent file |
| DQ-02 consistency | PASS | CP-1 endpoints == independent HR count, 12 seasons (`reconcile=`) |
| DQ-03 consistency | PASS | career regular-season HR 385 == CI-4 |
| DQ-04 consistency | PASS | 2026 HR 45 == CI-1 |
| DQ-05 completeness | WARN | 2 of 45 2026 HRs lack hit coordinates (SP-2) |
| DQ-06 validity | PASS | hc radius / `hit_distance_sc` median 1.010 (p10 0.996, p90 1.016) |
| DQ-07 validity | PASS | DR-1 convention: LHB 2026 ground balls median loc_x +70.8 ft |
| DQ-08 completeness | PASS | 2026 HR plate_x/plate_z/EV/distance non-null |
| DQ-09 consistency | PASS | HR register PA positions == curve steps |
| DQ-10 validity | PASS | 15 clip rows carry all five resolver keys |
| DQ-11 consistency | WARN (by design) | 1 `truncated_pa` excluded in 2026 (702 event rows → 701 PA) |
| DQ-12 validity | WARN | 7 of 15 clip rows have no sourced pitcher name |
| DQ-13 consistency | PASS | `season_hr_no` == the `des` counter for all 45 (DH-1 guard) |

## 2 · Independent harness (`out/dp_uc58_verification.csv`): **28 / 28 PASS**
Re-derived from the raw parquet with plain pandas: lineage; season HR and PA (12 seasons); carry-in totals; 2026 HR PA positions under an independent DH order; the DH-1 Game-1 position; CP-1 pitch count; HR quality, HB-1 and barrel rate (2022–26); HP-01…05 grade logic; WP-1 max and the 6/28 trap; walk-off logic; spray count, approximations, SP-1 radius, and the pull count from the bearing bar; pitch-map counts by hand × group; zone means; PA/HR by hand; clip keys exist as HR pitches; postseason and spring exclusion; 18 receipt-bound strings in the prompt; the prompt's DATA block == `design_data.json`; the brief's numbers; DQ has 0 FAIL; 8 keyframes; design-data counts.

The first run was 24/28. All four were real:
- V01: the pin count expectation was wrong (unique files);
- V03: PA-X1, fixed in the kernel;
- V10: NA-1, fixed in the harness itself;
- V23: the prompt string followed V10.

## 3 · Client claims (`out/dp_uc58_hp_grades.csv`)
| HP | Grade | Governed value |
|---|---|---|
| HP-01 max EV lowest of tenure | SUPPORTED | 113.0 (2022–25: 113.8–116.7) |
| HP-02 avg EV lowest | SUPPORTED | 106.3 |
| HP-03 avg HR shortest | SUPPORTED | 402 ft |
| HP-04 longest shorter than all but one | SUPPORTED | 460 (2024: 447) |
| HP-05 91% barrels, 2nd-lowest | SUPPORTED | 91% (2023: 89%) |
| HP-06 lefty breaking-ball power compromised | **NOT SUPPORTED** (count leg) | 2 HR; 2023 had 1; 2025 had 7. EV leg too few to call |
| HP-07 not crushing RHP fastballs / FF | SUPPORTED | RHP FB HR mean EV 105.9, FF 105.4, both lowest |
| HP-08 max EV in the 9th, 4/30 DH | **PARTLY** | 1st inning of DH Game 1, off Logan Webb |
| HP-09 max distance, Coors, 5th, 4/3 | SUPPORTED | 460 ft |
| HP-10 max WPA = STL walk-off | SUPPORTED | +.446; 2nd = 6/28 at NYM +.371 |
| HP-11 three HR vs NYM 6/20 | SUPPORTED | 3rd, 3rd, 7th; 15-3 |
| HP-12 LHP breaking 4/26, 9/15 + WC | SUPPORTED | CU, SL; WC SL off Dylan Lee |
| HP-13 RHP four-seam top 3 | SUPPORTED | 5/15 PIT 109.5, 5/8 COL 109.2, 6/28 NYM 108.3 |
| HP-14 Labor Day, delivered a victory | SUPPORTED | 8th, 2 out, solo, the only run of a 1-0 win |
| HP-15 45 dots | SUPPORTED WITH CONDITION | 43 exact + 2 approximate |

## 4 · Certification: **READY-CONDITIONAL**
| # | Condition (carried into the prompt) |
|---|---|
| C1 | Two spray dots are approximate (SP-2), one is the 460-ft max-distance HR. Hollow + footnote |
| C2 | One CBP outline for every park (SP-3). Caption mandatory; no "would have been out" |
| C3 | DH-1 order resolved on 3 of 25 DH days; 22 fall back to game_pk (HR totals exact; a step can sit at most one game's PAs off). None affects a 2026 position |
| C4 | HB-1, WP-1, HL-1, SP-1/2/3, PM-1, GR-1 provisional (first use) |
| C5 | 7 clip pitchers unnamed; names appear only where sourced |
| C6 | `play_id`s resolve on the DPO's machine (StatsAPI outside the cloud allowlist) |
| C7 | Claude Design's video export path is unconfirmed; the frame-capture fallback is in the brief |

Privacy: public-figure performance data only; no PII; fine for external publish once the DPO approves (privacy-watchdog, `07`). Publish decision: human DPO.
