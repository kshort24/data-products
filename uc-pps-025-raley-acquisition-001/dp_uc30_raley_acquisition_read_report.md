# Acquisition Read — Brooks Raley (LHP)
### Trade-deadline intake dossier · Philadelphia Phillies · 2026-08-04 · first look at a pitcher the organization has never worked with

**Prepared for:** manager / pitching coach / catchers / Raley — intake meeting
**Throws:** L · **Age:** 38 (`age_pit`, 2026) · **Arsenal:** 4 pitches (sweeper, cutter, sinker, changeup)
**Governance:** Use Case #31 (`uc-pps-025`, build `dp_uc30`). Locked KPI functions inherited verbatim from `dp_uc29` (Kilian acquisition read). Four NEW KPIs specified before use: Release Slot Angle (RSA), Release Distinctiveness Index (RDI), Sightline Offset (SLO), Release Tipping Delta (RTD). DQ scorecard: **38/38 PASS**.

> ⚠️ **Read this first — data window & sample sizes.**
>
> * **Source:** `data/opponents/raley.parquet`, entity-locked to `pitcher == 548384`, regular season only, deduped. 4,184 pitches, 2020-07-24 → **2026-08-02** (T-2 as of build).
> * **He has thrown zero pitches for the Phillies.** Every 2026 row in the cache is Mets. This is an intake dossier, not a self-scout — there is no in-org baseline and no assigned role yet.
> * **The history is split at Tommy John surgery and the two halves are never blended.** Pre-TJ = 2020-07-24 → **2024-04-19** (last outing before surgery), 3,162 pitches / 770 BF. Post-TJ = **2025-07-19** (return) → 2026-08-02, 1,022 pitches / 269 BF. The 15-month rehab interval is a true gap and is never interpolated.
> * **Post-TJ is the forward-looking tier and it is small: 269 batters faced.** It clears the 100-BF publication threshold but every rate below carries real error bars. Splits within it (vs LHH = 100 BF) are directional.
> * **His 2015–2019 KBO seasons are outside Statcast and outside this repo.** A recorded gap, not a zero.
> * **Benchmark population:** all Phillies left-handed pitchers, 2015–2026, with ≥300 tracked pitches — **n = 28**. Raley is scored *against* this population, never included in its centroid.
> * **Bat-tracking fields (bat speed, swing length) exist only from 2023**, so the pre-TJ tracking numbers cover a fraction of that era. Miss-distance samples are tiny (32 LHH whiffs, 61 RHH whiffs post-TJ) and are labelled wherever used.

---

## Bottom line

**1. The results are real, but they are outrunning the contact.** Post-TJ he has held hitters to **.185/.257/.273, a .239 wOBA**, with 2 home runs in 269 batters faced. Underneath that: **hard-hit rate has risen from 26.2% to 33.1%** and expected wOBA on contact is **.307**. A 0.7% home-run rate on 33% hard contact is not a skill you can bank. Buy the pitcher; do not buy the .239.

**2. He is missing meaningfully fewer bats than the pitcher you remember.** Whiff rate has fallen **29.9% → 21.9%**. It is almost entirely one pitch: **the sweeper went from 37.2% whiff to 23.2%**, and the shape moved with it — it has **gained 2.3 inches of induced vertical break** (2.5 → 4.8 in), which is to say it lost depth. The velocity is fine (85.4 → 85.0 mph, and July 2026 was his hardest-throwing month post-surgery at 86.4). This is a shape problem, not a health problem.

**3. The funky-look hypothesis is correct, and the surgery made it funkier.** His release slot **dropped and widened** post-TJ (Release Slot Angle 63.6° → 60.8°; release point moved 3.7 inches further toward the arm side). At 60.8° he owns the **5th-lowest slot among 30 Phillies left-handers since 2015** — below Hamels, Suárez, Sánchez, Luzardo, Strahm, Alvarado, and every other lefty in the org's recent history except Milner, Backhus, Vargas and Diekman.

