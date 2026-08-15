# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy**

## Use case as submitted
> Justin Crawford has supposedly turned a corner. Since roughly mid-June he has been hitting the ball
> much better — batting average slowly climbing, OBP bouncing back, wOBA coming up. **These are
> assumptions that should be tested first.** Assess performance against those KPIs and any other
> top-line results before digging into why. His profile tends to be high-swing / high-chase but
> low-whiff, putting a lot of balls in play and using his speed to beat them out. Check ground-ball
> rate and average launch angle on BIP, since those have frequently been cited as indicators he will
> not succeed at the big-league level. Consider whether performance against LHP/RHP has changed —
> this could coincide with the acquisition of Derek Hill and reduced opportunities against LHP.
> Call out specific pitch types or groups he is having success against. Contextualise against other
> Phillies CFs in the Statcast era *(context-window code supplied)*.

## Validator disposition — **GO**, 0 blocking, 4 conditions

The requester explicitly framed the premises as assumptions to be tested. That is a well-formed
use case and it sets the report's structure: **§1 answers the four assertions before §4 explains
anything.**

| # | Condition | Resolution |
|---|---|---|
| C-1 | "Roughly mid-June" is not a date | Fixed at **2026-06-15** and declared. **Because the requester chose it after observing the outcome, a 9-point breakpoint sensitivity scan is a required deliverable, not an optional one** (`uc-pos-008` both-framings rule). A mid-May breakpoint reverses the sign |
| C-2 | "Hitting the ball better" conflates results with contact quality | Split into two measurable families: **results** (BA/OBP/wOBA/BABIP) and **contact** (launch angle, GB rate, EV, hard-hit, xwOBAcon). They diverge, and the divergence is the finding |
| C-3 | The Derek Hill link asserts a mechanism | Hill's debut derived from the data (**2026-06-13**), not assumed. Tested by direct standardisation (PL-1), not by eyeballing splits |
| C-4 | "Success against pitch types" has no floor | 40-pitch floor for pitch-type rows, 50-PA floor for any PA-denominated rate. **The post-break offspeed cell is 17 PA and is labelled below floor everywhere it appears** |

## Source-system profiler — fitness for purpose

| CDE | Physical column | Fitness |
|---|---|---|
| `batter_name` / `batter_id` | `player_name` / `batter` | ✅ exactly one value after filter; MLBAM **702222** confirmed by filter, not assumed |
| `season_year` / `game_month` | `game_year` / `game_date.dt.month` | ✅ 6 buckets in 2026, **including March** — calendar, no Mar/Apr merge |
| `plate_appearance_key` | `game_pk` + `at_bat_number` | ✅ |
| `pa_result_event` | `events` | ✅ all values map to the governed PA / AB / hit / walk sets |
| `pitch_result_description` | `description` | ✅ **zero unmapped values** against governed SWINGS/WHIFFS |
| `pitch_in_zone_flag` | `zone` (`>9` = out of zone) | ✅ non-null on every chase denominator row |
| `pitch_type` / `pitch_group` | `pitch_type` → `PITCH_GROUP` | ✅ 11 types present; all map, `other` bucket empty |
| `handedness_faced` | `p_throws` | ✅ complete |
| `exit_velocity` / `launch_angle` | `launch_speed` / `launch_angle` | ⚠ **0.74% NULL on 2026 BIP** — real sensor gaps. Handled per the uc-pos-009 standard; also the trigger for defect **O-8** |
| `batted_ball_type` | `bb_type` | ✅ 0% NULL on BIP — classifier-derived, complete where `launch_angle` is not |
| `expected_ba` / `expected_woba_on_contact` | `estimated_ba_using_speedangle` / `estimated_woba_using_speedangle` | ⚠ 2.6% / 1.8% NULL on BIP; named `xba_bip` / `xwobacon_bip` per **O-4** |
| `hit_distance` | `hit_distance_sc` | ✅ used only for the infield-hit proxy, never as a rate denominator |
| `centre_fielder_id` | `fielder_8` (on the `pps` frame) | ✅ the join key for the whole context layer |
| wOBA constants | `wOBA and FIP Constants.csv` | ✅ 2026 row present |

**Population.** `pos` = rows where PHI is batting (`home_team=='PHI' & inning_topbot=='Bot'` OR
`away_team=='PHI' & inning_topbot=='Top'`), excluding `game_type` S/E. 270,954 rows 2015–2026.
Crawford: **1,323 pitch rows, 362 PA, 109 games, 2026 only** — a rookie season, no prior-year baseline
exists inside this data plane.

## Domain steward — rulings applied

1. **SWINGS list** — the 8-value notebook list including `swinging_pitchout`. Ratified `uc-pos-010`; inherited unchanged.
2. **`month`** — `game_date.dt.month`, calendar. March 2026 is 4 games / 13 PA. **Not merged into April**; retained and flagged below floor.
3. **PA floor 50** — the standing batter standard. It places **both March (13) and August (42)** below floor. **August is the requester's strongest month.** This is disclosed rather than worked around; no exception was granted.
4. **BIP floor 50 tracked** — metric-specific, for launch-angle and batted-ball-share statistics only. Below it, `mean_la` / `median_la` / `mean_ev` are NULL, never zero.
5. **BABIP denominator** — `AB − K − HR + SF`, the standard form. Introduced this build because the requester's premise ("hitting the ball better") cannot be adjudicated without it.
6. **Context-window thresholds** — the DPO's supplied snippet (>80 CF games in a season; >10 defensive pitches in a game) is **transcribed without alteration**. Changing a requester-supplied threshold silently is a governance failure even when the change would be defensible.

## Window rule — both framings priced

Per the `uc-pos-008` / `uc-pos-010` precedent, when a window is outcome-selected:
- **Narrative window** — before/from 15 June, as submitted. Shipped as the primary contrast, marked descriptive.
- **Sensitivity evidence** — all 9 candidate breakpoints from 1 May to 1 August, with pre/post PA and wOBA. Shipped as a first-class receipt (`dp_uc34_breakpoint_scan.csv`) and rendered in both the report and the dashboard.

**The scan is not a caveat, it is a finding:** the sign of the effect depends on the boundary.
