# 06 · Consumer Success — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `analytics-enabler`, `consumer-onboarding-agent`, `dashboard-specifier`, `query-builder`

## Primary persona — Kellen, as requester and bullpen-analytics owner

He arrives with a script already written and a set of beliefs already formed. What he needs is not a
restatement of the script but a **price** on it, and an answer to the one question the note itself raises:
*does this hold?* Three things follow for how the deliverables are shaped:

- The verdict goes first, before any table. He does not need to be walked to the finding.
- Every premise he stated gets an explicit verdict — supported, overstated, or rejected — rather than being
  quietly routed around. Two of his are rejected; a report that softened that would be worthless to him.
- The what-if is interactive, because "does this hold" has a follow-up ("what if I move Shugart up?") that no
  static table can answer.

## Secondary personas (not the requester — read this if the package travels)

| Persona | What they should take from it | What they should not |
|---|---|---|
| **Pitching coach / bullpen coordinator** | The BS-1 tier column and the Holman handedness plan. Alvarado is the arm to protect; Shugart is the arm with length. | The AAA rates. They describe International League hitters. |
| **Advance scout** | The opposing starter's splitter drift (23.4% → 39.4%) and the platoon split (.192 wOBA vs LHB, .419 vs RHB, 47/23 PA). | The identity. It is inferred. Confirm the name before briefing anyone on it. |
| **Front office / roster** | BS-2: seven available arms cover about six and a half innings at their averages. That is a roster question as much as a game question. | The recommended script. That is tonight's judgment, not a policy. |
| **Analytics team** | D-8. Any prior work that called `pitcher_season_workload(relievers_only=True)` and got nothing back got a bug, not a result. | — |

## How to read the deliverables

| Artifact | Read it for | Read it in this order |
|---|---|---|
| `dp_uc43_bullpen_script_report.pdf` | the argument, in full, with caveats attached | 1 |
| `dp_uc43_bullpen_control_room.html` | the what-if: rebuild the script, watch the arithmetic move | 2 |
| `out/dp_uc43_availability_D1.csv` | the ledger you would actually hand to a coach | 3 |
| `out/dp_uc43_multi_inning_propensity.csv` | who can be asked for two | 3 |
| `out/dp_uc43_defect_exposure.csv` | what the governed kernel got wrong under this build | 4 |
| `05_quality_certification.md` | the five conditions attached to the certification | before acting |

## Using the dashboard

1. **Set the framing first.** *Which night was "last night"* is the top-left control and it is not cosmetic —
   it changes five of nine tiers. D+1 is the default because the log supports it.
2. **Then choose a capacity basis.** *His average outing* is the conservative read; *his season high* prices
   the everybody-stretches scenario. The finding lives in the difference between them, so look at both.
3. **Then rebuild the script.** Click an inning, then click an arm. The meter recomputes on every change.
   The thing to notice: giving an arm a second inning **does not move the meter**, because he still makes one
   appearance. That is the arithmetic the whole report turns on, made tactile.
4. **Compare the presets.** *Yours* and *Revised* differ by one swap — the two-inning ask moves off Holman
   and onto Shugart. Under *season high* they price within 0.7 BF of each other. The difference is not the
   number; it is which league the ceiling was set in.
5. **The Holman map** filters by batter side and pitch type. Turn off the four-seam to see the
   splitter/slider plan underneath it.

## Worked example — re-running this for a different game

```python
# 1. Change the anchor. Everything else follows.
ANCHOR   = pd.Timestamp('2026-09-18')
TARGET_A = ANCHOR + pd.Timedelta(days=1)

# 2. Re-declare the pen. MLBAM ids only — never names.
SUBJECTS = {'Mayza, Tim': 641835, 'Duran, Jhoan': 661395, ...}

# 3. Re-run. The D-8 remediation is not optional:
apps = add_rolling_workload(add_rest_days(appearance_summary(load_pps(), mcgs_func=mcgs)))
apps['is_start'] = apps['is_start'].fillna(False).astype(bool)

# 4. The requirement side is club- and season-specific — re-derive it, don't reuse 37:
gm = apps.groupby('game_pk').agg(bf=('batters_faced','sum'), last=('inning_exited','max'))
REQUIRED = gm[gm.last == 9].bf.median()
```

## Persona action note

If you act on one thing tonight, make it the Alvarado line. He is the only arm that is AMBER under both date
framings, he is carrying 61 pitches across four appearances in seven days, he has gone multiple once in
sixty-one outings, and he is scripted for the eighth inning of a bullpen game. Everything else in this package
is an argument about shape. That one is an argument about an arm.

## Reuse patterns worth carrying forward

1. **Price a plan, don't just describe the inputs.** BS-2 turns "nine arms, nine innings" into a number with
   a benchmark. Any future UC that receives a *plan* rather than a *question* should look for the equivalent.
2. **Two capacity modes beat one.** The average mode was true and too loud. Shipping the ceiling alongside it
   made the finding smaller and more defensible — and produced a better headline.
3. **The interactive surface should make the arithmetic tactile, not decorative.** The single most useful
   thing the dashboard does is refuse to move the meter when you give an arm a second inning.
4. **When a KPI can't discriminate, say so and check whether that's the answer.** OP-1 returned one row.
   That null *is* the finding: a two-inning open never reaches a hitter twice.
