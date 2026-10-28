# Technical feasibility brief: can the client's Python drive the animation?
**UC #58 · `uc-pos-023` · `dp_uc58` · 2026-10-27 · data-architect + data-engineer + kpi-calculator, reviewed by data-quality-engineer**
Scope (from intake): we assess **the client's reference Python** in `Schwarber_2026_Home_Runs.md` as the engine behind the Claude Design animation. That means pandas data prep plus plotly-express sketches for every scene. Claude Design's own rendering is out of scope, except where the handoff depends on it.

## Verdict
**As a data engine: fit after six fixes. As the animation renderer: not fit, and it shouldn't be.**
- The code gets the *shape* of every scene right.
- It has two defects that would put wrong pictures on screen:
  - **CP-1:** the x-axis counts pitches, not PA.
  - **DH-1:** on doubleheader days the games run in the wrong order.
- It has four defects that would put wrong or missing labels on screen: WP-1, SP-2, PM-size and SRC-D.
- All six are fixed in `dp_uc58_kernel.py` / `dp_uc58_build.py`, by import from the house kernels wherever a governed answer already existed.
- The plotly-express calls produce static faceted figures with no time axis, no transitions and no clip-cut points. The right split:
  - **Python produces the governed data**: `out/dp_uc58_design_data.json`, embedded in the prompt.
  - **Claude Design produces the motion.**

## Cell-by-cell assessment
| # | Client cell | What it does | Verdict | Fix (where) |
|---|---|---|---|---|
| 1 | `pd.read_csv("c:\\Users\\kshort4\\Downloads\\ks26.csv")` ×3, `concat` | Loads three ad-hoc CSV pulls | **Not portable.** Another machine's paths; no entity lock; no de-dup | `load_career()`: house log 2022–26 + `opponents/schwarber.parquet` 2015–21, locked by MLBAM 656941, `PITCH_KEY` de-dup asserted |
| 1b | `concat([ks26, ks_pos, ks_nphl])` | Stacks 2026 on "Phillies Tenure" | **SRC-D risk.** If `ks_pos` holds 2026, every 2026 pitch is doubled and the 2026 line doubles. Can't be graded without the CSVs | De-dup on `PITCH_KEY` (0 duplicates in the governed frame) |
| 2 | `np.select` pitch_group | Fastballs / Offspeed / Breaking / Other | **Correct.** Identical to the house client map (CPG-1). Differs from the house `PITCH_GROUP` only on KN; 0 of 45 HRs affected | Inherited verbatim (`K57.client_pitch_group`) |
| 3 | `hrs['cumulative_hrs'] = cumcount()+1`, merge back on (year, date, game, at-bat), `ffill` | Running HR count | **Works, but CP-2:** the merge tags every pitch of the HR at-bat, so the step rises on the PA's first pitch. 307 of 385 steps sit on a non-HR pitch | PA grain fixes it (row 4) |
| 4 | `zfig['cumulative_pa'] = groupby('game_year').cumcount()+1` over pitch rows | x-axis | **CP-1, fatal for the animation.** It counts pitches: 2026 ends at **3,026** "PA" vs **701** PA. Seasons stretch 4.1–5.6× by their own P/PA, so the lines don't compare like for like | `cumulative_metric.cumulative_frame(df, 'hr')` (house engine, one row per PA, endpoint `reconcile=` asserted vs an independent HR count) |
| 5 | sort `['game_year','game_date','game_pk','at_bat_number']` | Chronology | **DH-1 (found in this build):** game_pk order ≠ game order on doubleheader days. On 4/30 game 823472 was Game 1 (MLB.com: the 350th career HR off Logan Webb), but it sorts second, so HRs #10 and #11 swap and the "max EV" stop lands 5 PA late. The house `cumulative_metric` has the same sort | `game_seq()`: sv_id (2015–16) → the `des` HR counter on DH days with a HR in every game (2023-07-15, 2026-04-30) → game_pk fallback (22 DH days; totals unaffected; a step can sit at most one game's PAs off). DQ-13 asserts `season_hr_no` == the `des` counter for all 45 |
| 6 | `px.line(..., color='Season', facet_col='src', template='plotly_dark')` | Cumulative chart | **Wrong form for the storyboard.** Three facets vs one overlaid field; 12 cycled categorical hues vs three era colors; no step shape | Keyframes K1–K4 (`line_shape='hv'`, era tokens); the motion spec is in the prompt §3–§4 |
| 7 | `hrs.groupby('game_year').agg(home_runs=('des','size'))` | Season table | **Correct.** Reconciles: 385 career regular-season HR = Wikipedia through 9/15 + 0 after | `season_table.csv` with min-rank ties (2019 = 2024 = 5th) |
| 8 | Spray `px.scatter(x='loc_x', y='loc_y')` (commented out) | Spray chart | **Blocked as written:** `loc_x/loc_y` don't exist in the pull ("I really need my loc_x and loc_y columns") | DR-1 `derive_loc` (house hc → ft, cbp-spray convention); **SP-1** radius = `hit_distance_sc`, validated against hc radius (median ratio 1.010, p10–p90 0.996–1.016); convention check (LHB ground balls median `loc_x` +70.8 ft) |
| 8b | — | 2 HRs without `hc_x/hc_y` | **SP-2:** one of them is the max-distance HR (4/3 Coors, 460 ft); the other is 9/5 vs ATL (435 ft). "45 dots" fails silently | Bearing from the `des` field name (both "right field" → +36°), hollow marker, footnote |
| 9 | `agg(max_ev, mu_ev, max_dist, mu_dist)` + barrels merge, `Barrels/HR` | Thump table | **Correct** (`(level, df)` adapted). `Barrels/HR` is a different KPI from barrel rate | **HB-1** HR barrel share, named; house `barrel_rate_g` (per BIP) shipped beside it |
| 10 | Pitch map `px.scatter(size='release_speed')` + `add_shape(rect, x ±0.83, sz mean)` | Pitch maps | **Zone correct** (house 0.83 ft half-width; mean `sz_top/sz_bot` fine for drawing). **`size='release_speed'` misleads:** marker area encodes velocity the viewer can't read | PM-1: balls drawn as circles of 2.9 in (0.242 ft), true scale |
| 11 | `df.sort_values('delta_home_win_exp', ascending=False)` | Max WPA | **WP-1:** dHWE is home-team perspective; road HRs sort to the bottom. The 6/28 HR at Citi Field (+.371, 2nd of the year) ranks **45th of 45** on raw dHWE. The client caught it by eye | `wp1()` (mirror of the dp_uc51 pitching rule) |
| 12 | `ks26[(events=='home_run') & (game_type != 'R')]` | Playoff HR | **Includes spring** (3/22 at NYY, SPR-1) alongside the WC HR | `hr_non_regular_2026.csv` tags each (`spring_excluded`, `postseason_wc_postscript`) |
| 13 | `df = …` reassigned in 8 places, `z` in 5 | Notebook state | **Order-dependent.** Re-running one cell alone uses the wrong `df` | Single build script; deterministic; no shared mutable names |

