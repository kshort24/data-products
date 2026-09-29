# Offensive Advance Scout: the Phillies lineup vs Chris Sale (LHP)
### NL Wild Card Series, Game 1 · Philadelphia @ Atlanta · Truist Park · 2026-09-29 · 2:00 p.m. ET (NBC)

**Prepared for:** manager, hitting coach, advance meeting. One page per hitter, one page on Sale, one rule to carry into the dugout.  
**Opponent starter:** Chris Sale, LHP (ATL), MLBAM 519242 · 27 starts in 2026, last on 2026-09-23  
**Governance:** Use Case #50 (`uc-pos-018`, build `dp_uc50`). Lineage `uc-pos-001` (Phillies vs Wacha, the first lineup-vs-starter card) → this. KPIs are inherited by import, not copied: `dp_uc44_kernel` (nresults, whiff, chase, hard-hit), `dp_uc46_kernel` (certified directional family), `barrel_rate.py`, `dp_uc48_kernel` (xwOBAcon). New and provisional: XW-1 (PA-based xwOBA), HL-1 (inner/middle/away band), LR-1 (your Harper rank, generalised), TT-1 (time through the order). DQ 15 PASS / 2 WARN / 0 FAIL.

> ⚠️ **Read this first: data window and sample sizes.**
> • Regular season only, 2015 through Game 162 (2026-09-27). Hitters are locked by MLBAM id across the Phillies log and every MLB opponent file, with precedence dedup (378,334 rows → 360,327). No postseason or spring PA vs Sale exist for these nine.  
> • Head-to-head samples are small by nature: the biggest book is 27 PA. **PA is printed on every line; THIN = under 10 PA, directional only.** Where it matters, xwOBA is the number doing the work, not wOBA.  
> • Sale's 2025 is PARTIAL in this repo (`sale.parquet` ends 2025-05-23). His profile here is 2026 only, which is complete.  
> • Carry-ins, never computed on: batting order (your prompt), game time and network (MLB.com / NBC listings), Harper's quote (your notebook).

---

## Bottom line

1. **Sale is the 2026 version of Sale, and a little harder.** Sale in 2026: 27 starts, 650 PA, .258 wOBA, .267 xwOBA, 30.8% K, 4.8% BB. Four-seam 96.1 mph (+1.3 over 2024). Slider 40% of pitches, 38% whiff, .228 wOBA.
2. **The lefties can't be the plan.** The lefties have 1 hit in 2026: LHB vs Sale 24 PA, .066 wOBA. Career LHB .217 in 52 PA. Harper's .190 career OPS makes Sale the toughest of the 20 lefties he's seen 20+ times.
3. **The right side carries the offense.** The righties have done the work: RHB career .278 wOBA in 111 PA, 2026 .289 (.332 xwOBA). Bohm is the best bet on the card (25 PA, .365 wOBA). Turner (.323) and Hill (hard contact in a thin book) follow.
4. **Don't count on the order turning over.** No third-time relief: .262 / .254 / .258 wOBA the 1st / 2nd / 3rd+ time through. Getting to him early is no easier than later. What does change the 3rd time through is the HR rate (1.2% → 2.4%).
5. **The rule: make the slider a ball.** The slider is 40% of what he throws, with a 38% whiff rate and a .228 wOBA against. The four-seam is where the damage is: 96.1 mph, .285 wOBA, 27% whiff. Every hitter's plan below is a version of *hunt the heater in the zone, let the slider go.*

## 1 · Chris Sale, 2026

![Sale arsenal](out/dp_uc50_fig2_sale_arsenal.png)

