# 04 — Engineering Build · uc-pos-marsh-breakout-001

## data-engineer — build record

**Script:** `marsh_breakout_analysis.py` (this folder; run as `python marsh_breakout_analysis.py <MLB_repo_path> <out_path>`, defaults to `./out`). Built 2026-07-13, run live against the mounted parquet layer. New-files-only: nothing in the MLB repo was edited; outputs land in `MLB/out/`.

**Pipeline:** load LAA parquet + PHI 2022–2026 parquets → entity lock 669016 → `game_type=='R'` → dedup pitch key → idempotent wOBA-weight join → locked KPI kernel + derived indicator functions → 16 CSVs.

## technical-lineage-builder — hop summary (condensed)

| Consumable | Source columns | Transform |
|---|---|---|
| `marsh_breakout_results_by_season.csv` | events, w* weights, estimated_* | locked get_stats by season |
| `_discipline_by_season.csv`, `_discipline_platoon.csv`, `_twostrike_discipline.csv` | description, zone, balls, strikes | locked swing/whiff lists → panel |
| `_battedball_by_season.csv`, `_firstpitch_bip.csv` | launch_speed/angle, launch_speed_angle, bb_type | type=='X' filters, threshold flags |
| `_spray_by_season.csv` | hc_x, hc_y, stand, bb_type | spray angle atan2 → pull/oppo/air |
| `_platoon_by_season.csv` | + p_throws | locked get_stats × p_throws |
| `_pitchgroup_by_season.csv` | pitch_type → {fastball, breaking, offspeed} | group map + get_stats + panel |
| `_countstate_by_season.csv` | balls, strikes | two_strike / ahead / even_or_behind |
| `_pa_funnel.csv` | strikes, game_pk, at_bat_number, p_throws | distinct-PA funnel + shares |
| `_2026_monthly.csv`, `_2025_halves.csv` | game_date | window slices of the above |
| `_pace_per600.csv`, `_earlycount_pa.csv` | derived | per-600 scaling; balls+strikes<=1 |
| `_dq_receipts.csv` | all | see 05 |

## Output manifest (16 files, `MLB/out/marsh_breakout_*.csv`)

results_by_season · discipline_by_season · battedball_by_season · spray_by_season · platoon_by_season · discipline_platoon · pitchgroup_by_season · countstate_by_season · firstpitch_bip · 2026_monthly · twostrike_discipline · pa_funnel · pace_per600 · earlycount_pa · 2025_halves · dq_receipts
