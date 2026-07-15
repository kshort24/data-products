# Kyle Schwarber, All-Star & Derby Runner-Up — The Approach Behind the First Half

**dp_uc20 · uc-pos-004-schwarber-first-half-allstar-001 · v1.0.0** — Phillies position-player (pos) value stream
Prepared 2026-07-14 (All-Star break) · Entity lock: batter == 656941 · Regular season only

> **DATA WINDOW:** Career pitch log 2015-06-16 → **2026-07-12** (complete first half — 93 games appeared). CHC/WSN/BOS era via `data/opponents/schwarber.parquet`; PHI era via `data/phillies/phils_{2022–2026}.parquet`. Receipts for every table: `out/dp_uc20_schwarber_first_half_*.csv` (17 files + 3 figures). **Manual carry-ins (not derivable from the pitch log): 2026 All-Star selection; Home Run Derby runner-up.** If quoted after 2026-07-12, staleness must be stated.

---

## Bottom line

Schwarber's 32-HR, .391-wOBA half is **not new strength — it is the most committed version of a trade he has been drifting toward for a decade.** Bat speed is flat year-over-year (74.2 mph), exit velocity sits inside his career band, and his swing is actually *shorter* than 2024. What changed: he swings at strikes at the highest rate of his career (.675 in-zone), converts a career-high share of contact into pulled air (.320), has nearly evicted the ground ball (27.5%, career low), and front-loads his damage before two strikes (.663 wOBA even-or-behind; 12 HR in PA that end within two pitches). The bill is a career-worst 35.3% whiff rate and 34.7% K rate — and he pays it on purpose, because the walks survived (13.5% BB, chase a manageable .252) and the runs did too: 107.4 wRC/600, third-best of his career.

## 1. The measurables

Bats L / throws R, age 33 (b. 1993-03-05), listed 6'0"/229 — *reference carry-ins.* What Statcast measures directly (receipts: `_battracking`, `_battedball`, `_2026_hr_log`):

| Measurable | 2024 | 2025 | 2026 1H |
|---|---|---|---|
| Avg bat speed (mph) | 75.0 | 74.2 | 74.2 |
| Fast-swing rate (≥75 mph) | .706 | .698 | .684 |
| Swing length (ft) | 7.64 | 7.46 | 7.44 |
| Attack angle (°) | — | 14.5 | 14.7 |
| Avg EV (mph) | 93.6 | 94.3 | 93.4 |
| 90th-pct EV | 109.2 | 109.8 | 109.1 |
| Max EV | 115.6 | 117.2 | 113.2 |

The 32 first-half homers averaged **403.6 ft at 106.6 mph off the bat, longest 460 ft** — the raw material the Derby audience saw was on display all half. But note the direction of every row above: flat or slightly down. The engine did not get bigger.

## 2. The KPI panel, against his career

**.254/.359/.558 (.917 OPS), wOBA .391, 32 HR in 415 PA** — a 46.3 HR/600 pace, dead-even with his 56-HR 2025 (46.7), with career highs nowhere in the engine and everywhere in the outcomes mix. 2016 (5 PA, injury year) excluded from narrative.

