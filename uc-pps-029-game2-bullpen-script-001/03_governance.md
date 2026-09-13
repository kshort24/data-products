# 03 · Governance — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `data-tagger`,
`privacy-watchdog`, `version-controller`

## 1 · Rule-1 search (mandatory before any KPI or function is declared new)

Per `repo-search-before-declaring-kpi-new.md`. Searched: the two governed notebooks
(`Baseball Functions.ipynb`, `Bullpen_Functions.ipynb`), the `phillies-data-analyst` /
`phillies-pitchmix-analysis` / `pitcher-scouting-report` / `wheeler-scouting-report` skills, the MLB repo's
`dp_uc*` build scripts and use-case specs, and the control plane's `data-products/` tree.

| Candidate object | Prior art found? | Disposition |
|---|---|---|
| `appearance_summary`, `add_rest_days`, `add_rolling_workload`, `pitcher_season_workload`, `build_bullpen_workload` | **YES — `Bullpen_Functions.ipynb`** | **Inherited verbatim.** Section B of `dp_uc43_kernel.py` is a transcription, not a re-derivation. |
| `get_stats`, `measure_calcs`, `mcgs`, `nresults`, `whiff_rate`, `chase_rate`, `pitch_mix`, `lhb_pitch_mix`, `rhb_pitch_mix`, `fpsr`, `putaway_rate`, `bb_type_by_level`, `hard_hit_rate` | **YES — `Baseball Functions.ipynb`** | **Inherited verbatim.** Section A. Known defects measured, not patched. |
| `PITCH_COLORS`, `STAND_COLORS`, `STRIKE_ZONE`, Phillies red/blue | **YES — `skills/phillies-pitchmix-analysis/assets/pitch_colors.py`** | Inherited verbatim. |
| `_apply_woba_weights` | **YES — `mlb_data.py`** | Behaviour replicated verbatim; **deliberately not applied to the AAA frame**. |
| **`bullpen_availability_tier` (BS-1)** | **NO.** `uc-pps-016` (Alvarado multi-stint workload flag) flags *one* arm's stint pattern; it does not classify a pen. `dp_uc12` produced a reliever dashboard with first-batter OBP, not availability. No tiering function anywhere. | **NEW — provisional, unratified.** |
| **`script_capacity` / `script_coverage_risk` (BS-2)** | **NO.** `dp_uc16_bullpen_games_inventory` counts historical bullpen games; it does not price a prospective script. | **NEW — provisional.** |
| **`multi_inning_propensity` (BS-3)** | **PARTIAL.** `pitcher_season_workload` already emits `multi_inning_apps` as a count. No rate, no pitch-floor variant, no max-BF. | **NEW wrapper over an inherited count** — the count is inherited, the rate/floor/ceiling framing is new. Provisional. |
| **`opener_tto_delta` (OP-1)** | **NO.** `n_thruorder_pitcher` is used nowhere in the repo's pitcher UCs. | **NEW — provisional, and it could not execute** (see §3). |
| `two_prop_z` | **YES — `uc-pos-016`/`dp_uc42`** | Inherited; **not used in the shipped analysis** (no proportion comparison survived design). Retained in the kernel for reuse. |

Four new objects, one of which failed to execute. No existing object was silently re-implemented.

## 2 · New governed objects (provisional — ratification requires an independent second use)

### BS-1 · `bullpen_availability_tier`
- **Grain:** one pitcher × one target game. **Population:** Phillies relievers with ≥1 logged 2026 appearance.
- **Inputs (all inherited):** `days_of_rest`, `pitches_last_3d`, `appearances_last_3d`, pitches thrown
  yesterday, season mean pitches per relief outing.
- **Definition:**
  - **RED** if he threw yesterday *and* yesterday's count was ≥ his season mean outing, **or** he has 3
    appearances in the last 3 days.
  - **AMBER** if he threw yesterday *below* his mean, **or** he has 2 appearances in the last 3 days,
    **or** his 3-day pitch load is ≥ 1.5× his mean outing.
  - **GREEN** otherwise.
- **Null rule:** a pitcher with no prior 2026 appearance returns **GREEN + `debut`**. Rest is undefined for a
  debutant, not zero — collapsing that to zero would have made Holman look maximally rested rather than
  unmeasured.
- **Why it exists:** the client's premise treats *an appearance* as the unit of unavailability. The log shows
  appearance count and pitch load diverge sharply (three of five arms in the anchor game threw nine pitches).
  BS-1 separates them.
- **Status:** thresholds are this build's judgment. The *inputs* are governed; the *cut-points* are not.
  Do not ratify until a second UC reuses them against a pen whose tiers are independently known.

### BS-2 · `script_capacity` / `script_coverage_risk`
- **Grain:** one script (an ordered list of inning→arm assignments) × one capacity mode.
- **Definition:** capacity = Σ over **distinct arms** of that arm's expected batters faced. `average` mode
  uses his 2026 mean BF per relief outing for every arm. `ceiling` mode substitutes his **season maximum BF**
  for any arm assigned ≥2 innings, leaving one-inning arms at their mean.
