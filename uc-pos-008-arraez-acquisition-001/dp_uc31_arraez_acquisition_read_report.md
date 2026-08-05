# Luis Arraez — Acquisition Read

### Deadline acquisition onboarding · Phillies batting department · built 2026-08-04
### `uc-pos-008-arraez-acquisition-001` · UC #32 · build `dp_uc31` · **Internal — Restricted**

> **Data window.** Every forward-looking number in this report comes from **2026 regular season only** — 464 plate appearances, 1,727 pitches, through **2026-08-02**. Seasons 2019–2025 appear as a *shadow* backdrop to test whether the profile is stable; they carry no forward-looking claim. Arraez has **zero Phillies plate appearances** in the data. This is a pre-arrival dossier, not a review.
>
> **One premise in the request does not match the log.** The request describes Schwarber as the current leadoff hitter. Through 2026-08-02 the leadoff hitter is **Trea Turner** (399 PA in the slot); Schwarber has 374 PA batting **second** and has not led off since June. Because the lineup is being reshuffled around this acquisition, the premise may be true of a lineup card written after the cache closed. The model prices **both** framings rather than choosing one. See §6.

---

## The bottom line

**He is the player you described, with one correction and one warning.**

The correction: **he is not a wild at-bat hitter.** He sees 3.72 pitches per plate appearance — *below* league average, and below his own 2019–2022 rate of 4.0–4.1. The wildness is real but it lives in exactly one place: once he has two strikes, he expands to a **56.3% chase rate**, swings at 73% of everything, and fouls off **42%** of what he swings at. He almost never takes a called third strike (1.1% of two-strike pitches). So the at-bats *feel* wild because the endings are wild. The beginnings are efficient.

The warning: **2026 is the first season of his career in which the results are meaningfully ahead of the contact.** His .337 wOBA sits **33 points above** his .304 xwOBA. Across 2019–2025 that same gap was one-tenth of a point. Nothing in the batted-ball data supports a step forward — exit velocity is 86.0 mph, barrel rate is **0.7%**, and his bat speed of 61.6 mph produces a hard-swing rate of **0.0%**. Set expectations at a **.300–.310 wOBA** the rest of the way, not .337.

**Three things are genuinely elite and are not going anywhere.**

1. **Two-strike survival.** 90.1% of his two-strike plate appearances do not end in a strikeout. The best Phillie is Bryson Stott at 66.9%. Schwarber is at 43.0%. This is the single largest skill gap between Arraez and the roster he is joining.
2. **Scoring-position conversion.** He drove in **34.3%** of the runners who were already in scoring position when he came up — best on the team — and struck out **once** in 89 such plate appearances.
3. **Strikeout avoidance, full stop.** 4.5% for the season. The next-best Phillies regular is more than double that.

**On the lineup question: the entire decision is worth about four runs over a full season, and Mattingly is not wrong.** Arraez's projected run contribution spans 23.5 to 27.4 runs per 162 games across all nine slots — a range of **3.95 runs**, well under half a win. Cleanup is his best individual slot. Against the *observed* lineup, moving him to leadoff and Turner to cleanup would **cost** 2.6 runs. Against the *stated* lineup, swapping him with Schwarber is worth **+0.65 runs** — indistinguishable from zero.

If you want the model's actual preference, it is neither option you named: **bat him second**, leave Schwarber at cleanup. That configuration prices out best of everything tested — and the reason has nothing to do with Arraez's own production. It is about who is standing behind him. See §6.3.

---

## 1. Top-line results

