# Layer 2 — Data Architect Blueprint + KPI Calculator Specs
### UC-PPS-021

## A. Architecture — output model

**Pattern:** single-source analytical product. One canonical input frame (the entity-locked Nola career log) sliced into named grains, each aggregated so every cell is comparable to the career/season baseline. No cross-domain fact joins; the only merge is season wOBA weights (1:many on `game_year`).

```
phils_2015..2026.parquet
   └─ filter role=pitching, pitcher==605400, game_type==R, dedup(game_pk,ab,pitch)
        └─ merge wOBA constants on game_year  (many:1, no fan-out)
             ├─ nresults(game_year) ⊕ xwobacon(game_year) ─────► season_trend
             ├─ nresults(stand)[2026] ⊕ fpsr/putaway/whiff/chase/hard_hit/air ─► by_stand + process_by_stand
             ├─ groupby(stand,pitch_name)+whiff [2026] ─────────► arsenal
             ├─ game_lines(all 2026 starts) ───────────────────► recency_game_lines + recency_split
             ├─ usage/velo by month [2026] ────────────────────► monthly_usage / monthly_velo
             ├─ fpsr/chase/putaway/edge/ooz-CS/chase-up by year ► process_abs_by_year
             ├─ air_gb ⊕ hard_hit ⊕ xwobacon by year ──────────► contact_quality_by_year
             └─ des-parse name map × 7 named hitters ──────────► dodgers_h2h
```

**Join strategy:** all KPI helpers aggregate to their grain *before* any merge, so merges are key-unique. The H2H path resolves batter ids by **des-parse** (modal name per batter id) then filters the career log per id — no external id table, no fan-out. Validated in `05`.

## B. KPI Calculator — specs (locked functions inherited verbatim)

| KPI | Input grain | Output grain | Formula (abstract) | Null/edge | Provenance |
|---|---|---|---|---|---|
| woba | pitch | level | `Σ weighted events / PA` | season weights load-applied | locked (UC8→15) |
| krate/bbrate/hr_rate | pitch | level | K/BB/HR ÷ PA | — | locked |
| whiff_rate | swing | level | whiffs ÷ swings | null if 0 swings | locked |
| chase_rate | O-zone pitch | level | O-swings ÷ (`zone>9`) | — | locked |
| putaway_rate | 2-strike pitch | level | K ÷ pitches@2strk | null if none | locked |
| first_pitch_strike_rate | 1st pitch | level | (1st − called-ball 1st) ÷ 1st | — | locked (`fpsr`) |
| hard_hit_rate | BIP | level | EV≥95 ÷ BIP | null if 0 BIP | locked |
| edge_rate | located pitch | level | edge-band ÷ located | drops null-loc | **UC8 (approved)** |
| ooz_called_strike_rate | O-zone pitch | level | OOZ called-K ÷ OOZ | — | **UC8 (approved)** |
| air_rate/gb_rate | BIP | level | air/ground ÷ BIP (`bb_type`) | null if 0 BIP | **UC8 (approved)** |
| chase_up_rate | above-zone pitch | level | swings ÷ (`plate_z>sz_top`) | — | UC8 helper |
| **xwobacon** | BIP | level | mean `estimated_woba` on `type=='X'` | null if 0 BIP | **report-local (DQ-hardened)** |
| ip_computed | terminal event | game | Σ EVENT_OUTS ÷ 3 | baserunning outs uncredited | report-local |

**KPI Calculator verdict:** all locked functions copied **verbatim** from `dp_uc15_nola_vs_royals.py` (byte-identical); the UC8 trio copied verbatim with its constants (`PLATE_HALF=0.83`, `BALL_FT=2.94/12`, `TAKES`). Values plausible and internally consistent (2026 wOBA .358 with xwOBAcon .384; L/R contact quality within .005). The only non-locked rate, `xwobacon`, was hardened this session (BIP-only mean) after the pitch-level column was found contaminated.

## C. Semantic layer (consumption rules)

- Rates are **non-additive across grains** — never average `whiff_rate` across pitch rows; re-aggregate from pitch grain.
- `woba` (FanGraphs-weighted) is the governed line; it sits ~.01 below the Statcast `woba_value/denom` figure — do not mix the two in one comparison.
- `xwobacon` is xwOBA **on contact only** — compare it to other contact-quality reads, not to full wOBA (which includes BB/K).
- All H2H is **career and directional** below ~40 PA; the PA column is the error bar and must be shown.
