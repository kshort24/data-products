# 02 · Engineering Design
**data-architect · eda-agent · metadata-mapper · dashboard-specifier**

## 1 · Data model
Pitch grain throughout (`game_pk, at_bat_number, pitch_number`), regular season, subject locked by `batter == 624641 & phillies_role == 'batting'`. Derived grains, each built from the pitch frame by an inherited function:
| Frame | Grain | Built by |
|---|---|---|
| season panel | subject × season | `panel()` = inherited KPI functions + EV-1 + K46 pull-air + OZ-1 + BT-1 |
| hitter pool | batter × season, Phillies 2015–26, ≥50 PA (220 rows) | K54 `hitter_seasons` + EV-1/pull-air/OZ-1 |
| RHB pool | subset: stand R, 2022–26 (42 rows) | the client's scatter population |
| CM-1 cumulative | subject PA × season | K54 `cumulative_frame` (endpoints reconciled) |
| pitch groups | season × {95+ FB, <95 FB, breaking, offspeed} | K40 `PITCH_GROUP` + client velocity split (>94.9) |
| fielding games | season × position | Phillies fielding rows, `fielder_k == id` |

No joins across grains except left merges on the level keys (EN-2 asserted on the subject).

## 2 · EDA findings (eda-agent; full reports in `eda/dp_uc56/`)
- `subject_regular_season.md`: 4,223 rows; 81% null on `estimated_ba` and `hc_*` = non-BIP pitches (expected); no null `zone` on pitches with a type.
- `hitter_pool.md`: 220 hitter-seasons; bat-tracking columns null before 2024 (78% of rows), as designed.
- The 2026 platoon mix (138 LHP / 112 RHP PA, 55% vs LHP) is the single biggest usage confounder; every chapter that compares seasons notes it.
- BABIP .281 in 2026 is his lowest Phillies season; GB% 46.4% his highest.

## 3 · Metadata map (new physical outputs)
| Column | Meaning | Glossary |
|---|---|---|
| `ev50`, `ev90`, `ev_max`, `ev_mu`, `n_ev` | EV distribution on tracked BIP | EV-1 / GL-1 |
| `oz_pa`, `oz_ab`, `oz_hits`, `oz_xhits`, `oz_ba`, `oz_xba`, `oz_gap`, `oz_call` | OZ-1 | OZ-1 |
| `ooz_contact_rate` | 1 − K54 `ooz_whiff_rate` | inherited |
| `flag`, `baseline`, `v2026`, `delta`, `bar`, `flagged` | WA-1 decline flags | WA-1 |

## 4 · Dashboard spec (dashboard-specifier)
Eight chapters in the client's order: Bottom line → The 2026 line (F1, F2) → Uptick? (F3) → Over the hump? (F4) → Approach (F5, F7) → Velocity & breaking (F6) → Five seasons (F8) → Walkaway (F9) → Notebook graded. Scoreboard header with the 2026 line (xwOBA in red: the number that disagrees with the results). Chapter rail on wide screens; single column below 860 px; charts on white paper cards in both themes; plotly from the pinned CDN (MLB `CLAUDE.md`).
