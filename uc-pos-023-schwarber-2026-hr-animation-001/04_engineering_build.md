# 04 · Engineering Build
**technical-lineage-builder · data-engineer**
`uc-pos-023-schwarber-2026-hr-animation-001` · UC #58 · `dp_uc58` v1.0.0 · built 2026-10-27 19:52–20:04 ET

## 1 · Code (MLB root)
| File | sha256 (16) | Role |
|---|---|---|
| `dp_uc58_kernel.py` | `d262136169db4bb1` | Governed kernel: inheritance by import (K57 chain + `cumulative_metric`), `load_career`, DH-1 `game_seq`, WP-1, CP-1 `cum_hr`, `client_frame_cum` (client's cell verbatim), HB-1 `hr_quality`, SP-1/2 `spray`, `direction`, `wall_outline`, `walkoff`, GR-1 |
| `dp_uc58_build.py` | `23e2c5010e4b0d43` | T1: all receipts, HP-01..HP-15, clip list, design data, DQ |
| `dp_uc58_build_keyframes.py` | `ba2bf477eae9343f` | T2: 8 PNG keyframes from receipts only; `brand_tokens.json` |
| `dp_uc58_build_prompt.py` | `edca3b2abe6398b2` | T3: the Claude Design prompt, every number templated from receipts |
| `dp_uc58_verification.py` | `44146123ceda9ffe` | T4: independent harness (raw parquet, plain pandas) |
| `dp_uc58_technical_feasibility_brief.md` | — | T3: cell-by-cell assessment of the client's Python |

## 2 · Lineage (technical-lineage-builder): source → screen
| On screen | Receipt | Transformation | Source columns |
|---|---|---|---|
| S1–S3 step lines | `cum_hr_by_pa.csv` → `design_data.s1_s3_curves` | PA rows (PA-X1) → DH-1 order → running HR (CP-1) | events, game_type, game_date, game_pk, at_bat_number, pitch_number, sv_id, des |
| S3 stop captions | `hr_register_2026.csv` | HL-1 tags; WP-1; result from all rows of the game | launch_speed, hit_distance_sc, inning, inning_topbot, delta_home_win_exp, bat/fld/post scores, pitcher (+ CI-3 names) |
| S4 table | `season_table.csv` | count by season; min-rank | events, team (inning_topbot → home/away) |
| S5 dots | `spray_2026.csv` | DR-1 loc → bearing; radius = distance; SP-2 fallback | hc_x, hc_y, hit_distance_sc, des |
| S5 thump cards | `hr_quality_by_season.csv`, `headlines.spray_by_season` | client agg + HB-1 + house barrel rate; DR-1 direction | launch_speed, hit_distance_sc, launch_speed_angle, type |
| S6–S7 balls | `pitchmap_2026.csv` | CPG-1 group; PM-1 zone | plate_x, plate_z, pitch_type, p_throws, sz_top, sz_bot |
| Clip cuts | `clip_list.csv` | HL-1 rows in scene order, `resolve_play_ids.py` schema | game_pk, inning, inning_topbot, at_bat_number, pitch_number |

## 3 · Run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc58_build.py && python dp_uc58_build_keyframes.py && python dp_uc58_build_prompt.py && python dp_uc58_verification.py
```
Deterministic; ≈ 25 s (build 5 s, keyframes ≈ 15 s). The anchor guard refuses to run if the house log passes 2026-10-01.

## 4 · Build log (defects found and fixed in this run)
| # | Found by | Defect | Fix |
|---|---|---|---|
| B-1 | carry-in reconcile (MLB.com Game 1 = 350th HR) + DQ-13 (`des` counter) | **DH-1:** 4/30 games in game_pk order put HR #10/#11 in the wrong order | `game_seq()` (sv_id → des counter → game_pk) |
| B-2 | harness V03 | PA counted runner-out rows (2021 473 vs 470) | PA-X1: house `NON_PA` passed to `cumulative_metric` |
| B-3 | build | `barrels` column collision on the barrel-rate merge | renamed `bip_barrels` |
| B-4 | build | `load_phils_cols` appends `phillies_role` (duplicate column) and needs `game_year` | column list fixed |
| B-5 | device | deletes not permitted in connected folders (stray partial grades file) | moved to `out/_to_delete/` for the DPO |
| B-6 | render QA | K5 legend over dots; K6 footer over axis title; K8 zero-lines; K7 hard-coded number | fixed; K7 templated |
| B-7 | ENV-3 | device `/sessions` at 100%; no pyarrow | render stack in `/tmp/pyrender`, `TMPDIR=/tmp/piptmp` |

## 5 · Client frame (CP-1 evidence)
`cp1_client_vs_governed_axis.csv`: the client's cell on the same regular-season rows ends 2026 at **3,026** vs **701** PA (stretch 4.32×; range 4.15–5.6× across seasons). Its HR totals agree with the governed curve every season; only the x-axis is wrong.
