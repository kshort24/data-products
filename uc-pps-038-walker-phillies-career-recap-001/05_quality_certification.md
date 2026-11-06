# 05 · Quality & Certification
Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (`out/dp_uc62_dq_scorecard.csv`): **15 PASS / 0 WARN / 0 FAIL**
| Rule | Check | Result |
|---|---|---|
| DQ-01 | Entity lock: every career row `pitcher == 592836` | PASS (20,611 rows) |
| DQ-02 | No duplicate pitch keys (EN-2) | PASS |
| DQ-03 | Regular season only | PASS |
| DQ-04 | House anchor ≤ 2026-10-01 | PASS (last regular game 2026-09-27) |
| DQ-05 | Career-frame PHI rows equal house rows by season | PASS |
| DQ-06 | OU-2 outs = public IP: 2024 251, 2026 68, tenure 1,208 | PASS (exact) |
| DQ-07 | 2026 5 G / 4 GS / 8 HR = CI-1 | PASS |
| DQ-08 | `release_speed` on typed pitches ≥ 99% | PASS (100%) |
| DQ-09 | `woba_denom` on PA ends ≥ 99% | PASS (99.4%) |
| DQ-10 | XW-1 fallback ≤ 2% per season (warning rule) | PASS (0) |
| DQ-11 | AB-1 automatic-pitch rows (warning rule) | PASS (0) |
| DQ-12 | KR-1 fit excludes the subject | PASS (194 = 198 − 4) |
| DQ-13 | All four tenure seasons in the KP-1 pool | PASS |
| DQ-14 | Non-MLB rows dropped are receipted | PASS (0) |
| DQ-15 | Lineage pins hold | PASS (10) |

## 2 · Independent harness (`dp_uc62_verification.py` → `out/dp_uc62_verification.csv`): **47 / 47 PASS**
| Family | What it does | Checks |
|---|---|---|
| A | Recomputes pitches, PA, K%, HR by season and tenure BF from **raw parquet with pandas only** (no kernel import) | 5 |
| B | Reconciles outs to public IP, 2026 G/GS/HR, the 4/22 bulk outing, the 2025 swing role | 6 |
| C | Refits KR-1 with `numpy.polyfit`, recomputes pool size and the four Phillies ranks | 5 |
| D | Re-scores PR-1 with an independently written PA-1 rule; checks bars, call and the seen/unseen disclosure against the BID | 4 |
| E | 14 published values present in the report; same bottom line in report and dashboard; 9 figures embedded; PDF newer than its source; V1–V7 clean; plotly by CDN | 20 |
| F | Carry-ins labelled; no uncarried or medical claims; DQ no FAIL; 7 HP rows; lineage | 7 |

## 3 · Visual standard (`out/dp_uc62_visual_audit.csv`)
All 9 figures pass `recap_viz.audit` V1–V7 (N-A where a standard does not apply). Eyeball QA found and fixed: F6 (seven cramped panels → one pitch × season bubble matrix), F4/F5 legend colliding with axis titles, F1 subtitle naming n = 198 where the gray set is 194, F9 clipped 2026 label.
**Palette:** house red `#E81828` / navy `#002D72`. The skill validator passes CVD separation (ΔE 22.4 protan), normal-vision floor (42.4) and contrast, and **fails the lightness band on navy** (L 0.32). Brand-mandated; compensated by secondary encoding (square = before, circle = Phillies, direct year labels, legend).

## 4 · Catches (with "could intake have caught it?")
| Catch | Found by | Intake could have? |
|---|---|---|
| Client frame loses 483 pitches (O-26) | HP-01 reproduction | Yes, with an id-vs-name row count at T0. Now standard for multi-club pitchers |
| `ev_mu` 2015 mechanism (EV-1) | HP-06 bar met, then the mechanism test | No: the registered bar was the wrong test. The grade says so (PARTLY) |
| My turn-1 CR-4 claim was wrong | HP-07 on the pinned stack | Yes: run the call before asserting it |
| 4/22 "start" (CI-4) was bulk relief | game log + house first-pitch rule | Yes, at carry-in reconciliation |
| 2023 "15 wins" crept into a takeaway with no carry-in source | harness F regex + review | Removed before publish |
| Family A first FAILED: raw recompute used only 2026 club codes | harness | Harness defect, fixed (club union 2015–26); the governed frame was right |

## 5 · Certification (`certification-agent`): **READY-CONDITIONAL**
Present and consistent: lineage (03 §3), DQ scorecard, glossary entries (01 §5), KPI specs written before code (BID, 03 §2), data model (02), acceptance criteria (BID scope), harness 47/47. Conditions C1–C6 in `00` §8.