- **Requirement side:** the median staff batters-faced across regulation (`inning_exited == 9`) Phillies games
  in the same season — **37.0**, n=106, IQR 34.2–40.0.
- **Edge cases:** an unassigned inning contributes nothing and is reported separately; an arm with no season
  history (Holman) falls back to his supporting-tier mean and the substitution is labelled in the output.
- **Known weakness, disclosed:** the average mode assumes an arm delivers his norm regardless of how many
  innings he is given, which makes a *concentrated* script look worse than a distributed one. That is why the
  ceiling mode exists and why both are shipped. Neither mode alone is the answer.

### BS-3 · `multi_inning_propensity`
- **Grain:** pitcher × season (or career). **Population:** relief outings only (`is_start == False`).
- **Emits:** relief appearances, multi-inning appearances and rate, appearances ≥6 BF and rate, appearances
  ≥30 pitches and rate, max pitches, max BF, 80th-percentile pitches.
- **Zero-denominator rule:** returns `NaN`, never 0 — the D-1 lesson (a zero numerator is not a zero rate).
- **Known weakness, disclosed:** `innings_spanned` is `inning_exited − inning_entered + 1`, a **span, not
  outs recorded**. A reliever who gets one out in the 7th and two in the 8th spans two innings. BS-3 therefore
  slightly over-counts length. The BF columns are shipped alongside as the honest cross-check and they tell
  the same ordering.

### OP-1 · `opener_tto_delta` — **specified, executed, could not discriminate**
- **Intent:** split an opener's results by `n_thruorder_pitcher` to test whether he holds up on a second look.
- **Result:** Mayza's entire 2026 population is `n_thruorder_pitcher == 1` (987 of 987 pitches). The KPI
  returns a single row and has no comparison arm.
- **Disposition:** this is a **genuine null, not a defect** — and it is load-bearing in the opposite
  direction. A two-inning open reaches batters 1–6, all still first-time-through, so the two-inning ask does
  not need second-look evidence at all. The binding constraint on Mayza is pitch count. Recorded as a KPI
  that could not execute, in the same register as `uc-pos-011`'s O-7.

## 3 · Technical lineage (column-level, abbreviated — full trace in the receipts)

```
phils_2026.parquet
  └ filter game_type=='R' ∧ phillies_role=='pitching'          → L0 MLB pitch log (22,021)
      └ merge wOBA and FIP Constants.csv on game_year          → +wBB..wHR  [MLB ONLY]
          └ appearance_summary(mcgs_func=mcgs)                 → L1 (632)   [D-8 here]
              └ .is_start.fillna(False)                        → L1' remediated
                  ├ add_rest_days(within='season')             → prev_appearance_date, days_between, days_of_rest
                  ├ add_rolling_workload((3,7,14))             → pitches_last_{3,7,14}d, appearances_last_*
                  ├ pitcher_season_workload(relievers_only)    → L2 avg_pitches, avg_bf, multi_inning_apps…
                  │   ├ bullpen_availability_tier(...)         → BS-1  → availability_D1 / _D2
                  │   ├ script_capacity(script, mean, max)     → BS-2  → script_capacity_modes
                  │   └ multi_inning_propensity(...)           → BS-3  → multi_inning_propensity
                  └ groupby(game_pk).sum(batters_faced)        → staff_game_workload → median BF = 37 (max_inn==9)
  └ filter phillies_role=='batting'                            → opponent-facing log
      ├ pitcher==641816 → nresults / whiff_rate / chase_rate / pitch_mix  → opp_starter_*
      └ game_date==anchor → des-parse modal name per batter    → atl_order  [O-10 workaround]

lhvp26.parquet  [NO wOBA weights merged — DQ-5]
  └ filter game_type=='R' ∧ pitcher==680880                    → 348 pitches, 104 PA
      ├ lhb_pitch_mix / rhb_pitch_mix, pfx×12                  → holman_mix_by_stand
      ├ whiff_rate / chase_rate on ['stand','pitch_type']       → holman_whiff_chase
      ├ fpsr / putaway_rate on ['stand']                        → holman_fpsr / _putaway
      ├ events counting by stand                                → holman_counting_by_stand  [NO wOBA]
      └ appearance_summary + add_rest_days                      → holman_appearances
```

Two transformations are **not** present anywhere in this lineage and their absence is deliberate:
`hard_hit_rate` on the AAA frame (O-8 exposure: 6 of 73 BIP untracked) and any wOBA/xwOBA on the AAA frame
(DQ-5 comparability).

## 4 · Defect register additions

