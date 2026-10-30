# 04 · Engineering Build
**technical-lineage-builder · data-engineer**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0 · built 2026-10-29 20:15–20:31 ET

## 1 · Code (MLB root)
| File | sha256 (16) | Role |
|---|---|---|
| `dp_uc60_kernel.py` | `534e2399cb87064b` | inheritance + registries + Section B/C |
| `dp_uc60_schwarber_recap.py` | `dc7ef68f26952cbf` | T1 build: every receipt, `headlines.json`, DQ |
| `dp_uc60_hp.py` | `a118beaf380a6c37` | 8 HP grades from headlines |
| `dp_uc60_build_figs.py` | `23452cb0c878cc98` | F1–F8, Tier 3 audit, figure specs |
| `dp_uc60_narrative.py` | `8d05661213ce8216` | all prose, templated |
| `dp_uc60_build_report.py` / `_build_pdf.py` | `7d67753c230cc2e9` / `93c5e0c19af9dc8a` | markdown → PDF (6 pp, cap 10) |
| `dp_uc60_build_dashboard.py` | `dfa90e1143d81751` | 7-chapter dashboard (+ `_artifact.html`) |
| `dp_uc60_build_card.py` | `2e91dcaf33d96d28` | season card PNG |
| `dp_uc60_verification.py` | `ecb751efa15f6284` | harness |
| `phillies_dp/recap_viz.py`, `data/_schema/*.json` | `e6c9436a…`, `852b9765…`, `3ace7b10…` | SD-3 / SD-1 / SD-2 |

## 2 · Lineage (source → page)
| On page | Receipt | Transformation | Source columns |
|---|---|---|---|
| Season card, §2 table, F1 | `season_panel`, `context_pool_200` | K57 panel per season / per batter-season | events, woba weights, estimated_woba_using_speedangle, description, zone, type, launch_speed(_angle) |
| F2 | `cum_woba_by_pa` | `cumulative_metric` woba, DH-1 order, PA-X1 exclusions | events, woba_value, woba_denom, game_seq |
| F3, §3 | `by_month_2026`, `by_half_2026` | panel by month / SD-2 half | + game_date |
| §4, F4 | `bk1_pre_post`, `bk1_*_scan`, `bat_speed_swings_2026` | SD-2 windows; RC-5 scans; BP-0 swings | bat_speed, swing_length, launch_speed |
| F5, F6 | `ev_bip_2022_26`, `season_panel` | BIP EV; SW-8 | launch_speed, launch_angle |
| F7 | `context_pool_200`, `season_panel` | OLS on 117 pool seasons | chase (zone > 9 swings), K / PA |
| F8 | `hand_group_2025_26`, `dumbbell_hand_group` | panel by hand × house pitch group | p_throws, pitch_type |

## 3 · Run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc60_schwarber_recap.py && python dp_uc60_hp.py && python dp_uc60_build_figs.py && python dp_uc60_build_report.py && python dp_uc60_build_pdf.py && python dp_uc60_build_dashboard.py && python dp_uc60_build_card.py && python dp_uc60_verification.py
```
Deterministic. ≈ 21 s build, ≈ 40 s figures, ≈ 15 s PDF. The anchor guard refuses to run past 2026-10-01.

## 4 · Build log
| # | Found by | Defect | Fix |
|---|---|---|---|
| B-1 | render QA | CAT-1: season categories collapsed onto 2015 (F1, F5) | `type="category"`; text traces in place of annotations |
| B-2 | render QA | box traces sharing one `name` (F1, F6) | unique per-year names, `legendgroup` context |
| B-3 | title audit vs receipts | F7 "chased more than ever" (2020 was higher) and "about as much as that predicts" (R² 0.0002) | retitled to the data |
| B-4 | title audit | F8 "fastballs still paid": righty fastballs fell .495 → .386 | retitled "The Leak Was Righty Fastballs" |
| B-5 | harness V08 | F4 subtitle printed K40 tracked-swing means over a BP-0 chart | both printed, both verified |
| B-6 | PDF QA | caveats list collapsed inside a blockquote; F3 subtitle clipped | blank quote line; subtitle wrap |
| B-7 | ENV-3 | new VM; render stack missing | `pip -r requirements-render.txt` to `/tmp/pyrender` (weasyprint 70 OK) |