| Season | PA | BA | OBP | SLG | OPS | wOBA | xwOBA | ISO | K% | BB% |
|---|---|---|---|---|---|---|---|---|---|---|
| 2019 | 366 | .334 | .396 | .439 | .835 | .360 | .334 | .104 | 7.9% | 9.6% |
| 2020 | 121 | .321 | .364 | .402 | .765 | .335 | .357 | .080 | 9.1% | 6.6% |
| 2021 | 480 | .293 | .352 | .374 | .727 | .319 | .340 | .081 | 10.0% | 8.5% |
| 2022 | 603 | .316 | .372 | .421 | .792 | .348 | .341 | .104 | 7.1% | 8.0% |
| 2023 | 617 | .354 | .376 | .469 | .845 | .363 | .355 | .115 | 5.5% | 4.1% |
| 2024 | 672 | .314 | .341 | .393 | .733 | .320 | .330 | .079 | 4.3% | 3.1% |
| 2025 | 677 | .291 | .321 | .391 | .711 | .307 | .303 | .100 | 3.1% | 5.0% |
| **2026** | **464** | **.324** | **.347** | **.441** | **.788** | **.337** | **.304** | **.117** | **4.5%** | **4.5%** |

*Receipt: `dp_uc31_a1_season_line.csv`. 2026 row is the primary window; all other rows are shadow.*

Three things to read off this table.

**The batting average is real and it is his floor.** Eight straight seasons between .291 and .354. Nothing in the profile threatens it.

**The 2026 ISO of .117 is a career high** and it is built out of **23 doubles and 7 triples**, not home runs — he has four. The triples total is a career high by three. Attack angle moved from 3.9° in 2025 to **7.6°** in 2026 and average launch angle rose to 14.6°, both career highs. Something in the swing did change. It produced more balls in the gaps, not more balls over the fence.

**The walk rate collapsed and has not come back.** 9.6% as a rookie, 4.5% now. He is not a patient hitter any more; he is a hitter who puts the bat on the ball. That matters for the leadoff argument in §6.

---

## 2. Underlying indicators — what the results are standing on

| Season | Avg EV | EV90 | Barrel% | Hard-hit% | Avg LA | GB% | Bat speed | Fast-swing% |
|---|---|---|---|---|---|---|---|---|
| 2022 | 88.9 | 99.4 | 3.6% | 30.2% | 12.9 | 41.2% | — | — |
| 2023 | 88.0 | 98.7 | 3.5% | 25.7% | 11.1 | 42.8% | 62.3 | 0.2% |
| 2024 | 86.1 | 97.9 | 1.6% | 23.7% | 13.3 | 42.2% | 61.3 | 0.2% |
| 2025 | 84.7 | 96.6 | 1.1% | 16.7% | 11.2 | 45.2% | 60.4 | 0.3% |
| **2026** | **86.0** | **97.1** | **0.7%** | **20.3%** | **14.6** | **39.1%** | **61.6** | **0.0%** |

*Receipts: `dp_uc31_b2_batted_ball.csv`, `dp_uc31_b4_bat_tracking.csv`.*

**Zero.** Out of 817 tracked swings in 2026, none reached 75 mph. That is not a slump indicator — it is the design of the player. He is the extreme end of a distribution the rest of your lineup does not occupy.

**The barrel rate is 0.7% and falling for four straight years.** Seven-tenths of one percent. The gap between his .337 wOBA and his .304 xwOBA is not a measurement artifact; it is 33 points of batted-ball fortune sitting on top of the weakest contact of his career. Expect it to come out.

**Plate discipline is not what the reputation says.**

| Season | Swing% | Chase% | Z-swing% | Whiff% | Z-contact% | O-contact% | P/PA |
|---|---|---|---|---|---|---|---|
| 2022 | 42.8% | 24.2% | 63.0% | 7.1% | 94.4% | 89.5% | 4.01 |
| 2024 | 49.5% | 34.9% | 63.0% | 6.9% | 95.3% | 88.7% | 3.62 |
| 2025 | 49.4% | 34.2% | 62.6% | 5.3% | 95.9% | 92.4% | 3.65 |
| **2026** | **48.9%** | **32.1%** | **64.5%** | **7.9%** | **93.4%** | **89.2%** | **3.72** |

*Receipts: `dp_uc31_b1_discipline.csv`, `dp_uc31_a3_pitches_per_pa.csv`.*

A **32.1% chase rate is above league average.** He is an aggressive hitter who happens to make contact with everything — 89.2% contact on pitches outside the zone. He is not working counts. He is not grinding. He is swinging early and often and hitting the ball where it is pitched. The 3.72 P/PA confirms it.

