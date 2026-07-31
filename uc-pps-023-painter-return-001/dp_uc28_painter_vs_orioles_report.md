# Return Read — Andrew Painter (RHP) vs the Baltimore Orioles
### PHI @ BAL · Oriole Park at Camden Yards · 2026-07-31 · first start back from Triple-A

**Prepared for:** manager / pitching coach / J.T. Realmuto / Andrew Painter — advance meeting
**Throws:** R · **Arsenal:** 6 pitches (4-Seam, Sinker, Slider, Sweeper, Split-Finger, Curveball)
**Governance:** Use Case #29 (`uc-pps-023`), build artifact `dp_uc28`. Locked KPIs inherited verbatim from `dp_uc11` (get_stats/nresults, whiff, chase, putaway, FPSR, hard-hit). Three new KPIs specified this cycle: **Release Consistency Index**, **Fastball Upper-Third Rate**, **Cross-Level Stuff Delta**.

> ⚠️ **Read this first — data window, sample sizes, and what this report is not.**
>
> • **Entity lock:** MLBAM `pitcher == 691725`. No name filtering anywhere in the build.
> • **MLB tier:** `phils_2026.parquet`, `phillies_role=='pitching'`, `game_type=='R'` — **1,141 pitches / 299 PA over 14 starts**, 2026-03-31 → 2026-06-17. (52 spring-training pitches excluded.)
> • **AAA tier:** `lhvp26.parquet` (Lehigh Valley), **396 pitches / 101 PA over 5 starts**, 2026-06-28 → 2026-07-26. Cache current through 2026-07-30.
> • **The two tiers are never blended.** Every rate is computed inside its own level. The AAA sample is **below** the 100-BF convention for publishing pitcher rate stats — every AAA number below is printed with its PA or swing count.
> • **Batted-ball quality is directional only.** `launch_speed` is populated on 36% of pitches (balls in play only) and `estimated_woba` on 26%. No xwOBA headline appears in this report, at either level.
> • **There is no Orioles scouting in this report.** Painter has never faced Baltimore, and the repo holds zero Orioles hitter rows and zero PHI-vs-BAL pitching rows. Rather than fabricate a lineup plan, the opponent section is limited to handedness logic and park context flagged as carry-in. **This is a self-scout, not an attack plan.**
> • **Benchmark population:** 31 right-handed pitchers with ≥150 four-seamers thrown in 2026 Phillies games (Phillies staff plus every opposing RHP), from `phils_2026.parquet`. Small pool — percentiles are directional, not precise.

---

## Bottom line