| Season | PA | HR | BA | OBP | SLG | OPS | wOBA | K% | BB% | HardHit% | Barrel% | P/PA | HR/600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 (CHC) | 273 | 16 | .246 | .352 | .487 | .839 | .363 | 28.2 | 12.8 | 42.9 | 12.3 | 4.26 | 35.2 |
| 2017 | 486 | 30 | .210 | .313 | .466 | .778 | .332 | 30.9 | 11.9 | 42.0 | 15.2 | 4.34 | 37.0 |
| 2018 | 491 | 26 | .238 | .328 | .466 | .794 | .341 | 28.5 | 11.8 | 45.3 | 12.8 | 4.36 | 31.8 |
| 2019 | 606 | 38 | .249 | .333 | .530 | .864 | .356 | 25.7 | 10.7 | 51.3 | 14.6 | 4.19 | 37.6 |
| 2020 | 223 | 11 | .188 | .305 | .393 | .698 | .307 | 29.6 | 13.0 | 48.4 | 11.5 | 4.28 | 29.6 |
| 2021 (WSN/BOS) | 472 | 32 | .264 | .371 | .551 | .922 | .390 | 26.9 | 13.3 | 52.4 | 17.6 | 4.21 | 40.7 |
| 2022 | 666 | 46 | .218 | .320 | .504 | .824 | .355 | 30.0 | 12.5 | 54.5 | 20.1 | 4.32 | 41.4 |
| 2023 | 716 | 47 | .196 | .338 | .473 | .811 | .350 | 29.9 | 16.9 | 48.8 | 16.4 | 4.29 | 39.4 |
| 2024 | 689 | 38 | .247 | .361 | .484 | .846 | .365 | 28.6 | 14.8 | 55.5 | 15.6 | 4.14 | 33.1 |
| 2025 | 719 | 56 | .239 | .357 | .561 | .918 | .390 | 27.4 | 14.0 | 59.6 | 20.8 | 4.26 | 46.7 |
| **2026 1H** | **415** | **32** | **.254** | **.359** | **.558** | **.917** | **.391** | **34.7** | **13.5** | **53.4** | **19.4** | **4.30** | **46.3** |

Read the last row twice: a **career-worst strikeout rate** living inside a **career-best wOBA**. That contradiction is the whole report.

## 3. Run creation (SC-1, new KPI this UC)

wRC from the locked wOBA and FanGraphs season constants: **74.3 runs created in 415 PA — 107.4 wRC/600**, behind only 2021 (110.3) and 2025 (108.2). At his 2026 PA pace that is a ~124-wRC full season, within range of 2025's 129.6 despite the strikeout spike. Receipt: `_wrc_by_season.csv` (2026 constants are FanGraphs in-season values — flagged provisional in the spec).

## 4. What did NOT change: the engine

Rule out "got stronger" first: bat speed flat (§1), avg EV 93.4 and hard-hit 53.4% *below* 2025 (94.3 / 59.6), barrel 19.4% vs 20.8. On pure contact quality this is his 2022/2025 band, not a new tier. Same engine; different firing schedule and direction — the Marsh finding, one weight class up.

## 5. What changed: the approach

| Indicator | 2023 | 2024 | 2025 | 2026 1H | Career note |
|---|---|---|---|---|---|
| Swing rate | .377 | .399 | .418 | **.443** | highest since 2015 rookie half |
| In-zone swing rate | .558 | .607 | .641 | **.675** | **career high** |
| First-pitch swing rate | .233 | .271 | .275 | **.316** | career high |
| Chase rate | .216 | .209 | .215 | .252 | worst since 2015, still moderate |
| Whiff rate | .315 | .320 | .331 | **.353** | **career worst** |
| Zone rate seen | .470 | .479 | .477 | .461 | near career low |
| P/PA (SC-2) | 4.29 | 4.14 | 4.26 | 4.30 | stable — patience retained |
| Pulled-air rate | .259 | .245 | .272 | **.320** | **career high** |
| Ground-ball rate | .346 | .409 | .343 | **.275** | **career low** |
| Air rate (FB+LD) | .539 | .513 | .569 | **.628** | **career high** |
| Sweet-spot rate | .354 | .331 | .363 | **.417** | **career high** |

Pitchers are throwing him *fewer* strikes than ever (.461 zone seen) and he is attacking the ones he gets harder than ever. The signature is **selective aggression, not indiscriminate aggression**: in-zone swing up 3.4 points on 2025 while P/PA held at 4.30 and the walk rate held at 13.5% — he added the A-swing without surrendering the count. Where the damage lands (receipts: `_countstate`, `_earlycount_pa`):

