# Trea Turner, 2026 — The Down Year, and the July That Argues With It

**dp_uc24 · uc-pos-006-turner-2026-offense-001 · v1.0.0** — Phillies position-player (pos) value stream
Prepared 2026-07-21 · Entity lock: batter == 607208 · Regular season only

> **DATA WINDOW:** Career pitch log 2015 → **2026-07-20** (98 team games in 2026 — first half **plus the first 3 games of the second half**, post All-Star break). WSN/LAD era via `data/opponents/turner.parquet`; PHI era via `data/phillies/phils_{2023–2026}.parquet`. Receipts for every table: `out/dp_uc24_turner_2026_review_*.csv` (16 files + 5 figures). **Manual carry-ins (not derivable from the pitch log): 2026 All-Star break date (07-16); roster/health context.** Any line below the 50-PA floor is flagged inline and is directional only. If quoted after 2026-07-20, staleness must be stated.

---

## Bottom line

1. **This is, by the numbers, the first below-average offensive season of Turner's career.** .246/.296/.396 (.691 OPS), wOBA .303, **wRAA −4.8 runs** — the only qualified season he has ever finished below league-average run value. OPS is down ~110 points on his three prior Phillies years (.773 / .804 / .807). Receipts: `_results_by_season`, `_wrc_by_season`.
2. **It is not a luck story.** xwOBA (expected wOBA — contact quality plus strikeouts and walks) is **.295 — the lowest of his Phillies era** (.383 / .322 / .325 in 2023–25). wOBA .303 actually sits *above* it. The results are down because the contact is down, not because the hits stopped falling.
3. **The engine is basically intact — the shape is what broke.** Bat speed 70.1 mph (flat/up), barrel rate 6.8% (up on 2025), hard-hit 41.0% (stable). What collapsed is **pulled air: .117 — a Phillies-era low, his lowest since 2020** (career-typical .14–.17), on a **35.2% pull rate that is likewise a Phillies-era low**. He is hitting the ball the other way and on the ground instead of pulling it in the air, and the swing decisions slipped with it — chase up to .351, in-zone swing *down* to .692, whiff up to .283.
4. **A specific, new hole: soft stuff.** vs offspeed he is at **.184 wOBA with a 37.8% strikeout rate** (was .283 in 2025); vs breaking .260. The fastball damage survives (.352 wOBA) — pitchers have simply stopped needing to throw him one.
5. **The heating-up is real but young.** July: **.980 OPS, 5 HR in 62 PA**, with the process partly back (barrel 13.6%, line-drive rate .273, pulled-air .159). The trailing-100-PA line has climbed from a **.455 OPS trough to .973**. But July wOBA (.412) outran its xwOBA (.337), and the post-break piece is a **14-PA, 3-HR cameo** — encouraging, not yet a floor. **So-what:** treat the recovery as a live hypothesis to protect, not a solved problem.

---

## 1. The KPI panel, against his whole career

**.246/.296/.396, .691 OPS, wOBA .303, 14 HR in 433 PA** — a 19.4 HR/600 pace. Full history below (WSN → LAD → PHI); 2015 (44 PA) and small partial lines flagged. Receipt: `_results_by_season.csv`.