1. **His stuff was never the problem, and Triple-A did not change it.** Against a 2026 MLB RHP pool, his four-seam sat at the **55th percentile in velocity** (96.5 mph), **52nd in ride** (16.3" IVB), **52nd in extension** (6.48 ft), and **48th in elevation** (54.2% upper-third). Perfectly ordinary shape, thrown to perfectly ordinary places. And it got whiffed at **10.6% per swing — 26th percentile, roughly half the pool median of 20.0%.** Up in the zone, where a 96-with-ride four-seam is supposed to eat: **10.1%, 23rd percentile.** A pitch that good should not miss that few bats.

2. **The most likely reason is that his arm slot moves with the pitch — more than almost anyone's.** Across his six pitch types his mean arm angle spans **13.8°** (curveball 52.1° down to sweeper 38.2°), against a **pool median of 4.25°** and a 90th percentile of 9.9°. That is **the 96th percentile of slot variance in a 23-pitcher pool.** His four-seam and his sweeper leave his hand **6.3 inches apart horizontally**. This is a hypothesis, not a proof — but it is the only thing in the data that reconciles average shape and average location with bottom-quartile bat-missing. **At Triple-A it got wider, not tighter: 15.0°.**

3. **What actually changed at Triple-A was sequencing, not stuff.** Four-seam usage **33.1% → 49.2%** (+16.1 pts), slider **21.4% → 8.3%** (−13.1), sweeper **11.4% → 19.7%** (+8.3), splitter **14.4% → 6.8%** (−7.6). Raw stuff barely moved: +0.6 mph on the four-seam, −0.2" of ride. **He did not fix a pitch. He rebuilt an attack plan around the fastball** — which is the correct instinct, because the thing that broke at the big-league level was abandoning it.

4. **The delivery is still in motion, and that is tonight's biggest unknown.** Across 13 MLB starts his four-seam release point sat in a tight **2.1-inch band**. Then in his final MLB start (6/17) and his first Triple-A start (6/28) it jumped **~5 inches toward the middle of the rubber** — and those were two of his worst outings. He moved back on 7/4 and has stayed back. But across the five AAA starts his slot has been **falling and widening every single time out** (arm angle 47.1° → 40.6°; release 6.5 inches wider) while **extension has dropped every start** (6.45 → 6.29 ft) even as velocity climbed (96.6 → 97.8). **He is throwing harder by reaching, not by getting down the mound.**

5. **The single tonight-specific risk: he shelved his best pitch against left-handed hitters.** The splitter was his most effective MLB weapon vs LHH — **39.5% whiff on 76 swings**, thrown 21.4% of the time. At Triple-A that dropped to **10.6% usage**, replaced by the sweeper (4.4% → 17.6%). His whiff rate against lefties fell to **15.0% (65 PA)** from 21.5% at the big-league level. Against right-handers at AAA he threw **zero** splitters and **zero** curveballs. **If Baltimore stacks lefties, the splitter has to come back tonight.**

---

## What went wrong in the majors

Splitting the 14 MLB starts in half tells a clean story, and it is not a stuff story.

| | First 8 GS (3/31–5/13) | Last 7 GS (5/18–6/17) |
|---|---|---|
| Plate appearances | 172 | 127 |
| **Chase rate** | **.357** | **.265** |
| **In-zone rate** | **.447** | **.522** |
| **4-seam usage** | **.367** | **.277** |
| Whiff/swing | .228 | .216 |
| Strikeout rate | .198 | .150 |
| Walk rate | .070 | .094 |
| wOBA against | .367 | .408 |
| 4-seam velocity | 96.5 | 96.6 |

Velocity is flat to the decimal. What collapsed is **chase — from .357 to .265**. Hitters simply stopped leaving the zone for him. His response was to throw more strikes (in-zone .447 → .522) and *fewer* fastballs (.367 → .277), leaning harder on secondaries into the zone. The strikeouts went away, the walks went **up** anyway, and the damage rose.

That is the profile of a pitcher whose stuff is intact and whose deception isn't.

![Arsenal shape by level](out/dp_uc28_fig1_arsenal_movement.png)

---

## The four-seam problem, benchmarked

This is the section that matters most, because it is the only place where Painter's numbers are genuinely poor rather than merely uneven.

| Four-seam metric | Painter MLB | Pool median | Pool 75th | **Painter percentile** | Painter AAA |
|---|---|---|---|---|---|
| Velocity (mph) | 96.54 | 96.09 | 97.54 | **55th** | 97.18 |
| Induced vertical break (in) | 16.27 | 16.22 | 17.71 | **52nd** | 16.02 |
| Extension (ft) | 6.48 | 6.47 | 6.69 | **52nd** | 6.38 |
| Upper-Third Rate *(new KPI)* | .542 | .542 | .610 | **48th** | .508 |
| **Whiff / swing** | **.106** | **.200** | **.303** | **26th** | **.212** |
| **Whiff / swing, upper third** | **.101** | **.250** | **.344** | **23rd** | **.259** |

*Population: 31 RHP with ≥150 four-seamers in 2026 Phillies games.*

Everything about the pitch is average except the one thing that counts. And the location breakdown makes it worse, not better:

| Four-seam whiff/swing | MLB | AAA |
|---|---|---|
| Heart of the zone | **.091** (121 swings) | .167 (84 swings) |
| Shadow (edges) | **.074** (27 swings) | .357 (14 swings) |
| Chase zone | .185 (27 swings) | .182 (11 swings) |
| **Upper third or above** | **.101** (99 swings) | **.259** (54 swings) |
| Lower two thirds | .111 (81 swings) | .169 (59 swings) |

**Read the last two rows carefully.** At the major-league level, elevating the fastball did *nothing* — .101 up versus .111 down. The standard prescription for a high-ride four-seam simply did not work for him. At Triple-A it started working: .259 up versus .169 down.

The honest caveat: **.212 against Triple-A hitters is exactly the median MLB four-seam whiff rate (.200).** His minor-league fastball, against minor-league hitters, performs like a league-average big-league fastball. That is progress from .106. It is not a weapon yet.

![Usage versus bat-missing](out/dp_uc28_fig5_usage_whiff.png)

---

## The tipping hypothesis

Painter's arm angle by pitch type, both levels:

| Pitch | MLB arm angle | MLB release-x | AAA arm angle | AAA release-x |
|---|---|---|---|---|
| Curveball | 52.1° | −24.6" | 50.2° | −23.4" |
| Sinker | 49.7° | −24.6" | 46.2° | −24.9" |
| **4-Seam** | **48.4°** | **−25.4"** | **46.2°** | **−24.3"** |
| Split-Finger | 46.1° | −26.8" | **40.9°** | **−28.0"** |
| Slider | 43.9° | −28.0" | 43.0° | −25.8" |
| **Sweeper** | **38.2°** | **−31.7"** | **35.3°** | **−31.6"** |
| **Spread** | **13.8°** | 7.1" | **15.0°** | 8.2" |

Against the benchmark pool, a spread of 13.8° is the **96th percentile** (median 4.25°, 90th percentile 9.9°, n=23). Only one pitcher in the pool separates his slots more.

Two things deserve emphasis, in both directions:

- **This is not proof.** Statcast's `arm_angle` is derived from release coordinates, so some spread is the unavoidable consequence of different grips and intents — every pitcher's sweeper releases lower than his four-seam. The pool comparison is what makes it interesting: *his spread is three times the median.*
- **It got worse at Triple-A, in a specific way.** His splitter moved from 46.1° to 40.9° — it left the fastball cluster and joined the breaking balls. That pitch's entire value is that it looks like a fastball out of the hand. **A splitter released 5° flatter than the four-seam is a splitter the hitter can identify.**

This is testable tonight, and it should be tested.

---

## What Triple-A actually changed

### Usage — the real adjustment

| Pitch | MLB usage | AAA usage | Change | MLB whiff | AAA whiff |
|---|---|---|---|---|---|
| 4-Seam Fastball | 33.1% | **49.2%** | **+16.1** | .106 | .212 |
| Slider | 21.4% | **8.3%** | **−13.1** | **.377** | .263 |
| Split-Finger | 14.4% | **6.8%** | **−7.6** | **.384** | .357 |
| Sweeper | 11.4% | **19.7%** | **+8.3** | .210 | .303 |
| Sinker | 10.8% | 9.6% | −1.2 | .087 | .053 |
| Curveball | 8.9% | 6.3% | −2.6 | .250 | .167 |

He cut usage on his **two best MLB bat-missers** — the slider (.377 whiff on 244 pitches) and the splitter (.384 on 164) — and reallocated to the fastball and the sweeper. Note the sweeper earned it: at AAA it posted a **.410 CSW rate**, the highest of any pitch at either level.

The slider/sweeper tags are consistent enough across the two feeds to trust this. Sliders average −6.3" and −6.9" of horizontal break at MLB and AAA respectively; sweepers −15.7" and −15.8". These are distinct pitches in both feeds, not a tagging artifact.

Where each pitch is being thrown changed too — most sharply for the splitter, which he went from throwing near the zone (46.3% in-zone at the big-league level) to burying (18.5% at Triple-A, 40.7% of them in the waste tier):

![Location tier mix by level](out/dp_uc28_fig4_location_tiers.png)

### Stuff — barely moved *(new KPI: Cross-Level Stuff Delta)*

| Pitch | Δ velo | Δ spin | Δ ride | Δ horizontal | Verdict |
|---|---|---|---|---|---|
| 4-Seam | +0.64 | +84 | −0.25 | −0.55 | velocity real, shape unchanged |
| Sinker | +0.19 | +35 | −1.70 | −0.89 | flatter, marginal |
| Slider | −0.61 | +114 | −2.28 | −0.57 | flatter, shelved anyway |
| Sweeper | +0.08 | +118 | −1.19 | −0.08 | unchanged shape, more usage |
| **Split-Finger** | **+2.75** | **+94** | −1.00 | **+2.43** | **materially different pitch** |
| Curveball | −0.13 | +1 | −1.62 | −0.22 | unchanged |

*AAA minus MLB. Deltas under 0.5 mph and 1.0 inch sit inside cross-park measurement noise.*

Only the **splitter** changed meaningfully — and not obviously for the better. It gained 2.75 mph and 2.4 inches of arm-side run, which compressed its separation from the fastball:

| Separation from 4-seam | MLB | AAA | Change |
|---|---|---|---|
| **Split-Finger** | **9.13 mph** | **7.03 mph** | **−2.11** |
| Slider | 8.44 | 9.69 | +1.25 |
| Sweeper | 13.57 | 14.13 | +0.56 |
| Curveball | 15.40 | 16.17 | +0.77 |
| Sinker | 1.38 | 1.83 | +0.45 |

A splitter seven miles per hour off the fastball, released five degrees flatter than the fastball, is not the same weapon that produced a .384 whiff rate in the majors.

The spin increases (+84 to +118 rpm on four of six pitches, but **+1 rpm on the curveball**) are hard to attribute. A uniform calibration offset between the minor- and major-league Hawk-Eye installs should have moved the curveball too. Flagged as unexplained; not load-bearing for any conclusion here.

### The arc within Triple-A — genuinely better late

| | Early: 6/28, 7/4 (37 PA) | Late: 7/10, 7/21, 7/26 (64 PA) |
|---|---|---|
| Strike rate | .617 | **.660** |
| CSW rate | .195 | **.275** |
| Chase rate | .321 | **.354** |
| First-pitch strike | .595 | **.672** |
| **Hard-hit rate** | **.458** (24 BIP) | **.273** (44 BIP) |
| Upper-Third Rate | .444 | **.553** |
| K / BB | 10 / 3 | 15 / 5 |
| 4-seam velocity | 96.9 | 97.4 |

Every process indicator moved the right way, and the best of the five starts was **7/21 — 73.6% strikes, 34.5% CSW, 52.3% chase, 8 K, 1 BB.** The one wobble was 7/10 (54.3% strikes, 4 walks, 7.1% whiff), which is also the start immediately after he moved his release point back.

---

## The delivery — the live variable

![Velocity and extension by start](out/dp_uc28_fig2_velo_by_start.png)

Two trends are running in opposite directions, and they should not be.

**Velocity is up.** Four-seam average by AAA start: 96.6 → 97.4 → 97.6 → 96.8 → **97.8**. Top-end 99.1.

**Extension is down, every single start:** 6.451 → 6.397 → 6.337 → 6.334 → **6.293 ft.** That is roughly **two inches lost across five starts**, on top of the four-plus inches already given back from his early-April peak of 6.64.

The consequence is that the radar gun overstates the gain. Perceived velocity — Statcast's `effective_speed`, which credits extension — adds **+0.31 mph** to his MLB four-seam but only **+0.22** to his AAA four-seam. Of the +0.64 mph of raw velocity he has gained, roughly a sixth is handed straight back at the release point.

![Release drift and consistency](out/dp_uc28_fig3_release_drift.png)

**The release-point event.** Across 13 MLB starts his four-seam release sat between −24.7" and −26.8" — a 2.1-inch band. Then:

| Start | Level | 4-seam release-x | Note |
|---|---|---|---|
| … 13 MLB starts … | MLB | −24.7" to −26.8" | tight, stable |
| **2026-06-17** | MLB | **−20.5"** | last start before being optioned (12 four-seams — directional) |
| **2026-06-28** | AAA | **−20.05"** | first Triple-A start (44 four-seams — solid) |
| 2026-07-04 | AAA | −25.3" | back in the old band |
| 2026-07-10 | AAA | −25.6" | |
| 2026-07-21 | AAA | −25.8" | best start of the stint |
| 2026-07-26 | AAA | −25.3" | |

**This is mechanical, not measurement.** The 6/28 and 7/10 starts were both played at Lehigh Valley — the same park, the same camera install — and their release points differ by 5.6 inches. A park calibration difference cannot produce that.

So there is a clean two-start signature (6/17 and 6/28) where he drifted five inches toward the middle of the rubber, and those were two of the shakiest outings in the sample. He corrected it and has held the correction for three starts.

**But the slot is still moving.** Measured across all pitches, his arm angle has fallen every start of the AAA stint: **47.1° → 45.4° → 44.0° → 42.2° → 40.6°**, and his average release has widened from −20.9" to −28.5". Some of that is the sweeper usage increase pulling the average. Not all of it. **Release Consistency Index** — the within-start dispersion of his four-seam release, in inches — is essentially unchanged (MLB mean ≈ 1.16", AAA ≈ 1.20"), so he is repeating whatever he is doing on a given night. He is just not doing the same thing from night to night.

---

## Platoon — the lefty question

| | MLB vs LHH | MLB vs RHH | AAA vs LHH | AAA vs RHH |
|---|---|---|---|---|
| Plate appearances | 185 | 114 | **65** | **36** |
| Whiff / swing | .215 | .237 | **.150** | **.351** |
| Chase rate | .317 | .332 | .341 | .343 |
| In-zone rate | .511 | .423 | .459 | .504 |
| CSW rate | .280 | .239 | .216 | .298 |
| Putaway rate | .166 | .158 | .151 | .286 |
| Hard-hit rate | .367 | .325 | .277 | **.476** |
| wOBA against | .384 | .385 | .363 | .287 |

**Usage against left-handed hitters:**

| Pitch | MLB vs LHH | AAA vs LHH | MLB whiff vs LHH |
|---|---|---|---|
| 4-Seam | 38.9% | 48.6% | — |
| **Split-Finger** | **21.4%** | **10.6%** | **.395 (76 swings)** |
| Slider | 19.5% | 6.3% | — |
| Curveball | 13.5% | 9.8% | — |
| **Sweeper** | **4.4%** | **17.6%** | — |
| Sinker | 2.3% | 7.1% | — |

He swapped his best left-handed weapon for his worst one. The splitter — 39.5% whiff on 76 major-league swings against lefties, comfortably his most reliable put-away pitch — went from a fifth of his pitches to a tenth. The sweeper, which for a right-hander breaks *toward* a left-handed hitter's barrel, quadrupled.

His whiff rate against lefties at Triple-A: **15.0%.** That is the lowest platoon number anywhere in this report.

Against right-handers at Triple-A he threw **zero splitters and zero curveballs** — four-seam plus sweeper accounted for **73.8%** of his pitches. It produced a fine whiff rate (.351) and an alarming hard-hit rate (.476 on 21 tracked balls in play — small, directional).

---

## Times through the order

| Level | Pass | PA | Whiff | Chase | CSW | **Hard-hit** | wOBA |
|---|---|---|---|---|---|---|---|
| MLB | 1st | 127 | .227 | .320 | .264 | **.315** | .372 |
| MLB | 2nd | 122 | .216 | .325 | .259 | **.359** | .430 |
| MLB | 3rd+ | 50 | .235 | .330 | .276 | **.429** | .303 |
| AAA | 1st | 45 | .283 | .345 | .277 | **.261** | .240 |
| AAA | 2nd | 44 | .184 | .288 | .220 | **.353** | .373 |
| AAA | 3rd+ | 12 | .160 | .600 | .182 | **.455** | .563 |

The results columns are noisy — MLB wOBA actually *falls* on the third pass, on 50 PA. The process column is not: **hard-hit rate climbs on every pass at both levels**, .315 → .359 → .429 in the majors and .261 → .353 → .455 at Triple-A. The bats get on him progressively, even when the outcomes haven't caught up yet.

Third-time-through samples are small at both levels. Treat this as a lean, not a law.

---

## Baltimore and the ballpark — what we do and don't have

**We have nothing on the Orioles.** No hitter cache in the repo, no prior Painter-vs-Baltimore pitches, no confirmed lineup carried in. Everything below is handedness logic applied to Painter's own splits, plus general park knowledge flagged as carry-in. **No number in this section comes from Orioles data, because there isn't any.**

- **If the lineup leans left-handed**, the splitter question becomes the game. His MLB record against lefties with that pitch (.395 whiff, 76 swings) is the best evidence in this report; his Triple-A record without it (.150 whiff, 65 PA) is the worst.
- **If the lineup leans right-handed**, the four-seam/sweeper pairing he built at Triple-A is the plan he has been rehearsing — but it is also where his hard contact lives (.476 at AAA, small sample), and the arm-slot gap between those two exact pitches is his widest (10.2° at MLB, 10.9° at AAA).
- **Camden Yards** *(carry-in, not computed)*: the left-field wall was pushed back and raised in 2022, which suppresses right-handed pull power; the right-field line remains short. For a right-hander whose damage risk is elevated fastballs and hung breaking balls, the park is friendlier to mistakes to left than to mistakes that pull left-handed hitters to right.

---

### The single attack rule

**Fastball first, splitter to lefties, and never show the sweeper twice in a row to the same hitter.**

---

## Game-plan takeaways

**For Painter**

1. **Lead with the fastball.** The Triple-A re-sequencing (49.2% four-seam) is the correct instinct. The failure mode in the majors was the opposite — 27.7% four-seam over the final seven starts, with the strikeout rate falling to .150.
2. **Elevate to about 55%, not more.** His best Triple-A block ran a .553 Upper-Third Rate. The pool 75th percentile is .610, and he has never converted elevation into whiffs at the major-league level. Earn it before you push past it.
3. **Stop reaching for the extra tick.** Velocity is up 0.6 mph while extension is down nearly two inches across the stint. In perceived terms that trade is close to break-even, and it costs deception. Get down the mound.

**For J.T. Realmuto**

4. **The splitter is the out pitch against lefties — not the sweeper.** .395 whiff on 76 major-league swings. Call it down and arm-side with two strikes; at Triple-A he threw it in the zone only 18.5% of the time and still generated a .409 chase rate. It works when it's buried.
5. **Do not run four-seam into sweeper back-to-back to the same hitter early in the game.** Those two pitches leave his hand 6.3 inches apart with a 10-degree arm-angle gap — the widest separation in his arsenal. Break up the pattern with the sinker or the slider, which sit between them.
6. **Watch the release in the first inning.** If the four-seam is coming out around −20 inches instead of −25, that's the 6/17 and 6/28 signature — the two shakiest starts in the sample. Get it to the dugout before the second time through.

**For the pitching department**

7. **Arm-slot uniformity is the highest-leverage cue available.** 13.8° of spread across his arsenal, against a pool median of 4.25° — 96th percentile. This is the only finding that explains average shape, average location, and 26th-percentile bat-missing at the same time. Everything else in his profile says the fastball should work.
8. **Test the tipping hypothesis tonight, deliberately.** Log first-pitch swing rates and whiff-by-pitch following same-slot versus different-slot sequences. One start won't settle it, but the instrumentation costs nothing and the question is worth a real answer.
9. **The splitter needs a decision.** It gained 2.75 mph and lost two miles of separation from the fastball, and its release dropped five degrees flatter — moving it from the fastball cluster into the breaking-ball cluster. Either pull the velocity back toward 87–88 and restore the slot match, or accept it as a hard arm-side pitch and stop asking it to be a chase weapon. It cannot be both.
10. **Extension is the quiet regression.** 6.64 ft in early April, 6.29 ft on 7/26. That is a real and monotonic loss, and it is happening while he throws harder.

**For the manager**

11. **Plan for 85–90 pitches, five or six innings.** His Triple-A counts were 80, 69, 70, 87, 90. He is stretched to roughly 90 and no further.
12. **Leash markers, in priority order:** (a) four-seam release drifting toward −20 inches; (b) chase rate under 25% through two innings — .265 chase over the final seven MLB starts is precisely the number that got him optioned; (c) hard contact, which climbs every time through the order at both levels and is the one weakness that has never gone away (.352 MLB, .338 AAA — both above average).
13. **Have someone warm before the third time through.** The results don't scream it, but the contact quality does: .315 → .359 → .429 hard-hit in the majors, .261 → .353 → .455 at Triple-A. If the slot-variance theory is right, the third look is exactly where it should bite.

---

## Candid data-window and freshness caveats

- **The Triple-A sample is 101 plate appearances.** That is below the 100-BF publishing convention only barely, and well below what anyone should want for a platoon split. The vs-LHH figure (.150 whiff) rests on **65 PA**; the vs-RHH hard-hit figure (.476) rests on **21 tracked balls in play**. Both are printed because they are directionally alarming, not because they are settled.
- **The 6/17 release-point reading rests on 12 four-seams.** It is the corroboration for 6/28 (44 four-seams), not independent evidence. If you drop 6/17 entirely, the finding survives on the AAA data alone.
- **No expected-outcome metrics appear in this report.** `estimated_woba_using_speedangle` is 26% populated and, per the standing repo fix from UC-PPS-021, is not trustworthy at pitch level. Contact conclusions rest on `launch_speed` and hard-hit rate only.
- **Cross-level spin deltas are unexplained.** Four pitch types gained 84–118 rpm at Triple-A while the curveball gained 1. No conclusion in this report depends on spin.
- **The benchmark pool is 31 pitchers (23 for arm spread), drawn only from 2026 Phillies games.** It is not a league-wide population. Percentiles are directional. The gap between Painter's 13.8° and the 4.25° median is large enough to survive a wider pool; the exact percentile is not.
- **Zero Orioles data.** Recorded as a FAIL on opponent coverage in the DQ scorecard and classified non-blocking, because this use case was scoped as a self-scout. If an attack plan is wanted, it needs an Orioles cache built first.
- **Camden Yards park notes are carry-in domain knowledge, not repo-computed.** They are flagged as such in the text and carry no numbers.
- **Tonight's Baltimore lineup was not retrieved** and nothing has been assumed about it.

**Artifacts.** Build script `dp_uc28_painter_vs_orioles.py`; 23 CSV receipts and 5 figures in `out/dp_uc28_*`; DQ scorecard `out/dp_uc28_dq_scorecard.csv`; freshness manifest `out/dp_uc28_freshness_manifest.csv`; console receipt `out/dp_uc28_console_receipt.txt`. Governance trail in `Agents for Data Products/data-products/uc-pps-painter-return-001/`.

**Closure step.** Post-game backtest — compare tonight's actual pitch mix, four-seam release point, arm-angle spread, and whiff-by-location against the projections above. The tipping hypothesis in particular should be marked supported, unsupported, or still open.
