# 02 · Engineering Design
Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model (`data-architect`)
| Object | Grain | Built by | Notes |
|---|---|---|---|
| Career frame | pitch (pitcher, game_pk, at_bat_number, pitch_number) | CF-2d `career_frame_for` (K53) with the subject passed in | regular season, MLB clubs only, EN-2 fan-out assert |
| House log | pitch | K53 `load_house` (LP-1, pitching role) | 2015–26, anchor asserted |
| Season table | subject × game_year | build T1.2 | K44/K48/K50/K51/K52 KPIs merged on `game_year` |
| Phillies pool (KP-1) | pitcher × game_year × p_throws | K52 `house_pitcher_seasons` + XW-1/WB-1 | ≥ 100 PA; 198 rows |
| Pitch-type pool | game_year × pitcher × pitch_type | K48 `arsenal_table` | ≥ 150 of the pitch (CX-1 floor) |
| Windows | early / market / tenure / y2024 / before_all / career | kernel `window_metrics` | pooled, not averaged |
| Game log | appearance | K49 `game_score` (GS-1) | 245 MLB appearances |
| Outs | PA | K51 `outs_by_pa` (OU-2) on the full Phillies defensive log | tenure only; OU-1 before 2023 (labelled) |

## 2 · Joins (`join-validator`)
- Season table: one-to-one merges on `game_year`; row count asserted at 12.
- OU-2 joins the subject's PAs out of the full defensive log; the first pitcher of the PA owns it. Sum reconciles to public IP exactly (DQ-06), which is the join test.
- Pool merges (XW-1, WB-1) on (pitcher, game_year, p_throws): 198 in, 198 out.

## 3 · EDA (`eda-agent`)
`eda/dp_uc62/career_frame.md` (house `eda.to_file`). Findings that shaped design:
- `estimated_woba_using_speedangle` present on every tracked BIP; XW-1 fallback 0 in every season (DQ-10).
- 2015 EV readings sit on BIP far more often than later years (16% non-BIP vs 39–46%): this decided HP-06.
- The four-seamer falls under 50 pitches in 2026, so F4/F5 show no 2026 four-seam dot.
- No automatic-pitch rows (AB-1) for this subject (DQ-11).

## 4 · Metadata map (`metadata-mapper`)
| Published label | Physical source | Term |
|---|---|---|
| wOBA (house) | K44 `nresults.woba` (FanGraphs weights, every PA) | locked |
| wOBA (Statcast) | WB-1 `woba_sc` | locked basis |
| xwOBA | XW-1 `xwoba` | locked |
| K%, BB% | K44 `krate`, `bbrate` (unintentional BB only, O-14) | locked |
| Whiff, chase, zone | K44 `whiff_rate`, `chase_rate`, `in_zone_rate`; K48 `arsenal_table` per pitch | locked |
| Hard-hit, barrel | K44 `hard_hit_rate`, K51 `barrel_rate` | locked |
| Runs on watch | K48 `runs_created` | locked |
| IP | OU-2 outs ÷ 3 | locked (UC51) |
| KR-1, CE-1, PR-1 | kernel Section C | new, provisional |

## 5 · Dashboard spec (`dashboard-specifier`)
- Masthead with status chips (READY-CONDITIONAL, DQ, harness, PR-1 call, anchor).
- Four summary tiles: batters faced + Phillies rank, wOBA before → tenure, worst-seasons rank, cost per inning.
- **Season inspector** (select a season → 14 KPIs + Phillies rank). Seasons ≥ 100 PA only.
- Eight hash-routed tabs: The story · What the Phillies got · What they bought · What broke · Luck, measured · What it cost · How it ended · Receipts.
- Nine plotly figures from receipt JSON, re-themed at render for dark mode; hover on every mark.
- Plotly from the pinned CDN (`phillies_dp.render.plotly_script_tag`), never inlined.
