# 02 · Engineering Design: `uc-pps-036`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dq-rule-definer` · `dashboard-specifier`

## 1 · Data model
**One pitch-grain frame, many groupbys.** CF-2c `career_frame_ext` = CF-2b (`dp_uc51_kernel.career_frame_mlb`: regular season, MLB games only, the subject's own name) plus EN-2. EN-2 joins `EXTRA_COLS` (release_pos_x/z, spin_axis, arm_angle, xSLG, hit distance, launch_speed_angle, woba_value, woba_denom) by `(pitcher, game_pk, at_bat_number, pitch_number)`, from the house log first and the subject's own file second. It asserts there is no fan-out.

| Precedence | Source | Why it ranks here |
|---|---|---|
| 1 PHI | `phils_*`, pitching role | house log, freshest (2025 Sept, 2026) |
| 2 FILE | `data/opponents/mayza.parquet` | dedicated pull (2017–25) |
| 3 NPHL_ID | other opponent files, rows with the id | completeness only; all dropped as duplicates |
| 4 VS_PHI | `phils_*`, batting role | dropped as duplicates |

House populations come from the same LP-1 loader (`load_phils_cols`, regular season, pitching role) with the extra columns. Postseason is a separate call. **No cross-grain joins.**

**Environment decision.** Build, figures, dashboard, PDF and harness all ran on the laptop VM where the data lives. `/sessions` was 100% full, so `requirements-render.txt` was installed with `pip --target /tmp/pyrender`, the UC49 pattern. Cloud was used only to view staged PNG/PDF and for the headless dashboard screenshots.

## 2 · EDA findings that changed the build
EDA went to file: `phillies_dp.eda.to_file(s26, "mayza_2026_regular", "dp_uc52")` → `eda/dp_uc52/mayza_2026_regular.md` (1,093 × 74; 30 columns with nulls; xBA/xSLG/bb_type 83% null = non-BIP rows).

| # | Finding | Consequence |
|---|---|---|
| E-1 | CF-2's projection lacks release point, spin axis, launch_speed_angle and woba_value/denom (the build failed twice) | EN-2 enrichment (CF-2c) |
| E-2 | Career 2017 (340 pitches) and 2025 (301) are short | Flagged "small seasons" on F1 and in caveats |
| E-3 | Arm angle exists only from 2025 (76% coverage in 2026) | Arm angle quoted, not used in DS-1 |
| E-4 | Mayza's SL is Statcast-tagged SL (no ST) | BS-1 population = SL only |
| E-5 | House wOBA ≠ Statcast-basis wOBA by .014 for 2026 | WB-1 companion; two bases labelled |

## 3 · Metadata map (physical → CDE)
| Physical column | CDE / term | Status |
|---|---|---|
| `pitcher` | Pitcher (entity key) | exact |
| `player_name` | Pitcher name | **AMBIGUOUS** in batter-keyed pulls. Display only |
| `release_pos_x` / `release_pos_z` | Release side / height (ft, catcher view) | exact |
| `release_extension` | Extension (ft) | exact |
| `pfx_x` / `pfx_z` (×12) | Horizontal break / induced vertical break (in) | exact |
| `spin_axis` | Spin axis (deg) | exact; display only |
| `launch_speed_angle` (== 6) | Barrel | exact (BR-1) |
| `woba_value` / `woba_denom` | Statcast-basis wOBA (WB-1) | exact; **not** house wOBA |
| `strikes` | Count **before** the pitch | exact. The client read it as post-pitch (DEF-1) |

## 4 · DQ rule design (handed to `05`)
12 rules across uniqueness, validity, completeness, consistency and timeliness. No designed WARNs.

## 5 · Dashboard specification
- **Structure:** hero (title, dek, theme bar) → sticky chapter nav → 4 stat tiles → read-first box → bottom line → 8 chapters → appendix (notebook graded, five product forms) → footer with lineage.
- **Chapters:** 1 Results (F1 + LHP relief table) · 2 Contact (F2, F3) · 3 Platoon (F4 + split table) · 4 Stuff and delivery (F5, F6) · 5 Bullet slider (F7) · 6 Weapons (F8) · 7 Success Rate (F9) · 8 Comps (F10).
- **Interactions:** hover on every mark; lazy draws (IntersectionObserver); nav highlights the visible chapter.
- **Theme:** house CSS tokens, light + dark under `prefers-color-scheme`, toggle (Match my system / Brand light / Notebook dark); figure layouts re-themed in JS.
- **Packaging:** plotly via `phillies_dp.render.plotly_script_tag()` (jsdelivr plotly.js-dist-min@3.0.1); Artifact body variant written alongside.
- **Mobile:** single column below 820 px, checked at 390 px (no horizontal overflow).
