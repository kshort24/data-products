# Aaron Nola | 2026 | Better Process Than Results, and a Book Built on the Curve
### Season recap + career pitch-sequencing engine · `uc-pps-040` · build `dp_uc64` v1.0.0 · UC #64 · data through 2026-10-01

> **Read this first: data window and sample sizes.**
> - **Frame:** house log `phils_2015..2026`, pitching role, entity-locked to **MLBAM 605400** (the name filter returns the same rows; the 'Nola' substring also matches Nolan Hoffman 676510, so names are never the key). Regular season only for every rate; the Wild Card Game 3 start (10/01, 38 pitches) is one line in §5.
> - **2026:** 33 starts, 2,955 pitches, 745 PA. **Career sequencing pool:** 30,079 pitches, 7,767 completed PA (2015–26), as the client ruled (Q-C "career-wide everything").
> - **Reconciliation (REC-1):** log K = 177 = public; walks 57 + 2 intentional = 59 = public; outs 524 reconstructed vs 526 public (0.4% short, an OU-1 blind spot on no-event rows). ERA, W-L and WHIP are public carry-ins (CBS Sports, ESPN), not log-derived.
> - **Sequencing numbers are small and noisy by nature.** Every lift prints its n and a 90% PA-cluster bootstrap interval. Of 176 rankable sequences, 28 clear their interval where ~18 would by chance: **real signal in aggregate, but any single sequence could be noise.**
> - Statcast cannot say who called a pitch (guardrail G4). "Batterymate" differences are differences in what was thrown with each catcher behind the plate.

---

## Bottom line

1. **The process was mid-pack or better; the damage came on fastballs in the air.** Against 40 Phillies starter seasons since 2015, 2026 Nola ranks 65th percentile in whiff (27.1%), 77th in chase (33.3%), 67th in CSW (29.8%), but 5th in wOBA (**.343**) and dead last in HR per PA (**5.0%**). Expected wOBA (.315, 27th pct) says he deserved better than he got. The curve earned **+1.1** runs per 100; every fastball variety was underwater (four-seam -2.1, sinker -2.8, cutter -3.0). Public line: 33 GS, 175.1 IP, 4.67 ERA, 177 K, 59 BB (CI-1).
2. **The arc bent in the summer, mostly in results.** First half .355 wOBA (426 PA), second half .327 (319 PA); xwOBA barely moved (.318 → .310). August was the best month (.306 wOBA, .280 xwOBA, 29.3% K). Second-half starts with Stubbs averaged a 59.0 Game Score (8 starts) vs 41.8 with Realmuto (5). That is descriptive, not causal: `uc-pps-027` showed the July plan travels across catchers.
3. **The prior products, re-read at season's end:** the 7/05 changeup pivot held (share 12.6% → 20.1%; two-strike fastball rate 47.8% → 39.0%) and lefties got easier (.386 → .304 wOBA; walks 11.9% → 9.2%). Two tripwires did not cooperate. The changeup to lefties got *hit more* as he threw it more (.192 → .311 wOBA, 54 PA). Lefty first-pitch strikes (59.2%) stayed under his 2017–24 norm (62.0%).
4. **He finishes hitters with the curve, and that is the best thing in his book.** Ending a PA on two straight curves holds hitters to **.222** xwOBA vs LHB and **.174** vs RHB (career levels .301 / .280), with a strikeout in ~45% of those PAs. The worst endings are sinkers to lefties (sinker-sinker .366, changeup-sinker .388) and changeup-then-four-seam to righties (.396).
5. **The setups that add run prevention beyond the pitch itself:** vs RHB the **sinker sets up the changeup** (lift +3.2 (90% +1.4 to +5.0; n 304)) and the four-seam (+2.3 (90% +0.7 to +3.9; n 349)); vs LHB the **changeup sets up the curve** (+1.8 (90% +0.2 to +3.3; n 535)). The costliest: changeup → four-seam vs RHB (-2.4 (90% -4.8 to -0.2; n 394)) and sinker → curve → curve vs LHB (-7.3 (90% -12.5 to -2.5; n 154)).
6. **"He used to rely on a sequence…": not as a sequence.** Under the pre-registered bar, **0 of 43 testable sequences FADED** from his young era (2015–19) to 2025–26; 3 GREW, all vs lefties. The one staple that slipped on both counts is **two straight curves to righties** (raw +3.7 → -0.3, lift +1.1 → -2.0 runs/100, n 121 recent), inside the noise. The 2025–26 decline is mostly in the pitches (fastball run value), not in their order.
7. **Batterymates:** vs RHB Realmuto and Stubbs games show the **same book** (p = 0.73). Vs LHB they differ beyond chance (p = 0.002 over 2023–26, and still p = 0.002 on 2023–25 alone, before the July pivot). Stubbs games throw fewer back-to-back four-seams to lefties (10.2% → 5.9% of pairs) and more cutter pairs. The difference is real but small.
8. **Stretch S-1:** 2026 was the **least predictable mix of his career** (2.17 bits of next-pitch entropy, 9th of 41 Phillies SP seasons). Knowing the previous pitch tells a hitter almost nothing (0.034 bits).