| Season | Team | PA | HR | BA | OBP | SLG | OPS | ISO | wOBA | xwOBA | K% | BB% | HR/600 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | WSN | 44 | 1 | .225 | .295 | .325 | .620 | .100 | .278 | .343 | 27.3 | 9.1 | 13.6 |
| 2016 | WSN | 324 | 13 | .342 | .370 | .567 | .937 | .225 | .395 | .413 | 18.2 | 4.3 | 24.1 |
| 2017 | WSN | 448 | 11 | .283 | .337 | .450 | .787 | .167 | .337 | .349 | 17.9 | 6.7 | 14.7 |
| 2018 | WSN | 738 | 19 | .271 | .340 | .415 | .755 | .144 | .330 | .352 | 17.9 | 8.9 | 15.4 |
| 2019 | WSN | 568 | 19 | .297 | .350 | .496 | .847 | .199 | .355 | .377 | 19.9 | 7.2 | 20.1 |
| 2020 | WSN | 259 | 12 | .335 | .394 | .588 | .982 | .253 | .413 | .394 | 13.9 | 8.5 | 27.8 |
| 2021 | WSN→LAD | 645 | 28 | .327 | .372 | .535 | .907 | .208 | .386 | .394 | 17.1 | 6.0 | 26.0 |
| 2022 | LAD | 707 | 21 | .297 | .341 | .465 | .806 | .168 | .349 | .374 | 18.5 | 6.2 | 17.8 |
| 2023 | PHI | 692 | 26 | .265 | .316 | .456 | .773 | .192 | .332 | .383 | 21.7 | 6.2 | 22.5 |
| 2024 | PHI | 541 | 21 | .294 | .336 | .467 | .804 | .174 | .348 | .322 | 18.1 | 5.0 | 23.3 |
| 2025 | PHI | 641 | 15 | .302 | .353 | .454 | .807 | .152 | .350 | .325 | 16.7 | 6.6 | 14.0 |
| **2026** | **PHI** | **433** | **14** | **.246** | **.296** | **.396** | **.691** | **.149** | **.303** | **.295** | **22.4** | **6.2** | **19.4** |

Read the 2026 row against the three above it: every rate stat moved the wrong way at once. The batting average fell 56 points off 2025, the on-base fell 57, the slug fell 58, and the strikeout rate jumped back to a 2023-level 22.4% after two years of trimming it to the mid-teens. This is not one leak; it is the whole profile a half-step slow.

## 2. Run creation (SC-1) — the flag that matters

wRC from the locked wOBA and FanGraphs season constants (receipt: `_wrc_by_season.csv`):

| Season | PA | wOBA | lg wOBA | wRAA | wRC | wRC/600 |
|---|---|---|---|---|---|---|
| 2021 | 645 | .386 | .31 | +38.2 | 116.3 | 108.1 |
| 2024 | 541 | .348 | .31 | +16.5 | 79.8 | 88.5 |
| 2025 | 641 | .350 | .31 | +19.1 | 94.8 | 88.7 |
| **2026** | **433** | **.303** | **.32** | **−4.8** | **46.7** | **64.8** |

**wRC/600 of 64.8 is comfortably the worst full-season pace of his career** (career band 77–122; his three Phillies years were 80 / 88 / 89). The negative wRAA is the headline: for the first time as a regular, his bat has been a slight *drag* on league-average run production rather than a lift. *(2026 constants are FanGraphs in-season values → wRC provisional ±2% until season close.)*

## 3. What did NOT break: the engine

Rule out "he got old and weak" first, because the measurables do not support it (receipts: `_battracking`, `_battedball`):

| Measurable | 2024 | 2025 | 2026 | Read |
|---|---|---|---|---|
| Avg bat speed (mph) | 70.0 | 69.5 | **70.1** | flat / up |
| Fast-swing rate (≥75) | .155 | .164 | **.178** | up |
| Swing length (ft) | 7.52 | 7.48 | 7.55 | stable |
| Avg EV (mph) | 89.1 | 89.3 | 88.8 | slightly down |
| 90th-pct EV | 103.8 | 104.2 | 103.5 | slightly down |
| Hard-hit % (EV≥95) | .408 | .421 | **.410** | stable |
| Barrel % | .069 | .058 | **.068** | up on 2025 |

The bat is not slower and the barrels are not gone — barrel rate actually ticked *up* from 2025, and bat speed is the fastest of his three tracked years. On pure contact quality this is his normal band, maybe a hair soft at the very top end (90th-pct EV 103.5, lowest of the three). A top-end EV dip at age 33 is worth one August look, but it is not the story of this season.

## 4. What broke: the shape and the swing decisions

If the engine is intact, the runs went missing in **where the ball goes** and **which pitches he offers at** (receipts: `_spray_by_season`, `_discipline_by_season`, `_pitchgroup_by_season`, `_platoon_by_season`).

