# Brandon Marsh, First-Time All-Star — What Actually Changed in 2026

**dp_uc18 · uc-pos-marsh-breakout-001 · v1.1.0** — Phillies position-player (pos) value stream
Prepared 2026-07-13 (All-Star break) · Entity lock: batter == 669016 · Regular season only

> **DATA WINDOW:** Career pitch log 2021-07-18 → **2026-07-12** (complete first half — 91 of the Phillies' 97 games). LAA era via `data/opponents/marsh.parquet`; PHI era via `data/phillies/phils_{2022–2026}.parquet`. Receipts for every table: `out/dp_uc18_marsh_breakout_*.csv` (16 files). If quoted after 2026-07-12, staleness must be stated.

---

## Bottom line

Marsh's first All-Star half is **not a power gain — it is an approach inversion plus a role change.** Raw contact quality (EV, hard-hit, barrel) is flat against 2023–25. What changed: he swings far earlier and far more often at strikes (swing rate .413 → .532 in two years), avoids two-strike counts at a career-best rate, converts the same power into career-high pulled-air contact, and plays every day — platoon removed — for the first time. The bill is a 4.7% walk rate and a career-worst chase rate; so far the exchange is decisively positive, with honest regression flags below.

## 1. The first half, against his career

**.301/.333/.490 (.823 OPS), wOBA .354, 15 HR, 32 XBH in 363 PA** — career highs in average and slugging, a 24.8 HR/600 pace vs a prior best of 20.1 (2024).

| Season | PA | BA | OBP | SLG | OPS | wOBA | HR | XBH | K% | BB% | HR/600 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2021 (LAA) | 260 | .254 | .315 | .356 | .671 | .295 | 2 | 17 | 35.0 | 7.7 | 4.6 |
| 2022 (LAA+PHI) | 460 | .245 | .291 | .384 | .676 | .294 | 11 | 33 | 34.3 | 5.9 | 14.3 |
| 2023 | 470 | .277 | .366 | .457 | .823 | .356 | 12 | 43 | 30.6 | 11.9 | 15.3 |
| 2024 | 478 | .248 | .326 | .417 | .743 | .324 | 16 | 36 | 32.2 | 10.5 | 20.1 |
| 2025 | 426 | .277 | .336 | .440 | .775 | .334 | 11 | 38 | 25.8 | 8.7 | 15.5 |
| **2026 1H** | **363** | **.301** | **.333** | **.490** | **.823** | **.354** | **15** | **32** | **26.4** | **4.7** | **24.8** |

The OPS exactly ties his 2023 peak — but the composition is inverted. 2023 was OBP-built (11.9% walks, .366 OBP); 2026 is damage-built: a career-low 4.7% walk rate (17 BB all half) alongside career-high BA and SLG. He is not a better version of 2023 Marsh; he is a different hitter.

## 2. What did NOT change: the raw power

Rule out "got stronger" first: average EV 89.5, hard-hit rate 46.1%, 90th-percentile EV 103.8, barrel rate 9.4% — all inside a point of his 2023–25 norms. Same engine; different firing schedule and direction.

## 3. What changed: the approach — passive to predatory

| Indicator | 2024 | 2025 | 2026 1H |
|---|---|---|---|
| Swing rate | .413 | .471 | **.532** |
| In-zone swing rate | .614 | .663 | **.709** |
| First-pitch swing rate | .227 | .320 | **.319** |
| Chase rate | .237 | .290 | **.377** |
| Zone rate seen | .466 | .486 | .471 |
| % of PA reaching 2 strikes | 57.5% | 54.5% | **51.2%** |
| wOBA, PA ended in ≤2 pitches | .443 | .388 | **.498** |

Pitchers are not feeding him more strikes (zone seen flat) — he is attacking the ones he always got. The strikeout improvement is **count-avoidance, not two-strike skill**: his two-strike K rate (.516) sits in his career band (.47–.56); he simply reaches two strikes in a career-low 51.2% of PA (62% as a rookie). When he ends the PA early it's a career-best .498 wOBA, and his first-pitch balls in play post career highs in barrel rate (12.5%), sweet-spot rate (57.5%), and air rate (60%) — receipts in `_firstpitch_bip` and `_earlycount_pa`.

The cost is visible and accepted: career-worst .377 chase rate, walks gone.

## 4. Where the extra slug comes from: direction, not force

| Indicator | 2023 | 2024 | 2025 | 2026 1H |
|---|---|---|---|---|
| Sweet-spot rate (8–32°) | .392 | .441 | .404 | **.461** |
| Pulled-air rate | .147 | .174 | .181 | **.199** |
| Oppo rate | .325 | .307 | .293 | **.260** (career low) |
| Avg launch angle | 12.0 | 13.5 | 11.8 | 13.0 |

Career highs in sweet-spot and pulled-air contact, career low in opposite-field contact. For a lefty at Citizens Bank Park, moving the same EV from oppo/ground into pull-air is the cheapest slugging available.

What he's hunting is explicit in the pitch-group table: **.401 wOBA and an 18.6% K rate vs fastballs** (713 pitches), against .253 wOBA vs offspeed and a .447 chase rate vs breaking balls. He has narrowed his attack window to early fastballs and accepted worse outcomes everywhere else.

## 5. The role change: the platoon is gone

Career-long weakness vs LHP (wOBA .246–.256 in 2024–25, shielded to 18.8% LHP exposure in 2024). In 2026: **91 of 97 games, 27.3% of PA vs LHP — full-time exposure — slugging .404 with 7 XBH vs lefties (99 PA)**, wOBA .292, up ~40 points on the prior two seasons. Still not a strength — 36.4% K rate and a .238 expected-contact proxy vs LHP say "playable," not "solved." But playable plus everyday volume is most of the counting-stat case that made him an All-Star.

Dating the shift: 2025's results turned in the second half (wOBA .370, 8 HR in 199 PA) **without** the swing-profile change (swing rate .469). The aggression appears only from Opening Day 2026 — an offseason/spring codification of what late 2025 taught, not mid-stream drift.

## 6. The narrative: tangible actions each persona could have taken

*Inference consistent with the indicators — the data cannot see intent. Each claim traces to §1–§5.*

**Brandon Marsh — commit the A-swing early, pull the ball in the air.** Flat zone-seen with a +10-point in-zone swing jump is a swing-*decision* change, not a pitcher-behavior change: he arrived with a pre-committed plan to attack the first fastball in the zone. Career-high pulled-air and sweet-spot with flat EV is the signature of swing-intent (pull-side lift), not strength. He kept 2025's two-strike contact gains (zone contact .85–.89 the last two seasons vs .78–.84 before) — which is what makes the trade survivable.

**The hitting department — reframe "win the count" into "end the count."** The transition is discontinuous at the season boundary; that is what an installed offseason plan looks like: convince a high-whiff hitter that his walks were a byproduct of passivity, not a skill worth protecting, and point him at the pitch he crushes. The early-count damage numbers are the plan working. Their open second-half item is the exhaust: a .447 chase rate vs breaking balls the league will target.

**The manager — take the platoon off.** Someone decided in April, with a career .25-wOBA-vs-LHP hitter, to keep writing him in against lefties. Ninety-one games in 97 and 27% LHP exposure is a bet on rhythm over matchup optimization — and the everyday volume directly produced the All-Star counting-stat case. The vs-LHP improvement then reinforced the decision.

## 7. Candid caveats (read before extrapolating)

- **He is outrunning contact quality:** wOBA .354 vs a .322 expected proxy; vs LHP the gap is wider (.292 vs .238). Some of the .301 average is weather.
- **June carried the half** (9 HR, .604 SLG in 116 PA); **July is cold** (.179/.250/.256, wOBA .232 — 44 PA, below the 50-PA floor, directional only).
- **The league's counter is obvious:** .447 chase vs breaking balls with a 4.7% walk rate means the profile has no safety net if teams stop throwing early fastballs. The structural gains (two-strike funnel, pulled-air, everyday role) survive regression; the batting average does not need to.

---

*Locked KPI mechanics inherited verbatim from Baseball Functions (get_stats/measure_calcs wOBA with FanGraphs season weights; chase = swings at zone>9; hard-hit = EV≥95 on type=='X'; barrel = launch_speed_angle==6). "xwOBA"/expected columns are the locked BIP-weighted proxy (`estimated_woba_using_speedangle` mean), not full Statcast xwOBA. IBB (1) excluded from BB per locked definitions. 2022 blends LAA and PHI stints (traded ~2022-08-02). DQ: 9,877 deduped pitches, 0 duplicate keys, all null rates <0.5% — `out/dp_uc18_marsh_breakout_dq_receipts.csv`. Governance package: `Agents for Data Products/data-products/uc-pos-marsh-breakout-001/`.*
