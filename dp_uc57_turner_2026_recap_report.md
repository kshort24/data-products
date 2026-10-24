# Sounding the Alarm
### Trea Turner · 2026 season recap · uc-pos-022 · dp_uc57 v1.0.0 · data through 2026-10-01

| AVG | OBP | SLG | wOBA | xwOBA | IZ swing | Popup/BIP | PA |
|---|---|---|---|---|---|---|---|
| .242 | .297 | .378 | .298 | .293 | 68.9% | 8.0% | 700 |

## 1 · Bottom line

1. **Yes, it was atrocious by his own standard.** wOBA .298, xwOBA .293, OPS .675: last of his 10 seasons with 300+ PA on all three (previous low wOBA .331, 2018). He ran below every Phillies season at 5 of 6 hundred-PA checkpoints. Against the house pool it is the 40th percentile: below average, not bottom-tier.
2. **It does not start with breaking-ball recognition.** Against righty breaking balls his chase (34.8% → 34.8%) and contact were unchanged. He has never been able to touch them off the plate (7th percentile), and that did not get worse.
3. **The recognition break is on fastballs: he took strikes.** In-zone swing rate fell 73.9% → 68.9% (z -3.4), the strongest change in his profile, led by fastballs from both sides. When he swung at an in-zone fastball the hard contact held.
4. **The real decline is against righties.** xwOBA vs RHP .318 → .277. Against lefties the results collapsed (.347 → .276) but the expected line barely moved (.340 → .324).
5. **The popups and the flat swing are real, but they are not one mechanism.** Popups rose 5.0% → 8.0% of balls in play, mostly on breaking balls and slow lefty fastballs, and mostly in August-September. His swing got 1.4 deg flatter than his peers' on every pitch type (flattest of 12 Phillies). Breaking-ball popups were not flatter than his other breaking-ball contact, so PP-1 grades the link PARTLY.
6. **A position change can't be graded from his bat.** He played shortstop all year; there is no contrast in his data. The front office's view (CI-2) is quoted, not modeled.

> **Read this first**
>
> - Regular season only. Baseline = his 2023-25 Phillies seasons (1,871 PA); 2016-22 (Washington, Los Angeles) is shown as context, never pooled.
> - Every change call uses the bars fixed in the BID before any split was computed: |z| ≥ 1.96 CHANGED, 1.00-1.96 LEANS, below 1.00 SAME; cells under 30 BIP or 50 in the denominator print TOO FEW TO CALL.
> - Bat-path fields exist for 2025-26 only. Every swing-path comparison is 2025 vs 2026, netted against the same Phillies peer cohort UC40a used (PB-1).
> - Your notebook frame includes spring, exhibition and postseason rows and a one-year (2025) comparison. Each claim is reproduced on that frame first, then graded on the governed one.

## 2 · How bad was 2026?

*Q1* · He finished at .242/.297/.378 in 700 PA, which reconciles to FanGraphs (CI-1: wRC+ 83, 1.1 WAR). The season had one good month (July: .381 wOBA) between a flat spring and an August-September where popups jumped to 15% and 14% of balls in play. The bat itself was not slower: bat speed 70.0 mph, in line with 2024-25. What moved was the swing decision in the zone and the quality of the swing plane.

![Worst of his 10 full seasons, wire to wire](out/dp_uc57_f1_cumulative.png)

![Below the house median on the results, and his own floor on every one of them](out/dp_uc57_f2_season_card.png)

## 3 · Recognition: in the zone vs out, by hand

*Q2 · Q3* · PR-1 asks whether he swings at strikes and lays off balls, pitch group by pitch group. Against righties' breaking balls the answer did not change (swing gap .376 → .364, SAME; contact gap .472 → .522). Against lefties' breaking balls it improved (whiffs per swing 36.3% → 25.8%, CHANGED). The gap collapsed on fastballs (vs RHP .398 → .287; vs LHP .511 → .408) and on righty changeups (.450 → .230). Your RHP read is right about the contact: off the plate, righty breaking balls are close to untouchable for him (29.5%, 7th percentile). It is a standing weakness, not a 2026 one, and he did not chase them more. The extra expanding against righties came on fastballs (32.0% → 36.3%, LEANS) and offspeed (40.7% → 52.0%, LEANS).

![Recognition broke down on fastballs, not breaking balls](out/dp_uc57_f3_decision_map.png)