| Indicator | 2023 | 2024 | 2025 | 2026 | Career note |
|---|---|---|---|---|---|
| Pull rate | .422 | .480 | .415 | **.352** | **PHI-era low** (lowest since 2020) |
| Pulled-air rate | .153 | .169 | .149 | **.117** | **PHI-era low** (lowest since 2020) |
| Oppo rate | .286 | .257 | .281 | **.326** | highest of PHI era |
| Line-drive rate | .237 | .213 | .242 | **.212** | career-low band |
| GB pulled rate | .624 | .625 | .526 | **.469** | he's not even pulling his grounders |
| In-zone swing rate | .742 | .748 | .728 | **.692** | lowest since 2020 |
| Chase rate | .353 | .339 | .311 | **.351** | back to his worst |
| Whiff rate | .296 | .261 | .248 | **.283** | up |
| First-pitch swing | .388 | .390 | .382 | **.330** | down — later into counts |

The pattern is coherent: **he is pulling the ball less, lifting it to the pull side much less, and getting to fewer of the strikes he used to ambush** — while chasing more of the ones off the plate. Fewer pulled fly balls and line drives is, mechanically, fewer extra-base hits, and the slugging line (.396) shows it.

**By pitch group, the leak has an address:**

| 2026 vs | wOBA | xwOBA | K% | Whiff | Chase |
|---|---|---|---|---|---|
| Fastball | .352 | .352 | 15.6 | .194 | .343 |
| Breaking | .260 | .232 | 29.0 | .384 | .336 |
| **Offspeed** | **.184** | **.188** | **37.8** | **.408** | **.407** |

The fastball is still a strength; **offspeed is a crater** — .184 wOBA and a 37.8% strikeout rate, down from .283 the year before, with a chase rate over .40. Pitchers have noticed: he is seeing the same ~15% offspeed diet but doing nothing with it.

**The platoon edge evaporated.** vs LHP he is at **.632 OPS / .286 wOBA in 144 PA** — after .884 and .833 in 2024–25. The right-handed hitter who used to feast on lefties has, this year, been worse against them than against righties (.719 OPS). *144 PA — real enough to flag, not enough to close the book.*

## 5. The heating-up question

The season is not one flat line — it bottomed in May and has climbed since (receipts: `_2026_monthly`, `_2026_rolling_form`, `_2026_half_split`).

| Month | PA | OPS | wOBA | xwOBA | Barrel% | LD% | Pulled-air% |
|---|---|---|---|---|---|---|---|
| Mar | 23 | .445 | .201 | .243 | .059 | .176 | .294 |
| Apr | 116 | .755 | .334 | .296 | .049 | .183 | .098 |
| May | 117 | .529 | .232 | .291 | .071 | .226 | .107 |
| Jun | 115 | .693 | .307 | .286 | .050 | .200 | .088 |
| **Jul** | **62** | **.980** | **.412** | **.337** | **.136** | **.273** | **.159** |