---

## 3. Two strikes — the skill that will change your dugout

This is the part of the profile that is genuinely rare, and it is bigger than the reputation suggests.

| | PA reaching 2K | K | **Survival rate** | Hits | BA | SLG | wOBA | RE24/PA |
|---|---|---|---|---|---|---|---|---|
| **Luis Arraez** | 213 | 21 | **.901** | 53 | .264 | .333 | .278 | **+0.008** |
| Bryson Stott | 227 | 75 | .670 | 47 | .220 | .290 | .246 | −0.025 |
| Alec Bohm | 191 | 66 | .655 | 26 | .149 | .183 | .188 | −0.073 |
| Edmundo Sosa | 110 | 39 | .646 | 18 | .177 | .255 | .199 | −0.007 |
| Justin Crawford | 169 | 63 | .627 | 31 | .199 | .237 | .230 | −0.032 |
| J.T. Realmuto | 170 | 64 | .624 | 26 | .173 | .247 | .239 | −0.025 |
| Bryce Harper | 244 | 101 | .586 | 37 | .179 | .290 | .268 | −0.008 |
| Trea Turner | 253 | 106 | .581 | 36 | .154 | .188 | .186 | −0.077 |
| Adolis García | 164 | 84 | .488 | 24 | .160 | .253 | .214 | −0.063 |
| Brandon Marsh | 215 | 111 | .484 | 30 | .149 | .224 | .193 | −0.048 |
| Kyle Schwarber | 286 | 163 | .430 | 30 | .120 | .260 | .228 | −0.055 |

*Receipt: `dp_uc31_c3_two_strike_vs_phillies.csv`. All 2026, Phillies regulars ≥150 PA.*

**He is the only hitter on this roster who is not a net negative with two strikes.** Every other regular posts a negative RE24 per two-strike plate appearance. Arraez is +0.008 — barely positive, but the distance from Turner (−0.077) and Schwarber (−0.055) is enormous over a season.

**How he does it.** Once he has two strikes:

| | Swing% | Chase% | Whiff% | Foul% of swings | Called-strike% | Pitches per 2K PA |
|---|---|---|---|---|---|---|
| 2026 | 73.0% | **56.3%** | **4.7%** | 42.2% | **1.1%** | 2.19 |

*Receipt: `dp_uc31_c2_two_strike_economy.csv`.*

He abandons the strike zone entirely and protects. A 56.3% chase rate would be a catastrophic number for any other hitter; paired with a 4.7% whiff rate it becomes a weapon. **He almost cannot be struck out looking** — 1.1% of two-strike pitches are called strikes.

**The honest limit.** Surviving is not damaging. His two-strike slash is **.264/.296/.333** with a .272 xwOBA. He converts strikeouts into weak contact and singles, not into damage. And at 2.19 pitches per two-strike plate appearance he is *not* running up pitch counts — the "wild eight-pitch at-bat" is memorable, not typical.

---

## 4. Where the slug comes from — pitch group and handedness

| Pitch group | Hand | PA | BIP | BA | SLG | ISO | wOBA | **xwOBAcon** | Avg EV | Hard-hit% |
|---|---|---|---|---|---|---|---|---|---|---|
| Fastball | RHP | 202 | 187 | .362 | **.481** | .119 | .377 | **.331** | 88.5 | 25.7% |
| Fastball | LHP | 109 | 93 | .320 | .400 | .080 | .321 | .267 | 83.1 | 16.1% |
| Breaking | RHP | 68 | 59 | .317 | .450 | .133 | .353 | .277 | 87.4 | 17.0% |
| Breaking | LHP | 26 | 25 | .292 | **.500** | .208 | .308 | **.253** | **78.1** | 8.0% |
| Offspeed | RHP | 50 | 46 | .208 | .271 | .063 | .214 | .266 | 83.8 | 15.2% |
| Offspeed | LHP | 5 | 4 | *thin* | *thin* | — | — | — | — | — |

