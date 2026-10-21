# 03 · Governance: `uc-pps-036`

Agents: `business-glossary-agent` · `kpi-calculator` · `technical-lineage-builder` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 0 · Rule-1 search (before anything was declared new)
Search: `grep -l` over `dp_uc*_kernel.py`, `phillies_dp/*.py`, the ledger and every control-plane `03_governance.md` (file names only; no prior UC folder opened).

| Candidate | Search terms | Result |
|---|---|---|
| Season card, runs on watch, house percentile | `runs_created`, `house_percentile`, `season_recap` | **Found** (UC48/49/51) → imported via `dp_uc51_kernel` |
| Career frame | `career_frame` | **Found** CF-2b (UC51) → **generalized** CF-2c (EN-2 extra columns) |
| xwOBA | `xwoba`, `expected woba` | **Found** XW-1 (UC50) → imported; companion WB-1 added (see §2) |
| Barrel rate | `barrel_rate`, `launch_speed_angle` | **Found** BR-1 → imported |
| Release / extension / arm angle | `release_extension`, `release_pos_x`, `arm_angle` | **Found** as columns in UC44–51 kernels; no reusable function → plain aggregation (no KPI) |
| Pitch map by side | `lhb_pitch_mix`, `pitch_map` | **Found** K44 → imported (HP-11) |
| Quick-AB / success rate | `tm_success`, `success_rate`, `quick at bat` | **0 hits** in kernels → **QA-1 (new)**; client function inherited by IX-1 for HP only |
| Bullet slider | `spin_axis`, `bullet` | UC50 kernel uses `spin_axis` for a different purpose → **BS-1 (new)** |
| Delivery similarity | `similar`, `comps`, `euclid` | UC44 `benchmark_population` is a grade population, not a distance → **DS-1 (new)** |
| Reliever role | `role`, `starter`, `STARTER_WORKLOAD` | UC51 CX-1b is a pitch-count cut, not a role → **RP-1 (new classifier)** |

## 1 · Business glossary
| Term | Definition | Status |
|---|---|---|
| **House wOBA** | K44 `nresults`: FanGraphs season weights over every PA event except pickoffs; errors and fielder's choices count as outs. Used for all ranks. | Approved (inherited) |
| **Statcast-basis wOBA (WB-1)** | Σ `woba_value` / Σ `woba_denom` over PA ends with `woba_denom` > 0, the same rows and denominator as XW-1. It is NOT house wOBA. | New, basis companion (not a KPI) |
| **Runs on watch** | Runs scored during the PAs he pitched (`runs_created`). Not ERA. | Approved (inherited) |
| **Quick-AB success rate (QA-1)** | Share of completed PAs in which he reaches two strikes (post-pitch count) or gets a ground ball within the first three pitches. It is NOT the notebook's `tm_success_rate`. | New, provisional |
| **Bullet slider (BS-1)** | Pitcher-season SL averaging ≤ 4.0 in of horizontal AND ≤ 4.0 in of induced vertical break (50+ sliders). | New, provisional |
| **Delivery distance (DS-1)** | z-scored Euclidean distance over six features (below). Smaller = more alike. | New, provisional |
| **Reliever (RP-1)** | Phillies pitcher-season with starts ≤ 20% of games; start = first Phillies pitcher of the game. | New, provisional classifier |