**4. Against a left-handed hitter, the ball leaves his hand essentially on that hitter's own eye line.** Sightline Offset vs LHH is **0.08 ft — about one inch** — against a Phillies-LHP population average of **0.96 ft (11.5 in)**. The ball appears from behind the LHH's front shoulder. Against right-handers the same geometry produces the opposite extreme: **6.34 ft of cross-body travel**, the widest kind of look, and that is where the damage lives (xwOBAcon **.349 vs RHH**, **.239 vs LHH**).

**5. The one change that pays for itself immediately: stop leading on the sweeper to right-handers with two strikes.** In two-strike counts vs RHH he throws the sweeper 44.7% of the time for an **11.5% whiff rate** and puts 60.2% of them in the zone. In the same counts his **cutter whiffs 48.0% and puts hitters away 30.0%** — and he uses it only 20.3% of the time. That is the game plan in one line.

---

## What he was, and what he is now

Everything below is split at the surgery. Never quote a blended Raley number.

| | Pre-TJ (2020–2024) | Post-TJ (2025–2026) | Δ |
|---|---|---|---|
| Window | 2020-07-24 → 2024-04-19 | 2025-07-19 → 2026-08-02 | |
| Outings / pitches / BF | 213 / 3,162 / 770 | 75 / 1,022 / 269 | |
| **BA / OBP / SLG** | .205 / .286 / .320 | **.185 / .257 / .273** | better |
| **wOBA** | .271 | **.239** | −.032 |
| K% / BB% | 29.0% / 8.1% | 24.2% / 7.4% | K down |
| HR rate | 2.1% | **0.7%** | 2 HR in 269 BF |
| **Whiff %** | 29.9% | **21.9%** | **−8.0 pts** |
| Chase % | 30.9% | 29.2% | flat |
| Zone % (strict) | 46.3% | 50.2% | +3.9 pts |
| CSW % | 31.0% | 29.5% | −1.5 pts |
| First-pitch strike % | 63.6% | 64.3% | flat |
| **Hard-hit %** | 26.2% | **33.1%** | **+6.9 pts** |
| **xwOBAcon** | .350 | .307 | −.043 (178 BIP) |
| Avg velocity | 85.4 | 85.0 | −0.4 mph |
| Arm angle (native) | 33.5° | **31.5°** | slot dropped |
| Release side / height | 2.82 / 5.69 ft | **3.13 / 5.60 ft** | wider + lower |

**The honest read.** Three of these move together and tell one story: fewer whiffs, more strikes in the zone, harder contact. He has traded some swing-and-miss for control of the count. That is a normal and often sensible age-38 post-surgery adaptation — and it is a *fragile* one, because it makes him more dependent on contact management and on the defense behind him. The .239 wOBA is what happens when a 33%-hard-hit profile also runs a 0.7% home-run rate. Regression to something like a .290–.310 wOBA is the sober expectation, which is still a useful late-inning reliever.

**The health signal is good.** Velocity is stable across the post-TJ window and his highest-velocity month (86.4 mph, July 2026) is his most recent full one. There is no decay pattern in the monthly arc. What *is* drifting is bat-missing: 26.7% whiff in May 2026 → 21.1% in June → 17.0% in July, while chase rate rose over the same span (28.1% → 35.2%). He is getting more swings at balls and fewer misses on them — consistent with a breaking ball that is no longer finishing.

---

## The arsenal

Four pitches post-TJ. The curveball and four-seamer he threw pre-surgery are gone (0 thrown since the return) — a 6-pitch mix has become a 4-pitch mix.

### Post-TJ arsenal

| Pitch | Usage | Velo | IVB (in) | HB (in) | Whiff % | Chase % | CSW % | Putaway % | Hard-hit % | xwOBAcon (BIP) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Sweeper** | 39.4% | 80.9 | +4.8 | −16.8 | 23.2% | 31.4% | 30.7% | 25.0% | 37.1% | .361 (70) |
| **Cutter** | 25.1% | 86.7 | +6.4 | −3.8 | 24.8% | 33.6% | 29.7% | 25.5% | 28.9% | .237 (45) |
| **Sinker** | 22.7% | 90.3 | +4.5 | +17.0 | 13.0% | 16.3% | 33.8% | 13.0% | 47.1% | .297 (34) |
| **Changeup** | 12.8% | 84.2 | −0.3 | +17.2 | 22.4% | 33.3% | 18.5% | 15.9% | 13.8% | .292 (29) |