July is the best month by a distance — and, unlike a pure batting-average mirage, **part of the process came with it**: the barrel rate doubled (13.6%), the line-drive rate is a season high (.273), and the pulled-air rate ticked back up (.159 from May/June's .09–.11). The trailing-100-PA line tells the same story: **OPS from a .455 trough to .973, wOBA from .204 to .412.**

Two honest brakes on the enthusiasm: July's wOBA (.412) ran ahead of its xwOBA (.337), so some of it is hot sequencing; and the **post-All-Star-break sample is 3 games / 14 PA** (.583/.643/1.500, 3 HR) — a fun cameo, well below any threshold, quoted here only because it is literally the newest data. The signal is "the shape is trending back toward his norms," not "he is fixed."

## 6. Tangible actions each persona could take

*Inference consistent with the indicators — the data cannot see intent. Each claim traces to §3–§5.*

**Trea Turner — get back to the pull side, in the air.** The engine is fine (bat speed up, barrels up), so this is a direction-and-decision fix, not a strength fix. The Phillies-era-low .352 pull rate and .117 pulled-air rate (his lowest marks since 2020) are the difference between this line and his .80-OPS norm, and July's uptick rode pulled-air climbing back to .159. Concretely: hunt the inner-half fastball he still crushes (.352 wOBA) and drive it, rather than serving pitches oppo — he's gone the other way at a career-high .326 clip while his in-zone swing rate fell to .692. Attack the hittable strike earlier.

**The hitting department — two named projects.** (1) **The offspeed hole is new and severe** (.184 wOBA, 37.8% K, .407 chase). That is a pitch-recognition / two-strike-plan item, not a swing-path item, and it is the single most fixable leak in the profile. (2) **The vanished platoon edge** (.632 OPS vs LHP, down from .88/.83) deserves a mechanical/timing look — it is uncharacteristic and, at 144 PA, still early enough to intervene before it hardens. Protect the July gains: pulled-air and line-drive rate are the leading indicators to watch, not batting average.

**The manager — bank the form, don't overreact to the cameo.** The recovery is real enough (trailing-100-PA OPS .973) to keep him in his normal lineup spot and let the process reattach; it is *not* real enough (14 post-break PA) to build a narrative on. If the soft top-end EV (90th-pct 103.5, a career low) is fatigue rather than age, a scheduled rest day or two in the dog days is cheap insurance. The one thing the data argues against is treating .691 as the new true talent — the contact quality says a hitter in the .295 xwOBA range who is trending up, not a .69-OPS hitter.

## 7. Candid caveats (read before extrapolating)

- **The down year is real and process-backed**, not a luck artifact — xwOBA .295 is a career low and sits *below* his wOBA. Do not expect a full snap-back to .80 OPS on batted-ball luck alone.
- **July is 62 PA and the post-break window is 14 PA.** Both clear the bar for "encouraging"; neither clears it for "fixed." Every small-sample line above is labeled with its PA on purpose.
- **wOBA .303 vs xwOBA .295** — a small overrun, i.e. the results are, if anything, slightly *ahead* of the contact. The risk is to the downside if the barrels don't hold.
- **vs-LHP .632 (144 PA)** and the **offspeed .184 (45 PA at the group level for the month splits)** are the two loudest leaks but also the two smallest samples in the deep-dive — flagged as directional, priority-to-watch.
- **"xwOBA" here is the PA-level mean of Statcast `estimated_woba_using_speedangle`** (populated on every PA — batted balls scored by exit velocity/launch angle, strikeouts as 0, walks/HBP at their wOBA value), so it behaves as full expected wOBA. The on-contact version (xwOBACON, .350 in 2026) is the separate `xwoba_con` receipt column. **2026 wOBA/wRC constants are in-season FanGraphs values** and will move by season's end; wRC provisional to ±2%.
- **Bat-tracking (bat speed, swing length, attack angle) is 2024+ only** and covers ~49% of swings; treat those three rows as directional, not census.

---

*Locked KPI mechanics inherited verbatim from dp_uc20 / dp_uc18 / Baseball Functions (get_stats wOBA with FanGraphs season weights; chase = swings at zone>9; hard-hit = EV≥95 on type=='X'; barrel = launch_speed_angle==6; pulled-air via hc_x/hc_y spray angle). NEW KPIs this UC: RF-1 season-to-date OPS trajectory (hero figure), RF-2 trailing-100-PA rolling-form wOBA/OPS — specs in governance 03, provisional. SC-1 wRC and SC-2 P/PA inherited from uc-pos-004. IBB excluded from BB per locked definitions. DQ: 23,250 deduped pitches, 0 duplicate keys, all BIP null rates ≤0.94% — `out/dp_uc24_turner_2026_review_dq_receipts.csv`. Governance package: `Agents for Data Products/data-products/uc-pos-006-turner-2026-offense-001/`. Ledger: this is UC #25 / uc-pos-006 / dp_uc24 — ledger update pending.*