## 2 · KPI specifications (`kpi-calculator`), written before code; the harness implements from these
**QA-1 `quick_ab_rate`** · grain: any level · population: PAs whose last pitch carries an `events` value · formula: success if ∃ pitch with `pitch_number` ≤ 3 whose post-pitch strike count ≥ 2 (post-pitch = next pitch's `strikes`; on the last pitch, 3 for a strikeout, else `strikes` + 1 if `type`=='S' and `strikes`<2), OR ∃ pitch ≤ 3 with `type`=='X' and `bb_type`=='ground_ball' · null/edge: PAs without an event are excluded; fouls with two strikes do not add · test: harness D (2026 and career, exact).

**BS-1 `bullet_slider`** · grain: pitcher-season · population: LHP, `pitch_type`=='SL', ≥ 50 · formula: hb_in = 12·mean(pfx_x), ivb_in = 12·mean(pfx_z); bullet = |hb_in| ≤ 4 ∧ |ivb_in| ≤ 4 · test: harness D.

**DS-1 `delivery_distance`** · grain: LHP pitcher-season, ≥ 150 pitches · features: mean release_pos_x, release_pos_z, release_extension (all pitches); primary fastball (FF or SI, whichever is more frequent) velocity, 12·pfx_x, 12·pfx_z · formula: z-score each over the population (ddof 0); Euclidean distance to Mayza 2026; nearest season per other pitcher · test: harness D (nearest comp, Alvarado rank).

**RP-1 `house_pitcher_seasons.role`** · starts / games ≤ 0.2 → RP · test: harness C (n=32).

**WB-1 `woba_statcast`** · basis companion of XW-1 (same filter and denominator) · test: harness D (2026 and both platoon sides).

## 3 · Technical lineage (published numbers)
| Published number | Receipt | Built from |
|---|---|---|
| Season line, career ranks (§1–2, F1, F2) | `dp_uc52_career.csv` | CF-2c → nresults, runs_created, HH, BR-1, XW-1, WB-1, QA-1 |
| LHP relief table (§2) | `dp_uc52_house_lhp_rp.csv` | LP-1 → house_pitcher_seasons (RP-1) → KP-1 |
| Barrel line (F3) | `dp_uc52_house_lhp_barrel_woba.csv` | LP-1 LHP → nresults + BR-1, OLS (`np.polyfit`) |
| Platoon (§4, F4) | `dp_uc52_platoon_2026.csv`, `dp_uc52_weapons_2026.csv` | CF-2c 2026 by `stand` |
| Stuff (§5, F5–F7) | `dp_uc52_arsenal_2026.csv`, `dp_uc52_delivery_house_lhp.csv`, `dp_uc52_shapes_house_lhp.csv`, `dp_uc52_bullet_slider.csv` | CF-2c + LP-1 → DS-1 inputs, BS-1 |
| Quick-AB (§7, F9) | `dp_uc52_quick_ab_house.csv` | LP-1 → QA-1 |
| Comps (§8, F10) | `dp_uc52_delivery_distance.csv` | DS-1 |
| HP grades (§9) | `dp_uc52_hp_grades.csv`, `dp_uc52_hp_values.json` | client frames + client functions (IX-1) |
| Every narrative number | `dp_uc52_headlines.json` | all of the above, through `dp_uc52_narrative.py` |

## 4 · Defect exposure
| Defect | Exposed here? | Evidence |
|---|---|---|
| MI-1 (non-MLB rows via CF-2) | No | CF-2b dropped 0 rows (asserted) |
| NM-1 (CF-2 name stamp) | No | CF-2b stamps the subject's name |
| **EN-2 / CF-2 projection gaps** (new) | **Yes** | Build failed on `launch_speed_angle`, then on `woba_denom`; fixed by CF-2c |
| **WB-1 basis mismatch** (new) | **Yes** | First draft compared house wOBA .285 with xwOBA .288; the same-basis actual is .299 |
| **HX-1 NF-1 drops `launch_speed_angle`** (new) | **Yes** | Client-frame barrel rank 9/9 vs governed 6/9; HP-04 graded on CF-2c |
| **DEF-1 `tm_success_rate` pre-pitch count** (client) | **Yes** | 40.1% (client) vs 59.0% QA-1, career |
| **RQ-1 kaleido string-x scatter** (new, render) | **Yes** | F1 collapsed to one x position; numeric x fixed it |

## 5 · Privacy, tagging, versioning
- **Privacy:** CLEAR. Public MLB performance data; carry-ins are published reporting. No medical inference about the 2025 IL stint.
- **Tags:** Internal · domain Pitching · subject area bullpen / season recap · product `uc-pps-036` · no PII.
- **Versioning:** v1.0.0, anchor 2026-10-01. **v1.1.0** = any further 2026 postseason appearance (postseason ledger only) or verified 2027 status (carry-in line). Changing QA-1, BS-1 or DS-1 thresholds after publication is **breaking**.

## 6 · Ratification path
| Object | Recommendation |
|---|---|
| IX-1 (source-pinned extraction) | **Ratify** (second clean use) |
| CF-2c (EN-2) | Fold into CF-2b upstream as an optional `extra_cols` (non-breaking) |
| WB-1 | Upstream into XW-1 output (E-2) |
| QA-1, BS-1, DS-1, RP-1 | Provisional; second use required |
