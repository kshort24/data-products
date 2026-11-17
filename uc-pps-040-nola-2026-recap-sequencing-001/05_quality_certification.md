# 05 · Quality & Certification
Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc64_dq_scorecard.csv`): **21 PASS / 3 WARN / 0 FAIL** (5 INFO)
| # | Check | Result | Evidence |
|---|---|---|---|
| DQ-01 | anchor | PASS | 2026-10-01 |
| DQ-02 | entity_lock_O26 | PASS | id rows == name rows == 31077 |
| DQ-03 | dedup | PASS | 0 duplicate (game_pk, at_bat, pitch) |
| DQ-04 | hoffman_guard | PASS | {'Hoffman, Nolan': [676510], 'Nola, Aaron': [605400]} |
| DQ-05 | cde_delta_run_exp | PASS | 22.0 null of 30079 |
| DQ-06 | cde_lsa_on_bip | PASS | 43.0 untracked of 5164 BIP |
| DQ-07 | cde_fielder_2 | PASS | 0 null |
| DQ-08 | REC-1 strikeouts | PASS | log 177 vs public 177 (exact) |
| DQ-09 | REC-1 walks (house nresults: events == 'walk') | WARN | log 57 vs public 59 (house rule excludes 2 IBB (registered, not a defect)) |
| DQ-10 | REC-1 walks + intent_walk | PASS | log 59 vs public 59 (exact) |
| DQ-11 | REC-1 outs (OU-1 events) vs IP x 3 | WARN | log 517 vs public 526 (OU-1 blind spot: outs on no-event rows) |
| DQ-12 | REC-1 outs (inning-state reconstruction) vs IP x 3 | WARN | log 524 vs public 526 (residual 2 outs (0.4%) after reconstruction) |
| DQ-13 | REC-1 games started | PASS | log 33 vs public 33 (exact) |
| DQ-14 | REC-1 games | PASS | log 33 vs public 33 (exact) |
| DQ-15 | PT-H SL tag | INFO | 19 SL rows kept as tagged: [{'game_year': 2026, 'n': 19, 'velo': 83.1, 'ivb_in': -0.8, 'hb_in': 3.6, 'spin': 2322.7}] |
| DQ-16 | seasons_rows | PASS | 12 |
| DQ-17 | ASB SD-2 | PASS | no games inside the break window |
| DQ-18 | catcher name 592663 | PASS | Realmuto, J.T. |
| DQ-19 | catcher name 596117 | PASS | Stubbs, Garrett |
| DQ-20 | catcher name 665561 | PASS | Marchán, Rafael |
| DQ-21 | SQ-0 vs SQ-1 token order | PASS | 1.0000 of PAs identical |
| DQ-22 | PA ends | INFO | 7767 batter PAs; non-PA terminal rows (pickoff/CS) excluded: 20 |
| DQ-23 | SQ-1 k=2 XX windows dropped | INFO | 25 |
| DQ-24 | SQ-2 k=2 baseline join | PASS | 0 unmatched |
| DQ-25 | SQ-1 k=3 XX windows dropped | INFO | 21 |
| DQ-26 | SQ-2 k=3 baseline join | PASS | 0 unmatched |
| DQ-27 | SQ-1 k=4 XX windows dropped | INFO | 14 |
| DQ-28 | SQ-2 k=4 baseline join | PASS | 0 unmatched |
| DQ-29 | SQ-2 centering k=2 | PASS | mean lift 0.000 runs/100 (≈0 expected; first pitches excluded from windows) |

WARNs are dispositioned disclosures: walks exclude 2 IBB by house rule (exact with IBB); outs are 9 short on OU-1 events and 2 short (0.4%) after inning-state reconstruction.

## 2 · Independent harness (`dp_uc64_verification.py` → `out/dp_uc64_verification.csv`): **43 / 43 PASS**
Reads raw parquet with plain pandas, never imports the kernel or house KPI functions; re-derives windows, baselines, lifts, endings, GJSD and entropy with plain-Python PA loops.

| ID | Check | Independent | Receipt | Tol | Result |
|---|---|---|---|---|---|
| V01 | career regular-season pitches | 30079.0 | 30079.0 | 0.0 | PASS |
| V02 | 2026 regular-season pitches | 2955.0 | 2955.0 | 0.0 | PASS |
| V03 | pitching rows named 'Nola, Aaron' map to one id (EN-3: batting rows carry the hitter's name) | 1.0 | 1.0 | 0.0 | PASS |
| V04 | 2026 strikeouts (REC-1) | 177.0 | 177.0 | 0.0 | PASS |
| V05 | 2026 walks + IBB (REC-1) | 59.0 | 59.0 | 0.0 | PASS |
| V06 | 2026 starts (distinct games) | 33.0 | 33.0 | 0.0 | PASS |
| V07 | 2026 K% (house PA rule) | 0.238 | 0.238 | 0.0011 | PASS |
| V08 | 2026 HR/PA | 0.05 | 0.05 | 0.0011 | PASS |
| V09 | 2026 whiff per swing | 0.2705278592375366 | 0.2705278592375366 | 0.002 | PASS |
| V10 | 2026 CSW | 0.2978003384094754 | 0.2978003384094754 | 0.0005 | PASS |
| V11 | 2026 xwOBA (XW-1 by direct sum) | 0.3145675675675676 | 0.3145675675675676 | 0.0006 | PASS |
| V12 | SQ-1 windows k=2 | 22251.0 | 22251.0 | 0.0 | PASS |
| V13 | SQ-1 windows k=3 | 15342.0 | 15342.0 | 0.0 | PASS |
| V14 | SQ-1 windows k=4 | 9528.0 | 9528.0 | 0.0 | PASS |
| V20 | SQ-2 lift SI-CH vs RHB (career) — note: receipt mean over non-null rv windows | 3.2 | 3.2 | 0.06 | PASS |
| V21 | SQ-2 lift SI-FF vs RHB (career) — note: receipt mean over non-null rv windows | 2.34 | 2.34 | 0.06 | PASS |
| V22 | SQ-2 lift CH-KC vs LHB (career) — note: receipt mean over non-null rv windows | 1.81 | 1.81 | 0.06 | PASS |
| V23 | SQ-2 lift CH-FF vs RHB (career) — note: receipt mean over non-null rv windows | -2.39 | -2.39 | 0.06 | PASS |
| V24 | SQ-2 lift SI-KC-KC vs LHB (career) — note: receipt mean over non-null rv windows | -7.26 | -7.26 | 0.06 | PASS |
| V25 | SQ-2 lift FF-KC-KC vs RHB (career) — note: receipt mean over non-null rv windows | 2.2 | 2.2 | 0.06 | PASS |
| V26 | SQ-2 lift FF-KC-FF-FF vs LHB (career) — note: receipt mean over non-null rv windows | 7.13 | 7.13 | 0.06 | PASS |
| V30 | SQ-3 ending xwOBA KC-KC vs LHB | 0.2224 | 0.2224 | 0.0006 | PASS |
| V30n | SQ-3 ending PA count KC-KC vs LHB | 335.0 | 335.0 | 0.0 | PASS |
| V31 | SQ-3 ending xwOBA KC-KC vs RHB | 0.1736 | 0.1736 | 0.0006 | PASS |
| V31n | SQ-3 ending PA count KC-KC vs RHB | 437.0 | 437.0 | 0.0 | PASS |
| V32 | SQ-3 ending xwOBA FF-KC-KC vs LHB | 0.1789 | 0.1789 | 0.0006 | PASS |
| V32n | SQ-3 ending PA count FF-KC-KC vs LHB | 131.0 | 131.0 | 0.0 | PASS |
| V33 | SQ-3 ending xwOBA FF-KC-KC vs RHB | 0.1544 | 0.1544 | 0.0006 | PASS |
| V33n | SQ-3 ending PA count FF-KC-KC vs RHB | 132.0 | 132.0 | 0.0 | PASS |
| V34 | SQ-3 ending xwOBA CH-FF vs RHB | 0.396 | 0.396 | 0.0006 | PASS |
| V34n | SQ-3 ending PA count CH-FF vs RHB | 117.0 | 117.0 | 0.0 | PASS |
| V35 | SQ-3 ending xwOBA SI-SI vs LHB | 0.3659 | 0.3659 | 0.0006 | PASS |
| V35n | SQ-3 ending PA count SI-SI vs LHB | 146.0 | 146.0 | 0.0 | PASS |
| V40 | SQ-4 rankable count | 176.0 | 176.0 | 0.0 | PASS |
| V41 | SQ-4 clear count | 28.0 | 28.0 | 0.0 | PASS |
| V42 | SQ-5 verdicts reproduce from filed bar | 124.0 | 124.0 | 0.0 | PASS |
| V43 | SQ-6 GJSD 2023-26 R vs S, LHB | 0.0253 | 0.0253 | 0.0002 | PASS |
| V44 | PI-1 2026 H(next | side) | 2.1715 | 2.1715 | 0.0002 | PASS |
| V45 | report has no nan / None / FILL tokens (word-bounded) | 0.0 | 0.0 | 0.0 | PASS |
| V46 | report figures exist | 10.0 | 10.0 | 0.0 | PASS |
| V47 | visual audit V1-V7 all PASS / N-A / registered exception | 1.0 | 1.0 | 0.0 | PASS |
| V48 | DQ scorecard has 0 FAIL | 0.0 | 0.0 | 0.0 | PASS |
| V49 | dashboard written | 1.0 | 1.0 | 0.0 | PASS |

Harness finding (fixed in the harness, not the build): V03 first counted batting-role rows, where `player_name` is the hitter (EN-3), and saw 140 'pitchers' named Nola. Scoped to pitching rows: 1.

## 3 · Visual audit (`out/dp_uc64_visual_audit.csv`, `recap_viz` V1–V7)
| Figure | V1 | V2 | V3 | V4 | V5 | V6 | V7 |
|---|---|---|---|---|---|---|---|
| f1_context | PASS | PASS | PASS | N-A | PASS | PASS | PASS |
| f2_career | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| f3_starts | PASS | PASS | PASS | N-A | PASS | PASS | PASS |
| f4_pivot | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| f5_lift_grid | PASS | EXCEPTION (comparison inside the measure: same pitch, same count, same side) | N-A | N-A | PASS | PASS | PASS |
| f6_ranked | PASS | PASS | PASS | N-A | PASS | PASS | PASS |
| f7_endings | PASS | PASS | PASS | N-A | PASS | PASS | PASS |
| f8_eras | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| f9_battery | PASS | PASS | N-A | N-A | PASS | PASS | PASS |
| s1_predictability | PASS | PASS | N-A | N-A | PASS | PASS | PASS |

Eyeball QA (two rounds) beyond the machine audit: F6 interval/point mismatch fixed; F9 window aligned to the test (2023–26); F4 clipped labels fixed; F8 and F4 titles toned to the evidence.

## 4 · Code pins at certification (sha256)
| File | sha256 |
|---|---|
| `dp_uc64_build_dashboard.py` | `75614d4bed067e1f5bcd11e746b6f1b7add7fcbcc88b496427bcab750378a61e` |
| `dp_uc64_build_figs.py` | `075889717b0ca540ded56cd73b6b991a477fcd949185064de710098b8bb5b7d8` |
| `dp_uc64_build_pdf.py` | `7f850abd4f8a0447e28a64a42d7819c3f0f3e72b9f5a2b06a94400c880bcada7` |
| `dp_uc64_build_report.py` | `ec079ebe7c74d564d4117d279dd0386710a875f1f556136e4658b232caeb3402` |
| `dp_uc64_kernel.py` | `32a83b8491dd628e3d44504a01dd25af9a30ed336a4ffa570c885889b9cf5390` |
| `dp_uc64_narrative.py` | `9364b97087740db75a45564b960f3e03f30c350fd717da0f78b399dd53f4e3f9` |
| `dp_uc64_nola_recap.py` | `eb2dce789dd82b7824638d2fa82fa53905eedaa9127a7db5a0f3dc4283eb6a66` |
| `dp_uc64_verification.py` | `2e82811223db2cdae83efc62c81c783105d66827f9aba3cde45d56953ca6b260` |

## 5 · Certification verdict (`certification-agent`): **READY-CONDITIONAL**
| Artifact | Present | Consistent |
|---|---|---|
| BID with specs filed before code | yes | yes (bars unchanged after compute; additions classified in `03` §2) |
| Entity lock + REC-1 | yes | yes (dispositions recorded) |
| Lineage (12 pins) | yes | asserted every build |
| DQ scorecard | yes | 0 FAIL |
| Independent harness | yes | all PASS |
| Visual audit | yes | 10/10 (1 registered exception) |
| Glossary | yes | provisional (DPO ratification) |
| Privacy | yes | clear |

**Conditions:**
- **C1** DPO ratifies the SQ family, PT-H, OUT-1, PI-1 and the PC-1 definition (provisional until then).
- **C2** Sequence-level results are published as *candidates*: report and dashboard must keep the calibration line (28 of 176 vs 17.6 by chance) next to any ranked list.
- **C3** Batterymate copy keeps the G4 sentence (no pitch-call attribution).
- **C4** Ledger patch pasted (UC52–UC64 pending).
