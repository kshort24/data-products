# 01 · Strategy & Intake
**use-case-validator · source-system-profiler · domain-steward-proxy**

## Use case as submitted
> Stott turned around his 2026 season; results grew steadily since an atrocious April. Over the
> last 4 months, has he made a change in approach? First assess the facts — how did performance
> alter month-to-month. Video title: **"Bryson Stott drawing 14 walks between strikeouts."**

## Validator history
Pass 1 returned **NO-GO / 6 blocking**, revised to a different 6 after a repo search overturned
three. Amendments 1–3 added AP-6…AP-10 and took the count to **14 blocking**. Six cleared on
data-plane access (`00`). **This build proceeded under explicit DPO instruction with the residual
items disclosed rather than closed.**

## Source-system profiler — fitness for purpose

| CDE | Physical | Fitness |
|---|---|---|
| `batter_name` | `player_name` | ✅ exactly one value after filter |
| `season_year` / `game_month` | `game_year` / `game_date.dt.month` | ✅ 6 buckets in 2026 (**incl. March**) |
| `plate_appearance_key` | `game_pk` + `at_bat_number` | ✅ |
| `pa_result_event` | `events` | ✅ |
| `pitch_result_description` | `description` | ✅ all values map to the governed SWINGS/WHIFFS sets |
| `pitch_number_in_pa` | `pitch_number` | ✅ first-pitch count == PA count every month |
| `pitch_in_zone_flag` | `zone` (`>9` = out-of-zone) | ✅ |
| `exit_velocity` / `launch_angle` | `launch_speed` / `launch_angle` | ⚠ populated on fouls — **O3 from uc-pps-024**; all contact metrics filter `type=='X'` |
| `expected_woba_on_contact` | `estimated_woba_using_speedangle` | ⚠ AP-5 descoped, see below |
| wOBA constants | `wOBA and FIP Constants.csv` | ✅ 2026 row present |

**Population.** `pos` = rows where PHI is batting (`home_team=='PHI' & inning_topbot=='Bot'` OR
`away_team=='PHI' & inning_topbot=='Top'`), excluding `game_type` S/E. 270,954 rows 2015–2026.
Stott: 11,780 pitch rows across 2022–2026.

## Domain steward — rulings applied
1. **SWINGS list** — notebook authority is the 8-value list. Ratified for this build.
2. **`month`** — calendar month from `game_date`. March 2026 is 2 games / 13 PA. **Not merged into April**; retained and flagged.
3. **IBB** — `discipline_ratio` defaults to unintentional-only, per the wOBA convention (`dp_uc24` L222). Stott has no IBB in the streak window, so the two conventions agree here (verified).
4. **AP-5 (results-vs-process divergence) descoped** — its band was uncalibrated at intake and calibrating it is a separate exercise. Contact quality is reported directly instead.

## Window rule — **both framings priced**
Per the Arraez precedent (`uc-pos-008`) when a premise is outcome-selected:
- **Narrative window** — the 11 games / 14 BB / 0 K, Jul 29 → Aug 9. Shipped as illustration.
- **Pre-registered window** — calendar August, and the monthly panel generally. Shipped as evidence.
BB% and K% inside the narrative window are marked **descriptive, not inferential**.