*Receipt: `dp_uc31_d1_group_x_hand_2026.csv`. Offspeed vs LHP is 4 balls in play — reported for completeness, not usable.*

**All of the real damage is fastballs from right-handers.** 187 balls in play, .481 slugging, and — critically — a **.331 xwOBAcon that supports it**. This is the one cell in the matrix where the results and the contact quality agree. Right-handed fastballs are what he hits, and it is not luck.

**The apparent power against left-handed breaking balls is fake.** A .500 slugging percentage on 25 balls in play at an average exit velocity of **78.1 mph** and a **.253 xwOBAcon**. He is finding grass. That will stop.

**The platoon split is the real finding, and it points the opposite way from the raw line.**

| | PA | BA | OBP | SLG | wOBA | **xwOBA** | Gap | K% | BB% |
|---|---|---|---|---|---|---|---|---|---|
| vs LHP | 140 | .315 | .329 | .441 | .327 | **.256** | **+71** | 8.6% | 2.1% |
| vs RHP | 324 | .328 | .367 | .440 | .342 | .324 | +18 | 2.8% | 6.8% |

*Receipt: `dp_uc31_d4_by_hand_2026.csv`.*

The slugging is identical against both hands. The **deserved** production is not close. Against left-handers he is outrunning his contact by 71 points of wOBA, striking out three times as often, and walking almost never. **Against left-handed pitching he is a singles hitter having a good year, and the results will regress toward the .256 xwOBA.** Against right-handers he is exactly what the reputation says.

*By pitch type, the cutter is his best (.400/.480, .422 xwOBAcon, 29 PA) and the changeup his worst (.184/.316, 42 PA). Receipt: `dp_uc31_d3_pitch_type_2026.csv`.*

---

## 5. Runners in scoring position

| Context | PA | BA | OBP | SLG | wOBA | K% | RE24/PA | Runners faced | Scored | **Conversion** |
|---|---|---|---|---|---|---|---|---|---|---|
| Bases empty | 301 | .314 | .346 | .432 | .340 | 5.3% | +0.020 | — | — | — |
| Men on, no RISP | 74 | .308 | .338 | .477 | .342 | 5.4% | +0.041 | — | — | — |
| **RISP** | **89** | **.382** | **.405** | **.441** | **.324** | **1.1%** | **+0.077** | 108 | 37 | **.343** |

*Receipt: `dp_uc31_e1_context_2026.csv`.*

**One strikeout in 89 plate appearances with a runner in scoring position.** His run-expectancy contribution per plate appearance nearly quadruples from bases-empty (+0.020) to RISP (+0.077).

Against the roster:

| Hitter | RISP PA | BA | OBP | SLG | K% | Runners faced | Scored | **Conversion** |
|---|---|---|---|---|---|---|---|---|
| **Luis Arraez** | 89 | .382 | .405 | .441 | **1.1%** | 108 | 37 | **.343** |
| Bryson Stott | 97 | .333 | .412 | .642 | 12.4% | 116 | 35 | .302 |
| Alec Bohm | 113 | .309 | .372 | .495 | 13.3% | 142 | 42 | .296 |
| Edmundo Sosa | 50 | .273 | .260 | .523 | 16.0% | 63 | 18 | .286 |
| Brandon Marsh | 94 | .256 | .319 | .439 | 27.7% | 117 | 33 | .282 |
| Justin Crawford | 81 | .300 | .370 | .400 | 16.1% | 104 | 28 | .269 |
| Bryce Harper | 102 | .286 | .392 | .442 | 19.6% | 119 | 32 | .269 |
| Trea Turner | 92 | .235 | .272 | .400 | 21.7% | 112 | 23 | .205 |
| J.T. Realmuto | 84 | .232 | .333 | .377 | 19.0% | 103 | 21 | .204 |
| Adolis García | 57 | .214 | .368 | .381 | 28.1% | 72 | 13 | .181 |
| Kyle Schwarber | 87 | .238 | .414 | .571 | 33.3% | 100 | 15 | **.150** |

