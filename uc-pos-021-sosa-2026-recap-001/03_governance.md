# 03 · Governance
**kpi-calculator · technical-lineage-builder · privacy-watchdog · data-tagger · version-controller**

## 0 · Rule-1 search (before declaring anything new)
| Need | Hits | Disposition |
|---|---|---|
| Slash, wOBA, xwOBA, BB/K, chase/whiff/swing, HH, barrel, CR-1, RF-2/RF-2x, KP-1, PA-1, CM-1 | K55 → K54 → K40 chain | **Inherit** (pinned) |
| Out-of-zone contact | K54 `ooz_whiff_rate` | Inherit (1 − whiff) |
| Chase cost | K54 CC-1 `take_reference` / `chase_cost` | Inherit |
| Change points in 2026 | K55 ER-1 | Inherit (parameters unchanged) |
| Uptick at a date | K54 TR-1 `tr1_metrics` / `tr1_ledger` | Inherit (bars unchanged) |
| Pull AIR% | K46 `pull_air_rate` v1.1.0 (notebook cell 56 cannot run: O-7) | Inherit |
| EV90 | UC27 `ev90` (0.90 quantile, BIP) | Reuse definition in EV-1 |
| EV50 / max EV / mean EV | client code (`ev_mu` in `inds`; ev50/ev90/ev_max commented) | EV-1 (client definitions; GL-1) |
| Bat speed | K40 BT-1 | Inherit |
| Out-of-zone BA sustainability | none | **New, provisional OZ-1** |
| Contract walkaway | none (no salary data in house) | **New, provisional WA-1** (carry-in band + data flags) |
| Client functions (`nresults`, `hard_hit_rate`, `chase_rate`, `whiff_rate`, `barrel_rate`, `inds`) | K44 + `barrel_rate.py` + IX-1 | Inherit for HP reproduction only |

## 1 · Inheritance (pins)
`dp_uc56_kernel.py` asserts 16 file hashes at import: `dp_uc55_kernel.py` `9bdcce59…`, `dp_uc46_kernel.py` `a45ac9a7…`, `barrel_rate.py` `6282f090…`, plus 14 through K55 (K54, K40a and the K53 chain). Drift halts the build.

## 2 · KPI specs (kpi-calculator)
### OZ-1 (provisional; bars pre-registered in the BID)
- Population: `pa_rows(df)` with `zone > 9` and `pitch_type` notna on the terminal pitch.
- AB = events not in `NON_AB`; hits = `HIT_EV`. OZ-BA = hits/AB.
- OZ-xBA = Σ xBA / AB where xBA = `estimated_ba_using_speedangle` on BIP (actual hit indicator when null; 1.72% of out-of-zone BIP), 0 on non-BIP AB.
- `oz_gap` = OZ-BA − OZ-xBA → RAN HOT ≥ +.030 · RAN COLD ≤ −.030 · else EARNED.
- "Sustainable" = (EARNED or RAN COLD) and OZ contact ≥ Phillies-RHB 2022–26 median.
- Null handling: seasons with 0 OZ AB → NaN, never 0.

### WA-1 (provisional; rule pre-registered in the BID)
- Band: floor $4.4M (CI-3), ceiling = max CI-5 AAV ($6.4M) rounded down to $0.5M → **$6.0M**.
- Decline flags: 2026 vs mean of 2023–25 (bat speed: 2024–25): DF-1 bat speed −1.0 mph · DF-2 EV90 −1.0 mph · DF-3 hard-hit −.040 · DF-4 barrel −.020 · DF-5 xwOBA −.020 · DF-6 OZ contact −.030. A flag trips when the 2026 value is worse by at least the bar.
- Result: **0 of 6** → term up to 2 years → walkaway **$6.0M AAV × 2 = $12M**.

### EV-1
Mean, median (EV50, GL-1), 0.90 quantile (EV90) and max of `launch_speed` on `type == 'X'` rows where `launch_speed` notna; `n_ev` carried.

## 3 · Lineage (technical-lineage-builder)
`data/phillies/*.parquet` → K55 `load_house` (anchor assert) → `subject_rows` (id lock, EN-2) → inherited KPI functions / EV-1 / OZ-1 / K46 → `out/dp_uc56_season_panel.csv` → `headlines.json["season"]` → `dp_uc56_narrative.py` → report, PDF, dashboard. Carry-ins enter only through `K.WA_COMPS`, `K.WA_SALARY`, `K.WA_FLOOR_M` (labelled) and narrative text tagged CI-n.

## 4 · Defects found by building
| ID | What | Where | Disposition |
|---|---|---|---|
| **WB-2** (new, inherited) | `nresults_unrounded` uses 2026 wOBA weights for every event when `game_year` is not in the level; pooled 2023–25 wOBA read .3219 vs .3190 per-season-weighted | K40 → K54 | K56 wrapper (non-breaking; identical when `game_year` in level); escalated for a spine v1.1 and a sweep |
| D-1 | All-Star gap finder returned July 1 (`argmax` on a leading NaN) | K56 `asb_first_game` | fixed (`fillna(0)`); correct date 2026-07-16 |
| J-2 | nullable `pd.NA` serialised as the string "<NA>" in headlines | build `num()` | fixed; harness asserts no "<NA>" |
| J-3 | figure glob caught `figure_specs.json` | dashboard builder | fixed (explicit keys) |
| H-1 | harness barrel check dropped NA `launch_speed_angle` rows (Q-3 again) | harness | fixed (`eq(6).fillna(False)`) |
| Q-1 | F3 on a date axis stacked same-day PAs into vertical jumps | figures | re-plotted on the PA index |
| Q-2 | F6 title "the 2026 hole was offspeed" overclaimed (offspeed xwOBA rose) | figures | retitled to the swing-and-miss finding |
| Q-3 | F9 subtitle: paired `$` rendered as MathJax | figures | HTML entity |
| SH-1 | carried UC55 figure shell was cut 2 lines short (no JSON/specs written) | figures | restored; SPECS assert |
| CL-2 | client `inds` `ev_mu` averages all tracked pitches incl. fouls | client notebook | graded, not edited |
| ENV-3 | `/sessions` 100% (4th occurrence) | device | `/tmp/pyrender`, `TMPDIR=/tmp/uc56/tmp` |

## 5 · DQ rule definitions
17 rules (LIN, ANC, ENT, SRC-4/5/6, CM-1, POS-1, SEN-1/2/3, GL-1, PAR-1, TR-1, OZ-1, WA-1, RATE-1). Scorecard in `05` §1.

## 6 · Privacy (privacy-watchdog / data-tagger)
**LOW.** Subject is a public figure; data are on-field performance and publicly reported salaries. No PII beyond name and MLBAM id. Teammate rows appear only as unnamed context dots (names in hover). Tags: domain `baseball-ops/offense`, sensitivity `internal`, product `uc-pos-021`. External sharing: OK after DPO review; the walkaway is an internal negotiating position and should not leave the front office (T-5).

## 7 · Versioning (version-controller)
v1.0.0, new product. The WB-2 wrapper is **non-breaking** for inherited consumers (K56-local). Upstream fix in K54 would be **breaking** for any pooled-wOBA receipt in UC34–UC55; consumer notice drafted in `07` §1 (T-6).
