# Layer 3 — Technical Lineage (column-level)
### UC-PPS-021 · source physical column → transformation → KPI → receipt

Traces each KPI from its physical source columns through the vendored helper to the published receipt. Helpers are byte-identical to the UC8→UC11→UC15 locked line (copied into `dp_uc25_nola_vs_dodgers.py`).

| KPI (target) | Source physical column(s) | Domain | Transformation | Helper → receipt |
|---|---|---|---|---|
| `woba` | `events` + `wBB…wHR` | At-Bat Outcomes, wOBA Weights | Σ(weighted events)/PA; weights merged on `game_year` | `nresults` → season_trend, by_stand, dodgers_h2h |
| `krate/bbrate/hr_rate` | `events` | At-Bat Outcomes | K/BB/HR ÷ PA | `nresults` → season_trend |
| `whiff_rate` | `description` | Pitch Outcomes | whiffs ÷ swings | `whiff_rate` → arsenal |
| `chase_rate` | `description`,`zone` | Pitch Outcomes, Strike Zone | O-swings ÷ (`zone>9`) | `chase_rate` → process_abs_by_year |
| `putaway_rate` | `strikes`,`events` | Strike Zone, At-Bat Outcomes | K ÷ pitches@2strk | `putaway_rate` → process_by_stand |
| `first_pitch_strike_rate` | `pitch_number`,`type` | Pitch Outcomes | (1st − called-ball 1st) ÷ 1st | `fpsr` → process_by_stand |
| `hard_hit_rate` | `launch_speed`,`type` | Batted Ball Profile | EV≥95 & X ÷ BIP | `hard_hit_rate` → contact_quality |
| `edge_rate` | `plate_x/z`,`sz_top/bot` | Strike Zone | dist-to-zone ≤ 0.245 ft ÷ located | `edge_rate` (UC8) → process_abs_by_year |
| `ooz_called_strike_rate` | `zone`,`description` | Strike Zone, Pitch Outcomes | OOZ called-K ÷ OOZ | `ooz_called_strike_rate` (UC8) → process_abs_by_year |
| `air_rate/gb_rate` | `bb_type`,`type` | Batted Ball Profile | air/ground ÷ BIP | `air_gb_rate` (UC8) → contact_quality |
| `chase_up_rate` | `plate_z`,`sz_top`,`description` | Strike Zone | above-zone swings ÷ above-zone | `chase_up_rate` (UC8 helper) → process_abs_by_year |
| **`xwobacon`** | `estimated_woba_using_speedangle`,`type` | Batted Ball Profile | mean on `type=='X'` | `xwobacon` (report-local) → contact_quality, by_stand, h2h |
| `ip_computed` | `events` | At-Bat Outcomes | Σ EVENT_OUTS ÷ 3 | `ip_from_events` → recency_game_lines |
| H2H per hitter | `des` (→ id), `events`, `stand` | At-Bat Outcomes | des-parse modal name → id → per-id `nresults`/`xwobacon` | → dodgers_h2h |

### xwOBAcon lineage note (the DQ fix)
`estimated_woba_using_speedangle` is populated on balls in play. The **locked** `get_stats.xwoba` averages it over *all* pitch rows (a minority of non-BIP rows carry 0.0), contaminating the mean. This UC introduces `xwobacon` = the same field averaged over `type=='X'` only — the fit-for-purpose contact-quality read. **Lineage anchor / OPEN ITEM (O1):** promote `xwobacon` to the glossary and deprecate the pitch-level column for xwOBAcon reporting repo-wide.

**Reproducibility:** every figure and table regenerates by running `dp_uc25_nola_vs_dodgers.py` against the parquet cache (no network). Vendored helpers are byte-identical to the locked line. *Freshness caveat:* the pre-game receipts were built on the 7/16 cache; re-running against the post-7/22 cache will include the 7/22 start (see `08_post_game_backtest.md` and O4).