---

## Part I — The season

### 1 · The line, in context

![F1](out/dp_uc64_f1_context.png)

| Season | PA | wOBA | xwOBA | K% | BB% | HR/PA | Whiff | Chase | CSW | RV/100 |
|---|---|---|---|---|---|---|---|---|---|---|
| 2018 | 830 | .249 | .258 | 27.0% | 6.6% | 2.0% | 27.7% | 30.0% | 33.0% | +1.58 |
| 2022 | 809 | .262 | .260 | 29.0% | 3.5% | 2.3% | 27.9% | 34.0% | 33.6% | +0.79 |
| 2023 | 792 | .303 | .299 | 25.1% | 5.7% | 4.0% | 26.0% | 34.7% | 30.7% | -0.08 |
| 2024 | 822 | .309 | .304 | 23.8% | 6.1% | 3.6% | 25.2% | 32.1% | 29.2% | +0.24 |
| 2025 | 406 | .344 | .327 | 23.9% | 6.9% | 4.4% | 25.2% | 33.5% | 30.0% | -0.57 |
| 2026 | 745 | .343 | .315 | 23.8% | 7.7% | 5.0% | 27.1% | 33.3% | 29.8% | -0.75 |

*2018 = peak reference (3rd in Cy Young voting); 2025 = injury-shortened (406 PA). wOBA is the house FanGraphs-weighted line; xwOBA is XW-1 (PA-denominated).*

The **.028** gap between wOBA and xwOBA is the widest of his career, and the home run is the reason: 5.0% of PA ended in one (37 allowed). Strikeouts (23.8%, 42nd pct) matched his lowest full-season rate since his 2015 debut. But whiff per swing was *above* every 2023–25 season and chase was in line with them, so the low K rate is not a bat-missing collapse. Hitters chased and missed about as often as they did against his good years; the contact they did make carried.

![F2](out/dp_uc64_f2_career.png)

### 2 · The arc

![F3](out/dp_uc64_f3_starts.png)

| Window | PA | wOBA | xwOBA | K% | BB% | HR/PA | RV/100 |
|---|---|---|---|---|---|---|---|
| 1st half (≤ 7/12) | 426 | .355 | .318 | 23.9% | 7.3% | 4.7% | -0.91 |
| 2nd half (≥ 7/16) | 319 | .327 | .310 | 23.5% | 8.2% | 5.3% | -0.54 |
| March | 22 | .371 | .396 | 31.8% | 9.1% | 9.1% | -2.41 |
| April | 118 | .369 | .335 | 23.7% | 9.3% | 3.4% | -0.75 |
| May | 106 | .329 | .316 | 19.8% | 4.7% | 3.8% | -0.48 |
| June | 132 | .394 | .318 | 23.5% | 8.3% | 6.8% | -1.82 |
| July | 121 | .338 | .302 | 24.0% | 6.6% | 5.8% | -0.82 |
| August | 140 | .306 | .280 | 29.3% | 8.6% | 4.3% | +0.35 |
| September | 106 | .315 | .329 | 18.9% | 7.5% | 4.7% | -0.75 |

*Halves use the governed SD-2 `asb_2026` boundary. March is 22 PA (one start): directional only.*

The shape is an uneven first half (6 starts under a 40 Game Score, 4 at 60+ across 19 starts), then an August that looked like vintage Nola. Then a September that gave some back (xwOBA .329, K 18.9%). Public carry-ins agree on the turn: a 5.86 ERA through 13 starts (MLB.com, June) and a 2.93 ERA over 11 starts from August 1 (CBS Sports). His last regular-season outing (9/26) lasted 1.0 IP; the Wild Card start came on short rest (CI-4).