**What changed in the shapes.** The **sweeper flattened**: +2.3 inches of IVB versus pre-TJ, and whiff fell from 37.2% to 23.2%. It still sweeps (−16.8 in of horizontal break, essentially unchanged) but it no longer dives, and a sweeper that stays on plane is a sweeper hitters can cover. The **changeup gained depth** (+1.7 → −0.3 in IVB) and is now his cleanest contact-suppression pitch (13.8% hard-hit, .292 xwOBAcon) — but it is only usable against right-handers and he throws it 12.8% of the time. The **cutter and sinker are unchanged** in velocity and shape.

**The sinker is the problem pitch on contact:** 47.1% hard-hit, 13.0% whiff, 16.3% chase. It is a strike-getter and nothing else.

---

## The signature: where the ball comes from, and what hitters do with that

This is the section the pitching department asked for. The question was whether Raley's release point is genuinely unusual, and whether it changes how hitters pick the ball up.

### He sits in the bottom fifth of the organization's left-handed history

Release Slot Angle (RSA) is a geometric proxy — the angle from the rubber-centre origin up to the release point, viewed from behind. Lower means lower and wider. It exists because Statcast's native `arm_angle` field is only present in this repo from 2025 onward, and the benchmark the consumer asked for spans 2015–2026.

| Rank (low → high) | Pitcher | Release side (ft) | Release height (ft) | RSA (°) |
|---|---|---|---|---|
| 1 | Hoby Milner | 3.83 | 4.51 | 49.7 |
| 2 | Kyle Backhus | 3.15 | 4.25 | 53.5 |
| 3 | Jason Vargas | 3.25 | 5.36 | 58.8 |
| 4 | Jake Diekman | 3.33 | 5.62 | 59.3 |
| **5** | **Raley — post-TJ** | **3.13** | **5.60** | **60.8** |
| 9 | *Raley — pre-TJ* | *2.82* | *5.69* | *63.6* |
| 12 | Matt Strahm | 2.33 | 5.41 | 66.7 |
| 13 | Jesús Luzardo | 2.45 | 5.76 | 67.0 |
| 18 | Ranger Suárez | 2.11 | 5.85 | 70.2 |
| 22 | Cristopher Sánchez | 1.90 | 6.06 | 72.6 |
| 29 | José Alvarado | 1.15 | 6.55 | 80.0 |
| 30 | Bailey Falter | 0.91 | 5.73 | 81.0 |

*(Full 30-row table in `out/dp_uc30_lhp_release_benchmark.csv`; population mean release side 2.30 ft, mean height 5.87 ft.)*

Raley moved **four places lower** on this list after surgery. Whatever the rehab did to his delivery, it dropped and widened the slot — and against left-handed hitters that is a gift.

### Sightline Offset — the number that makes "funky" concrete

Sightline Offset is the lateral distance between the release point and the centre of the batter's box the hitter is standing in. It answers "how far across my body does this ball start?"

| | Raley post-TJ | Raley pre-TJ | Phillies LHP population (n=28) |
|---|---|---|---|
| **vs LHH** | **0.08 ft (≈1 in)** | 0.39 ft | 0.96 ft (≈11.5 in) |
| **vs RHH** | **6.34 ft** | 6.03 ft | 5.51 ft |

Against a left-handed hitter the ball leaves his hand almost exactly on that hitter's own line — it emerges from behind the front shoulder, which is the textbook reason low-slot lefties are uncomfortable at-bats for left-handed hitters. Against a right-hander the identical geometry produces a 6.3-foot cross-body path: a long, clean, early look, with the ball travelling across the hitter's field of view rather than at him.

> **Method note.** The population figures above and Raley's are computed the same way — from each pitcher's mean release point — so they are directly comparable. Computed pitch-by-pitch and then averaged, Raley's post-TJ vs-LHH figure is 0.19 ft rather than 0.08 ft, because pitch-to-pitch scatter around a near-zero mean can only push the average up. Both forms are in `out/dp_uc30_sightline.csv`. The conclusion is identical at either figure.