| vs | Pitch | Usage | Velo | Whiff% | Chase% | wOBA | xwOBA | PA ended |
|---|---|---|---|---|---|---|---|---|
| LHB | Slider | 38.6% | 80.0 | 44% | 39% | .239 | .187 | 65 |
| LHB | Sinker | 32.9% | 95.5 | 9% | 39% | .277 | .287 | 51 |
| LHB | 4-Seam Fastball | 27.2% | 96.9 | 32% | 38% | .298 | .238 | 44 |
| RHB | 4-Seam Fastball | 45.9% | 96.0 | 27% | 32% | .283 | .311 | 215 |
| RHB | Slider | 40.3% | 79.7 | 36% | 37% | .225 | .224 | 204 |
| RHB | Changeup | 13.3% | 88.5 | 30% | 41% | .275 | .318 | 67 |

By side: LHB .264 wOBA / 33% K in 162 PA; RHB .256 / 30% in 488 PA. Lefties see a slider-sinker pitcher and righties see a four-seam-slider pitcher, with the changeup almost only for righties.

![Sale TTO](out/dp_uc50_fig3_sale_tto.png)

Four 2026 starts against Philadelphia: 99 PA, 04-18 .243, 04-26 .137, 09-04 .362, 09-11 .199 wOBA by start.

## 2 · The lineup card

![Lineup glance](out/dp_uc50_fig1_lineup_glance.png)

| # | Hitter | Bats | 2026 vs LHP PA | wOBA | xwOBA | vs Sale PA | AVG/OBP/SLG | wOBA | K% | Sale rank (LR-1) | Read |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Trea Turner | R | 235 | .275 | .324 | **27** | .280/.333/.400 | .323 | 26% | #4 of 15 | Unlucky against lefties, and the soft stuff is the leak |
| 2 | Kyle Schwarber | L | 258 | .389 | .387 | **27** | .200/.259/.520 | .327 | 37% | #5 of 9 | Career damage, 2026 silence |
| 3 | Bryce Harper | L | 268 | .299 | .314 | **21** | .095/.095/.095 | .084 | 52% | #1 of 20 | The one pitcher he hasn't solved |
| 4 | Alec Bohm | R | 193 | .351 | .337 | **25** | .304/.360/.478 | .365 | 24% | #4 of 8 | The matchup bat: contact that Sale hasn't beaten |
| 5 | Derek Hill | R | 138 | .328 | .284 | **7** THIN | .286/.286/.429 | .307 | 14% | — (7 PA < 20) | Fastball or nothing |
| 6 | Bryan De La Cruz | R | 41 | .288 | .311 | **9** THIN | .125/.222/.250 | .217 | 44% | — (9 PA < 20) | The slider test |
| 7 | Bryson Stott | L | 145 | .325 | .309 | **4** THIN | .000/.250/.000 | .173 | 0% | — (4 PA < 20) | A results rebound without the damage |
| 8 | Edmundo Sosa | R | 138 | .358 | .341 | **23** | .190/.261/.190 | .218 | 35% | #1 of 2 | A lefty masher Sale has figured out |
| 9 | J.T. Realmuto | R | 123 | .261 | .320 | **20** | .111/.200/.222 | .194 | 35% | #4 of 15 | Hitting it at people, not over them |

*LR-1 rank: 1 = the lowest OPS among LHP the hitter has faced 20+ times (your Harper cut). All nine vs Sale, career: 163 PA, .199/.258/.325, .258 wOBA.*

**The one-page notecard** (print this one):

![Lineup notecard](out/dp_uc50_fig4_lineup_notecard.png)

## 3 · The index cards

### 1 · Trea Turner (R): Unlucky against lefties, and the soft stuff is the leak

![Trea Turner](out/dp_uc50_card_1_turner.png)

Your read holds on results: .275 wOBA against lefties in 235 PA. The contact says otherwise (.324 xwOBA), so part of it is luck. The real leak is spin. Against LHP breaking balls he has a .218 wOBA, and against changeups .212. The pull habit sits on the inner third (65% pulled), where it pays (.336). On away pitches he already goes the other way more than he pulls (37% oppo, 31% pull). Those balls are simply weak (.241).