*Receipt: `dp_uc31_e4_spcr_vs_phillies.csv`.*

**Arraez converts more than twice as many scoring-position runners as Schwarber does.** Schwarber's RISP line is not bad — a .391 wOBA, .571 slugging, .414 OBP. But a third of those plate appearances end in a strikeout, and a strikeout scores nobody from second. Arraez's contact-first approach is worth the most in exactly the situation the cleanup spot produces most often.

**The caveat this deserves.** 89 plate appearances is one-fifth of a season, and RISP performance is famously unstable. Across 2019–2025 his conversion rate by season runs .296 / .560 / .286 / .304 / .345 / .285 / .222 — a mean near .305 with real scatter. The 2026 figure is at the high end of his own range, not a new skill. What *is* stable is the mechanism: he does not strike out, and the ball is in play. Treat **.30** as the honest expectation, not **.34**.

---

## 6. The lineup decision

### 6.1 How the model works

For each lineup slot, the 2026 Phillies produced an observable **opportunity mix** — how often a plate appearance in that slot arrives with the bases empty, with men on, or with a runner in scoring position. Independently, each hitter has an observable **run-expectancy contribution per plate appearance in each of those three contexts**. Multiply and scale by the slot's plate appearances per game.

$$\text{SPRC}(h,s)=\Big[\sum_{c}W(s,c)\cdot \text{RE24/PA}(h,c)\Big]\times \text{PA/g}(s)\times 162$$

No simulation, no assumed transition matrix, nothing that is not directly observed in the 2026 log. **The single limitation is that the opportunity weights $W(s,c)$ are held fixed at what the 2026 lineup actually produced.** Re-ordering hitters would, over a full season, slightly change those weights. The model does not capture that second-order effect, and that is its largest caveat.

### 6.2 What the slots actually offer

| Slot | PA/game | Bases-empty | Men on | **RISP** | RISP PA/game |
|---|---|---|---|---|---|
| 1 | 4.57 | 67.6% | 32.4% | **17.6%** | 0.80 |
| 2 | 4.45 | 60.6% | 39.4% | 20.3% | 0.90 |
| 3 | 4.30 | 58.5% | 41.5% | 21.8% | 0.94 |
| **4** | **4.26** | 52.2% | **47.8%** | **25.0%** | **1.06** |
| 5 | 4.16 | 59.2% | 40.8% | 24.3% | 1.01 |
| 9 | 3.71 | 56.9% | 43.1% | 25.8% | 0.96 |

*Receipt: `dp_uc31_f1_slot_opportunity.csv`.*

**Your instinct about the cleanup spot is correct and the data is clean on it.** Slot 4 produces the most men-on plate appearances (47.8%) and the most RISP plate appearances per game (1.06) of any slot in the order.

**But the leadoff spot buys 0.31 extra plate appearances per game** — about 50 more over a season. The two effects run against each other and very nearly cancel. That is the whole reason the lineup decision is worth so little.

### 6.3 The answer

| Scenario | Projected RE24 per 162 |
|---|---|
| **A. Observed 2026** — Turner 1st / Arraez 4th | **28.48** |
| A-swap — Arraez 1st / Turner 4th | 25.90 |
| **B. Stated premise** — Schwarber 1st / Arraez 4th | **73.25** |
| B-swap — Arraez 1st / Schwarber 4th | 73.90 |
| **C. Model preference** — Arraez 2nd / Schwarber 4th | **75.04** |
| *Delta, Turner framing (A-swap − A)* | **−2.58** |
| *Delta, Schwarber framing (B-swap − B)* | **+0.65** |
| *Arraez's own spread, best slot − worst slot* | **3.95** |

*Receipt: `dp_uc31_f7_swap_scenario.csv`. Scenario totals are pair sums and are only comparable within a framing — Turner and Schwarber are very differently productive hitters in 2026.*

**Read it in three steps.**

**First: the whole question is small.** Arraez's projected contribution across all nine slots runs from 23.49 (ninth) to 27.44 (cleanup). **Three and nine-tenths runs** separates his best lineup slot from his worst. That is roughly a third of a win. Whatever Mattingly does here, it is not the decision that determines the season.

