# Trea Turner — The Power Outage, and the August That Made It Worse

### UC #40 · `uc-pos-014-turner-2026-recency-001` · `dp_uc40` · Phillies Offense value stream · as of **2026-09-02**

> **Data window & reliability.** Full career Statcast, 2015-08-21 → 2026-09-02, across two source
> systems (`turner.parquet` for the Washington/Los Angeles years, `phils_{2023..2026}.parquet` for the
> Phillies years). Turner locked to MLBAM **607208**; **602 PA over 135 games** in 2026. Regular season
> only in every rate; 1,139 postseason rows excluded and labelled. Windows: **Mar 26–Jun 30 (371 PA)**,
> **July (102 PA)**, **Aug 1–Sep 2 (129 PA)** — all three above the standing 50-PA floor. Cells below the
> floor carry **⚠** wherever they appear and nothing is ranked on them.
> Every number below was recomputed on an independent code path: **711/711 PASS**. DQ **22 PASS / 3 WARN /
> 0 FAIL**. This product **extends `uc-pos-006` / `dp_uc24`** (2026-07-21); all **84** of that product's
> published figures were reproduced exactly before a single new claim was made.

---

## §1 · The verdicts — every question answered before anything is explained

| # | The question as asked | Verdict | The number |
|---|---|---|---|
| **Q1** | What is going on **recently**? | **He has fallen off a cliff since the parent product shipped** | Aug 1–Sep 2: **.207/.279/.276**, wOBA **.251**, ISO **.069**, **1 HR in 129 PA**. Trailing-100-PA wOBA peaked at **.421 on 2026-07-21** and now reads **.238** |
| **Q2** | And this year in general? | **The worst season of his career, on every rate** | .239/.292/.376, wOBA .294 — **rank 1 of 11** (i.e. lowest) qualified seasons in BA, OBP, SLG, OPS, ISO, wOBA **and** BABIP. 35th percentile of 220 Phillies hitter-seasons |
| **Q3** | Where has he struggled? | **Power and contact quality — not strikeouts** | ISO .137 (career low). K% 21.8% is essentially tied with 2023 for his career high, but it has been **falling all year** (22.6% → 21.6% → 19.4%). The damage is gone, the plate skills are not |
| **Q4** | What has "good" looked like? | **Two different kinds of good, and 2026 has neither** | Peak (2020–21, WSN): .982/.907 OPS on **46.2% hard-hit** and a **1.146 OPS vs LHP**. Phillies-good (2023–25): .795 OPS built on **.329 BABIP** and contact volume, not slug. 2026 loses the slug leg *and* the BABIP leg |
| **Q5** | Underlying indicators? | **He is getting under the ball. That is the one signal that clears the noise bar** | Aug–Sep **popup rate 15.2% of BIP** vs a .050 Phillies norm — **z = 4.12**, the only measure in the whole panel that is *clearly* beyond sampling noise. Launch angle up (11.2° → 14.6°), exit velocity down (89.5 → 85.7) |
| **Q6** | Actions for hitting-department personas? | **Answerable only as hypotheses** | No coaching, medical, or intervention log exists in this data plane. §7 maps observables to persona remit as **testable hypotheses**. Nothing here identifies causation |
| **Q7** | Has his approach changed? | **YES vs his Phillies self — and in the least useful direction** | In-zone swing **.739 → .688**, first-pitch swing **.387 → .328**, while chase went **up** .335 → .343. AD-1 (in-zone swing − chase) **.345 = 2nd lowest of 11 career seasons**. He takes more strikes *and* chases more balls |
| **Q8a** | Certain pitches / pitch groups? | **Sweepers and sliders, decisively** | ST + SL = **632 pitches, 27.8% of everything he sees**, and against them: **.182 and .243 wOBA on 40.7% and 35.9% whiff**. Breaking-ball usage against him has climbed **34.6% → 40.3%** across the three windows |
| **Q8b** | Lefty/righty trend? | **Both are down; the right-handed side is the lowest of his eleven qualified seasons** | vs RHP **.686 OPS — rank 1 of 11 (lowest)**, next-lowest .745. vs LHP .630, a dead heat with 2017 for his lowest. **The 2020–21 left-handed edge (1.185 / 1.146 OPS) has been gone since 2022** |

### The three submitted premises, adjudicated