**Sale.** vs Sale: 27 PA, .280/.333/.400, .323 wOBA / .334 xwOBA. Sale ranks #4 toughest of 15 LHP he's seen 20+ times.  
**Plan.** Sale shows righties the four-seam 46% of the time. Hunt it in the zone. The changeup (13%) runs away, and that away ball is his weakest contact. Let it go.

### 2 · Kyle Schwarber (L): Career damage, 2026 silence

![Kyle Schwarber](out/dp_uc50_card_2_schwarber.png)

Your card reproduces exactly: 27 PA, .327 wOBA, .779 OPS on a .520 SLG. 1 in 5 balls in play is a barrel (20%), and 47% are hit hard. 2026 is the problem: 12 PA, .091/.167/.091, 33% K. He still hits lefties overall (.389 wOBA, 13% barrels in 258 PA). The damage is on fastballs (.474 wOBA) and not on breaking balls (.269, 41% whiff).

**Sale.** vs Sale career: 27 PA, 5 hits, 2 HR. 2026: 1 hit in 12 PA.  
**Plan.** Sale shows lefties the slider 39% and the sinker 33%. The four-seam is only 27%. Don't chase the slider to get to it. Take it until he has to come in.

### 3 · Bryce Harper (L): The one pitcher he hasn't solved

![Bryce Harper](out/dp_uc50_card_3_harper.png)

The ranking holds, but the number is .190 OPS, not .100: 21 PA, .095/.095/.095, 52% strikeouts. That is #1 of 20 lefties he's seen 20+ times. The median of the other lefties is .817. The mechanism is the chase: 56% of Sale's pitches out of the zone get a swing, and 47% of swings miss. 2026 vs all LHP is his softest year (.299 wOBA). Breaking balls are the leak (.252, 40% chase).

**Sale.** 2026 vs Sale: 12 PA, 0 hits, 8 K.  
**Plan.** Make him throw strikes. The slider below the zone is the out pitch. A walk is a win in this matchup.

### 4 · Alec Bohm (R): The matchup bat: contact that Sale hasn't beaten

![Alec Bohm](out/dp_uc50_card_4_bohm.png)

He has hit lefties every season: at least .345 wOBA against LHP in all 7 seasons with 40+ PA. 2026: .351 wOBA, .812 OPS, with only 12% strikeouts and 14% whiffs in 193 PA. He already does what Turner's card asks for. On away pitches he goes the other way 42% of the time and pulls just 24%. He's warm too: .371 xwOBA and 51% hard-hit over the last 30 days.

**Sale.** vs Sale: 25 PA, .304/.360/.478, .365 wOBA. 2026: 11 PA, 1.064 OPS. Sale is #4 of 8 LHP for him, near the middle.  
**Plan.** Batting 4th behind two lefties Sale has handled, he's the lineup's best RHB bet. Same approach: middle-away, use right field.

### 5 · Derek Hill (R): Fastball or nothing

![Derek Hill](out/dp_uc50_card_5_hill.png)

All-or-nothing against lefties: .492 SLG and 11% barrels, but 31% strikeouts in 138 PA. The contact grades lower than the line (.284 xwOBA vs .328 wOBA). The damage is on fastballs (.362 wOBA, 14% barrels). Breaking balls get 42% whiffs and 40% chases.

**Sale.** vs Sale: 7 PA, .286/.286/.429, .423 xwOBA. 83% of his balls in play were hit hard. That includes the 104-mph four-seam he doubled off in the 2nd inning on 9/11.  
**Plan.** Sit four-seam (46% to RHB). Two strikes: shorten up and give the slider nothing below the knees.

### 6 · Bryan De La Cruz (R): The slider test

![Bryan De La Cruz](out/dp_uc50_card_6_cruz.png)

The thinnest book on the card: 41 PA against lefties in 2026 (.288 wOBA). Pooled 2024–26, lefties beat him with spin: .224 wOBA on breaking balls with 42% chases. Fastballs are a different story (.340, 57% hard-hit).