**Second: against the lineup that actually exists, do not make the swap.** Turner has been the leadoff hitter and Turner is having a poor year — his projected contribution is barely above one run per 162 in any slot. Moving Arraez up and Turner to cleanup **costs 2.58 runs**, because it takes the roster's best scoring-position converter out of the spot with the most scoring-position chances and replaces him with the worst one (Turner's RISP conversion is .205; his two-strike RE24 is the worst on the team).

**Third: if the premise is right and Schwarber is leading off, the swap you proposed is a coin flip** — +0.65 runs per 162, which this model cannot distinguish from zero. But the model's preferred answer is a third option neither of you named: **Arraez second, Schwarber fourth**, worth **+1.79** over the stated arrangement.

### 6.4 Why second, and why it is not about Arraez

Arraez's on-base percentage is **.356** and it does not change with the slot. What changes is how many plate appearances he gets and **who is standing behind him**.

| Slot | Arraez baserunners/game | vs incumbent, per 162 | Next two slots | Their conversion | **Runners cashed (upper bound)** |
|---|---|---|---|---|---|
| 1 | 1.63 | +27.6 | 2, 3 | .222 | 58.4 |
| **2** | **1.58** | +11.7 | **3, 4** | .261 | **66.9** |
| **3** | 1.53 | −6.7 | **4, 5** | **.284** | **70.5** |
| 4 | 1.51 | **+47.2** | 5, 6 | .260 | 63.9 |
| 9 | 1.32 | +54.4 | 1, 2 | .190 | 40.6 |

*Receipt: `dp_uc31_f8_table_setting_supply.csv`. The final column applies a scoring-position conversion rate to all baserunners supplied, so it is an **upper bound**, not a run total. Do not add it to the SPRC figures — they would double-count.*

Leading off maximises the *number* of baserunners he creates, but hands them to slots 2 and 3, who convert at .222. Batting second hands them to slots 3 and 4 — Harper and the cleanup spot — who convert at .261. Batting third is better still on this measure.

**And the cleanup spot has the largest upgrade of all: +47 baserunners per 162 over its 2026 incumbents.** Slot 4 has been Bohm (199 PA) and Marsh (149 PA) at a combined .287 on-base percentage. Arraez at .356 in that spot is the single biggest on-base improvement available anywhere in the order.

**So the honest summary is:** cleanup maximises his own run creation and fixes the roster's weakest on-base slot; second maximises what the lineup does with the runners he creates. The difference between them is about one run. **Mattingly's choice is defensible and you should not spend capital arguing against it.**

---

## 7. What the batting department should actually do

You said you expect his approach needs little guidance. **That is correct, and the data says leave it alone.** Three specific things are worth acting on anyway.

**For the hitting coach — protect the approach, do not upgrade it.**
The temptation with a 0.7% barrel rate and a 61.6 mph bat speed is to look for launch angle. Resist it. The attack angle already moved 3.7° in 2026 and produced career-high doubles and triples — the adjustment has happened and it worked. Any further push toward lift trades away the contact rate that is the entire asset. **The one measurable to monitor is O-contact rate (89.2%).** If that starts falling, the two-strike survival skill is eroding and everything else follows.

**For the hitting coach — the left-handed matchup is the real coaching conversation.**
His .441 slugging against left-handers is supported by a **.256 xwOBA**. Expect that line to come apart. Against LHP his walk rate is 2.1% and his strikeout rate triples. This is the one split where an approach adjustment — take a pitch, force the count — has a plausible payoff, and it is also the one place he is *least* likely to want to change. Frame it as matchup-specific, not as a swing change.

**For the manager — the two-strike skill has in-game value beyond the box score.**
On a roster whose regulars survive two strikes 43–67% of the time, a hitter at 90% is a different tool. In a late-inning spot needing a ball in play — runner on third, fewer than two out — he is the highest-probability contact on the roster by a wide margin. That is a pinch-hit and lineup-protection consideration, not a batting-order one.