### Does it actually change how hitters track him?

Partially yes, and the honest answer is more nuanced than the geometry alone suggests.

| Post-TJ | vs LHH | vs RHH |
|---|---|---|
| Whiff % | 20.6% | 22.6% |
| **Miss distance on whiffs (in)** | **3.76** (n=32) | **2.45** (n=61) |
| Swing length (ft) | 7.24 (n=162) | 7.38 (n=287) |
| Bat speed (mph) | 69.5 | 69.8 |
| **xwOBAcon** | **.239** (67 BIP) | **.349** (111 BIP) |
| Hard-hit % | 28.4% | 36.0% |

**He does not miss more left-handed bats — but when left-handers miss, they miss by 53% more distance** (3.76 vs 2.45 inches). Pre-TJ that gap was 3.58 vs 3.01 inches; it widened as the slot dropped. Left-handers also shorten up on him (7.24 ft of swing length vs 7.38 vs RHH). The picture is a hitter who is defensive and imprecise rather than one who is being blown away — which is exactly what the contact-quality split says too: **.239 xwOBAcon vs LHH against .349 vs RHH.**

**Read this cautiously.** Miss distance rests on 32 and 61 whiffs. It is corroborating evidence for a geometric argument, not a finding that stands on its own.

### One of my own metrics does not support the headline, and that is worth saying

The **Release Distinctiveness Index** — how far a pitcher's release point sits from the population centroid, in standard deviations — puts Raley post-TJ at **1.26 against a population average of 1.20**. By that measure he is *perfectly ordinary*. The reason is that RDI is a distance and ignores direction: Alvarado (2.03) and Falter (1.99) are just as far from the centre, in the opposite direction. **Raley's distinctiveness is directional, not distance-based.** RSA and Sightline Offset carry the argument; RDI does not, and should not be cited in support of it.

### Tipping check — a small, real flag

Release Tipping Delta post-TJ is **5.3 inches** — the largest gap between any two pitch-type mean release points — against within-pitch-type noise of about 2.3 inches. Specifically, **the sweeper is released about 3.2 inches wider and 4.0 inches lower than the cutter** (and 3.4 in wider, 2.6 in lower than the sinker).

This is a genuine but modest signal, and it is *improving*: pre-TJ the same figure was 7.7 inches. Still, at a slot this wide, a 5-inch separation on his most-used pitch is findable by a decent advance department. Worth a bullpen session and a video check before it becomes a scouting report on him.

---

## The approach, by batter hand

He is **not** a left-handed specialist and should not be used as one. Post-TJ he threw **661 pitches to right-handers and 361 to left-handers**, and **70 of his 75 outings included at least one right-handed hitter**.

### vs LHH — 100 BF, .213 wOBA, .239 xwOBAcon

| Pitch | Usage | Whiff % | Chase % | Zone % | Putaway % | Hard-hit % | xwOBAcon (BIP) |
|---|---|---|---|---|---|---|---|
| Sweeper | 40.3% | 27.1% | 38.6% | 42.4% | 26.4% | 13.8% | .210 (29) |
| Sinker | 31.4% | 7.1% | 18.4% | 56.2% | 10.0% | **55.0%** | .334 (20) |
| Cutter | 25.8% | 20.5% | 25.0% | 56.5% | 0.0% | 23.5% | .176 (17) |

*No changeup vs LHH — correctly.*

**The plan against left-handers is already close to right.** The sweeper is the pitch: he lands 42.4% of them in the zone (i.e. most of them finish off the plate, which is where a sweeper belongs), left-handers chase it 38.6% of the time, and it produces a .210 xwOBAcon. With two strikes he goes to it **75% of the time for a 38.6% whiff rate** — the best two-strike combination he has against either hand.

**The leak is the sinker.** He throws it 31.4% of the time to left-handers, gets 7.1% whiffs, and gives up **55.0% hard contact**. It is a get-me-over pitch that left-handers are squaring. First-pitch strike rate vs LHH is only 59.0% (vs 67.5% against RHH), which suggests he is using it to get ahead and not succeeding at that either.