| P | Premise | Verdict |
|---|---|---|
| **P1** | He has struggled this year | **TRUE, unambiguously.** Lowest qualified season on seven independent rate metrics |
| **P2** | Something is happening *recently* | **TRUE, and boundary-robust.** The breakpoint scan flips sign at exactly 2026-07-21 and worsens monotonically after it: Δ-OPS −.082 → −.143 → −.175 → −.222 → −.280 |
| **P3** | His approach has changed | **TRUE against his Phillies baseline, FALSE against his career.** vs 2023–25 the shift is real and unhelpful; vs his 12-season history his chase (10th of 11) and in-zone swing (6th of 11) are inside his own range |

**One sentence:** Turner is having the worst season of his career because his contact stopped being
damaging — and since the moment the July surge peaked he has been getting under the ball, popping up at
three times his normal rate and slugging .276, while simultaneously posting the best strikeout and walk
rates of his season. **This is a contact-quality and timing problem wearing the costume of a plate-discipline
improvement.**

---

## §2 · The season, calibrated

![career by season](dp_uc40_fig1.png)

| KPI | 2026 (602 PA) | PHI norm 2023–25 (1,871 PA) | Career best (season) | Pool percentile |
|---|---|---|---|---|
| **OPS** | **.668** | .795 | .982 (2020) | **35th** |
| **wOBA** | **.294** | .346 | .413 (2020) | **38th** |
| SLG | .376 | .460 | .588 (2020) | 39th |
| OBP | .292 | .335 | .394 (2020) | 35th |
| BA | .239 | .287 | .342 (2016) | 43rd |
| **ISO** | **.137** | .173 | .253 (2020) | **43rd** |
| BABIP | .282 | .329 | .388 (2016) | — |
| K% | 21.8% | 19.0% | 13.9% (2020) | 39th |
| BB% | 6.5% | 6.0% | 8.9% (2018) | 45th |
| xwOBA (per-PA) | .292 | — | — | — |

Three things this table settles before the diagnosis starts:

1. **It is not luck.** xwOBA **.292** sits essentially on top of wOBA **.294**. The expected-outcome model
   agrees with the results. A .282 BABIP looks like misfortune until you notice xwOBAcon is **.341**, his
   lowest of the Statcast era (2023–25: .383 / .369 / .361). He is not being robbed; he is hitting the ball
   worse.
2. **It is not a strikeout problem, and it is getting less like one.** Monthly K% runs 21.7 / 19.8 / 23.9 /
   24.3 / 21.6 / **18.3** — August is his best strikeout month of the season, and his August walk rate (9.2%)
   is his best too. Whatever is wrong is downstream of his decisions.
3. **The cohort matters (G8).** "Worst of his career" is stated against an enumerated cohort: **his eleven
   qualified seasons, 2016–2026** (2015 is 44 PA and excluded by the 50-PA floor). Against the *population*
   — 220 Phillies hitter-seasons of ≥50 PA since 2015, 100 players — he is a 35th-percentile bat, not a
   catastrophe. Both facts are true and the report keeps both.

---

## §3 · Recently — and the loop the parent product left open

![trajectory and rolling form](dp_uc40_fig2.png)

The parent product (`uc-pos-006`, delivered 2026-07-21 on data through 07-20) published a **.980 OPS / 62 PA
July** and explicitly refused to call it a recovery, flagging it *"real-but-young."* That figure reproduces
exactly here. **The call has now resolved, and it resolved against the optimistic reading.**

| Window | PA | BA | OBP | SLG | OPS | wOBA | ISO | HR | K% | BB% |
|---|---|---|---|---|---|---|---|---|---|---|
| Mar 26 – Jun 30 | 371 | .237 | .286 | .358 | .644 | .285 | .121 | 9 | 22.6% | 5.9% |
| **July** | 102 | .287 | .333 | **.564** | **.897** | **.381** | **.277** | **7** | 21.6% | 5.9% |
| **Aug 1 – Sep 2** | 129 | **.207** | .279 | **.276** | **.555** | **.251** | **.069** | **1** | **19.4%** | **8.5%** |

The rolling-form line (RF-2, trailing 100 PA) puts a finer point on it: it peaked at **.421 on 2026-07-21 —
the day the parent product was delivered** — and has fallen 183 points to **.238**. The season-to-date wOBA
line (RF-1) never once crosses into the 2023–25 band; the July surge lifted the cumulative line from .283 to
.306 and it has been sliding since.

