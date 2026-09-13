# 02 · Engineering Design — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Engineering Design department
Agents: `data-architect`, `eda-agent`, `join-validator`, `metadata-mapper`, `dq-rule-definer`, `dashboard-specifier`

---

## Data model

Two frames, deliberately not joined to each other.

```
                         phils_2015..2026.parquet  (game_type == 'R')
                                      |
              +-----------------------+-----------------------+
              |                                               |
      SUBJECT FRAME                                   BENCHMARK FRAME
  phillies_role == 'pitching'                      p_throws == 'R', BOTH roles
  pitcher == 691725, game_year == 2026             all 12 seasons
  grain: one pitch                                 grain: one (game_year, pitcher, pitch_type)
  1,861 rows -> PRE 1,141 / POST 720               393,126 pitches -> 14..232 pitcher-seasons per type
              |                                               |
              +------------------> SG-1 <---------------------+
                       subject value vs population moments
                                     |
                             out/dp_uc44_grades.csv
```

Three supporting frames:

| Frame | Filter | Rows | Used for |
|---|---|---|---|
| Opponent hitters | `phillies_role=='pitching'`, 12 ATL `game_pk` | 1,660 | Atlanta lineup profile, `des`-parse identity |
| Opponent starter | `phillies_role=='batting'`, `pitcher==656550` | 260 | Holmes arsenal, **vs Philadelphia only** |
| AAA (supporting) | `lhvp26.parquet`, `pitcher==691725` | 396 | Context only. **No wOBA weights. Never blended** |

**Grain discipline.** The benchmark frame is a *pitcher-season*, not a pitcher. A 2019 Zack Wheeler and a 2024
Zack Wheeler are two population members, because the question the grade answers is "how does this pitch rank
among pitch-seasons a Phillies game has actually contained", not "among pitchers".

### Joins and the fan-out check (`join-validator`)

There is exactly one merge in the published path — the benchmark population's own `groupby().agg()`, which
cannot fan out by construction. Verified anyway:

- `benchmark_population('FF')` → 232 rows, **0 duplicate (game_year, pitcher)** pairs. Asserted in verification family C.
- Subject-to-population is a comparison, not a join: the subject value is a scalar, the population a vector.
- The Atlanta lineup table is a `groupby('batter')` over one frame — no cross-frame merge, so no opportunity
  for the union fan-out that bit `uc-pos-007`.
- `mix_by_stand` n sums to the window's per-stand pitch count for all six (window × stand) combinations.
  Asserted.

**Where a fan-out *would* have happened and was designed out:** the obvious construction of the head-to-head
table is to merge Painter's rows onto the Atlanta lineup table on `batter`. That produces a row per
(hitter × pitch) and silently multiplies every lineup-level rate. The build instead computes both tables
independently at their own grain and joins them **in the renderer**, never in the data.

## EDA findings that shaped the build (`eda-agent`)

| # | Finding | Consequence |
|---|---|---|
| E-1 | The post-option arsenal contains a pitch type (`CH`, 160 pitches, 22.2%) that has **zero** occurrences pre-option; `FS` (164 pitches, 14.4% pre-option) has **zero** occurrences post-option | Forced AR-1 into existence. Forced the grading-window decision |
| E-2 | `CH` and `FS` differ by +3.1 mph, −3.1" IVB, −3.0" HB — far outside within-pitch season drift | The two are not the same pitch retagged. Stated as a shape finding, then controlled for separately (E-3) |
| E-3 | League splitter share across all pitchers in the Phillies log: 4.14% (June) → 5.39% (September), 6 arms throwing 165 in September | **The classifier did not move.** AR-1 readings now require this control by standing rule |
| E-4 | `estimated_woba_using_speedangle` is populated on **every** PA-ending row (strikeouts = 0.000, walks = 0.698) and null elsewhere | The field is true **xwOBA at PA grain**, not xwOBAcon. Both are computed and reported separately with their own n, so the `uc-pps-021` xwOBAcon confusion cannot recur |
| E-5 | Four-seam in-zone rate fell .474 → .422 **while** first-pitch-strike rate rose .612 → .638 and three-ball-count rate fell .096 → .065 | The four-seam zone drop is not a control problem. Forced the elevation-rate metric into the build to distinguish design from wildness |
| E-6 | Above-zone four-seam rate .349 vs a population mean of .200 (sd .076) | Confirmed E-5. Elevation grade 70 |
| E-7 | Post-option whiff by handedness: .322 RHH / .238 LHH, against a pre-option .237 / .215 | The platoon gap opened after the arsenal changed. Mechanism and observation agree, which is why a p = 0.075 result is published as a lean |
| E-8 | Sweeper to LHH: 62 pitches, 64.5% in the zone, 20.0% whiff, .523 xwOBA on 9 tracked PA | The single actionable cell in the package. Too small to grade, large enough to name |

## Design change forced by EDA

**Original design:** grade the full 2026 season for sample size; use the client's 2026-07-21 cut as the
trend split, since that is what his notebook does.

**Change:** grade the **post-option window only**, split at 2026-07-31.

**Why:** E-1 shows the two windows contain arsenals that differ in 37% of their pitches. A full-season grade
would blend a splitter he does not throw with a changeup he does, and would report a four-seam whiff rate
(.148) that is the average of two different pitch designs. The client's 07-21 cut lands between his last
pre-option start (06-17) and his first post-option start (07-31), so **it partitions the season identically**
— his numbers reproduce exactly — but the roster date is the one with a causal story attached, and a window
boundary should name its cause.

