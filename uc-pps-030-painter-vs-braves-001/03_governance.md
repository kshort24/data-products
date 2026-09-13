# 03 · Governance — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Governance department
Agents: `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `privacy-watchdog`, `data-tagger`, `version-controller`

---

## 1 · Rule-1 search (mandatory before any KPI or function is declared new)

Every candidate object was searched against the repo's existing governed set before being declared new.

| Candidate | Searched against | Result |
|---|---|---|
| `scouting_grade_20_80` | `Baseball Functions.ipynb`, `Bullpen_Functions.ipynb`, all `dp_uc*` kernels, `mlb_data.py` | **No collision.** No repo object maps a metric onto an ordinal scale |
| `benchmark_population` | `uc-pps-023` benchmark pool (RHP, ≥150 FF, 2026); `uc-pos-011` CF context pool; `uc-pps-025` population benchmark | **Near-miss, superseded.** All three are hard-coded one-off pools. SG-2 generalises them into a parameterised constructor with declared floors and a THIN rule. The three prior pools remain valid as historical artefacts; new work should use SG-2 |
| `grade_divergence_flag` | — | **No collision** |
| `pitch_grade` | `uc-pps-023` `cross_level_stuff_delta`; `uc-pos-008` AR-1..AR-7 decision model | **No collision.** Neither composites stuff and command |
| `grade_label` | house voice guide | **No collision.** Formalises an existing informal vocabulary |
| `arsenal_turnover_index` | `uc-pps-023` `cross_level_stuff_delta`; `uc-pos-010` approach-change metrics | **Near-miss, distinct.** `cross_level_stuff_delta` measures *shape* drift in one pitch across two levels. AR-1 measures *composition* drift in an arsenal across two time windows. Different grain (arsenal vs pitch), different axis (usage vs shape) |
| `pitch_map_centroid` | house pitch-map convention (`skills/phillies-pitchmix-analysis`), `lhb_pitch_mix`/`rhb_pitch_mix` | **Partial collision, extended.** The house `pitch_mix` already returns mean `plate_x`/`plate_z`. PM-1 adds usage share, a dispersion radius, and an explicit untracked-row accounting. PM-1 **does not replace** `pitch_mix`; the inherited function is untouched |

**Inherited verbatim, not re-derived:** `get_stats`, `measure_calcs`, `mcgs`, `nresults`, `whiff_rate`,
`chase_rate`, `pitch_mix`, `lhb_pitch_mix`, `rhb_pitch_mix`, `fpsr`, `putaway_rate`, `bb_type_by_level`,
`hard_hit_rate`, `SWINGS`, `WHIFFS` (`Baseball Functions.ipynb` via `dp_uc43_kernel`); `two_prop_z`
(`dp_uc42`); `_apply_woba_weights` (`mlb_data.py`); `PITCH_COLORS`, `STRIKE_ZONE` (house skill).

## 2 · New governed objects (provisional — ratification requires an independent second use)

### SG-1 · `scouting_grade_20_80`

**Plain language.** Express a pitcher's metric on the scouting scale every front office already speaks: 50 is
major-league average, every 10 points is one standard deviation of the population, 20 and 80 are the ends.

**Formula.** `grade = clip(50 + 10 × z, 20, 80)`, rounded to the nearest 5, where
`z = (subject − population mean) / population sd`, negated when lower is better.

**Grain.** One subject value × one declared population.
**Population.** Whatever `benchmark_population` (SG-2) returns. The caller must record the floor and n.
**Direction.** `higher_is_better=False` negates z first. Used for xwOBA allowed.
**Also returned.** `z`, `pctile`, population `mean`/`sd`/`n`, and `grade_pctile` — the same grade derived
rank-first (empirical percentile → normal quantile), which is robust to skew — and `divergence` between them.

**Edge cases.**
- NaN subject → NaN grade. A grade is never imputed and **50 is a real grade, not a default**.
- Population n < 5 → NaN grade.
- Zero-variance population → NaN grade (no division by zero, no infinite grade).
- Percentile is clamped to `[1/(n+1), 1−1/(n+1)]` so the rank-derived grade cannot be ±∞ at the extremes.
- Rounding is **half-up**, not numpy's banker's rounding: 52.5 → 55, 47.5 → 50. Asserted in verification.
- The clip is **lossy on purpose**. A 4-sigma pitch and a 6-sigma pitch are both an 80. Read `z` when the
  question is "how much better".

**Why the scale at all.** Because the consumers are coaches, and 50/55/60 is their native unit. The governance
cost of adopting a domain vocabulary is that its implicit assumption — normality — becomes a testable claim
this shop is now on the hook for. SG-3 is that hook.

### SG-2 · `benchmark_population`

**Plain language.** The comparison set. Every right-handed pitcher who threw in a Phillies regular-season game
between 2015 and 2026, counted once per season, who threw at least the floor number of that pitch type in
that season.

**Grain.** One row per `(game_year, pitcher)` — a **pitcher-season**.
**Scope.** Both `phillies_role` values, so the pool is the Phillies staff *plus every opponent arm that faced
them*. Not a Phillies-only pool.
**Floor rule.** 100 pitches. If that yields fewer than 25 pitcher-seasons, the floor drops to 50 **once** and
every grade drawn from the pool is stamped `THIN`. The floor is never lowered twice, and the rule is
mechanical rather than discretionary so that a thin pitch cannot be rescued by judgment.
**Null rule.** A pitcher-season with zero swings against the type gets `whiff_rate = NaN`, never 0 — the D-1
lesson inverted: a missing rate must not become a floor value.

**Declared bias, and why it is not a defect.** This is a **Phillies-schedule** population. Clubs Philadelphia
plays often are over-weighted; an arm that faced them twice contributes as much as one that faced them ten
times. The grades therefore mean *"relative to the arms this club actually sees"*, which is the
decision-relevant frame for an advance report and is **not interchangeable with a Statcast league percentile**.
Any external use of a grade must carry that sentence. This is condition C2 on publication.

**Population sizes this build (RHP, 2015–2026):** FF 232 · SI 138 · SL 92 · CH 56 · CU 45 · **ST 29 (THIN,
floor 50)**.

### SG-3 · `grade_divergence_flag`

**Plain language.** The 20-80 scale assumes the population is normal. When the z-derived grade and the
rank-derived grade disagree by 10 points or more, the population is skewed enough that the z-grade is
misleading, and the report must say so.

**Threshold.** 10 points — two full scouting increments, one population sigma.
**This build.** Shapiro-Wilk on the twelve populations behind the card: whiff rate **fails for the sweeper**
(p = .015, skew +0.92); in-zone rate **fails for the changeup** (p = .006) and the **sinker** (p < .001). Nine
of twelve pass. **Yet eleven of twelve grades come back identical either way**, and the twelfth (slider
command) differs by 5 — half the threshold. **The flag did not fire on this card.** Skewed populations do not
automatically produce wrong grades; they produce wrong grades *at the tails*, and Painter is not at a tail on
those three metrics. That distinction is the reason the flag is a computed comparison rather than a
population-level gate.

### SG-4 · `pitch_grade`

**Plain language.** A pitch is worth what it misses and where it lands. The headline grade is the mean of the
Stuff grade (whiff rate) and the Command grade (in-zone rate), rounded to the nearest 5.

**Deliberate exclusion.** Velocity, induced vertical break and horizontal break are graded and reported but
**not scored into** the pitch grade. Grading shape *and* outcome double-counts the same pitch, and it makes a
beautiful pitch nobody swings through look plus. A large gap between a plus shape grade and a below-average
stuff grade is itself the finding — which is exactly Painter's four-seam in the first half of 2026, and is
precisely the sentence this design makes it possible to write.

**Null rule.** Either input NaN → NaN. No half-grades, no imputation from the available half.

### SG-5 · `grade_label`

Controlled vocabulary so reports cannot invent adjectives:
≥70 plus-plus · ≥60 plus · ≥55 above average · ≥45 average · ≥40 below average · ≥30 well below average ·
else poor. Monotonicity asserted in verification.

### AR-1 · `arsenal_turnover_index`

**Plain language.** How much of a pitcher's arsenal on either side of a date is not shared with the other side.

**Definition.** `index = added_share + dropped_share`, where `added_share` is the share of the *after* window
thrown with a type whose *before* usage was under 2%, and `dropped_share` is the share of the *before* window
thrown with a type whose *after* usage is under 2%. Range 0–2.
**Why 2% and not zero.** A handful of misclassified pitches should not keep a retired pitch on the books.
**Grain.** One pitcher × one pair of windows.

**Why it matters.** A head-to-head history, a scouting card, or a projection built on the *before* window is
evidence about a pitcher who no longer exists, **in proportion to this index**. At 0 the history transfers; at
0.33 roughly a third of it does not. This build: **Painter pre→post = 0.37**; **April-vs-Atlanta → tonight =
0.33**. Those two numbers are why the report refuses to let the head-to-head table drive a plan.

**Mandatory control (standing rule from this UC forward).** Statcast pitch tags are a classifier output, not a
pitcher's declaration. **An AR-1 reading may not be called a pitcher decision until it is checked against a
league-wide tag-share series for the same window.** This build ran that control: league splitter share across
every pitcher in the Phillies log went 4.14% (June) → 5.39% (September) with six arms throwing 165 splitters
in September. The classifier did not move; Painter did. Receipt: `out/dp_uc44_tag_drift.csv`.

### PM-1 · `pitch_map_centroid`

**Plain language.** For each handedness × pitch type, the average location, its usage share, and how tightly
the pitches cluster around it.

**Definition.** Mean `plate_x`/`plate_z` over tracked pitches; `usage` = share of tracked pitches in the frame;
`dispersion_ft` = mean Euclidean distance from each pitch to its own cell centroid.
**Why dispersion ships with the centroid.** A tight centroid on a wide cloud is a location *average*, not a
location, and a bubble chart cannot tell you which you are looking at.
**Null rule.** Rows with null `plate_x`/`plate_z` are dropped from both the centroid and the denominator, so
usage is of *tracked* pitches; the dropped count ships in the receipt (0 this build).
**Coordinate convention, asserted not assumed** (`uc-pps-025` lesson): `plate_x` is catcher's view, negative =
third-base side = **inside to a right-handed hitter**, and arm-side for a right-handed pitcher. Confirmed in
the data: Painter's sinker and changeup carry `pfx_x` ≈ −12.7" (arm-side) and his sweeper +17.0" (glove-side).

## 3 · Technical lineage (column-level, abbreviated)

```
FOUR-SEAM STUFF GRADE (50)
  phils_2026.parquet
    -> game_type=='R' & phillies_role=='pitching' & pitcher==691725      [subject frame]
    -> game_date >= '2026-07-31'                                          [post-option window]
    -> pitch_type == 'FF'                                                 218 rows
    -> description in SWINGS  (110)  /  description in WHIFFS  (24)
    -> whiff_rate = 24/110 = 0.2182                                       [wr_safe, D-1 remediated]
  phils_2015..2026.parquet
    -> game_type=='R' & p_throws=='R' & pitch_type=='FF'                  [benchmark frame]
    -> groupby(game_year, pitcher) -> n, swings, whiffs
    -> n >= 100                                                           232 pitcher-seasons
    -> whiff_rate = whiffs/swings                                         mean .2160, sd .0748
  SG-1: z = (.2182-.2160)/.0748 = +0.026 -> 50 + 0.26 -> round5 -> 50
  SG-3: pctile .526 -> norm.ppf -> 50.6 -> round5 -> 50 ; divergence 0.0 -> no flag