**Sale.** vs Sale: 9 PA (THIN), .125/.222/.250, 44% K.  
**Plan.** Spit on the slider. If he doesn't chase it, Sale has to go to the four-seam, and that's the pitch he can drive.

### 7 · Bryson Stott (L): A results rebound without the damage

![Bryson Stott](out/dp_uc50_card_7_stott.png)

Against lefties the line came back: .325 wOBA in 145 PA, up from .274 and .257 in 2024–25. It's contact, not damage: 25% hard-hit and 4% barrels. The pitch he's never solved from a lefty is the breaking ball: .223 wOBA and 11% hard-hit, 2024–26.

**Sale.** vs Sale: 4 career PA, all in 2025 (THIN). He has not faced Sale in 2026.  
**Plan.** Same-side with the slider coming (39% to LHB). Stay up the middle and don't try to pull the slider.

### 8 · Edmundo Sosa (R): A lefty masher Sale has figured out

![Edmundo Sosa](out/dp_uc50_card_8_sosa.png)

On paper he's in the lineup for this: .358 wOBA and .829 OPS against lefties in 2026. He's also hot (.464 wOBA, 37 PA in the last 30 days, though the contact grades .323). Sale has figured him out anyway: 23 PA, .190/.261/.190, 35% K. The reason is the chase. He swings at 48% of lefties' pitches out of the zone, including 58% of changeups (2024–26).

**Sale.** Of the 2 lefties he's seen 20+ times, Sale is #1, the tougher one.  
**Plan.** Sale's changeup is 13% of what he throws righties, with a 41% chase rate. Make him throw it for a strike. Fastball in the zone, or take.

### 9 · J.T. Realmuto (R): Hitting it at people, not over them

![J.T. Realmuto](out/dp_uc50_card_9_realmuto.png)

The line against lefties is his lowest in 12 seasons (.261 wOBA, .562 OPS, 123 PA). The contact is better than that (.320 xwOBA). What's gone is lift: 2% barrels. Against LHP four-seams and sinkers he has 0 barrels in 74 PA. Last 30 days: .209 wOBA on .299 xwOBA.

**Sale.** vs Sale: 20 PA, .111/.200/.222, .194 wOBA. #4 of 15 LHP for him.  
**Plan.** Ninth, turning the lineup over. Get on base in front of Turner. A walk or a single up the middle is the job.

## 4 · The single attack rule

> **Make the slider a ball and the four-seam a strike.** Sale's slider is 40% of everything and his best pitch. Most of this lineup's damage against lefties comes on fastballs. Win the take, then win the heater.

### Game-plan takeaways

1. **Stack the right side in the middle innings.** Bohm, Hill and De La Cruz bat 4–6 and Sosa 8th. Late pinch-hit decisions should protect that platoon edge, not undo it.
2. **Harper and Schwarber: the walk is the win.** Both chase Sale's slider below the zone. A long at-bat in front of Bohm is worth more than a swing at a 1-2 slider.
3. **Sosa: no changeups.** His chase against lefties is the whole Sale problem. A strike or nothing.
4. **Turner: take the changeup away.** His away-pitch contact is his weakest. The four-seam is 46% of what Sale throws righties, so wait for it.
5. **Don't wait for the third time through.** Sale's results don't fade. If the Phillies are going to score off him, it'll be on fastball mistakes whenever they come.

## 5 · Your notebook, graded

