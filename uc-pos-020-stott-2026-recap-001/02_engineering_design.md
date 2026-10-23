# 02 · Engineering Design
**data-architect · eda-agent · metadata-mapper · dashboard-specifier**

## 1 · Data model
| Frame | Grain | Population | Built by |
|---|---|---|---|
| `s` | pitch | Stott batting, regular season 2022-26 | `subject_rows` (id lock, EN-2 assert) |
| PA atoms | plate appearance | `pa_rows(s)`, chronological per season | `pa_atoms` (wOBA house / XW-1) |
| Era labels | pitch → PA | client eras (verbatim `np.select`), ER-1, ER-1x | `client_era`, `label_rows` (PA-exact) |
| Tracked swings | swing | BP-0: swings excluding bunts, `attack_angle` notna, bat speed ≥25 | K40a |
| Grounders | batted ball | regular-season ground balls, both halves of every Phillies game, bunts excluded, field-frame spray | `grounders` |
| Hitter pool | batter × season | Phillies hitter-seasons 2015-26, ≥50 PA (220) | K54 `hitter_seasons` |

All frames are single-grain. No joins fan out (the subject keys are asserted unique).

## 2 · EDA (to file, never to context)
`eda/dp_uc55/subject_2022_26.md`, `io1_opportunities.md`, `stott_tracked_swings.md` via `phillies_dp.eda.to_file`.

Findings that shaped the design:
- Per-PA wOBA has SD ≈ 0.5. At about 600 PA a season, two-era differences under ~.08 are hard to detect (this is why the ER-1 power receipt exists).
- Contact depth is the bat-path column with the clearest movement 2025 → 2026.
- 2B sector grounders cluster at +10° to +36° and 3B at −50° to −26° (field frame).

## 3 · Metadata map (metadata-mapper)
| Physical column | Business name | Rule |
|---|---|---|
| `attack_direction` | swing direction | flipped to pull + for display (O-15); raw sign kept in receipts |
| `intercept_ball_minus_batter_pos_y_inches` | contact depth | inches in front of centre of mass (C2) |
| `intercept_ball_minus_batter_pos_x_inches` | contact side | lateral (C1); not published |
| `swing_path_tilt` | tilt | not compared year over year (O-16) |
| `fielder_4` / `fielder_5` | 2B / 3B on the field | fielding team's player on both halves (A-1 relies on this) |
| `hit_location` | fielded by | method check only (UC5 precedent) |

## 4 · Dashboard spec (dashboard-specifier)
Seven chapters, keyed to the client's questions:
1. The 2026 line (Q1, Q7)
2. Timeframes (Q2)
3. The A/B test (Q3)
4. All fields / LD vs FB / bat path (Q4, Q5)
5. Platoon, pitch types, velocity (Q6)
6. Defense and thump (Q8)
7. Notebook graded + three things for 2027

Plus a products appendix.

Tiles: slash line · xwOBA (five-year climb) · chase rate (the lever) · 2B IO-1.

House shell carried from UC54 (theme toggle, dark remap, sticky chapter rail, CDN-pinned plotly).
