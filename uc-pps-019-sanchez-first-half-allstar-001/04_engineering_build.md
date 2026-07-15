# 04 — Engineering Build
## uc-pps-019 · data-engineer + technical-lineage-builder

## Build record
- Script: `dp_uc21_sanchez_first_half.py` (this folder). Exit 0, first pass, 2026-07-14.
- Environment: sandbox mount of MLB repo; `MLB_DATA_ROOT` env var → portable to Kellen's machine via candidate paths (env → relative → absolute Windows).
- Kernel reuse: ~85% verbatim from dp_uc17 (loaders, locked KPIs, PD-set, figure scaffolds). New code limited to `qr_frame/qr_rate/qr_quality/scoreless_streak` (QR-1..3, SL-1) and QR panel wiring.

## Lineage (column-level, source → KPI)
| CDE / field | Source | Transform | Lands in |
|---|---|---|---|
| pitch log rows | `phils_2025/2026.parquet` | role=='pitching' ∧ pitcher==650911 ∧ game_type=='R' ∧ dedup(game_pk,at_bat_number,pitch_number) | all receipts |
| `events`, `description`, `zone`, `strikes`, `balls` | Statcast native | locked masks (SWINGS/WHIFFS, zone>9, strikes==2, pitch_number==1) | process KPIs, arsenal |
| `woba_*` weights | `wOBA and FIP Constants.csv` (FanGraphs) | season join on game_year | wOBA in all `nresults` outputs |
| `estimated_woba_using_speedangle` | Statcast native | mean over non-null | xwOBA everywhere |
| `bat_score`,`post_bat_score` | Statcast native | PA-final delta, clip ≥0 | runs-on-mound, RA9, SL-1 |
| `events` → outs | OUTS_MAP (dp_uc17) | event-map sum | IP, RA9, FIP, SL-1 |
| `pitch_number` (PA-final row) | Statcast native | ≤3 boolean on completed-PA population | **QR-1/QR-3** |
| `fielder_2` | Statcast native | id→name via batting-side modal name (no hand-keying) | battery split |
| `n_thruorder_pitcher` | Statcast native | clip(upper=3) | TTO |

## Receipts delivered (19 files → `<MLB repo>/out/`)
16 CSVs + 3 PNGs per the §E manifest in 02 — all new files, none overwritten. Figures also copied into this folder (`out_dp_uc21_fig*.png`) for report rendering.

## DQ scorecard summary (`out/dp_uc21_dq_scorecard.csv`)
entity_lock PASS · dedup PASS · game_type PASS · weights_join PASS · qr_population PASS (pitch_number non-null on all PA-final rows) · CDE completeness: core fields ≥0.99 non-null at pitch grain (xwOBA/launch fields null off-contact by design).