## What the numbers say about the client's notes (graded in `out/dp_uc58_hp_grades.csv`)
- **13 SUPPORTED**, counting HP-15 (SUPPORTED WITH CONDITION) with them.
- **HP-08 PARTLY:** the max-EV HR was the 1st inning of DH Game 1, not the 9th.
- **HP-06 NOT SUPPORTED** on the pre-registered count leg: 2 HR on lefty breaking balls is not the tenure low (2023: 1), though it is down from 7 in 2025.

## Feasibility of the handoff itself
| Risk | Likelihood | Mitigation |
|---|---|---|
| Claude Design can't export MP4 | unknown, confirm | Prompt §0 asks for per-segment MP4 or a fixed 1920×1080 stage with a segment selector. Fallback: capture the page at 30 fps with the pre-installed Playwright (`page.screenshot` per frame, or `recordVideo`), then `ffmpeg -framerate 30 -i f%05d.png -c:v libx264 -preset veryfast -pix_fmt yuv420p seg.mp4`. The repo's `Concat MP4s in Folder.ipynb` joins the segments and clips |
| Model drifts a number | medium | Every on-screen string is templated from receipts (`dp_uc58_build_prompt.py`); §6 self-check; `dp_uc58_verification.py` re-derives the prompt's numbers |
| Clip/segment mismatch | low | 16 segments ↔ 15 clips mapped in prompt §5; clip list in `resolve_play_ids.py` schema, ordered by scene so `download_clips.py` file names sort in edit order |
| `play_id` unresolved | certain here (StatsAPI outside the cloud allowlist) | Run locally: `python resolve_play_ids.py out\dp_uc58_clip_list.csv` → `python download_clips.py out\dp_uc58_clip_list_resolved.csv` |
| Pitcher names | 8 of 15 clip rows named (carry-ins); 7 by id only | Prompt rule §1.8: name only when given |

## Tier B (not built): a Python animatic
Plotly can drive a timing animatic (`frames` at 10-PA steps × 12 traces ≈ 75 frames, `line_shape='hv'`). It is useful for checking pacing before Claude Design, but it is not a deliverable. Bid at ≈ +55k / +7 min.