FOUR-SEAM COMMAND GRADE (25)
  ... same subject frame -> zone <= 9 (92 of 218) -> in_zone_rate .4220
  ... same benchmark frame -> in_zone -> mean .5420, sd .0501
  SG-1: z = -2.421 -> 50 - 24.2 = 25.8 -> round5 -> 25   [rank-derived also 25]

FOUR-SEAM PITCH GRADE (40)
  SG-4: mean(50, 25) = 37.5 -> round5 (half-up) -> 40

AR-1 TURNOVER (0.366)
  subject frame -> window split at 2026-07-31
    -> PRE  value_counts(pitch_type, normalize)  FS .1437
    -> POST value_counts(pitch_type, normalize)  CH .2222
    -> added   = types with before<.02 and after>=.02   = [CH], share .2222
    -> dropped = types with before>=.02 and after<.02   = [FS], share .1437
    -> index = .2222 + .1437 = .3659
  CONTROL: phils_2026 all pitchers -> crosstab(month, pitch_type, normalize='index')
    -> FS share 2026-06 .0414 vs 2026-09 .0539 -> classifier stable -> "pitcher decision"

xwOBA (PA grain) vs xwOBAcon (contact grain)
  estimated_woba_using_speedangle
    -> .mean() over ALL rows (nulls skipped) = xwOBA per PA        [183 non-null of 720]
    -> .mean() over type=='X' only           = xwOBAcon            [123 rows]
  Both published, both labelled, both carrying their own n.        [E-4 / DQ-8]