**For the front office / analytics — set expectations now, publicly and internally.**
The .324 average will attract attention. The .304 xwOBA and 0.7% barrel rate say the true talent right now is a **.300–.310 wOBA** hitter — roughly league average with an extreme distribution of how he gets there. He is a **complementary** piece who fixes a specific hole (the on-base collapse in the middle of the order), not a middle-of-the-order bat. Schwarber outproduces him in every single lineup slot by roughly 20 runs per 162 in this model. The acquisition is defensible on fit; it is not defensible as an upgrade in raw offensive value.

---

## 8. Caveats — read these before quoting anything above

1. **Four hundred and sixty-four plate appearances is two-thirds of a season.** Every 2026 number carries ordinary small-sample risk, and the split tables carry more. Sample sizes are printed on every row; use them.

2. **The RISP finding rests on 89 plate appearances** and his own seven-year history of scoring-position conversion ranges from .222 to .560. The mechanism is stable; the rate is not. Plan on .30.

3. **The lineup model holds the opportunity mix fixed.** Re-ordering the lineup would, over a season, change $W(s,c)$ slightly. The model does not capture that feedback. Given the total effect is under four runs, the omission is unlikely to reverse any conclusion — but it is a real limitation, not a footnote.

4. **Scenario totals are only comparable within a framing.** Scenario A totals ~28 runs and Scenario B totals ~73 because Turner and Schwarber are wildly different hitters in 2026. Compare A to A-swap, and B to B-swap. Do not compare A to B.

5. **The leadoff premise is unresolved.** The log says Turner; the request says Schwarber. This report prices both and picks neither. **The human DPO should confirm the current lineup card before this is circulated.**

6. **Zero Phillies plate appearances.** Everything here is inferred from a Giants hitter in a different park, a different lineup, and a different league context. Citizens Bank Park effects are not modelled.

7. **`xwOBAcon` sample counts.** The inherited contact-quality function reports its balls-in-play count using `size` semantics, which counts batted balls with no tracked estimate. The honest denominator is published alongside as `xwoba_con_n` in every receipt. Rates are unaffected. This is open item **O4**, carried from `uc-pps-025`.

8. **A definitional fork exists between the locked and new KPI kernels.** `truncated_pa` is counted as a plate appearance by the inherited `get_stats` and excluded by the new PA spine. It affects 2021 (1 PA) and 2025 (2 PA) only — **the 2026 primary window contains none**, so no forward-looking number in this report is touched. Verified explicitly (checks V-009a/b).

9. **The league reference table in the receipts stops at 2023.** It is not a 2026 benchmark and is not used as one. All benchmarking in this report is against the 2026 Phillies.

---

## 9. Provenance

**Sources.** `data/opponents/arraez.parquet` (15,228 regular-season pitches, 2019-05-18 → 2026-08-02, entity-locked to MLBAM **650333**); `data/phillies/phils_2026.parquet` (`phillies_role == 'batting'`, 112 games, through 2026-08-02); `wOBA and FIP Constants.csv`.

**Manual carry-ins** (not derivable from the pitch log, user-provided): the deadline acquisition itself; Mattingly's cleanup-spot decision; Harper's move back to the outfield; the leadoff-hitter premise (contested — see §6).

**Verification.** 368 independent checks, **368 PASS / 0 FAIL** (`dp_uc31_verification_results.csv`). Build-time DQ: **24/24 PASS**. Every table and figure traces to a CSV receipt in `out/`. No number in this report was computed anywhere except `dp_uc31_arraez_acquisition_read.py`.

**New KPIs introduced (provisional, pending glossary ratification):** AR-1 Two-Strike Survival Rate · AR-2 Two-Strike Damage Line · AR-3 Damage Profile by Pitch Group × Hand · AR-4 Scoring-Position Conversion Rate · AR-5 Lineup Slot Opportunity Profile · AR-6 Slot-Projected Run Contribution · AR-7 Table-Setting Value. Specifications in `04_architecture_and_kpi_specs.md`.
