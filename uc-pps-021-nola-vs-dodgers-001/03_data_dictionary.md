# Layer 2 — Data Dictionary
### UC-PPS-021 · column & table descriptions for the published outputs

Standardized descriptions for every physical element the data product emits (the 14 CSV receipts in `out/`). Each output column links to its CDE / Business Term in `02_business_glossary_and_domains.md`. Figures (6 PNG) each trace to one of these tables.

## Output tables (receipts)

| Table (`out/dp_uc25_*.csv`) | Grain (one row =) | Purpose | Figure |
|---|---|---|---|
| `nola_season_trend` | season (2015–2026) | wOBA/xwOBAcon/K/BB/HR/SLG trend | — |
| `nola_by_stand_2026` | batter side (L/R) | 2026 platoon results | — |
| `nola_arsenal_2026` | stand × pitch_name | usage/velo/spin/whiff by side | arsenal_map, usage_whiff |
| `recency_game_lines` | game (2026) | per-start line (ip_computed) | recency_approach |
| `recency_split` | segment (last-3 / prior / full) | recency vs season | — |
| `monthly_usage` | month × pitch | approach-shift usage tracks | recency_approach |
| `monthly_velo` | month × pitch | velo tracks (injury/fatigue rule-out) | — |
| `slider_arc` | start (since 6/13) | slider usage arc | — |
| `process_abs_by_year` | season | FPSR/chase/putaway/edge/OOZ-CS/chase-up | process_abs_panel |
| `contact_quality_by_year` | season | AIR/GB/hard-hit/HR/xwOBAcon | contact_quality |
| `process_by_stand_2026` | batter side | the lefty-leak indicators | process_abs_panel |
| `dodgers_h2h` | hitter (7 named) | career H2H vs Nola | dodgers_h2h_matrix |
| `dq_scorecard` | check | DQ results | — |
| `freshness_manifest` | source | window/rows/fitness | — |

## Column dictionary (shared KPI columns)

| Column | Type | Description | Range seen (2026) | Null rule |
|---|---|---|---|---|
| `woba` | float | wOBA-against (lower better) | .262–.377 (season) | never null at OK grain |
| `xwobacon` | float | xwOBA on contact (lower better) | .343–.400 (season) | null if 0 BIP in cell |
| `krate`,`bbrate`,`hr_rate` | float | K/BB/HR ÷ PA | K .238 / BB .075 / HR .051 | never null at OK grain |
| `slg` | float | SLG-against | .346–.509 | never null at OK grain |
| `first_pitch_strike_rate` | float | 1st-pitch strikes ÷ 1st pitches (higher better) | L .588 / R .735 | never null at OK grain |
| `putaway_rate` | float | K ÷ 2-strike pitches (higher better) | L .186 / R .231 | null if no 2-strike pitches |
| `whiff_rate` | float | whiffs ÷ swings (higher better) | .11–.43 by pitch | null if 0 swings |
| `chase_rate` | float | O-zone swings ÷ O-zone pitches | ~.33 | never null at OK grain |
| `edge_rate` | float | edge-band pitches ÷ located | .370 (2026) | never null |
| `ooz_called_strike_rate` | float | OOZ called strikes ÷ OOZ pitches | .034 (2026) | never null |
| `air_rate`,`gb_rate` | float | air / ground ÷ BIP | air .597 / gb .403 | null if 0 BIP |
| `hard_hit_rate` | float | EV≥95 ÷ BIP (lower better) | .396 (2026) | null if 0 BIP |
| `PA`,`H`,`HR`,`BB`,`K` (H2H) | int | per-hitter counting stats | 8–86 PA | never null |
| `stand_vs_nola` | str | L/R the hitter takes vs RHP Nola (switch→L) | L/R | never null |
| `ip_computed` | float | Σ terminal-event outs ÷ 3 (X.Y) | 4.1–7.0 | never null |

**Direction semantics:** for `first_pitch_strike_rate, putaway_rate, whiff_rate, chase_rate, edge_rate` higher is better; for `woba, xwobacon, slg, bbrate, hr_rate, hard_hit_rate, air_rate` lower is better. **Sample discipline:** every H2H row and small-sample cell prints its PA; only Freeman (86 PA) is treated as a real H2H sample, the rest as directional.