**Cost, stated:** 185 PA instead of 484. Every grade in the package carries that sample. The by-stand cells
are consequently ungradeable and ship as denominatored rates.

## Metadata mapping (`metadata-mapper`)

| Physical column | CDE / business term | Mapping | Note |
|---|---|---|---|
| `pitcher` | Pitcher (MLBAM id) | Exact | The entity key. Never `player_name` |
| `batter` | Batter (MLBAM id) | Exact | Display name is a `des` parse, not a key |
| `pitch_type` / `pitch_name` | Pitch Type | Exact | Classifier output, not a pitcher declaration — see AR-1 caveat |
| `release_speed` | Velocity | Exact | |
| `pfx_z` × 12 | Induced Vertical Break ("ride") | Derived | Gravity-corrected, inches |
| `pfx_x` × 12 | Horizontal Break ("run"/"sweep") | Derived | Negative = third-base side = arm-side for a RHP |
| `plate_x`, `plate_z` | Location at the plate | Exact | Catcher's view |
| `zone` ≤ 9 | In Zone | Derived | Preferred over `chase_rate`'s in-zone arithmetic (defect D-7/O-13) |
| `sz_top`, `sz_bot` | Strike-zone boundary | Exact | Subject's own means, not league constants |
| `description` ∈ SWINGS / WHIFFS | Swing / Whiff | Exact | Lists inherited verbatim |
| `estimated_woba_using_speedangle` | xwOBA | Exact | **PA grain** (E-4) |
| …restricted to type `X` | xwOBAcon | Derived | Reported separately, never as "xwOBA" |
| `launch_speed` ≥ 95 & type `X` | Hard-Hit | Derived | Denominator is *tracked* BIP (defect O-8) |
| `events` ∈ K / BB / HR sets | At-bat outcome | Exact | via inherited `get_stats` |
| `des` | Play description | Exact | Free text; used only for batter-name resolution |
| `game_type == 'R'` | Regular season | Exact | |
| `phillies_role` | Frame side | Exact | Repo-local, not a Statcast field |
| `arm_angle` | Arm slot | **Unmapped — descoped** | 54% null (DQ-6 FAIL) |
| `attack_angle`, `swing_path_tilt`, `bat_speed` | Bat-tracking CDEs | **Unmapped — out of scope** | Hitter-side fields; 51% null; no KPI in this UC needs them |

## DQ rules specified (`dq-rule-definer`; implemented and scored in `05`)

| Rule | Dimension | Threshold |
|---|---|---|
| DQ-1 | Uniqueness | Zero duplicate `(game_pk, at_bat_number, pitch_number)` in the subject frame |
| DQ-2 | Validity | Entity lock is an MLBAM id resolving to exactly one `player_name` |
| DQ-3 | Validity | `game_type == 'R'` only |
| DQ-4 | Completeness | `plate_x/z`, `zone`, `release_speed`, `pfx_x/z` 100% populated in the graded window |
| DQ-5 | Completeness | `release_extension` populated; nulls excluded, never imputed |
| DQ-6 | Completeness | `arm_angle` populated — **FAIL threshold 50%** |
| DQ-7 | Completeness | xwOBA populated on every PA-ending row (≤2 exceptions) |
| DQ-8 | Consistency | xwOBA on strikeouts == 0 and on walks > 0.6 — proves the field's grain |
| DQ-9 | Accuracy | Every benchmark population meets the 25-pitcher-season minimum or is stamped THIN |
| DQ-10 | Validity | No grade published below the subject pitch (50) or swing (25) floor |
| DQ-11 | Accuracy | z-derived and rank-derived grades agree within 10 points |
| DQ-12 | Timeliness | Log current through the anchor; target is D+1 |
| DQ-13 | Validity | Opponent starter id confirmed externally, not inferred |
| DQ-14 | Consistency | AAA rows carry no wOBA weights and enter no MLB rate |

## Dashboard specification (`dashboard-specifier`)

**Decision the dashboard serves:** "what do I throw this hitter, and does that change by side?" — a question a
static card answers once and a coach asks six times.

| Control | Values | Why it exists |
|---|---|---|
| Window | Pre-Option / Post-Option / Full 2026 | The whole finding is that these differ. A card that cannot show the difference cannot carry the finding |
| Side | Both / vs LHH / vs RHH | The client asked for maps by stand; the leak only appears when you isolate one |
| Pitch type | Six toggles, colour-coded to the house palette | The sweeper-to-lefties cell is invisible under six overlapping pitch clouds |

**Views:** live SVG pitch maps with usage-scaled centroids and hover counts; the grade rail; four receipt
tables (start log, Atlanta lineup, notecard reconciliation, DQ scorecard).

**Stated failure mode, designed around:** selecting a single side makes every cell too small to grade. The
card does **not** silently recompute grades on 62 pitches. It blanks the grade columns and says so in the note
under the rail. A dashboard that quietly regrades on a filtered subset is the most likely way this KPI family
gets misused, and the control is a design constraint rather than a warning.

**Constraints:** self-contained, no CDN, no external fetch (asserted in verification family G). Data embedded
as JSON. Renders at phone width.