| # | Subject | Your claim | Your value | Your method, today | Governed | Verdict |
|---|---|---|---|---|---|---|
| HP-01 | Turner | vs LHP 2026 'pretty bad' | (woba/ops printed, not quoted) | wOBA .266 / OPS .581 / 249 PA | wOBA .275 / xwOBA .324 / 235 PA | **HOLDS on results; process is league-average** |
| HP-02 | Turner | AIR% on pulls | 44% | 43.0% | 43.0% | **HOLDS; value moved to 43.0%** |
| HP-03 | Turner | Line-drive rate, straightaway | 30% | 28.8% | 28.8% | **HOLDS; value moved to 28.8%** |
| HP-04 | Turner | BA on balls hit oppo | .196 | .192 | .192 | **HOLDS; value moved to .192** |
| HP-05 | Turner | 'Too many pulls on pitches away from him' | (narrative) | — | Away-third BIP: pull 30.9%, oppo 36.8% (n=68); inner-third pull 64.9% | **DOES NOT HOLD as worded** |
| HP-06 | Schwarber | .327 wOBA / .779 OPS / 27 PA / .520 SLG | .327 / .779 / 27 / .520 | .327 / .779 / 27 / .520 | .327 / .779 / 27 / .520 | **REPRODUCED** |
| HP-07 | Schwarber | '1 in 5 BIP a barrel; less than half hit hard'; '5 career hits' | 20% / <50% / 5 | 20.0% / 46.7% / 5 | 20.0% / 46.7% / 5 | **REPRODUCED** |
| HP-08 | Harper | '.100 OPS vs Sale, BY FAR the worst of LHP with 20+ PA' | .100 | .190 (next worst .538, n=20) | .190 OPS, rank 1 of 20 (next worst .478) | **HOLDS in direction; value corrected** |
| HP-09 | Sale | Subtitle: FF mph / SL whiff / SI run / CH whiff | (computed in cell) | 96.1 mph / 38.4% / 18.00 in / 30.3% | 96.1 mph / 38.2% / 18.0 in / 30.3% | **REPRODUCED with one rounding note** |
| HP-10 | Sale | name-filtered 2026 frame is complete | (implicit) | 2565 pitches | 2575 pitches | **O-26 EXPOSURE** |
| HP-11 | Sosa | vs Sale (cell 137 output) | 23 PA / .451 OPS / .218 wOBA | 23 PA / .451 / .218 | 23 PA / .451 / .218 | **REPRODUCED** |
| HP-12 | Hill | 2026 barrel rate (cell 152) | .108 (14/130) | .108 (14/130) | .105 (14/133) | **REPRODUCED (client method); governed differs by 3 BIP** |

Notes: HP-01 your frame (`po26`) keeps spring and exhibition rows, and the governed frame is regular season. HP-05: the away pitch is where Turner's contact is weakest, but he isn't pulling it. The card says what holds instead. HP-08: '.100' does not reproduce from either frame today, and the ranking claim stands. HP-10 is O-26 again: a `nphl` name filter drops Sale pitches that were deduped into an earlier batter-keyed file.

## 6 · Candid caveats

- **Head-to-head is small.** 163 PA across nine hitters and four seasons. Every H2H line is directional. The cards lean on 2026-vs-LHP process (xwOBA, whiff, chase) and on pitch-group splits because those samples are 10–20× larger.
- **Pitch groups are a proxy for Sale.** 'Breaking balls from lefties' mixes many sliders and curves with Sale's 80-mph sweepy slider. Directional, not a Sale-shape comp.
- **HL-1 thirds are house geometry** (±0.28 ft on a ±0.83 ft plate). Cells under 25 BIP are marked * (FL-1) and are never quoted in the text as findings.
- **Coverage.** De La Cruz's non-Phillies 2025 is outside the repo (bdlc.parquet ends 2025-04-16). Sale's 2025 after 5/23 is present only against the Phillies. Neither changes a 2026 number.
- **Not modelled:** park, weather, bullpen usage after Sale, catcher framing, or the umpire.
- **Receipts:** `out/dp_uc50_*.csv` (every table), `out/dp_uc50_headlines.json` (every number in the prose), `dp_uc50_verification.py` (independent recompute). Governance trail: `Agents for Data Products/data-products/uc-pos-018-lineup-vs-sale-wc-g1-001/`.