### vs RHH — 169 BF, .255 wOBA, .349 xwOBAcon

| Pitch | Usage | Whiff % | Chase % | Zone % | Putaway % | Hard-hit % | xwOBAcon (BIP) |
|---|---|---|---|---|---|---|---|
| Sweeper | 38.9% | 20.5% | 25.5% | **60.3%** | 23.9% | **53.7%** | **.468 (41)** |
| Cutter | 24.8% | 26.7% | 37.6% | 48.2% | 30.0% | 32.1% | .277 (28) |
| Changeup | 18.3% | 22.2% | 33.3% | 28.1% | 12.5% | **14.3%** | .294 (28) |
| Sinker | 18.0% | 20.0% | 14.5% | 53.8% | 15.4% | 35.7% | .243 (14) |

**This is where the data product earns its keep.** His most-used pitch against right-handers is his worst pitch against right-handers. The sweeper vs RHH: **60.3% of them land in the zone**, right-handers chase only 25.5%, whiff only 20.5%, and hit it for **53.7% hard contact and a .468 xwOBAcon**. Eleven of the sixteen extra-base hits he has allowed post-TJ came on the sweeper — including seven of the eleven he has allowed to right-handers — and the location plot shows why — against right-handers it sits middle-away in the zone instead of finishing off the plate the way it does to lefties.

Meanwhile the **cutter is his best swing-and-miss pitch against right-handers** (26.7% whiff, 37.6% chase, 30.0% putaway, .277 xwOBAcon) and the **changeup is his best contact suppressor** (14.3% hard-hit). Between them they account for 43.1% of his usage vs RHH. That is backwards.

### Two-strike counts — the specific correction

| Bats | Pitch | Share of 2K pitches | Whiff % | Putaway % | Chase % | Zone % |
|---|---|---|---|---|---|---|
| **L** | Sweeper | **75.0%** | **38.6%** | 26.4% | 42.9% | 31.9% |
| L | Sinker | 10.4% | 14.3% | 10.0% | 50.0% | 60.0% |
| **R** | **Sweeper** | **44.7%** | **11.5%** | 23.9% | 31.4% | **60.2%** |
| **R** | **Cutter** | **20.3%** | **48.0%** | **30.0%** | 40.0% | 37.5% |
| R | Changeup | 28.4% | 19.4% | 12.5% | 46.7% | 19.6% |
| R | Sinker | 6.6% | 14.3% | 15.4% | 28.6% | 46.2% |

Against left-handers, the two-strike approach is correct and should not be touched. Against right-handers, he is throwing his 11.5%-whiff pitch twice as often as his 48.0%-whiff pitch.

### The single attack rule

> **Sweeper is the out pitch to lefties and must finish off the plate. Cutter is the out pitch to righties. Never let the sweeper be the two-strike pitch to a right-handed hitter unless it is going to land out of the zone.**

---

## For the pitching department — first time working with him

Four things, in the order I would take them.

**1. Restore depth to the sweeper.** This is the whole ballgame. It has gained 2.3 inches of induced vertical break since surgery and lost 14 points of whiff rate (37.2% → 23.2%). Horizontal break is intact at −16.8 inches, so the sweep is still there; what is missing is the dive. Whether that is a seam-orientation change, a release-height artifact of the lower slot, or a spin-efficiency shift is a question for the lab — the parquet says *what* changed, not *why*. Start there, because a sweeper back at 2.5 inches of IVB fixes his RHH problem and his whiff problem at the same time.

**2. Fix the sequencing before you fix anything mechanical.** The cutter/sweeper usage inversion against right-handers is free value available this week and requires nothing from his arm. Moving 15 points of two-strike usage from the sweeper to the cutter against RHH is the single highest-leverage change in this document.

**3. Clean up the sweeper release.** 5.3 inches of separation between the sweeper and the cutter/sinker release points, against 2.3 inches of natural noise. Not alarming, and better than it was pre-surgery, but at his slot it is visible. Bullpen and video before an opponent finds it.