```

Full column-level trace for every other published number: `out/dp_uc44_*.csv` receipts, one per table.

## 4 · Defect register

**No new kernel defects found in this build.** The six known defects were read against it (see `05` §3 and
`out/dp_uc44_defect_exposure.csv`); one is exposed, three are not, two are not applicable.

D-1/D-2 was **re-confirmed as a live defect** rather than assumed dormant: `whiff_rate(['pitch_type'], POST)`
happens to lose nothing here because every post-option pitch type recorded at least one whiff, but the same
call restricted to right-handed hitters silently drops the curveball. That assertion is in the verification
harness so the defect stays visible even in builds where it does no damage.

**Build-local remediation, kernel untouched:** `wr_safe()` computes whiffs/swings directly; `in_zone_rate` is
computed as `(zone <= 9).mean()` rather than through `chase_rate`'s `(pitches − ooz)/pitches` arithmetic.

## 5 · Known-defect exposure measured against this build

| Defect | Exposed? | Reading |
|---|---|---|
| D-1 / D-2 — `whiff_rate` inner join drops zero-whiff groups | **NO** | Every post-option pitch type recorded ≥1 whiff. Still reproduces on a handedness split; asserted |
| D-7 / O-13 — `chase_rate` counts NULL `zone` as in-zone | **NO** | 0 null `zone` values in the graded window |
| O-8 — `hard_hit_rate` counts untracked BIP as not-hard-hit | **NO** | 0 of 123 post-option BIP untracked. Hard-hit still reported as hits/**tracked** BIP with both counts printed |
| O-5 — `truncated_pa` counted as a plate appearance | **YES** | 1 occurrence in 185 PA. Effect on any published rate < 1 part in 185. Disclosed in the report's caveats |
| O-3 — `launch_speed` present on fouls | N/A | No exit-velocity KPI in this UC |
| O-7 — `pull_air_rate` not executable (no `loc_x`/`loc_y`) | N/A | No directional KPI in this UC |

## 6 · Privacy assessment (`privacy-watchdog`)

**CLEAR.** Every element is publicly observable professional athletic performance, published by MLB. Player
identity is the subject of the product, not an incidental disclosure. No health, contract, biometric or
personal data is present or derived. `des` free text is used only for name resolution and is not republished.
No re-identification surface: the entities are already named public figures.

One note for completeness: `arm_angle` and the bat-tracking fields (`bat_speed`, `swing_path_tilt`,
`attack_angle`) are biomechanical measurements. They are not used in this package — `arm_angle` by descope,
the bat-tracking fields by scope — but any future UC that builds on them should re-run this assessment, since
biomechanical data has a different sensitivity profile from outcome data even when both are league-published.

## 7 · Data tagging (`data-tagger`)

| Tag | Value |
|---|---|
| Sensitivity | **Internal — Restricted** |
| External publish | **Blocked** |
| Domain | Phillies Pitching (`pps`) |
| Subject area | Advance Scouting / Pitcher Evaluation |
| Data product membership | `uc-pps-030-painter-vs-braves-001` |
| Retention | Retain; supersede on the post-game backtest |
| Distribution | Manager, pitching coach, catcher, pitching analyst |
| Contains new governed objects | **Yes — 7, all provisional** |

## 8 · Versioning (`version-controller`)

**v1.0.0.** First release of this use case and of the SG/AR/PM object family.

**Breaking-change policy.** The following changes are **breaking** and require a major version, because they
silently move every grade in every downstream artefact:

1. Changing the `benchmark_population` season range, role scope, or handedness filter.
2. Changing `GRADE_FLOOR_PRIMARY`, `GRADE_FLOOR_FALLBACK` or `GRADE_POP_MIN`.
3. Changing which metrics feed `pitch_grade` (in particular, adding shape).
4. Changing the rounding rule or the 20/80 clip.

Non-breaking: adding a metric to the grade table; adding a pitch type; refreshing the cache **to a new anchor**
(which is a new UC, not a new version of this one).

**Consumer communication.** Any package that quotes a grade must quote the population with it. A grade without
its population is not a versioned artefact — it is a number with no contract.
