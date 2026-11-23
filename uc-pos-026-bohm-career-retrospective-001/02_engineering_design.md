# 02 · Engineering Design
Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model (`data-architect`)
| Object | Grain | Built by | Notes |
|---|---|---|---|
| House log | pitch | `load_house` = K49 LP-1 with the K58 column set, all game types | anchor asserted; TP-1 applied; `pitch_group` from house `PITCH_GROUP` |
| Subject frame | pitch (game_pk, at_bat_number, pitch_number) | `subject` | batter == 664761, batting role, regular season; `win` (W-3), `era2`, `risp` |
| Season panel | subject × game_year | K60 `season_panel` + CR-1 + K46 + WB-1 + K48 | 7 rows asserted (SEA-1) |
| Window panel | subject × W-3 window | same functions on `win` | + breaking-ball and RISP sub-panels |
| Platoon / pitch-group cells | subject × (game_year or era2) × p_throws [× pitch_group] | `season_panel` | PA printed on every cell |
| Hitter pool (KP-1) | batter × game_year | K54 `hitter_seasons` (≥50 PA) | n = 220; G-LD uses its ≥200-PA subset (n = 122) |
| Game table | game | `game_table` | final runs for/against per regular-season game; 1,842 games, 0 ties |
| PA table | PA (all Phillies batters) | `pa_table` | start/end score, terminal event, RISP |
| GW-1 | win | `deciding_pa` | exactly one PA per win (asserted) |
| LD spray frame | BIP | `spray_frame_for(stand="R")` | PA-L1 coordinates, DR-1 direction; RHB convention asserted |

## 2 · Joins (`join-validator`)
- Season and window panels: one-to-one merges on the level; row counts asserted (SEA-1, W-3 = 3).
- `deciding_pa` ⋈ `game_table` on game_pk: 927 deciding PAs for 927 wins; assert one per win (GW-1 DQ rule). This is the fan-out test for the new object.
- Client cell (HP-01): pitch rows ⋈ wins on game_pk reproduces 63 = 63 career rows, 11 = 11 in 2026, with 0 non-terminal-pitch rows.
- Leaderboard: governed PA (K57 `pa_rows`, TP-1) ⋈ GW-1 counts ⋈ runs on watch ⋈ RISP splits on batter. The first draft joined PA *keys*, not governed PA (3,586 vs 3,575); caught at T1 and fixed.

## 3 · EDA (`eda-agent`)
`eda/dp_uc67/bohm_reg_2020_26.md` (house `eda.to_file`, never to context). Findings that shaped design:
- `hc_x`/`hc_y` present on every Bohm line drive (723 of 723), so the spray chart needs no fallback (SPR-1).
- Breaking-ball cells inside the after-the-audit window are thin (25 PA): F5 signature reported with its PA, never ranked.
- `truncated_pa` exists in the 2024–26 log (TP-1). Not visible in EDA as a problem until the harness counted PA independently.

## 4 · Metadata map (`metadata-mapper`)
| Published label | Physical source | Term |
|---|---|---|
| wOBA (house) | K57 `nresults_unrounded` (WB-2 seasonal weights) | locked |
| xwOBA, xwOBAcon | XW-1 `xwoba_pa`; K57 `cell_panel.xwobacon` | locked |
| Luck gap | WB-1 `woba_sc` − XW-1 `xwoba` | locked pair |
| K%, whiff, in-zone whiff, chase, hard-hit, barrel | K57 `cell_panel` / K60 `season_panel` | locked |
| LD / GB / FB share | CR-1 `battedball_profile` | locked (provisional since UC #36, used repeatedly) |
| Pull-air | K46 `pull_air` | locked |
| Runs on watch | K48 `runs_created` | locked, label scoped |
| BA / wOBA with RISP | K37 `risp_rows` semantics (terminal pitch) | inherited from the parent |
| GW-1, XC-1, G-LD, RS-1, TP-1 | `dp_uc67_kernel` Section C / B | new, provisional |

## 5 · Dashboard spec (`dashboard-specifier`)
- Masthead with status chips (READY-CONDITIONAL, DQ, harness, H-F call, LD-angle verdict, anchor).
- Four tiles: 2026 wOBA + KP-1 rank · after-the-audit wOBA move · deciding runs + rank · BA w/ RISP + RS-1.
- **Season inspector**: select 2020–26 → 12 KPIs incl. runs on watch, BA w/ RISP and deciding runs.
- Eight hash-routed tabs: The story · The 2026 finish · 2026 in his career · The line-drive question (**F4 spray chart, house outline, here**) · Righties and righty spin · Run creation and RISP (leaderboard + the 2026 GW-1 log) · The Phillies career, closed · Receipts.
- Eight plotly figures from receipt JSON, re-themed at render for dark mode; hover on every mark. Plotly from the pinned CDN, never inlined.
