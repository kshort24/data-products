# 03 — Glossary Alignment & KPI Specs (business-glossary-agent + kpi-calculator) · uc-pps-020

## Ruling: NO NEW KPIs THIS UC
Every metric in the report resolves to a locked, previously ratified definition. No glossary term is created, redefined, or inferred. The velocity trace is a Statcast native measurable (`release_speed`), reported as data, not as a governed KPI — same treatment as bat-speed measurables in uc-pos-004.

## Locked KPI inventory (inherited verbatim from dp_uc21, lineage dp_uc11 → dp_uc17 → dp_uc21)
| KPI | Function | Grain / population | Origin |
|---|---|---|---|
| wOBA / K% / BB% / HR-per-PA / BA / OBP / SLG / OPS | `get_stats` / `nresults` | PA-resolved events, per season(/split) | UC3→UC8→UC11 kernel |
| xwOBA proxy (contact) | mean `estimated_woba_using_speedangle` | BIP only — labeled everywhere | kernel convention |
| Whiff rate | `whiff_rate` (WHIFFS/SWINGS lists) | swings | kernel |
| Chase rate / in-zone rate | `chase_rate` (zone>9) | OOZ pitches / all pitches | kernel |
| Putaway rate | `putaway_rate` | 2-strike pitches | kernel |
| First-pitch strike rate | `fpsr` | pitch_number==1 | kernel |
| Hard-hit rate | `hard_hit_rate` (EV≥95) | BIP | kernel |
| CSW | `csw_rate` (called_strike + whiffs / pitches) | all pitches | uc-pps-017 PD set |
| IP (event-outs), RA9 (on-mound runs), FIP | `outs_and_runs`, `fip` + season cFIP | PA-final rows | uc-pps-017 PD set |
| TTO splits | `n_thruorder_pitcher` clip 3 | PA, 2025/2026 only | uc-pps-017 PD set |
| Count leverage (share of PA to 2 strikes; pitch share ahead) | inline, same formulas as dp_uc21 §10 | PA / pitch | uc-pps-019 |

## Window definition (this UC's only novel parameter — a filter, not a metric)
`first_half(year)` ≡ regular-season games with `game_date ≤ cutoff(year)`, cutoffs user-provided: 2021-07-11 / 2024-07-14 / 2025-07-13; 2026 = full cache (complete first half, ASG 2026-07-14). Recorded here so the season-end refresh can re-parameterize without re-derivation.

## Conflict / duplicate scan
No conflicts with prior pps glossary usage. "First half" as used here matches uc-pps-017/018/019 and uc-pos-004 (pre-ASG window). "RA9 not ERA" and "IP from event outs" caveats carried verbatim from those UCs — consistent house convention maintained.