![He can't touch righty breaking balls off the plate, but he never could](out/dp_uc57_f4_rhp_breaking.png)

## 4 · Lefties and offspeed

*Q4* · Against lefties his wOBA fell .347 → .276. Split by the pitch that ended the PA, offspeed accounts for -0.029, fastballs -0.022 and breaking balls -0.021: three similar pieces, not one driver. On lefty offspeed specifically, the popups are the real change (5 of 31 balls in play) and the hard contact held (41.9%). The whiff increase only looks large against 2025, his best year; against 2023-25 it is noise. Expected wOBA on lefty offspeed was .291, the same as 2023-25 (.290).

![Against lefty offspeed: the popups are real, the extra whiffs are not](out/dp_uc57_f5_lhp_offspeed.png)

## 5 · Fastballs and the slow lefty fastball

*Q5 · Q6* · Your instinct that he should swing at more in-zone fastballs is the strongest call in the notebook: his in-zone fastball swing rate fell vs righties (71.8% → 65.1%) and lefties (77.7% → 69.8%), both CHANGED. Damage on the in-zone fastballs he did swing at held up (hard-hit SAME both sides). Popups on lefty fastballs leaned up (4.1% → 9.6%, z +1.95, just short of CHANGED). On slow lefty fastballs (under 95), xwOBA on contact fell .440 → .348 and popups tripled. It is the fourth straight year of decline on that pitch.

![The fastball leak is takes, not weak contact](out/dp_uc57_f6_fastballs.png)

![Slow lefty fastballs stopped being his best pitch to hit](out/dp_uc57_f7_lhp_velo.png)

## 6 · The bat path, full season

*Q7* · UC40a found the flat path on 2026-09-02; the same code on the full season reproduces that cut exactly (1100 swings, tilt 25.51) and extends it. Full-season tilt 27.9 → 25.3 deg, a -2.6 drop against a -1.2 peer median (net -1.4). He was already flat in 2025 and is now the flattest of 12 Phillies regulars. Contact moved +1.3 in further from his body (net +1.1; on breaking balls net +2.0). Attack angle did not move (net +0.2). Breaking-ball popups rose 4.9% → 11.6% (CHANGED), but they sat only -0.9 deg vs his other breaking-ball contact, short of the -2.0 bar set in advance. Within 2026, his flattest third of swings produced a .289 xwOBA on contact and 11.5% popups, vs .375 and 6.4% in the middle third. That supports working on the path, as an association: tilt also tracks pitch height, so it is not a controlled test.

![The swing flattened against everything, beyond the team-wide drift](out/dp_uc57_f8_swing_path.png)

![Popups came with the flatter swing, but not as a separate popup swing](out/dp_uc57_f9_contact_points.png)

## 7 · Shortstop, second base, or the outfield

*Q8* · His 2026 offense was produced entirely at shortstop, so the log holds nothing that could show whether another position would change it (HP-12, NOT TESTABLE). The front office's framing, quoted from NBC Sports Philadelphia (2026-10-15, CI-2): Dave Dombrowski, "If he plays shortstop like he did in '25, he can play shortstop. But if he plays it like he did in '26, he can't." Second base and the outfield are the named alternatives. The defensive line behind that (carry-ins, not computed here): OAA -10 (2025 +17), DRS -17, 21 errors. Seven years and $190M remain, with a full no-trade clause. Nothing in this product suggests a move would fix the swing decisions or the path.

## 8 · The notebook graded

Each claim was reproduced on your own frame and functions first (left), then graded on the governed build.

| # | Claim | Your frame | Governed evidence | Grade |
|---|---|---|---|---|
| HP-01 | An atrocious year | client frame: n/a (no season line in this cell; client 2026 BA by cell e.g. RHP breaking .225) | wOBA .298 / xwOBA .293 / OPS .675: last of his 10 seasons with >= 300 PA (2016-26) on all three; previous low wOBA .331 (2018). House pool: 40th pct wOBA of 220 Phillies hitter-seasons | **SUPPORTED** |
| HP-02 | Weakness against offspeed likely drove underperformance against lefties | client: LHP offspeed BA .190 2026 vs .306 2025 | vs LHP wOBA .347 -> .276; of the -0.071, offspeed -0.029, fastballs -0.022, breaking -0.021. xwOBA vs LHP .340 -> .324; on LHP offspeed .290 -> .291 | **PARTLY** |
| HP-03 | In-zone swing was down and chase was up | client: IZ swing vs RHP fastballs 69.3% -> 66.1% | IZ swing 73.9% -> 68.9% (CHANGED, z -3.36; n 1228); chase 33.5% -> 34.6% (SAME, z +0.75; n 1421); vs RHP chase 34.1% -> 37.3% (LEANS, z +1.75; n 919) | **PARTLY** |
| HP-04 | Almost no pulls or pull-airs | client frame: n/a (pull_air_rate not in this cell) | in-zone pull share 47.5% (2023-25) -> 40.5% (z -2.47); pull-air 18.7% -> 17.0% (z -0.85), Phillies 2026 median 17.9% | **PARTLY** |
| HP-05 | Flat bat path through contact, especially against breaking balls, led to an increase in pop-ups | client: popup rate vs RHP breaking 3.1% -> 13.1% | PP-1: breaking-ball popup rate 4.9% -> 11.6% (CHANGED, z +2.98); 2026 breaking-ball popups -0.9 deg vs other BIP (bar -2.0; n 17). Whole swing flatter: tilt 27.9 -> 25.3 deg, peer-netted -1.4, flattest of 12 Phillies | **PARTLY** |
| HP-06 | vs RHP: expanding the zone ... really cannot make contact when he expands on righty breaking balls | client: OOZ contact vs RHP breaking 36.1% (2025) -> 32.4% (2026) | OOZ contact 34.1% -> 29.5% (SAME, z -0.99; n 139) = 7th pct of 41 Phillies hitter-seasons; chase 34.8% -> 34.8% (SAME, z -0.02; n 400); expansion vs RHP is on fastballs (chase 32.0% -> 36.3% (LEANS, z +1.63; n 421)) and offspeed | **PARTLY** |
| HP-07 | vs LHP: could take offspeed pitches when he connected but he whiffed more and popped them up too much | client: LHP offspeed whiff 24.7% -> 39.6%, popups 6.1% -> 18.2% | hard-hit 35.1% -> 41.9% (SAME, z +0.69; n 31); whiff 36.2% -> 39.0% (SAME, z +0.47; n 82); popup 4.1% -> 16.1% (CHANGED, z +2.28; n 31) | **PARTLY** |
| HP-08 | Fastballs vs RHP: could chase a touch less and do more damage in the zone | client: chase vs RHP fastballs 29.5% -> 36.1% | chase 32.0% -> 36.3% (LEANS, z +1.63; n 421); IZ swing 71.8% -> 65.1% (CHANGED, z -2.77; n 478); in-zone contact: hard-hit 53.9% -> 57.6% (SAME, z +0.78; n 144), xwOBAcon .411 -> .371; PR-1 swing gap .398 -> .287 (CHANGED) | **PARTLY** |
| HP-09 | Fastballs vs LHP: more popups ... needs to swing at fastballs in the zone and chase less | client: popups vs LHP fastballs 3.4% -> 9.3% | popup 4.1% -> 9.6% (LEANS, z +1.95; n 94); IZ swing 77.7% -> 69.8% (CHANGED, z -2.42; n 245); chase 26.5% -> 29.0% (SAME, z +0.70; n 231) | **PARTLY** |
| HP-10 | Needs to do damage on slow lefty fastballs | client: LHP fastballs < 95 mph BA .350 (2025) -> .208 (2026) | < 95 mph: xwOBAcon .440 -> .348 (72 BIP); popup 3.6% -> 9.7% (CHANGED, z +2.00; n 72); hard-hit 48.7% -> 44.4% (SAME, z -0.62; n 72); 95+ bucket: 22 BIP, too few to call | **SUPPORTED** |
| HP-11 | If he can resolve the path of his barrel through the zone, he can get back to doing damage | client frame: n/a | 2026 tracked BIP by tilt third: flattest xwOBAcon .289, popup 11.5%; middle .375, 6.4%; steepest .332, 4.5% (157/156/157 BIP) | **PLAUSIBLE, NOT PROVEN** |
| HP-12 | Perhaps playing a different position improves his offense | client frame: n/a | He played shortstop all season: no position-change contrast exists in his data. Carry-in CI-2 only (Dombrowski, 2026-10-15) | **NOT TESTABLE** |

**Candid caveats**

- Small cells: lefty offspeed (31 BIP), lefty fastballs 95+ (22 BIP) and breaking-ball popups (17 tracked in 2026). Every rate prints its n.
- Tilt depends on pitch height, so the tilt-third association (HP-11) is not controlled for location. It is evidence for the direction, not proof.
- xwOBA on contact has no proportion test; differences are shown with n and never called CHANGED.
- PR-1 is a new, provisional KPI. Its gap z uses the unpooled Wald SE of the four legs; the legs themselves use the inherited two_prop_z.
- The PB-1 peer cohort is 8 Phillies hitters (200+ tracked swings in 2025 and 2026), as in UC40a. Peer-netting removes the team-wide tilt drift (O-16) but cannot rule out a sensor change.
- Pooled 2023-25 wOBA uses each season's own weights (WB-2, inherited from UC56).
- Your notebook maps knuckleballs to Breaking; the house map has them as offspeed (CPG-1). No Turner cell is affected in a way that changes a grade.
- The reconstructed 3D swing (Single-Swing Pilot) is not in this product. It stays Tier B until the pilot's Gate 2 closes.

**Three things for 2027**

1. **Swing at in-zone fastballs.** Getting back to his 2023-25 in-zone fastball swing rate (71.8% vs RHP, 77.7% vs LHP) is the cheapest fix on the board: the contact quality on those swings is still there.
2. **Steepen the path and track it monthly against peers.** The target is his own 2025 tilt (27.9 deg), peer-netted. Watch popups on breaking balls and slow lefty fastballs as the outcome check.
3. **Take the righty breaking ball off the plate.** He has never hit it. The plan is to lay off it, not to learn to hit it.

*Phillies Statcast house log through 2026-10-01; regular season. Carry-ins CI-1 (FanGraphs) and CI-2 (NBC Sports Philadelphia) are quoted, never computed on. 17 sha256 lineage pins; DQ 10 pass / 3 warn / 0 fail.*