### 3 · The prior products, re-read at season's end

![F4](out/dp_uc64_f4_pivot.png)

| Tripwire (source) | 2017–24 | 2026 thru 7/04 | 2026 from 7/05 | Read |
|---|---|---|---|---|
| Changeup share (`uc-pps-027`) | 16.4% | 12.6% | 20.1% | pivot held to the end (UC38 had 22.8% through 8/26) |
| CH when behind (`uc-pps-027`) | 18.9% | 12.5% | 26.6% | held |
| Two-strike fastball rate, BAT-4 (`uc-cat-001` → `uc-pps-027`) | 47.8% | 47.8% | 39.0% | held: fewer heaters to finish |
| LHB wOBA (`uc-pps-021`) | .289 | .386 (218 PA) | .304 (240 PA) | improved, still above his norm |
| LHB walk rate (`uc-pps-021`) | 7.4% | 11.9% | 9.2% | improved, still above his norm |
| LHB first-pitch strike (`uc-pps-021`) | 62.0% | 57.8% | 59.2% | **never recovered** |
| CH vs LHB wOBA (`uc-pps-021`) | .279 | .192 (36 PA) | .311 (54 PA) | **regressed** as usage rose |
| RHB walk rate (`uc-pps-027` E-6) | 5.1% | 1.9% | 4.7% | the E-6 tripwire fired and stayed (back to his norm) |

`uc-pps-027` closed in August with "he is not getting ahead of lefties, he is *escaping* them with the changeup". That is still the right sentence at season's end. The escape worked on the scoreboard, and it got more expensive per changeup once lefties expected it.

### 4 · The arsenal: the curve carried, the fastballs paid

| Pitch | 2018 use · velo · whiff/sw · RV/100 | 2025 | 2026 use · velo · IVB / HB (in) · whiff/sw · RV/100 |
|---|---|---|---|
| Curve | 31% · 78.0 · 41% · +2.6 | 29% · 78.2 · 39% · -0.6 | 33% · 78.4 · -10.3 / 14.8 · 41% · +1.1 |
| 4-Seam | 36% · 92.7 · 19% · +1.4 | 30% · 91.9 · 14% · -0.4 | 24% · 92.3 · 14.6 / -12.8 · 14% · -2.1 |
| Sinker | 13% · 91.4 · 15% · +1.5 | 18% · 90.7 · 11% · -0.4 | 18% · 91.6 · 8.2 / -17.4 · 12% · -2.8 |
| Changeup | 20% · 84.8 · 30% · +0.4 | 15% · 84.8 · 30% · +0.1 | 16% · 85.6 · 2.9 / -14.6 · 26% · +1.0 |
| Cutter | — (added 2021) | 7% · 86.2 · 27% · -2.5 | 8% · 86.2 · 7.6 / 0.7 · 26% · -3.0 |

*CU (2015–16 tag) is folded into KC (PT-H). 19 pitches tagged SL in 2026 (83 mph, ~4 in of sweep) are kept as tagged and are too few to read.*

The curveball is nearly the same pitch it was in 2018: same drop, a little less sweep, same 41% whiff per swing, positive run value, and it was his most-used pitch (33%). The four-seam has *more* ride than in 2018 (IVB 14.6 in vs 12.4) at a similar speed, yet its whiff rate fell from 19% to 14%, and the sinker and cutter were both worse than −2.5 runs per 100. Part II's job is to ask whether *order* can rescue those pitches.

### 5 · Catchers and the Wild Card

| Catcher (2026) | Starts | PA | wOBA | xwOBA | K% | BB% |
|---|---|---|---|---|---|---|
| Realmuto, J.T. | 15 | 333 | .372 | .325 | 24.0% | 7.2% |
| Stubbs, Garrett | 12 | 276 | .284 | .281 | 24.3% | 6.9% |
| Marchán, Rafael | 6 | 136 | .392 | .357 | 22.1% | 10.3% |

