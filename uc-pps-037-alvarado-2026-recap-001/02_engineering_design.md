# 02 · Engineering Design: `uc-pps-037`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dq-rule-definer` · `dashboard-specifier`

## 1 · Data model
**One pitch-grain frame, many groupbys.** CF-2d `career_frame_for` (CF-2c with the subject passed in) builds every regular-season MLB pitch for 621237, de-duplicated on `(pitcher, game_pk, at_bat_number, pitch_number)`:

| Precedence | Source | Why it ranks here |
|---|---|---|
| 1 PHI | `phils_*`, `phillies_role == 'pitching'` | house log, freshest; all tenure rows (asserted equal by year, DQ-09) |
| 2 FILE | `data/opponents/alvarado.parquet` | dedicated pull, TB 2017–20 |
| 3 NPHL_ID | other opponent files, rows with the id | completeness only |

The extras (release point, spin axis, `woba_value`/`woba_denom`, xSLG) are joined by pitch key (EN-2), with a fan-out assert. Postseason is a separate call and never enters a rate. **No cross-grain joins.** House context frames (leaderboard, pitcher × pitch, pitcher × pitch × season, RP seasons) are groupbys of the same house log.

**Environment decision.** Build, figures, dashboard, PDF and harness all ran on the laptop VM where the data lives (render stack pinned into `/tmp/pyrender`). The cloud sandbox did only render QA (Playwright screenshots, PDF rasterization) on staged copies.

## 2 · EDA findings that changed the build
EDA to file: `eda/dp_uc53/alvarado_2026_regular.md` (1,145 × 77) and `alvarado_tenure_regular.md` (5,322 × 77), MLB repo.

| # | Finding | Consequence |
|---|---|---|
| E-1 | xSLG null on 95.6% of tenure rows (not delivered for older Phillies seasons) | xSLG not used; xwOBA (XW-1) is the expected-contact measure |
| E-2 | 16 rows without `pitch_type` in 2026 (AB-1) | DQ-07 rule; thrown-pitch zone rate printed beside the house rate |
| E-3 | Velocity peaks in 2021–22 and falls in 2026, with a June→September fade | F6 + monthly table; D1/D2 signatures |
| E-4 | Cumulative module endpoint ≠ WB-1 (CM-D1) | CM-1a spec with reconcile assert |

## 3 · Metadata map (physical → CDE)
| Physical column | CDE / term | Status |
|---|---|---|
| `pitcher` | Pitcher (entity key) | exact |
| `player_name` | Pitcher name | **AMBIGUOUS** in batting-role rows (ENT-1). Display only |
| `phillies_role` | Phillies role (pitching / batting) | exact; required for the entity lock |
| `bat_score`, `post_bat_score` | Runs on watch inputs | exact (K48 `runs_created`) |
| `woba_value`, `woba_denom` | Statcast wOBA components (WB-1, CM-1a) | exact; `woba_value` present on some denom-0 PA ends (CM-D1) |
| `estimated_woba_using_speedangle` | xwOBA contact expectation (XW-1) | exact |
| `zone` | Strike-zone location | exact; null on AB-1 rows (counted in-zone by K44, D-7) |
| `description == automatic_ball/strike` | Automatic pitch (no pitch thrown) | **new term AB-1** |

## 4 · DQ rule design (handed to `05`)
13 rules across uniqueness, consistency, validity, timeliness, completeness and accuracy. Designed WARNs:
- DQ-08: zone null on AB-1 rows, disclosed.
- DQ-13: CM-D1 exposure, corrected in F9 and escalated.

## 5 · Dashboard specification
- **Structure:** hero (title, dek, 4 stat tiles, data-window box) → sticky chapter nav → 7 chapters → appendix (notebook graded, product forms) → footer with lineage.
- **Chapters:**
  1. Tenure (F1 + year table)
  2. 2026 vs his standard (F2)
  3. The cutter (F3–F5)
  4. The arm (F6 + monthly table)
  5. Command (F7)
  6. The ride (F8, F9)
  7. Move on or a blip? (F10 + ledger table + both cases + call)
- **Interactions:** hover on every mark; lazy draws (IntersectionObserver).
- **Theme:** house CSS tokens, light + dark under `prefers-color-scheme`, toggle (Match my system / Brand light / Notebook dark).
- **Packaging:** plotly via `phillies_dp.render.plotly_script_tag()` (jsDelivr pin, plotly.js 3.0.1); Artifact body variant written alongside.
- **Mobile:** single column below 820 px, checked at 390 px (F10's table is the phone reading path).
