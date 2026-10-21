# The Sheriff of the Phillies Bullpen
### Tim Mayza's 2026 season recap · LHP reliever · Philadelphia Phillies · 60 games · data through 2026-10-01

**Prepared for:** Pitching department, bullpen staff, front office · Tim Mayza

**Arsenal (2026):** Sinker 57% · Slider 30% · 4-Seam Fastball 12% · Split-Finger 2%

**Governance:** Use Case #52 (`uc-pps-036`) · build `dp_uc52` v1.0.0 · kernel `dp_uc52_kernel.py` imports `dp_uc51_kernel.py` (sha256 `4845bae2…`). New objects (QA-1, BS-1, DS-1, RP-1) are provisional. Independently verified; see `05_quality_certification.md`.

**Companion:** `dp_uc52_mayza_2026_dashboard.html`, the same story in 8 chapters.

> **Read this first: data window, sources, carry-ins.**
>
> - **Entity lock:** MLBAM 641835 (Tim Mayza, LHP), never a name filter. Regular season only: 1,093 pitches, 271 PA, 60 games, 2026-03-28 to 2026-09-25.
> - **Sources:** Phillies Statcast logs (2025-26) and his own pitcher file (Toronto, New York, Pittsburgh, 2017-25), de-duplicated by pitch key. No 2020 rows.
> - **Two wOBA bases.** House wOBA (.285: FanGraphs weights over every PA, errors count as outs) is used for ranks. xwOBA is only ever compared with Statcast-basis wOBA (.299: Statcast's own weights and denominator).
> - **House ranks** compare Phillies pitcher-seasons from 2015 to 2026. They are not MLB-wide.
> - **Runs on watch** = runs that scored during the plate appearances he pitched. It is not ERA.
> - **Postseason** stays in its own ledger: 6 pitches, 1 PA on 2026-10-01, no runs on watch.
> - **Carry-ins, never computed on:** claimed off waivers from Pittsburgh on 2025-08-31 (MLB Trade Rumors); later re-signed to a major-league deal (MLBTR headline; date not verified); his 2027 status is not verified. "The Sheriff" and #37 are from the client.

## 1 · Bottom line
1. **The results were real.** .285 wOBA and .654 OPS allowed, both 3rd-best of his 9 seasons. His xwOBA of .288 sits below the .299 he allowed on the same Statcast basis, so he did not need luck. Among 32 Phillies LHP relief seasons since 2015 (100+ PA) he ranks #11 in wOBA; the median is .304.
2. **He avoided traffic by throwing strikes, not by finishing faster.** Walk rate 5.9% (#6 of 32 Phillies LHP relief seasons), OBP allowed .277. His quick-AB rate of 57.6% beat the house median (55.1%) but was the lowest of his career, by a hair.
3. **The contact is the risk.** Hard-hit rate 45.2%, second only to his rookie year. Right-handed hitters barrelled 7.8% of balls and carried a .314 xwOBA, above the .307 they produced on the same basis.
4. **The delivery is the story.** A high, tight slot and 6.93 ft of extension (85th percentile of Phillies LHP seasons) sell a sinker that runs less than most and a 87.4 mph bullet slider. His nearest delivery comps are Cristopher Sánchez (2021) and José Alvarado (2026).

## 2 · Results: his third-best season

He allowed a .285 wOBA over 271 PA. K% 23.6%, BB% 5.9% and HR% 2.6% all sit inside his own career range. 28 runs scored on his watch across 60 games (0.47 per game, #16 of 32 Phillies LHP relief seasons).

![One of his best seasons, and the expected number is better still](out/dp_uc52_f01_career_woba.png)
*Receipt: out/dp_uc52_f01_career_woba.json · asserts: woba_sc_low==4, xwoba_low==5, woba_low==3, xwoba&lt;woba_sc*

*Top five of 32 Phillies LHP relief seasons by wOBA allowed (2015-26, 100+ PA), plus Mayza 2026.*

| # | Pitcher | Season | PA | wOBA | OPS | BB% | Runs on watch / G |
|---|---|---|---|---|---|---|---|
| 1 | Strahm, Matt | 2024 | 235 | .222 | .499 | 4.3% | 0.38 |
| 2 | Alvarado, José | 2022 | 210 | .258 | .570 | 9.5% | 0.41 |
| 3 | Alvarado, José | 2023 | 172 | .259 | .578 | 9.9% | 0.29 |
| 4 | Morgan, Adam | 2019 | 121 | .262 | .604 | 7.4% | 0.35 |
| 5 | Strahm, Matt | 2025 | 255 | .264 | .607 | 7.5% | 0.35 |
| 11 | **Mayza, Tim** | 2026 | 271 | .285 | .654 | 5.9% | 0.47 |

## 3 · Contact: louder, but priced in

Batters hit the ball harder than in any season since 2017 and lifted it more (average launch angle 7.5°). Barrels stayed moderate (6.4%, 6th-lowest of 9). A barrel-only line through 52 Phillies LHP seasons expects .310 on the house basis, and he allowed .285. xwOBA, which also counts his strikeouts and walks, expects .288 against the .299 he allowed on Statcast's basis. Either way, the results were not borrowed.

![Contact got louder: second-highest hard-hit rate of his career](out/dp_uc52_f02_contact_by_year.png)
*Receipt: out/dp_uc52_f02_contact_by_year.json · asserts: hh_high==2, barrel_low==6*

![On barrels alone he 'should' have allowed .310; he allowed .285](out/dp_uc52_f03_barrel_woba_house.png)
*Receipt: out/dp_uc52_f03_barrel_woba_house.json · asserts: barrel_context.resid&lt;0, n&gt;=30*


## 4 · Platoon: lefties are his, righties are the risk

Lefties managed a .269 wOBA with a 4.7% barrel rate, and their contact deserved even less (.254 expected against .288 actual on Statcast's basis). Righties struck out more (26.3%) and walked more (7.1%), but they also barrelled 7.8% and hit 49% of balls hard. Their .314 xwOBA is higher than the .307 they produced on the same basis.

![Sinker first to both sides; the slider lives below the zone to righties](out/dp_uc52_f04_pitch_map.png)
*Receipt: out/dp_uc52_f04_pitch_map.json · asserts: SI usage &gt; 50% vs both sides*

| Split | PA | wOBA (house) | wOBA (Statcast) | xwOBA | K% | BB% | Hard-hit | Barrel | Quick-AB |
|---|---|---|---|---|---|---|---|---|---|
| vs LHB | 115 | .269 | .288 | .254 | 20.0% | 4.3% | 40.7% | 4.7% | 64.3% |
| vs RHB | 156 | .296 | .307 | .314 | 26.3% | 7.1% | 49.0% | 7.8% | 52.6% |

## 5 · Stuff and delivery: higher, tighter, longer

Arsenal: Sinker 57% · Slider 30% · 4-Seam Fastball 12% · Split-Finger 2%. The four-seam has 13.6 in of ride (29th percentile of Phillies LHP four-seamers). The sinker runs 15.1 in, less than 66% of house LHP sinkers. Released 6.24 ft high (74th percentile) and 1.60 ft wide (22nd percentile, narrower than most), with 6.93 ft of extension. Arm angle 43° (tracked on 76% of 2026 pitches). Mound position is not in Statcast, so the data cannot separate slot from rubber position.

![A sinker that doesn't run much, and a hard slider that barely moves](out/dp_uc52_f05_arsenal_movement.png)
*Receipt: out/dp_uc52_f05_arsenal_movement.json · asserts: BS-1 bullet true; SI usage&gt;50%*

![Not 'bang average': higher, tighter to the body, and deeper down the mound](out/dp_uc52_f06_release_extension.png)
*Receipt: out/dp_uc52_f06_release_extension.json · asserts: ext pct&gt;=80, rel_z pct&gt;=70, rel_x pct&lt;=30*


### The bullet slider

His slider averages 87.4 mph with 1.3 in of horizontal and 1.0 in of vertical break, which makes it a bullet (BS-1: both under 4 in). That is uncommon, not unique: 11 of 37 other Phillies LHP slider seasons qualify, most of them Cristopher Sánchez's. Mayza's is among the hardest (94th percentile for velocity).

![Uncommon, not unique: the bullet slider is Cristopher Sánchez's pitch too](out/dp_uc52_f07_slider_shapes.png)
*Receipt: out/dp_uc52_f07_slider_shapes.json · asserts: BS-1 bullet and n_bullet_others&gt;=1*


## 6 · Weapons by side

Against lefties the sinker did the work: 63% usage, .227 wOBA on PAs it ended. Against righties the slider did: 31% whiffs and a .267 wOBA, thrown low and in on their back foot. The slider to lefties was the soft spot (20% whiffs, .340 wOBA). These cells hold 35 to 81 PA each.

![Two weapons: the sinker against lefties, the slider against righties](out/dp_uc52_f08_weapons.png)
*Receipt: out/dp_uc52_f08_weapons.json · asserts: SI&lt;SL vs L and SL&lt;SI vs R on wOBA*


## 7 · The Mayza Success Rate, revisited

QA-1 counts a plate appearance as a win when he reaches two strikes, or gets a ground ball, within the first three pitches. In 2026 that happened in 57.6% of 271 PA (38.4% reached two strikes, 21.4% ended on an early grounder). The notebook version returned about 40% because it read the count before each pitch, so it only credited two strikes within two pitches. Both are reported; the notebook's figure is graded in the appendix.

![The Mayza Success Rate: 57.6% of PAs went his way within three pitches](out/dp_uc52_f09_quick_ab_rate.png)
*Receipt: out/dp_uc52_f09_quick_ab_rate.json · asserts: 2026 QA-1 above house median*


## 8 · Who throws like him?

DS-1 measures distance across release side and height, extension, and primary-fastball velocity, run and ride over 62 Phillies LHP seasons. The nearest is Cristopher Sánchez's 2021. José Alvarado's 2026 ranks #2, so 'Alvarado lite' holds for the delivery. It does not hold for the results: Alvarado's 2022 and 2023 rank #2 and #3 in the house relief wOBA table, and Mayza's 2026 ranks #11.

![Who throws like him? Sánchez's 2021 delivery, then José Alvarado](out/dp_uc52_f10_comps.png)
*Receipt: out/dp_uc52_f10_comps.json · asserts: Sánchez nearest; Alvarado rank&lt;=3*


## 9 · Your notebook, graded

Each claim was reproduced with your own frames and functions first, then restated on the governed frame. Claims are graded, never overwritten.

| # | Your claim | Verdict | Governed value |
|---|---|---|---|
| HP-01 | Third-lowest wOBA and OPS of his career | **Confirmed** | wOBA #3, OPS #3 of 9 (0.285) |
| HP-02 | Three-true-outcome rates in line with prior seasons | **Confirmed** | K 0.236 · BB 0.059 · HR 0.026 |
| HP-03 | Highest hard-hit rate since his rookie year; more air, more distance | **Confirmed** | HH #2 high; LA #4, distance #5 high of 9 |
| HP-04 | Barrel rate only sixth-lowest, yet third-lowest wOBA | **Confirmed** | barrel #6 low, wOBA #3 low; xwOBA 0.288 vs Statcast-basis wOBA 0.299 |
| HP-05 | Release point 'bang average' among Phillies LHP | **Not Confirmed** | side 22nd, height 74th pct (n=62 seasons) |
| HP-06 | FF doesn't ride, SL doesn't sweep, SI vanilla, splitter unique | **Partly** | FF IVB 13.6 in (29th pct); SL horizontal break 1.3 in (10th pct); SI HB 15.1/IVB 9.4 in; FS: 0 house LHP seasons with 50+ |
| HP-07 | Bullet slider fairly unique among Phillies LHP (Sanchez, Vasquez; maybe Banks, Morgan) | **Partly** | BS-1: 11 other bullet seasons of 37 house LHP slider seasons |
| HP-08 | Slider usage right at 30% | **Confirmed** | 29.8% (regular season) |
| HP-09 | Gets down the mound: elite extension among Phillies LHP | **Confirmed** | 6.93 ft, 85th pct of 62 seasons |
| HP-10 | Slightly better vs LHB; vs RHB more K and BB, 7.8% barrel, 49% hard-hit | **Confirmed** | wOBA L 0.269 / R 0.296; Statcast basis L 0.288 / R 0.307; xwOBA L 0.254 / R 0.314 |
| HP-11 | Sinker pretty much down the middle more than half the time, to both sides | **Partly** | SI in zone L 57% / R 59%; zone 5 L 7% / R 9% |
| HP-12 | SL whiff abnormally low vs LHB, good vs RHB; SL the weapon vs RHB, SI vs LHB | **Confirmed** | SL vs R wOBA 0.267, whiff 31%; SI vs L wOBA 0.227 |
| HP-13 | Career 'success' about 40% over ~1,500 PA | **Confirmed** | QA-1 59.0% over 1603 PA; 2026 57.6% |
| HP-14 | 'Jose Alvarado lite' | **Confirmed** | DS-1: Alvarado 2026 is the #2 nearest delivery/stuff comp |

### Candid caveats
- Relief samples are small: 271 PA for the season and 35 to 156 PA in each split. Read direction, not decimals.
- House populations are Phillies pitchers only. A Phillies-relative rank is not an MLB rank.
- Career seasons 2017 and 2025 are short (<400 pitches). 2025 combines Pittsburgh and his September with the Phillies.
- QA-1, BS-1 and DS-1 are new and provisional. Their thresholds were written down before any results were computed.
- The 2027 roster question is out of scope. His contract status is an unverified carry-in.