**Breakpoint sensitivity (RC-5, mandatory — the DPO chose this window after seeing the outcome).** Ten
candidate cut dates from 1 June to 22 August:

| Cut | pre PA | post PA | Δ OPS | Δ wOBA |
|---|---|---|---|---|
| 2026-06-01 | 256 | 346 | +.080 | +.033 |
| 2026-07-01 | 371 | 231 | +.064 | +.023 |
| 2026-07-16 (All-Star break) | 415 | 187 | +.094 | +.036 |
| **2026-07-21 (parent's cut)** | 433 | 169 | **−.082** | **−.033** |
| 2026-08-01 | 473 | 129 | −.143 | −.055 |
| 2026-08-08 | 505 | 97 | −.175 | −.067 |
| 2026-08-15 | 529 | 73 | −.222 | −.087 |
| 2026-08-22 | 552 | 50 | −.280 | −.112 |

The sign flips **exactly at the parent's as-of date** and then worsens monotonically. This is the cleanest
possible receipt on both halves of the story: every cut *before* 07-21 says he was improving, every cut
*from* 07-21 says he is declining, and neither statement is an artifact of where the line was drawn.

---

## §4 · The mechanism — what actually moved

![mechanism](dp_uc40_fig3.png)

Ten measures across the three windows. Two moved down together, one moved up alarmingly, and the plate
discipline moved the *right* way while the results collapsed.

| Measure | Mar–Jun | July | **Aug–Sep** | PHI norm 2023–25 |
|---|---|---|---|---|
| Exit velocity (tracked BIP) | 88.9 | 88.5 | **85.7** | 89.5 |
| Hard-hit % | 39.9% | 46.6% | **31.5%** | 41.8% |
| Barrel % | 5.7% | 11.0% | **4.3%** | 7.0% |
| **Popup % of BIP** | 4.9% | 4.1% | **15.2%** | **5.0%** |
| Mean launch angle | 10.5° | 7.5° | **14.6°** | 11.2° |
| xwOBAcon | .342 | .399 | **.294** | .371 |
| Bat speed (mph) | 70.1 | 70.8 | 69.2 | 69.7 |
| Fast-swing % (≥75 mph) | 17.6% | 23.2% | 15.2% | 16.0% |
| Chase % | 35.8% | 31.1% | 32.2% | 33.5% |
| In-zone swing % | 69.6% | 69.0% | **66.0%** | 73.9% |
| K% | 22.6% | 21.6% | **19.4%** | 19.0% |

### The honest reading (ST-1 uncertainty bands)

A five-week window moves means by chance. Every shift above was priced against two baselines:

| Measure | vs July (102 PA) | vs PHI 2023–25 norm (1,871 PA) |
|---|---|---|
| **Popup rate** | +11.1 pts, z = **2.33** *(suggestive)* | +10.2 pts, **z = 4.12 — clearly beyond noise** |
| Exit velocity | −2.8 mph, z = −1.14 *(within noise)* | −3.8 mph, z = **−2.41** *(suggestive)* |
| Hard-hit rate | −15.1 pts, z = −1.98 *(suggestive)* | −10.2 pts, z = −1.93 *(suggestive)* |
| Fast-swing rate | −8.0 pts, z = −2.04 *(suggestive)* | −0.7 pts, z = −0.28 *(within noise)* |
| **Bat speed** | −1.63 mph, z = −2.21 *(suggestive)* | **−0.52 mph, z = −0.90 — within noise** |
| Launch angle | +7.0°, z = 1.42 *(within noise)* | +3.4°, z = 0.89 *(within noise)* |

Two conclusions follow, and the second one corrects an intuition worth stating out loud:

**The popup rate is the finding.** It is the only measure in the panel that clears the noise bar against a
well-powered baseline, and it is extreme: 15.2% of his balls in play in August–September, against a 5.0%
Phillies norm. Treated as a season, that rate would sit at the **97.7th percentile of 220 Phillies
hitter-seasons** — the fifth-highest of the 220. Higher launch angle plus lower exit velocity plus tripled
popups is the signature of getting **under** the ball: contact point drifting, or timing late enough that the
barrel arrives beneath the plane of the pitch.

**Bat speed is NOT the story, and it would have been easy to say it was.** August bat speed (69.2 mph) is
1.6 mph below July and reads like a decline — but against his own 2023–25 Phillies norm of 69.7 it is
**within noise (z = −0.90)**, as is his fast-swing rate. **July was the anomaly, not August.** He did not slow
down; he had one hot month in which he swung unusually hard, and then returned to his own normal swing while
his contact point deteriorated. Any intervention built on "get his bat speed back" would be chasing a
five-week spike.

![monthly](dp_uc40_fig4.png)

---

## §5 · What "good" looked like — two different players

There is no single Turner baseline. There are two, and the difference matters for what "fixed" would mean.

| | **Peak Turner (2020–21, WSN)** | **Phillies Turner (2023–25)** | **2026** |
|---|---|---|---|
| PA | 903 | 1,871 | 602 |
| OPS | .982 / .907 | .795 | **.668** |
| wOBA | .413 / .386 | .346 | **.294** |
| ISO | .253 / .208 | .173 | **.137** |
| Hard-hit % | 40.7 / 46.2 | 41.8 | **39.3** |
| Barrel % | 9.6 / 7.4 | 7.0 | **6.3** |
| Pull-air % of BIP | 13.1 / 17.6 | 18.7 | **15.9** |
| Chase % | 27.2 / 26.4 | 33.5 | **34.3** |
| In-zone swing % | 67.5 / 72.4 | 73.9 | **68.8** |
| **AD-1** (in-zone swing − chase) | .402 / **.460** | .404 | **.345** |
| K% | 13.9 / 17.1 | 19.0 | 21.8 |
| **vs LHP OPS** | **1.185 / 1.146** | .805 | **.630** |

**Peak good was damage plus judgment.** 2021 is his best full season and it is also his best AD-1 (.460, the
highest of his career): he swung at 72.4% of strikes and chased 26.4% of balls, and when he connected he
barreled 7.4% and pulled 17.6% of his balls in play into the air. He also destroyed left-handed pitching.

**Phillies good was different and thinner.** 2023–25 is a .795-OPS hitter whose value came from batting
average and on-base skill riding a **.329 BABIP**, not from slug — 2025's best Phillies season carried an
ISO of just .152 and 15 home runs. That is a profile with one leg. It is sturdy while the contact stays
loud and the balls keep finding grass; it has nothing to fall back on when they don't.

**2026 kicked out both legs at once.** The slug leg was already thin and is now .376. The BABIP leg went
.329 → .282 — and unlike the parent's July read, that drop is *earned*: xwOBAcon .371 → .341. A hitter whose
2025 value was "hits a lot of singles and doubles hard enough" cannot afford to lose 30 points of expected
contact quality, and he has.

---

## §6 · Approach — the change is real, and it is against himself

![platoon](dp_uc40_fig5.png)

"Approach" here means **decisions**, and is kept strictly separate from outcomes and from what pitchers
choose to do to him.

| Decision metric | 2023 | 2024 | 2025 | **2026** | Aug–Sep |
|---|---|---|---|---|---|
| Swing % | 53.1 | 53.7 | 51.4 | 50.4 | **47.0** |
| **In-zone swing %** | 74.2 | 74.8 | 72.8 | **68.8** | **66.0** |
| **Chase %** | 35.3 | 33.9 | 31.1 | **34.3** | 32.2 |
| First-pitch swing % | 38.8 | 39.0 | 38.2 | **32.8** | 33.1 |
| **AD-1 differential** | .389 | .408 | .418 | **.345** | .339 |
| Whiff % | 29.6 | 26.1 | 24.8 | 27.4 | 28.1 |

**Against his Phillies self the change is unmistakable.** He is taking 5.1 points more of the strike zone
than his 2023–25 norm and 5.9 points more first pitches, while chasing *more* than in 2025. AD-1 — in-zone
swing minus chase, the single number for whether he is separating balls from strikes — is **.345, the
second-lowest of his eleven qualified seasons**, ahead of only his 2016 rookie year.

**Against his whole career the picture is milder.** His chase rate ranks 10th of 11 (2nd-highest) and his
in-zone swing 6th of 11 — both inside his own historical range. So P3 is true relative to the baseline the
Phillies actually signed, and false relative to "he has become a different hitter."

*AD-1 is reported here beside both of its components and never alone — inherited verbatim from the
`uc-pos-005` OZ-3 caveat, because a differential can fall while judgment improves if a hitter cuts swings on
both sides of the zone. In this case it does not: his in-zone swings fell while his chases did not.*

Two pitcher-side observations belong here, clearly labelled as **opponent behaviour, not his approach**: the
share of pitches he sees in the zone fell 50.1% → 44.8% from July to August, and first-pitch strike rate
against him fell .608 → .585. Pitchers are working around the edges more, and he is answering by taking more
strikes rather than fewer balls.

---

## §7 · Splits — where the damage is being done to him

![pitch groups](dp_uc40_fig6.png)

### Pitch groups: spin is the hole, and the league has found it

| Window | Group | Usage | PA | BA | SLG | wOBA | Whiff |
|---|---|---|---|---|---|---|---|
| Mar–Jun | fastball | 53.1% | 210 | .279 | .437 | .343 | 18.8% |
| Mar–Jun | **breaking** | 34.6% | 124 | .185 | .286 | **.223** | **37.1%** |
| Mar–Jun | offspeed | 12.4% | 37 ⚠ | .189 | .189 | .168 ⚠ | 39.0% |
| July | fastball | 49.4% | 50 | .295 | .568 | .393 | 20.8% |
| July | breaking | 38.7% | 34 ⚠ | .281 | .531 | .367 ⚠ | 34.3% |
| **Aug–Sep** | **fastball** | 52.0% | 59 | **.173** | **.231** | **.226** | 21.3% |
| **Aug–Sep** | **breaking** | **40.3%** | 59 | .200 | .273 | **.239** | 35.4% |
| Aug–Sep | offspeed | 6.9% | 10 ⚠ | .444 | .556 | .466 ⚠ | 29.4% |

Breaking-ball usage against him has climbed from **34.6% to 40.3%** across the three windows — the league is
adjusting to a hitter it has learned cannot punish spin. But the alarming cell is the fastball row: in
August–September he is hitting **.173 and slugging .231 against fastballs**, a pitch group he handled at
.279/.437 through June. When a hitter stops hitting fastballs, that is a timing statement.

### Pitch types, full season — the sweeper is the wound

| Pitch | Pitches | Usage | wOBA | Whiff |
|---|---|---|---|---|
| **ST (sweeper)** | 256 | 11.2% | **.182** | **40.7%** |
| **SL (slider)** | 376 | 16.5% | **.243** | **35.9%** |
| FC (cutter) | 186 | 8.2% | .252 ⚠ | 28.9% |
| FS (splitter) | 54 | 2.4% | .262 ⚠ | 46.9% ⚠ |
| CH (change) | 194 | 8.5% | .280 ⚠ | 33.3% |
| CU (curve) | 138 | 6.1% | .303 ⚠ | 29.2% |
| SI (sinker) | 385 | 16.9% | .312 | 11.8% |
| FF (four-seam) | 617 | 27.1% | .366 | 22.1% |

**Sweepers and sliders account for 27.8% of every pitch he sees and he is posting .182 and .243 wOBA against
them on 40.7% and 35.9% whiff rates.** Nothing else in the arsenal is close to that combination of volume and
failure. He still handles fastballs and sinkers at a normal level over the full season — which is exactly why
the August fastball collapse reads as a timing symptom rather than a skill loss.

### Platoon: both sides are down, and the right-handed side is the career low

| Season | vs LHP (PA) | OPS | | vs RHP (PA) | OPS |
|---|---|---|---|---|---|
| 2020 | 64 | **1.185** | | 195 | .917 |
| 2021 | 166 | **1.146** | | 478 | .827 |
| 2022 | 182 | .882 | | 525 | .782 |
| 2023 | 205 | .713 | | 484 | .803 |
| 2024 | 169 | .884 | | 372 | .769 |
| 2025 | 204 | .833 | | 437 | .795 |
| **2026** | **197** | **.630** | | **405** | **.686** |

- **vs RHP .686 is rank 1 of 11 — the lowest of his qualified career**, and by a wide margin (next-lowest
  .745 in 2018). Two-thirds of his plate appearances come against right-handers, so this *is* the season.
- **vs LHP .630** is a dead heat with 2017 (.6298 vs .6296) for his lowest. More to the point, the
  extraordinary left-handed edge of 2020–21 has not existed since 2022 — a fact the parent product already
  flagged and this one confirms with a fourth season of evidence.
- **Recently the split is stark**: Aug–Sep vs RHP is **.193/.244/.265 with an 83.9 mph average exit velocity**
  over 90 PA. Against LHP in the same window he is .242/.359/.303 over 39 PA ⚠ — below floor, not rankable.

**It is not scheduling (PL-1).** Direct standardisation of the recent window to both earlier platoon mixes
moves wOBA by **less than 3 thousandths** (−.0026 against the March–June mix, −.0008 against July's). His
left-handed exposure is stable at 30–34% across every window and 32.7% for the season, in line with 2023–25
(29.8% / 31.2% / 31.8%). Nobody is hiding him and nobody is exposing him. The decline is performance.

---

## §8 · Could anyone in the Phillies hitting department drive better outcomes?

The requester asked whether specific personas could act on this. **Direction of causation is not identified by
this data product** — there is no coaching log, no medical record, no intervention timeline in this data
plane. What follows maps each *observable* to the persona whose remit it sits in, as a **testable
hypothesis**, ranked by how much of the gap it could plausibly close.

| # | Observable | Persona | Testable hypothesis | Why it ranks here |
|---|---|---|---|---|
| **1** | Popup rate 15.2% vs 5.0% norm (**z = 4.12**), launch angle **+3.4°** on exit velocity **−3.8 mph** | **Hitting coach / assistant hitting coach** | Contact point has drifted under the ball. A posture, hand-path, or timing cue — the standard "stay on top / meet it out front" family — would show up first as popups reverting toward 5% and mean LA falling back to ~11° | The only signal in the product that clearly clears sampling noise, and the most mechanically actionable |
| **2** | Aug–Sep fastball line **.173/.231**, versus .279/.437 through June, on unchanged whiff | **Hitting coach + advance scouting** | This is a timing signature, not a recognition one — he is making contact with fastballs and doing nothing with them. Machine work at game velocity and earlier load timing are the levers; measurable as fastball xwOBAcon, not as whiff | Second-largest recoverable block of value, and the metric to watch is *quality* of fastball contact |
| **3** | **ST/SL: 27.8% of all pitches seen, .182/.243 wOBA, 40.7%/35.9% whiff**; breaking usage against him **34.6% → 40.3%** | **Advance scouting / hitting coach** | Spin recognition and a two-strike plan against sweepers. A recognition intervention shows as **chase on breaking falling** while contact on breaking rises. Note the trap: chase may rise if he starts attacking spin earlier — the correct read-out is wOBA and whiff together | Structural, season-long, and the league is actively increasing the dose. Fixing this is slower but has the largest total exposure |
| **4** | In-zone swing **73.9% → 68.8%**, first-pitch swing **38.7% → 32.8%**, AD-1 **.345 (2nd lowest of 11)** | **Hitting coach / manager** | He is taking hittable pitches. A "green light in the zone early" plan is a one-conversation intervention with an immediate read-out (first-pitch swing rate, in-zone swing rate) | Cheap to test, fast to measure, but it corrects a symptom of hesitancy rather than a cause |
| **5** | Bat speed 69.2 mph in Aug — **within noise** of his 2023–25 norm (z = −0.90) | **Strength & conditioning / performance** | **The hypothesis this product would NOT prioritise.** A "get the bat speed back" program would be chasing a five-week July spike. Only worth pursuing if the S&C group has independent physical evidence the data plane cannot see | Explicitly de-prioritised, with the receipt for why |
| **6** | vs RHP **.686 — career low**; vs LHP edge gone since 2022 | **Manager / lineup construction** | There is no platoon deployment fix available here: he is worst against the handedness he faces two-thirds of the time, and the LHP side is 39 recent PA ⚠. Lineup-slot analysis is **out of scope** — batting order is not a column in this data plane (gap G-2) | Included to close the question, not because it offers a lever |
| **7** | Zone rate against him **50.1% → 44.8%**, first-pitch strike **.608 → .585** | **Opponent behaviour — no Phillies persona** | Pitchers are working the edges more. This is the confound to every hypothesis above: some of the recent decline is the league adjusting, not him regressing | The honest counterweight |

The two rows that matter are **1 and 2**, and they are the same physical story told at two grains: he is late
and under the ball. Everything else in this table is either downstream of that or is somebody else's decision.

---

## §9 · Governance — the parent product, audited in public

This UC extends `uc-pos-006` / `dp_uc24` (UC #25, delivered 2026-07-21). Under the standing
**parent-reproduction check**, that product's published figures were recomputed **on its own window
(≤ 2026-07-20) and its own definitions** before any new claim was made.

- **84 of 84 figures reproduced exactly** (7 metrics × 12 seasons, tolerance 5×10⁻⁴). The data plane is
  stable; nothing in the source has been silently revised.
- **Definitional drift: zero.** The parent's deprecated `get_stats` used raw plate appearances as the OBP and
  wOBA denominator; the current governed `nresults_unrounded` uses AB+BB+HBP+SF and AB+uBB+SF+HBP. For this
  subject the two agree to four decimals, because he has recorded no sacrifice bunts or catcher-interference
  events. The legacy function is retained in the kernel **for reproduction only** and is marked deprecated.
- **The parent's honesty correction held.** `uc-pos-006` was caught by its own verification gate calling a
  figure a "career low" when it was a Phillies-era low. This product enumerates the cohort for every
  superlative it makes (G8), which is how "rank 1 of 11 qualified seasons" gets phrased instead of a bare, un-cohorted superlative.

---

## §10 · Caveats, floors, and what this product does not claim

1. **The recent window is 129 PA / five weeks.** Above the floor, but every rate in it has wide error bars.
   Sub-splits inside it fall below floor fast and are marked ⚠ everywhere: Aug–Sep vs LHP (39 PA), Aug–Sep
   offspeed (10 PA), July breaking (34 PA), July vs LHP (32 PA), March (23 PA), September (9 PA).
2. **September is 9 PA.** It is charted for completeness and is ranked nowhere.
3. **The window was DPO-selected after seeing the outcome.** The breakpoint scan is the mitigation, and it
   shows the sign is robust from 2026-07-21 onward. The *size* of the decline still varies more than
   threefold across candidate cuts.
4. **No causation is identified anywhere in §8.** Persona rows are hypotheses mapped to remit.
5. **Bat tracking is 2024+ and Phillies-frames only** (gap G-3). No swing-measurable comparison to the
   2020–21 peak is possible; where the peak is discussed, it is on results and batted-ball data only.
6. **Batting order is not in this data plane** (gap G-2). Lineup-slot questions are out of scope.
7. **Known kernel defects D1–D6** are disclosed in `05_quality_certification.md`. The `_fix` variants used
   here leave the governed originals untouched. D6/O-8 (untracked BIP in the hard-hit denominator) has
   **zero impact on this build** — 2026 has 0 untracked balls in play.
8. **A new defect was found by this build's own verification harness, and is disclosed rather than
   patched: D-7 / O-13.** The governed `chase_rate_g` derives `in_zone_rate` by subtraction, so every row
   with a NULL `zone` is silently counted as an in-zone pitch. Exposure here is small but real — 2026
   season **.4719 published vs .4710 corrected**; the Aug–Sep window **.4528 vs .4482** (0.84% NULL zone).
   Every zone-rate figure in this report uses the corrected `in_zone_rate_fix`; both values ship in the
   receipts, and the governed original is left untouched upstream.
9. **xwOBAcon ≠ xwOBA** (O-4). Shifts are compared; levels are never cross-compared against wOBA.
10. **AD-1 and ST-1 are NEW-PROVISIONAL** and require DPO ratification before reuse. ST-1's z-scores are
   descriptive uncertainty bands on a non-random self-selected window — they are **not** hypothesis tests of
   a causal claim.

---

*Receipts: `dp_uc40_*.csv` (27 files) + `dp_uc40_headlines.json` · figures `dp_uc40_fig1..6.png` ·
independent verification `dp_uc40_verification.py` — **711/711 PASS** · package audit
`dp_uc40_package_audit.py` — **116/116 PASS** · governance trail `00`–`07` in this folder ·
bid and calibration in `BID_2026-09-03_uc-pos-014-turner.md` and `telemetry/`.
Generated 2026-09-03 · Phillies Offense value stream · Data Product Owner: Kellen Short.*
