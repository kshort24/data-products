# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy**

## Use case as submitted

> Alec Bohm has turned his season around since the All-Star break and is hitting the ball much better.
> His upswing has been an essential boon to a Phillies lineup that needs his bat to produce in the
> middle of the lineup. What changed? Were there specific actions that could have been taken by
> personas within the Phillies Offense Value Stream that potentially drove these positive outcomes?
> Start with an assessment of his performance, calibrating if the outcomes have been positive. Then
> consider the underlying metrics. Top-line: **SLG, BA with RISP, run creation** + any other KPIs the
> data-product-owner deems appropriate. Underlying: quality of contact — **pull-air** (prior digging by
> the DPO), hard-hit / air / barrel; swing decisions — is he still a guy who **rarely whiffs**? Has his
> **approach** changed? Other angles: **platoon splits** and **pitch_groups** (fastballs / breaking /
> offspeed, LHP/RHP). *(Working notebook snippet supplied — windows, level, KPI list, data dictionary,
> required functions, and a merge-chain method. Transcribed in §Method transcription below.)*

## Validator disposition — **GO**, 0 blocking, 6 conditions

| # | Condition | Resolution |
|---|---|---|
| C-1 | The snippet's comment says "any game **after 2026-07-16**" but its operator is `game_date > '2026-07-15'`, which **includes** the 16 Jul game | **The operator is governed** (code over comment). It is also the sensible reading: 16 Jul is the first game back. No Phillies game falls 13–15 Jul, so `< '2026-07-16'` / `> '2026-07-15'` are exact complements — verified §2 of the verification |
| C-2 | "BA with RISP" needs a PA-membership rule — base state can change mid-PA | The DPO operator (`on_2b`/`on_3b` non-null → `nresults`) counts a PA as RISP iff runners are in scoring position **on the terminal pitch**. Adopted, documented in the kernel docstring and the dashboard's interpretation rules; do not compare against any-pitch-RISP sources |
| C-3 | `pull_air_rate` — the requester's priority metric — **cannot execute** against the data plane (O-7, opened uc-pos-011: reads `loc_x`/`loc_y`, schema has `hc_x`/`hc_y`). Re-checked against the current `Baseball Functions.ipynb` cell 24 at intake: still unexecutable | **Remediated, not patched**: `pull_air_rate_fix` derives loc coordinates per the house `cbp-spray_AI.md` convention (origin 125.42/198.27, y-flip) and applies the governed ±4.7-slope boundary VERBATIM. Classification proven scale-invariant; coordinate convention asserted empirically (median pulled-GB `loc_x` = **−45.4 ft**, LF side for a RHB ✓). **Provisional pending DPO ratification** |
| C-4 | "Boon to the middle of the lineup" is untestable — batting-order slot is not a column in this data plane | Scoped to the governed proxies `runs_created` / RC-per-PA / BA-w-RISP; the lineup claim is flagged as requiring a batting-order carry-in (report §7.3) |
| C-5 | The submitted merge-chain has two paren transpositions (the `chase_rate` merge swallows the subsequent merges; the RISP `[level+['ba']]` selector sits outside the call) — it does not run as pasted | Repaired mechanically with intent preserved; the repaired chain runs as the **original-method verification path** (§15) and agrees with the kernel on every compared value. uc-pps-026 premise-correction precedent |
| C-6 | Post-break sub-cells were guaranteed to fall under the 50-PA floor | Confirmed at profile: post-RISP 42 ⚠, post-LHP 33 ⚠, post-offspeed 12 ⚠, March 21 ⚠. Flagged on every surface; no ranking leans on them |

## Layer-1 repo search — run before any KPI was called new (standing rule)