| ID | Where | Description | Scope | Disposition |
|---|---|---|---|---|
| **D-8** | `Bullpen_Functions.ipynb :: appearance_summary` | `is_start` is computed by comparing a nullable `Int64` `pitcher` against merged starter columns. On a **single-team frame** — which `pps` always is — one side of the `Top`/`Bot` merge is always null, so `False \| NA` evaluates to `pd.NA`. Every non-starter gets `<NA>`: **484 of 632** appearances. `~df['is_start']` then selects **zero rows**, and `pitcher_season_workload(relievers_only=True)` returns an **empty DataFrame with no error**. | **Repo-wide.** Every caller of the governed bullpen pipeline on a Phillies-only frame is affected, which is every caller. | Reproduced in verification family D. Remediated **build-locally** with `.fillna(False).astype(bool)`; the locked function is untouched. **Recommended fix upstream:** `.fillna(False)` inside `appearance_summary` before the `is_start` assignment returns. |
| **D-9** | `Baseball Functions.ipynb :: measure_calcs` | `measure_calcs` unconditionally executes `stats.rename(columns={'batter':'pitches'})`. Any `nresults(level, df)` whose level includes `'batter'` therefore loses the column and raises `KeyError: "['batter'] not in index"`. | **Repo-wide.** Blocks every per-batter results table computed through the governed path. | Reproduced in family D. Remediated build-locally by aliasing `batter → batter_id` before the call. **Recommended fix upstream:** make the rename conditional on the column not being a grouping key. |

## 5 · Known-defect exposure measured against this build

Receipt: `out/dp_uc43_defect_exposure.csv`. Summary:

| Defect | Exposure here | Effect on the deliverable |
|---|---|---|
| D-1 (whiff_rate inner join drops zero-whiff groups) | 6 of 6 Holman groups returned; 2 of 2 Mayza groups | **none** — no group dropped |
| D-7 / O-13 (`in_zone_rate` counts NULL `zone` as in-zone) | 0 null of 348 (AAA); 48 null of 22,021 (MLB) | ≤ 0.22% inflation on MLB; nil on AAA |
| O-3 (`launch_speed` present on fouls) | 61 non-BIP rows carry it | respected — every EV read is gated on `type=='X'` |
| O-8 (`hard_hit_rate` counts untracked BIP as not-hard-hit) | 6 of 73 AAA BIP untracked (8.2%) | **KPI not shipped** for the AAA tier |
| O-14 (`bbrate` is unintentional-BB/PA) | 11 intentional walks in the MLB frame | reported as unintentional-BB/PA where quoted |
| O-10 (no opponent pitcher name) | the entire opponent section | identity inferred and flagged WARN |
| DQ-5 / LV-1 (cross-level comparability) | AAA frame carries no wOBA weights | no wOBA/xwOBA computed at AAA |

## 6 · Privacy assessment (`privacy-watchdog`)

**LOW.** Every element is public on-field performance data for professional athletes, already published by
MLB Advanced Media. No PII beyond publicly rostered names and public MLBAM identifiers. No health data —
and this matters here, because two findings (Holman's 44-day gap, Kerkering's seven-day absence) sit adjacent
to a medical inference. **Neither is characterised.** The package reports the gap in the appearance log as a
fact and explicitly asserts no cause. No quasi-identifier combination creates re-identification risk for any
non-public individual. No external-publish flag raised; external publication was not the ask.

## 7 · Data tagging (`data-tagger`)

| Element | Sensitivity | Domain | Subject area | Product |
|---|---|---|---|---|
| L0/L1/L2 MLB pitch + appearance data | Public | Baseball Operations | Pitching | `uc-pps-029` |
| L0 AAA pitch data | Public | Player Development | Pitching · Minor League | `uc-pps-029` (supporting tier) |
| Opponent-facing log | Public | Advance Scouting | Opponent | `uc-pps-029` |
| BS-1 / BS-2 / BS-3 outputs | Internal | Baseball Operations | Bullpen Deployment | `uc-pps-029` |
| Recommended revision (§6 of the report) | **Internal — judgment, not measurement** | Baseball Operations | Bullpen Deployment | `uc-pps-029` |

The last row is tagged deliberately. The revision is labelled as judgment in the report itself; tagging it
as measurement would let it propagate downstream as if it were a computed result.

## 8 · Versioning (`version-controller`)

**v1.0.0 — initial release. No prior version, therefore no breaking change.** Semantics registered for the
next release:

- Re-tiering BS-1 (changing the cut-points) is **BREAKING** — downstream readers key on GREEN/AMBER/RED.
- Adding a capacity mode to BS-2 is **MINOR**; changing the 37-BF requirement basis is **BREAKING**.
- Refreshing the parquet cache and re-running is **PATCH** — but note the anchor game moves, which changes
  every availability figure. A refreshed run is a new game, not a correction to this one.
- Promoting BS-1/BS-2/BS-3 from provisional to APPROVED requires an independent second use, per standing
  repo practice. **Not done here.**
