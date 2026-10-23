# 05 · Quality & Certification
**dq-rule-definer · data-quality-engineer · certification-agent · brand-guardian**

## 1 · DQ scorecard (`out/dp_uc54_dq_scorecard.csv`): 12 PASS / 4 WARN / 0 FAIL
| Rule | Status | Detail |
|---|---|---|
| LIN-1 lineage pins | PASS | 12 files |
| ENT-1 id lock | PASS | 702222 + batting role, 1,681 pitches |
| ENT-2 wrong Crawford | PASS | `crawford.parquet` never read |
| SRC-1 game types | PASS | 125 spring + 25 postseason excluded from rates |
| AB-1 automatic balls/strikes | PASS | 0 subject rows without a pitch type |
| DUP-1 pitch key | PASS | 0 |
| REC-1 K40 vs K44 BA/SLG | PASS | .264/.353 both |
| REC-2 OBP basis | WARN | K44 .305 (÷ PA) vs K40 .309 (published basis) |
| SRC-3 AAA tier | PASS | 1,938 pitches, labelled, 25 untracked BIP |
| CM-1 endpoint reconcile | PASS | 6 metrics × 9 series, tol 1e-9 |
| RV-1 run value sign | PASS | +0.229 on walks |
| DR-1 spray convention | PASS | +63 ft |
| XO-2 coverage | PASS | 449 / 488 (92%), variant v3 |
| TP-1 truncated_pa | WARN | 34 pool PA (subject 0) |
| SF-1 sac-fly double play | WARN | 2 pool PA (subject 0) |
| O-8 untracked BIP | WARN | 4 subject BIP |

## 2 · Brand and palette
- All 10 figures pass the claim, Arial, title, subtitle and palette checks (`out/dp_uc54_brand_checks.csv`).
- **PG-1** pitch-group palette (#C77800 / #6250D6 / #1A9E77) passes all six validator checks in light and dark: worst adjacent CVD ΔE 23.6, normal-vision floor ΔE 29.1.
- The brand red/navy/gray trio encodes subject / reference / context, not categories, and always carries direct labels.
- Render QA looked at every PNG once, plus a second pass on the five that were fixed. Dashboard QA at 1280 light, 1280 dark and 390 phone: no page-level horizontal scroll, and dark-mode inks remap.

## 3 · Independent verification (`dp_uc54_verification.py`): **157 / 157**
| Family | Checks | What it re-derives without the build kernel |
|---|---|---|
| A lineage | 7 | sha256 of 5 parents; TR-1 bars unchanged in kernel and BID |
| B frame | 12 | anchor, pitch/game counts, spring and postseason exclusion, ENT-2 (incl. J.P. Crawford's PHI rows) |
| C context | 12 | pool n=220, better-than percentiles, launch-angle and attack-angle ranks, CX-1 n=9, 464 CF-games PA, matched-volume wOBA rank |
| D story | 25 | slash line, wOBA (own weights read), BABIP, ISO, xwOBA, swing/chase/whiff/OOZ contact, HH, GB, LA, RISP, attack angle, splits |
| E new objects | 55 | TR-1 (20 values + 10 verdicts + call), RC-5 deltas, rolling min/max/date, CC-1 totals/RHP/2-strike, reach rate, XO-2 (own neighbour search), AAA vs MLB hard-hit/heart/pull |
| F published strings | 39 | 17 key strings in both report and dashboard; figures, brand, PDF cap, CDN load, NaN, DQ |
| G carry-ins | 7 | each carry-in labelled next to its use; no OAA/DRS/WAR/games value in headlines or code |

## 4 · Catches (with "intake could have caught")
| # | Catch | Found by | Intake could have caught |
|---|---|---|---|
| Q-1 | ENT-2 `crawford.parquet` is J.P. Crawford | T0 id scan | Y (caught) |
| Q-2 | SRC-2 three duplicate MLB rows in an opponent file | T0 id scan | Y (caught) |
| Q-3 | SF-1 K40 drops SF-DP from denominators | CM-1 reconcile | N |
| Q-4 | XO-2 v1 neighbourhood scored 18–45%; selection rule added and disclosed | coverage assert | N (needs data) |
| Q-5 | CM-D2 hard-hit spec raises on nullable EV | build | N |
| Q-6 | REC-1 compared OBP on two bases; re-scoped to BA/SLG + REC-2 disposition | DQ | Y |
| Q-7 | F1 claim compared the CX-1 endpoint (464 PA) with the season line (465) | figure assert | N |
| Q-8 | **"Lowest launch angle of 189" misread from a floored percentile**; Haseley 2020 is flatter. Fixed in build (`la_rank_low`), narrative, figures, HP-14 | render QA / human read | N |
| Q-9 | `hits_short` used a different distance basis than UC34; dropped | build review | N |
| HC-1 | Harness assumed 0 PHI rows for 641487; J.P. Crawford batted for PHI 2017–18. Check corrected to "never in the subject frame" + ENT-2 exposure | harness | — (harness-side) |
| HC-2 | Harness "no inline plotly" matched the CDN filename; corrected | harness | — (harness-side) |

## 5 · Certification readiness (certification-agent): **READY-CONDITIONAL (C1–C5)**
Lineage, DQ, glossary entries, model, specs-before-code, harness, privacy, and BID-with-actuals are all present and consistent. Conditions are listed in `00` §6.
