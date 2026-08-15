# 04 · Engineering Build
**data-engineer · technical-lineage-builder**

## Artifacts

| File | Purpose |
|---|---|
| `dp_uc33_kernel.py` | loader + governed KPI kernel + AP-2/3/6/9/10 |
| `dp_uc33_verification.py` | independent verification, no kernel import |
| `dp_uc33_monthly_master.csv` | full curated `z`, 46 columns × 6 months |
| `dp_uc33_monthly_panel.csv` | presentation projection, rounded to 3 |
| `dp_uc33_context_pool.csv` | 217 Phillies hitter-seasons ≥ 50 PA |
| `dp_uc33_rolling_woba.csv` | AP-6, 2,822 rows |
| `dp_uc33_streak_games.csv` | L3 game counts |
| `dp_uc33_headlines.json` | scalars quoted in the report |
| `dp_uc33_fig1..5_*.png` | report figures |

## Pipeline
`phils_{2015..2026}.parquet` → role tag (`home/away × inning_topbot`) → drop `game_type` S/E →
`month = game_date.dt.month` → subject filter → per-layer aggregation → left-merge on `level` →
**named count columns filled to 0; rates left NULL** → `zfig = z[cols].round(3)`.

**Rounding is applied once, in `zfig`.** `z` is unrounded — this is what makes AP-9's BB/K exact
(see `05` D4).

## Column-level lineage (extract)

| KPI | Source columns | Transformation |
|---|---|---|
| wOBA | `events`, wOBA constants | per-row seasonal weight; den = AB + uBB + SF + HBP; **IBB excluded** |
| `swing_rate` | `description` | `isin(SWINGS)` ÷ row count |
| `srfp` | `description`, `pitch_number` | AP-2 on `pitch_number == 1` |
| `chase_rate` | `description`, `zone` | `(zone>9 & isin(SWINGS))` ÷ `(zone>9)` |
| `ooz_whiff_rate` | `description`, `zone` | `(zone>9 & SWINGS & WHIFFS)` ÷ `(zone>9 & SWINGS)` |
| `fpsr` | `type`, `pitch_number` | `(n − n[type=='B'])` ÷ n over `pitch_number==1` |
| `hard_hit_rate` | `launch_speed`, `type` | `(≥95 & type=='X')` ÷ `type=='X'` |
| `barrel_rate` | `launch_speed_angle`, `type` | `(lsa==6)` ÷ BIP |
| `ev90` | `launch_speed`, `type` | 0.90 quantile over BIP; **NULL below 40 BIP** |
| `bb_per_k` | `events` | BB count ÷ K count; **NULL when K==0** |
| `max_bb_run` | `events` ordered by date/game/AB | longest BB run between K |
| `cum_woba` | `events`, constants | cumulative num ÷ den by season, ordered |
