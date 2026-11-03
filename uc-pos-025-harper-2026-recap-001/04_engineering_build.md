# 04 · Engineering Build
**technical-lineage-builder · data-engineer**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0 · built 2026-11-02 18:05–18:17 ET

## 1 · Code (MLB root)
| File | sha256 (16) | Role |
|---|---|---|
| `dp_uc61_kernel.py` | `0466c66e4ab42818` | inheritance + subject + Section B/C |
| `dp_uc61_harper_recap.py` | `7277863e8279c110` | T1 build: every receipt, `headlines.json`, DQ |
| `dp_uc61_hp.py` | `b59c3b6a4f0fbb8f` | 6 HP grades |
| `dp_uc61_narrative.py` | `6ba98f86db99a522` | all copy (NC-1 registry) |
| `dp_uc61_build_figs.py` | `9bd4af50f491cac8` | F1–F3 + V1–V7 audit |
| `dp_uc61_build_card.py` | `27912eec578a4eb3` | reference notecard PNG |
| `dp_uc61_build_kit.py` | `32d8785d0c987873` | Claude Design kit + brief + manifest |
| `dp_uc61_verification.py` | `3061b1b0303207bd` | independent harness |

## 2 · Lineage (source → card)
| On card | Receipt | Transformation | Source columns |
|---|---|---|---|
| Headline dek, bullet 1 | `season_panel`, `context_pool_200`, `position_ledger_2026` | K57 panel; KP-1 percentile; fielder scan | events, woba weights, game_pk, fielder_2..9 |
| Bullet 2 | `season_panel`, `oz_by_half_2026` | chase (zone > 9), BB%/K% per PA, OZ-1 | zone, description, plate_x/z, sz_top/bot |
| Bullet 3 | `season_panel`, `by_half_2026` | hard-hit / barrel on BIP, EV p90, halves (SD-2) | launch_speed, launch_speed_angle, game_date |
| Bullet 4, TR headers | `hand_2026`, `by_year_hand` | panel by `p_throws` | p_throws + slash columns, estimated_woba_using_speedangle |
| TL-b | `cum_slash_2015_26`, `career_envelope` | CM-2 running sums in DH-1/DH-2 order | events, game_year, game_seq, at_bat_number |
| TR callouts | `hand_group_2026`, `hand_group_2019_25`, `zone_damage_2026`, `pitch_map_2026` | panel by hand × group; zone tallies; DMG-1 | pitch_type, zone, description, launch_speed |
| B | `spray_2026`, `season_panel`, `field_outline.json` | PA-L1, DR-1, SP-1 (HR at `hit_distance_sc`) | hc_x, hc_y, hit_distance_sc, bb_type |

## 3 · Run
```
cd "C:\Users\Kellen\OneDrive\Documents\Python Scripts\MLB"
python dp_uc61_harper_recap.py && python dp_uc61_hp.py && python dp_uc61_narrative.py && python dp_uc61_build_figs.py && python dp_uc61_build_card.py && python dp_uc61_build_kit.py && python dp_uc61_verification.py
```
Deterministic. ≈ 15 s build, ≈ 5 s figures, ≈ 2 s card + kit, ≈ 20 s harness. The anchor guard refuses to run past 2026-10-01.

## 4 · Build log
| # | Found by | Defect | Fix |
|---|---|---|---|
| B-1 | T2 run | nullable `launch_speed >= 95` → NA; `~x.damage` raised | `fillna(False).astype(bool)` on every flag (kernel + build) |
| B-2 | render QA | F2 legend over the LHP header; callouts on the x-axis titles; F1 reference label on the 2026 end label; F3 callout on the ticks | margins, legend row, label moved, callout under the subtitle |
| B-3 | render QA | F2 legend read "Fastballs: home run" for a star used by every group | neutral "Home run (any group)" key |
| B-4 | card QA | bullets overran the column (character wrap) | pixel-measured wrap |
| B-5 | copy audit | "borderline pitches" (OZ-1 is just-off-the-plate takes); "hard contact" (DMG-1 includes HR); "not bad luck" with no number | reworded to the definitions; xwOBA and wOBA both printed |
| B-6 | T1 receipt audit | `postseason_2026_pitches_excluded` counted spring training too | renamed `non_regular_2026_pitches_excluded` with types (F 49, S 27) |
| B-7 | ENV-4 | `/sessions` disk full; pip failed | TMPDIR + cache on `/tmp`; render stack to `/tmp/pyrender` |