**4. Leave the delivery alone otherwise.** The lower, wider slot he came back with is an asset, not a rehab artifact to be corrected. It is what produces the one-inch sightline against left-handers. Do not let anyone "clean it up" back toward where he was in 2021.

**What not to chase:** the velocity is fine (85.0 mph post-TJ vs 85.4 pre-, and trending up), and the strike-throwing is fine (64.3% first-pitch strikes, 7.4% walk rate). Neither needs work.

---

## For the battery — catchers and Raley

**Against left-handed hitters.** Sweeper is the primary and the put-away — 75% of two-strike pitches, 38.6% whiff. Keep it off the plate; the 42.4% zone rate is right and should not creep up. The cutter is a fine early-count strike (.176 xwOBAcon). **Cut the sinker back.** At 31.4% usage with 55.0% hard contact it is the one pitch left-handers are hurting, and every one of those is a pitch that could be a cutter.

**Against right-handed hitters.** Changeup and cutter forward, sweeper back — especially with two strikes. The changeup is his quietest pitch on contact (14.3% hard-hit) and he throws it 18.3%. The cutter is his best miss (26.7% whiff, 48.0% with two strikes) and he throws it 24.8%. The sweeper stays in the mix early in the count, but if it is going to be a strike to a right-hander it is going to get hit — .468 xwOBAcon, 53.7% hard contact, and 7 of the 11 extra-base hits right-handers have taken off him.

**For Raley directly.** Two things the data is telling you. First, hitters are chasing more and missing less than at any point in the post-surgery window (chase up to 35.2% in July, whiff down to 17.0%) — batters are expanding but making contact on pitches they used to swing through, which is the sweeper's flatter finish showing up in the box score. Second, when you do miss a left-handed bat you miss it by 3.8 inches, well clear of what right-handers manage — the look works, use it.

**Pitch-calling in one sentence per hand:** to a lefty, get ahead with the cutter and finish with a sweeper below the zone; to a righty, get ahead with the sweeper and finish with a cutter in on the hands or a changeup under it.

---

## For the manager — how to use him

**What his last 75 outings actually looked like:**

| | |
|---|---|
| Most common entry | **7th inning (34 of 75 outings)**; 6th (17), 8th (15) |
| Highest-frequency single situation | 7th inning, leading 1–3 runs — 18 outings |
| Typical outing | **median 14 pitches, 3–4 batters** (30 outings of exactly 3 BF, 22 of 4) |
| Multi-inning outings | 12 of 75 |
| Entered with inherited runners | **26 of 75** |
| Faced at least one RHH | **70 of 75** |
| Faced only LHH | 5 of 75 |
| Appeared on zero or one day of rest | 12 of 75 |

**He is a full-inning setup arm, not a matchup specialist.** The Mets used him almost exclusively as a 7th-inning bridge in close games, asked him to face three to four hitters of both hands, and were comfortable bringing him in with traffic. That usage pattern is transferable and I would not deviate far from it.

**On back-to-back days he is fine.** Twelve outings on zero or one day of rest: velocity dips about 0.9 mph (84.4 vs 85.3 on four-plus days), whiff rate dips to 18.6% — but the results hold (.215 wOBA) and the strike-throwing actually improves (**2.6% walk rate**). He does not lose the plate when he is tired.

**Curiously, he is worse with more rest, not less.** His three-days-rest bucket is his worst (.328 wOBA, 11.7% walk rate, 17.3% whiff) across 18 outings and 77 batters faced. That is a directional sample and nothing more — but it argues against parking him for long stretches. Use him.

**Where to protect him.** The right-handed contact is the exposure: .349 xwOBAcon, 36.0% hard-hit, and the sweeper he leans on is the pitch getting squared. Against a heavily right-handed heart of the order in a one-run spot, he is a below-average option until the sequencing changes. Against any lineup segment with two left-handers in it, he is one of the better looks in the bullpen.

**No first-batter problem.** First batter faced: 27.7% whiff, .260 wOBA. Second: 16.9% whiff, .218. Third and beyond: 20.8% whiff, .239. He does not need a hitter to find it, and he does not fade in longer outings.