| Finding | Consequence |
|---|---|
| `nresults`, `whiff_rate`, `chase_rate`, `hard_hit_rate`, `barrel_rate`, `inds`, `runs_created`, `risp_conversion`, `fpsr` all exist in `Baseball Functions.ipynb` | Consumed, not rebuilt; only `_fix` variants re-expressed (D1–D4 lineage) |
| `dp_uc33_kernel.py` / `dp_uc34_kernel.py` carry the `_fix` variants, `running_line_pa`, PL-1, `battedball_profile`, `xcontact`, pool-percentile machinery | **Inherited wholesale**; `running_line_pa` extended additively to `cum_slg` (uc-pos-011 BA/OBP precedent) |
| `runs_created` (notebook cell 14) ≠ **SC-1 wRC** (uc-pos-004) ≠ Bill James RC | Three distinct governed meanings — glossary disambiguation in `03_governance.md`. The notebook function is what the DPO's snippet calls, so it is the one consumed |
| No prior UC on Alec Bohm — `ls data-products/ \| grep -i bohm` and a repo-wide grep return nothing | First-touch subject. The DPO's "prior digging on pull-air" lives in monthly notebooks, not in a governed UC; the submitted snippet is its distillate |
| `PITCH_GROUP` map — `dp_uc18_marsh_breakout.py` L170 | Consumed verbatim (EP → `other`, 6 pitches, excluded from group panels) |
| Standing batter floor **50 PA**; `swinging_pitchout`-inclusive 8-value SWINGS list; `month` = calendar | All inherited unchanged |
| `swing_rate` is NOT in the notebook — it is AP-2 (uc-pos-010, provisional) | The snippet's `swing_rate` requirement consumed as AP-2; in-zone variants shipped as `zone_swing_whiff` per the DPO's `zone < 10` operator |

## Source-system profiler — fitness for purpose

| CDE | Physical column | Fitness |
|---|---|---|
| `batter_id` / `batter_name` | `batter` / `player_name` | ✅ MLBAM **664761** confirmed by filter; exactly one name, one stand (`R`); seasons 2020–2026 |
| `pa_result_event` | `events` | ⚠ **3 `truncated_pa` rows** (all pre-break) — the **O-5 fork** (uc-pos-008): counted as PA and AB with no outcome. 3/377 pre-break PA = worst-case 2-point BA effect; documented, not forked |
| `pitch_result_description` | `description` | ⚠ 5 `automatic_ball`/`automatic_strike` rows (pitch-timer calls) — non-swings, sit only in denominators; zero unmapped values against SWINGS/WHIFFS |
| `pitch_in_zone_flag` | `zone` | ⚠ 5 NULL rows — excluded from BOTH zone populations by the `<10` / `>9` pair; disclosed |
| `runners_on_2b/3b` | `on_2b` / `on_3b` | ✅ complete (nullable-by-design = base empty) |
| `bat_score` / `post_bat_score` | same | ✅ 0 NULL; monotone within PA (verified — first==min everywhere) |
| `exit_velocity` / `launch_angle` | `launch_speed` / `launch_angle` | ⚠ **1 untracked BIP** of 400 (0.25%) — sensor boundary; D6/O-8 exposure < 0.2 pt |
| `hit_coordinates` | `hc_x` / `hc_y` | ✅ **0 NULL on 2026 BIP** — the pull-air derivation loses nothing this season |
| `batted_ball_type` | `bb_type` | ✅ 0% NULL on BIP |
| `expected_woba_on_contact` | `estimated_woba_using_speedangle` | ⚠ 1 NULL on BIP; named `xwobacon_bip` per O-4 |
| `pitch_type` / `pitch_group` | `pitch_type` → `PITCH_GROUP` | ✅ 5 NULL + 6 `other` (EP) of 1,865; group panels cover 99.7% of pitches |
| wOBA constants | `wOBA and FIP Constants.csv` | ✅ 2020–2026 rows present |

**Population.** `pos` = PHI batting, `game_type` S/E excluded: 272,028 rows 2015–2026, fresh through
**2026-08-22** (T-1 at build). Bohm: 13,175 pitch rows career; 1,865 rows / 124 games / 512 PA in 2026;
all rows `game_type == 'R'`; PITCH_KEY duplicates: **0**.

## Domain steward — rulings applied

1. **SWINGS/WHIFFS** — 8-value / 5-value notebook lists, inherited unchanged (a foul tip is a whiff).
2. **Break windows** — the DPO operator, both sides above the 50-PA floor: no floor exception needed
   for the headline contrast (first UC in this family where that is true).
3. **Mean EV / LA** — tracked-BIP standard (`battedball_profile`), NOT `inds` over all rows: the
   governed `inds` averages `launch_speed` over tracked **foul balls** too (O-3 trap). Both shipped;
   the gap is ~6 mph and is quantified in `dp_uc37_inds_reconciliation.csv`.
4. **Requester-supplied thresholds transcribed without alteration** — the `zone < 10` in-zone rule and
   the RISP operator are the DPO's own; changing a requester threshold silently is a governance failure
   even when defensible.
5. **Window rule — both framings priced** (uc-pos-008/010/011 lineage): narrative window (the break) as
   the primary contrast, 10-point breakpoint scan as first-class receipt. The scan is a *finding* here,
   in the subject's favour: no candidate boundary reverses the sign.
