# 04 — Data Model & Technical Lineage · uc-pos-006 (dp_uc24)

**Agent roles:** data-architect + technical-lineage-builder · **Verdict: PASS** — grain locked, joins validated, column-level lineage complete for every CDE and KPI. Does not implement pipelines; specifies them for the data-engineer.

## Grain & keys
- **Base grain:** one row per pitch. **Primary key:** `[game_pk, at_bat_number, pitch_number]` (dedup enforced; 0 collisions).
- **Entity key:** `batter == 607208`. **Rollup grains produced:** season, (season × p_throws), (season × pitch_group), (season × count_state), month (2026), (season × game_date) for RF-1, PA-index for RF-2, half (pre/post-ASB).

## Join strategy (validated)
1. **Vertical concat** of `turner.parquet` (WSN/LAD) + `phils_{2023–2026}` batting rows. Union schema; non-PHI rows carry NaN for bat-tracking columns (2024+ only) — correct, and those rows are excluded from the bat-tracking grain by `bat_speed.notna()`.
2. **wOBA-constants join:** left join on `game_year == Season` from `wOBA and FIP Constants.csv`. Pre-existing weight columns dropped before join to prevent `_bad` suffix collisions. 0 null weights post-join → no fan-out (one constant row per season).
3. **Team-per-row** derived, not joined: `bat_team = away_team if inning_topbot=='Top' else home_team` → `era`.

## Column-level lineage (source → target → KPI)
```
events, description, type            ─► get_stats ─► BA/OBP/SLG/OPS/wOBA/K%/BB%/ISO/HR
launch_speed, launch_angle,          ─► batted_ball ─► Barrel%, HardHit%, LD%, air%, EV/EV90, sweet-spot
  launch_speed_angle, bb_type
estimated_woba_using_speedangle      ─► get_stats.xwoba (PA-level) ; batted_ball.xwoba_con (BIP)
hc_x, hc_y, stand, bb_type           ─► pulled_air ─► Pull%, Oppo%, Pulled-Air%
zone, description, balls, strikes    ─► discipline ─► Swing/Chase/Whiff/Z-swing/Z-contact/FP-swing
wBB…wHR (constants), events          ─► wrc (SC-1) ─► wRAA, wRC, wRC/600
pitches, plate_apps                  ─► ppa (SC-2) ─► P/PA
bat_speed, swing_length, attack_angle─► bat_tracking ─► avg bat speed, fast-swing%, swing length, attack angle
events, game_date (ordered)          ─► running_line (RF-1) ─► season-to-date OPS/wOBA trajectory
events, PA-ordered, wnum             ─► rolling_form (RF-2) ─► trailing-100-PA wOBA/OPS
```

## Lineage diagram (ASCII)
```
turner.parquet (2015-22) ┐
                          ├─concat─► entity-locked pitch log ─┬─► season rollups ─► results/wrc/ppa/battedball/spray/discipline
phils_2023..2026 (bat) ──┘   (607208, R, dedup)              ├─► 2026 month / half / rolling (RF-2)
wOBA+FIP constants ──join(game_year==Season)──────────────────┴─► (season×game_date) cumulative (RF-1) ─► hero figure
```
All 16 CSV receipts + 5 figures trace to exactly one function above. No transformation exists in the report that is not in this lineage.