**Expectation setting.** He will not sustain a .239 wOBA. Plan the bullpen around a competent, durable, left-handed-leaning setup man with a real platoon edge and a contact-management risk — not around the run-prevention line he has posted since coming back.

---

## Game-plan takeaways

1. **Move two-strike usage against right-handers from the sweeper to the cutter.** 11.5% whiff → 48.0% whiff. Free, immediate, requires nothing from his arm.
2. **Restore the sweeper's depth** (+2.3 in IVB since surgery). It fixes the RHH exposure and the whiff decline together.
3. **Cut the sinker against left-handers** (31.4% usage, 55.0% hard-hit). Replace with cutters.
4. **Lead with the changeup more against right-handers** — his best contact suppressor at 14.3% hard-hit, used only 18.3%.
5. **Protect the lower, wider slot.** It is the source of the one-inch sightline against LHH. Do not correct it.
6. **Deploy as a 7th-inning, 3–4 batter setup arm of both hands**, comfortable on back-to-back days, prioritized into lineup segments containing left-handed hitters.

---

## Candid data-window & freshness caveats

* **269 post-TJ batters faced.** Above the 100-BF publication threshold, well below what makes rate stats stable. The vs-LHH split is 100 BF; the two-strike-by-pitch cells are 10–88 pitches each. Every small cell is printed with its n in the tables above — read them.
* **The pre-TJ/post-TJ split is a design decision, not a natural experiment.** He also aged four years across that boundary and changed how he is used. The delta is "what changed," not "what the surgery caused."
* **Zero Phillies rows.** Everything here describes a Mets pitcher. There is no in-org baseline, no Phillies catcher framing context, and no assigned role. First-30-days monitoring should be treated as a genuine validation of this dossier, not a formality.
* **RSA is a proxy.** It correlates with Statcast's native `arm_angle` at r = 0.831 across the 10 pitchers where both exist — but the residuals are large (Banks +14.0°, Sánchez −12.1°, Backhus −7.7°). RSA reliably orders pitchers from low-slot to high-slot; it does not reproduce a specific arm angle. Where native `arm_angle` exists, prefer it. The full calibration is in `out/dp_uc30_rsa_calibration.csv`.
* **RDI does not support the distinctiveness claim** and is reported as a negative result above rather than quietly dropped.
* **Sightline Offset is geometry, not outcome.** It describes where the ball starts. The claim that this makes him harder to track rests on the miss-distance and contact-quality splits, and miss distance is 32 and 61 whiffs. Corroborating, not conclusive.
* **Bat-tracking coverage is asymmetric.** Bat speed and swing length begin in 2023, so the pre-TJ tracking row covers 86 and 136 swings out of 1,450. Pre/post tracking comparisons are indicative only.
* **KBO 2015–2019 is a recorded gap.** His professional record is longer than this dossier.
* **`estimated_woba_using_speedangle` is 26% populated** across all post-TJ pitches, which is expected — it exists on balls in play. All expected-contact figures here use `xwobacon` (BIP-only, 178 balls in play post-TJ); the contaminated pitch-level `xwoba` column is quarantined per uc-pps-021 open item O1 and is never published.
* **Open item O4, found by the verification harness during this build.** The BIP counts printed in parentheses next to every xwOBAcon figure count *all* balls in play, including a handful that carry no tracked xwOBA estimate. Post-TJ that is 178 printed against 176 actually estimated; pre-TJ, 462 against 457. The averages themselves are computed over non-nulls and are correct — only the sample-size labels are two-to-five too generous. The locked KPI function is inherited verbatim and was not edited to hide this; it is logged for the next revision.
* **Cache is T-2** (through 2026-08-02, built 2026-08-04). Any outing on 8/03 or 8/04 is not reflected.

**Artifacts.** Build script `dp_uc30_raley_acquisition_read.py` · 21 CSV receipts and 5 figures in `out/` · DQ scorecard `out/dp_uc30_dq_scorecard.csv` (38/38 PASS) · independent recompute harness `dp_uc30_verification.py` · governance trail `00_`–`07_` in this folder.