Stubbs caught the best of it (.281 xwOBA), consistent with `uc-cat-002`. He also caught 8 of the 14 second-half starts, after the pivot, so the split mixes catcher and calendar. Marchán's 6 starts (136 PA) are directional only.
**Wild Card Game 3 at Atlanta (10/01):** 38 pitches, 9 PA, 2 H, 1 HR, 2 BB, 1 K; public line 1.2 IP, loss (CI-4). Too small to read beyond the box score.

---

## Part II — Pitch sequencing

### 6 · How the engine credits a sequence

The client's `pitch_sequence()` is in the kernel **verbatim** (SQ-0). It labels every PA with its full pitch string (`FF-KC-KC`). Full strings are too fragmented to rank: 2026 alone had 502 distinct strings across 746 PA. So the engine works on the pieces, under the three rulings the client made at intake:

- **Windows (SQ-1):** every run of 2, 3 or 4 consecutive pitches *inside* a PA, wherever it sits ("identified within longer sequences"), pooled 2015–26 (Q-C).
- **Setup lift (SQ-2), the headline (Q-A):** score the *last* pitch of the window on run value (pitcher's view of Statcast `delta_run_exp`), **minus what that same pitch type earns in that same count against that same side**, from Nola's own history. A four-seam on 1-2 is compared only to other 1-2 four-seams. What is left is what the setup added. Reported as runs saved per 100 follow-up pitches, with CSW and whiff lifts on the same rule.
- **Endings (SQ-3), the readable view (Q-A):** the last 2–3 pitches of each PA, scored on how the PA ended: out (OUT-1), strikeout, **poor contact** (PC-1 = Savant launch_speed_angle 1–3, Weak/Topped/Under, per Q-B) and xwOBA (XW-1).
- **Stability (SQ-4):** rank only with n ≥ 50; shrink toward zero (n / (n + 100)); 90% intervals from 1,000 bootstrap resamples **of whole PAs** (windows inside one PA are not independent).
- **Curveball labels:** CU (2015–16) and KC (2017+) are one pitch (PT-H), so "young era" curve sequences line up with recent ones.

### 7 · The pairs, by side

![F5](out/dp_uc64_f5_lift_grid.png)

Read F5 row by row: "after this pitch, how much better or worse is the next one than it usually is?"

- **vs LHB:** the changeup is the setup pitch. After a changeup, the curve is +1.5 (shrunk, n 535) and another changeup +1.0. After a sinker, the curve is his worst lefty pair (-1.3, n 589): the arm-side sinker doesn't set up a curve that breaks back over the plate to a lefty.
- **vs RHB:** the sinker is the setup pitch. After a sinker, the changeup (+2.4) and the four-seam (+1.8) both play up. After a changeup, the four-seam is the worst righty pair (-1.9, n 394), and curve → changeup is close behind (-1.8).
- **The pairs he throws most (FF→KC, KC→FF, KC→KC) sit near zero on both sides.** That is expected: the high-volume pairs *are* the baseline. Their value is in the endings (§8), not in surprise.

### 8 · The sequences that maximize run prevention

![F6](out/dp_uc64_f6_ranked.png)

![F7](out/dp_uc64_f7_endings.png)

| Side | Sequence (k) | Use | Setup lift (runs/100, 90%) | CSW lift | Poor contact | n |
|---|---|---|---|---|---|---|
| LHB | FF-KC-FF-FF (4) | 1.2% | +7.1 (+2.9 to +12.0) | +13.8 pts | 75% | 62 |
| LHB | FF-SI-CH (3) | 1.0% | +5.1 (+2.0 to +8.6) | -0.6 pts | 83% | 81 |
| LHB | CH-FF-FF (3) | 1.6% | +4.0 (+0.8 to +7.1) | -2.0 pts | 80% | 130 |
| LHB | CH-CH-SI (3) | 0.9% | +5.0 (+0.7 to +8.7) | -13.0 pts | 50% | 76 |
| LHB | CH-KC-KC (3) | 1.1% | +4.1 (+1.3 to +6.7) | +0.5 pts | 74% | 92 |
| LHB | KC-SI-SI (3) | 1.0% | +4.2 (+0.2 to +8.3) | +3.0 pts | 50% | 81 |
| LHB | KC-FC (2) | 0.9% | +3.2 (+0.2 to +6.3) | +3.5 pts | 50% | 103 |
| LHB | CH-KC (2) | 4.7% | +1.8 (+0.2 to +3.3) | +3.3 pts | 62% | 535 |
| LHB | CH-KC-FF (3) | 1.7% | +2.4 (+0.2 to +4.6) | -1.7 pts | 65% | 136 |
| LHB | KC-FF-KC-KC (4) | 1.0% | +4.0 (+0.9 to +7.3) | -0.6 pts | 100% | 52 |
| LHB | FC-SI (2) | 0.5% | +2.4 (+0.1 to +4.7) | +8.1 pts | 71% | 63 |
| RHB | SI-CH-KC (3) | 0.8% | +8.2 (+3.3 to +12.6) | +10.1 pts | 77% | 56 |
| RHB | FF-SI-FF (3) | 1.0% | +6.5 (+3.6 to +9.6) | +5.5 pts | 70% | 76 |
| RHB | FF-SI-SI (3) | 1.3% | +5.7 (+3.1 to +8.2) | +1.0 pts | 62% | 92 |
| RHB | KC-FF-FF-KC (4) | 1.7% | +5.6 (+1.7 to +9.5) | +2.9 pts | 83% | 76 |
| RHB | SI-CH (2) | 2.8% | +3.2 (+1.4 to +5.0) | +0.3 pts | 62% | 304 |
| RHB | SI-FF (2) | 3.2% | +2.3 (+0.7 to +3.9) | +2.4 pts | 56% | 349 |
| RHB | FF-KC-KC (3) | 4.1% | +2.2 (+0.6 to +3.9) | +1.9 pts | 69% | 302 |
| RHB | SI-SI-CH (3) | 0.7% | +4.4 (+0.1 to +9.0) | -0.4 pts | 64% | 54 |
| RHB | SI-FF-FF (3) | 0.8% | +4.0 (+0.4 to +7.3) | -3.2 pts | 64% | 61 |
| LHB | SI-KC-KC (3) | 1.9% | -7.3 (-12.5 to -2.5) | -3.4 pts | 61% | 154 |
| LHB | KC-SI-KC (3) | 1.5% | -7.5 (-14.6 to -1.1) | -4.3 pts | 33% | 120 |
| LHB | KC-FF-CH (3) | 2.0% | -4.5 (-8.8 to -0.4) | -8.0 pts | 66% | 157 |
| LHB | CH-SI-CH (3) | 0.6% | -5.7 (-10.7 to -0.9) | -1.3 pts | 40% | 52 |
| LHB | KC-SI-FF (3) | 0.9% | -4.3 (-8.9 to -0.1) | -8.7 pts | 47% | 70 |
| RHB | FF-CH-FF (3) | 1.4% | -5.8 (-11.1 to -1.2) | -0.3 pts | 27% | 104 |
| RHB | CH-FF (2) | 3.7% | -2.4 (-4.8 to -0.2) | -3.4 pts | 53% | 394 |
| RHB | CH-KC-KC (3) | 0.8% | -5.2 (-10.3 to -0.1) | -8.0 pts | 64% | 56 |

*All 28 rankable sequences whose 90% interval excludes zero (20 help, 8 hurt), of 176. About 18 would clear by chance (binomial p = 0.009 for this many). Pairs alone: 6 of 46, about what chance gives; most of the signal is in triples (19 of 110). Overlapping windows mean these tests are not independent: treat the list as candidates, not verdicts.*

**What maximizes run prevention, in plain terms:**

1. **Finish with the curve, and don't be afraid to throw it twice.** Two-curve endings: .222 xwOBA / 44% K vs LHB (335 PA); .174 / 45% K vs RHB (437 PA). The best three-pitch ending on either side is four-seam → curve → curve (.179 L, .154 R). Against righties, four-seam → curve → curve also clears the setup-lift bar (+2.2 (90% +0.6 to +3.9; n 302)).
2. **To righties, show the sinker first.** Sinker → changeup and sinker → four-seam are his only two righty *pairs* whose lift clears zero, and three-pitch strings opening with four-seam → sinker (FF-SI-FF, FF-SI-SI) are at the top of the righty list.
3. **To lefties, the changeup is the setup, not the finisher.** Changeup → curve adds +1.8 runs/100 (n 535) and changeup → four-seam → four-seam clears too (+4.0 (90% +0.8 to +7.1; n 130)). The changeup *ending* a lefty PA (curve → changeup, four-seam → changeup) is neutral at best.
4. **What to stop doing:** sinker endings to lefties (SI-SI .366, CH-SI .388 xwOBA); sinker → curve → curve and curve → sinker → curve to lefties (both clearly negative); changeup → four-seam to righties (.396 xwOBA as an ending, negative lift as a pair).

**2026 only** (career baseline; small): vs LHB, four-seam → curve held up (+2.4 (90% +0.1 to +4.8; n 131)). Curve → four-seam was his worst high-volume lefty pair (-3.1 (90% -6.6 to -0.0; n 128)). No 2026 righty pair clears its interval (largest n 93).

### 9 · "He used to rely on a sequence in his younger years…"

![F8](out/dp_uc64_f8_eras.png)

Pre-registered (BID, before compute): eras **Young 2015–19** vs **Recent 2025–26**. Each era is scored against *its own* pitch-in-count baselines, so a fade means the **order** stopped working, not that the pitches got worse. FADED = lift down ≥ 1.5 runs/100 with the 90% interval of the difference excluding zero; both cells n ≥ 30.

| Verdict | Count (k = 2–3, testable) | Which |
|---|---|---|
| FADED | 0 | — |
| GREW | 3 | FF-SI vs LHB (-0.6 → +4.9), SI-CH vs LHB (-1.4 → +5.7), CH-FF-KC vs LHB (-2.0 → +6.5) |
| HELD | 40 | everything else with enough sample |
| THIN | 81 | under 30 in one era (usually the short 2025–26 window; 2025 was injury-shortened) |

What *did* change is usage and raw results, which is what the client's question is really about:

- **Two straight curves to righties was his #1 young-era pair** (13.5% of righty pairs). Its raw value went +3.7 → -0.3 runs/100 and its lift +1.1 → -2.0 (recent n 121; interval -6.0 to +1.7). It is the one staple that slipped on both counts. It is not proven, and it is the sequence to watch in 2027. (As an *ending*, two curves is still elite in 2025–26: §8.)
- **Sinker → curve to lefties** went +0.6 → -4.7 raw, lift -1.3 → -4.3 (recent n 99): never a good pair, now a bad one. As an ending its xwOBA went .214 → .376.
- **He mostly stopped doubling up four-seams to righties** (FF→FF 13.0% → 3.9% of righty pairs) and sinkers to lefties (SI→SI 7.2% → 1.7%).
- **G6 sensitivity** (2017–19 vs 2024–26): one FADED appears, **FF-SI-KC vs RHB** (+5.3 → -4.6; n 36 / 35), and it disappears under the filed windows. That makes it an era-boundary artifact candidate, not a finding (G6, G7).

**Read:** the young-era book still works as a book. Across the staples, raw value fell more than lift did. The four-seam, sinker and cutter themselves lost value in every count, and no ordering fixes that.

### 10 · Batterymates

![F9](out/dp_uc64_f9_battery.png)

| Scope | Side | Divergence (bits) | Null mean · 95th | p | Verdict |
|---|---|---|---|---|---|
| career, all in-scope catchers | L | 0.097 | 0.083 · 0.090 | 0.002 | DISTINCT BOOK |
| career, all in-scope catchers | R | 0.115 | 0.118 · 0.126 | 0.735 | SAME BOOK |
| 2023-26, Realmuto vs Stubbs | L | 0.025 | 0.008 · 0.014 | 0.002 | DISTINCT BOOK |
| 2023-26, Realmuto vs Stubbs | R | 0.010 | 0.012 · 0.019 | 0.729 | SAME BOOK |
| 2026, Realmuto vs Stubbs | L | 0.032 | 0.020 · 0.034 | 0.072 | SAME BOOK |
| 2026, Realmuto vs Stubbs | R | 0.062 | 0.050 · 0.077 | 0.172 | SAME BOOK |
| G7 robustness: 2023-25 only, Realmuto vs Stubbs | L | 0.029 | 0.012 · 0.019 | 0.002 | DISTINCT BOOK |
| G7 robustness: 2023-25 only, Realmuto vs Stubbs | R | 0.010 | 0.012 · 0.018 | 0.627 | SAME BOOK |

*SQ-6: generalized Jensen–Shannon divergence of pair usage across catchers vs 500 within-season shuffles of the starting-catcher label. Career scope = Realmuto 163, Rupp 46, Stubbs 35, Alfaro 31, Knapp 25, Marchán 14 starts.*

- **Righties get one book**, whoever catches (p = 0.73 career; 0.73 Realmuto vs Stubbs).
- **Lefties get a slightly different one with Stubbs**, and not only after the July pivot: the 2023–25 test alone gives p = 0.002. In Stubbs games: four-seam → four-seam 10.2% → 5.9%, four-seam → curve 12.3% → 9.2%, more four-seam → cutter (1.3% → 3.6%) and curve → curve (10.3% → 10.5%).
- **2026 alone can't tell them apart** (p = 0.07, 27 starts). The size is small: 0.025 bits of divergence.
- **This does not say who called it.** `uc-pps-027` found the 2026 adjustment travels across catchers (TR-1) and Nola wears PitchCom. The honest sentence: with Stubbs back there, the lefty book leans away from stacked four-seams.

### 11 · Stretch S-1 — predictability

![S1](out/dp_uc64_s1_predictability.png)

Next-pitch entropy rose from 1.88 bits (2019) to **2.17** (2026), 9th of 41 Phillies SP seasons since 2015. The cutter (2021) made a five-pitch mix and he spreads it evenly. The previous pitch narrows the guess by just 0.034 bits (pool median 0.034). Pattern-reading was not the problem: hitters had little to go on in guessing what came next.

### 12 · What to do with it

| For | Use this | Evidence |
|---|---|---|
| Pitching coach | Keep finishing with back-to-back curves; it is still elite in 2025–26 as an ending | §8, F7 |
| Pitching coach | To lefties: changeup → curve, not sinker → curve; retire sinker endings | §7–8 |
| Pitching coach | To righties: open with the sinker, then changeup or four-seam; avoid changeup → four-seam | §7–8 |
| Analyst | Watch two straight curves to righties in 2027: the one staple whose lift turned negative (not yet beyond noise) | §9 |
| Catchers | The lefty book with Stubbs (fewer stacked four-seams) is a real difference; whether it *helps* is not established | §10 |
| Front office | 2026 was better than the line (xwOBA 27th pct vs wOBA 5th) but the fastball damage is a pitch-quality problem, not a sequencing one | §1, §4, §9 |

These are profile-driven reads of a career pool, not a game plan for a specific lineup. A matchup plan belongs in a `uc-pps` advance scout that uses this engine as an input.

---

## Caveats
- **Credit is not causation.** Setup lift says a follow-up pitch did better than usual *after* a given setup. Location, tunneling and the hitter's own plan are not modeled. The count is controlled; the hitter is not.
- **Multiple comparisons.** 176 rankable sequences were tested. The calibration row (§8) is the honest summary: about 10 more sequences clear than chance alone would explain.
- **The era test has limited power.** Recent-era cells are small (2025 was injury-shortened), so HELD often means "can't detect 1.5 runs/100", not "proven unchanged". The double curve to righties is the clearest case of that.
- **Batterymate splits are non-random** (who catches depends on schedule, rest, and in 2026 the calendar). The within-season permutation handles season-level drift, not within-season timing; the 2023–25 check is the G7 guard.
- **Run value is Statcast's `delta_run_exp`** (22 of 30,079 career pitches null). Pitcher view = negative of the batting team's change. Poor contact uses Savant's launch_speed_angle (43 of 5,164 BIP untracked, excluded from the denominator).
- 2026 pitches tagged SL (19) are kept as tagged; 25 / 21 / 14 windows (k = 2 / 3 / 4) containing intentional balls or pitchouts are dropped (PT-H).

## Receipts & lineage
Kernel `dp_uc64_kernel.py` (imports `dp_uc63_kernel` by sha256 pin; 12 lineage files asserted at build). Build `dp_uc64_nola_recap.py`, figures `dp_uc64_build_figs.py`, this report `dp_uc64_build_report.py`, independent harness `dp_uc64_verification.py`. Receipts: `out/dp_uc64_*.csv` (every table above), `out/dp_uc64_headlines.json`. DQ: 21 PASS / 3 WARN / 0 FAIL (5 INFO). Visual audit V1–V7: 10 figures, all PASS (F5 registered V2 exception). Governance trail: `Agents for Data Products/data-products/uc-pps-040-nola-2026-recap-sequencing-001/` (BID, `00`–`07`).