- **Even-or-behind counts: .663 wOBA, 14 HR** — career high by ~120 points of wOBA.
- **PA ended within two pitches: .643 wOBA, 12 HR in 74 PA** — career best (prior best .563, 2025).
- **Two-strike PA: .223 wOBA, 57.4% K** — career-worst two-strike K rate, in a career-typical two-strike wOBA band.

He has effectively **written off the two-strike PA to maximize the pre-two-strike PA.** 60.5% of his PA still reach two strikes (career-normal), but the other 39.5% now produce most of a full season's damage.

Two more splits fill in the half (receipts: `_platoon`, `_pitchgroup`):

- **vs LHP: .415 wOBA, 11 HR in 159 PA (38.3% LHP exposure)** — the best vs-left half of his PHI era, on career-high lefty volume. The 2015–21 platoon liability is fully retired.
- **By pitch group:** fastball wOBA .472 (20 HR); offspeed .421 — up 90 points on 2025; breaking balls remain the tax: .272 wOBA, 45.9% K, chase up to .292. The league's obvious counter is more spin; so far he is out-slugging the tax.

## 6. The narrative: tangible actions each persona could have taken

*Inference consistent with the indicators — the data cannot see intent. Each claim traces to §1–§5.*

**Schwarber — sell out for the ball in the air, earlier.** Career-high in-zone swing and first-pitch swing with a *shorter* swing and flat bat speed is a decision change, not a body change: commit the A-swing to the first hittable pitch, accept the whiff. The 27.5% ground-ball rate says the swing is now organized around one outcome — pulled air — and .320 pulled-air with 86% of grounders pulled is total commitment to the plan.

**The hitting department — protect the walk while installing the aggression.** The aggression Marsh installed cost him his walk rate (4.7%); Schwarber's version kept 13.5% BB because the chase moved only 3.7 points. That is the harder trick and the more repeatable profile. Their open second-half item is the same one as Marsh's: breaking-ball chase (.292) is drifting up, and a 34.7% K rate leaves no batting-average floor if the pulled-air conversion cools.

**The manager — bank the lefty leverage.** .415 wOBA vs LHP on career-high exposure removes the last argument for resting him against tough lefties; the platoon card now runs the other way. The 4-hole is producing 107 wRC/600 — lineup construction around him is a solved problem for the second half.

## 7. Candid caveats (read before extrapolating)

- **The K rate is real and career-worst** (34.7%, two-strike K 57.4%). The profile holds only while ~1 in 5 balls in play is a barrel; a two-week EV dip turns this half's .254 BA into .210 fast.
- **wOBA .391 vs xwOBA proxy .378** — modest overrun, nothing like a red flag, but the direction is "hot," not "underpaid."
- **July is soft:** .336 wOBA, 2 HR in 48 PA — below the 50-PA floor, directional only.
- **2026 wOBA/wRC constants are in-season FanGraphs values** and will move by season's end; wRC figures are provisional to ±2%.
- **Max EV 113.2 is his lowest full-tracking top-end since 2015** — worth one look in August; a top-end EV decline at 33 would be the first true aging flag.

---

*Locked KPI mechanics inherited verbatim from dp_uc18 / Baseball Functions (get_stats wOBA with FanGraphs season weights; chase = swings at zone>9; hard-hit = EV≥95 on type=='X'; barrel = launch_speed_angle==6). "xwOBA" is the locked BIP-weighted proxy (`estimated_woba_using_speedangle` mean), not full Statcast xwOBA. NEW KPIs this UC: SC-1 wRC (run creation), SC-2 P/PA — specs in governance 03. IBB excluded from BB per locked definitions. DQ: 24,562 deduped pitches, 0 duplicate keys, all BIP null rates ≤1.1% — `out/dp_uc20_schwarber_first_half_dq_receipts.csv`. Governance package: `Agents for Data Products/data-products/uc-pos-004-schwarber-first-half-allstar-001/`. Ledger: this is UC #21 / uc-pos-004 / dp_uc20 — ledger update pending.*
