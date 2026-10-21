# 05 · Quality & Certification: `uc-pps-036`

Agents: `dq-rule-definer` · `data-quality-engineer` · `certification-agent`

## 1 · DQ scorecard (executed; `out/dp_uc52_dq_scorecard.csv`): **12 PASS / 0 WARN / 0 FAIL**
| Rule | Dimension | Rule (grain) | Result | Observed |
|---|---|---|---|---|
| DQ-01 | uniqueness | no duplicate pitch key, career frame (pitch) | PASS | 0 |
| DQ-02 | validity | regular season only in the rate frame | PASS | all R |
| DQ-03 | validity | release_speed in [60, 105] | PASS | 0 out |
| DQ-04 | validity | abs(pfx_x), abs(pfx_z) ≤ 3 ft | PASS | 0 out |
| DQ-05 | validity | spin_axis in [0, 360] | PASS | 0 out |
| DQ-06 | validity | release_extension in [4, 8] ft | PASS | 0 out |
| DQ-07 | completeness | pitch_type null ≤ 1% | PASS | 8 null (0.7%) |
| DQ-08 | completeness | 2026 BIP launch_speed tracked ≥ 95% | PASS | 0 untracked |
| DQ-09 | completeness | career BIP launch_speed_angle ≥ 90% | PASS | 6 null |
| DQ-10 | completeness | arm_angle coverage 2026 ≥ 70% (informational) | PASS | 76% |
| DQ-11 | consistency | woba_denom present on PA-ending rows | PASS | ≥ 99% |
| DQ-12 | timeliness | game_date ≤ anchor 2026-10-01 | PASS | max 2026-09-25 (RS) |

## 2 · Brand and palette compliance
- **10 / 10 figures pass** the in-process brand checks (Arial, title, subtitle, axis titles, palette, claim asserted): `out/dp_uc52_brand_checks.csv`.
- **PL-3 pitch palette** (SI amber, SL violet, FF red, FS blue) validated light **and** dark: `out/dp_uc52_palette_validation.txt`. UC51's green-for-slider failed CVD next to red (ΔE 3.1 deutan) and was rejected. Batter-side pair L #3B6FD8 / R #D22D49 passes both themes. The context gray fails the chroma floor by design; the subject is always direct-labelled.

## 3 · Verification harness: **74 / 74** (`dp_uc52_verification.py`, `out/dp_uc52_verification_log.csv`)
Imports no build kernel (asserted). Re-reads parquet, rebuilds the frame with its own Phillies-fielding filter and dedup, and re-implements each KPI from `03` §2, including house wOBA from the FanGraphs constants CSV.

| Family | What it recomputes | Checks |
|---|---|---|
| A · lineage | kernel hashes, file manifest, no-kernel-import | 14 |
| B · frame | pitch/game counts, dates, hand, dedup, career frame, postseason ledger, anchor | 9 |
| C · context | LHP RP population n, wOBA and BB% ranks (RP-1 re-implemented) | 3 |
| D · story | house wOBA, Statcast wOBA, xwOBA, K%, BB%, HH, barrel, QA-1 (2026 + career), platoon, career ranks, BS-1, DS-1 | 25 |
| E · figures | 10 figures, brand pass, 14 HP rows graded | 3 |
| F · published strings | caps, no nan/None, ordinals, key strings in report and dashboard, house wOBA string, section survival (RQ-2), pipe-free HP cells (RQ-3) | 16 |
| G · carry-in discipline | no carry-in value in headlines; labelled; no ERA | 4 |

**Sequence disclosure.** The house rule is to write the harness from `03` §2 *before* reading build output. In this session the build output had already been read when the harness was written, so definition-first held for the code (no kernel import, specs re-implemented) but not for the timing. The harness still caught WB-1, which the build had published wrong.

## 4 · What the build and the harness caught (Phase 2 field: "intake could have caught")
| # | Caught | By | Fix | Intake could have caught |
|---|---|---|---|---|
| 1 | SRC-1: client frames have no `game_type` filter. Correction to the BID: `get_phillies_data` already drops spring (S/E), so only postseason leaks (67 career pitches, 6 in 2026) | intake → HP build | rates regular-season only; postseason ledger | **Y** (caught; BID overstated the spring part) |
| 2 | SRC-2: stale root `pp26.csv` (134 pitches through 04-14). No impact: the client's platoon numbers match the live frame exactly | intake → HP-10 test | not used; E-5 archive | **Y** |
| 3 | DEF-1: `tm_success_rate` reads the pre-pitch `strikes` (two strikes within two pitches); 40.1% vs QA-1 59.0% | intake | QA-1 + HP-13 | **Y** |
| 4 | DEF-2: client success-rate figure draws the first facet's mean on both facets | intake | F9 uses the house median | **Y** |
| 5 | POP-1: barrel→wOBA scatter mixes `nphl` + `pps` + `pos` LHPs and hard-codes 73 PA | intake | F3 restated on house LHP seasons (100+ PA) | **Y** |
| 6 | ENV: device `/sessions` 100% full | T0 | `/tmp/pyrender` install | **Y** |
| 7 | EN-2: CF-2 projection lacks extra columns (build failed twice) | build | CF-2c | N |
| 8 | HX-1: NF-1 drops `launch_speed_angle`; client-frame barrel rank wrong | HP build | HP-04 graded on CF-2c; E-3 | N |
| 9 | **WB-1: house wOBA set against Statcast-basis xwOBA** ("expected agrees +.003"; the same-basis gap is −.011; platoon wording too) | harness D | two named bases; 3 sentences, F1, F3, platoon tables, HP-04/HP-10 restated | N |
| 10 | PAL-1: UC51 green slot fails CVD beside red | palette validator | PL-3 | N |
| 11 | RQ-1: kaleido 0.2.1 collapses string-x scatter (F1) | render QA | numeric x | N |
| 12 | **RQ-2: `SI<SL` in a caption opened a phantom HTML tag; the PDF silently lost §7–§9** | render QA (PDF look) | escape; section-survival guard in `build_pdf` + harness F | N |
| 13 | RQ-3: `|HB|` inside an HP cell split the markdown table | render QA | pipe-free cells; harness F | N |
| 14 | Harness sequence (see §3) | process | disclosed | N |

Six of 14 catches were intake-catchable, and all six were caught at intake. The eight build-time catches are render or engineering defects, plus one semantic catch (WB-1) that only a definition-first harness finds.

## 5 · Certification
**READY-CONDITIONAL** (C1–C5 in `00` §8). Lineage complete, glossary recorded, KPI specs written before code (`03` §2), DQ 0 FAIL, harness 74/74, brand 10/10, privacy CLEAR, anchor pinned.
