# Taijuan Walker, Phillie
### Four years, $72 million, and the gap the strikeouts never explained

**Prepared for:** front office, pitching department, pro scouting · **Throws:** R · **MLBAM:** 592836
**Governance:** UC #62 · uc-pps-038 · dp_uc62 v1.0.0 · Phillies Pitching (pps) · house log anchor 2026-10-01. KPIs inherited by import from the `dp_uc53` chain (sha-pinned); new and provisional: KR-1, CE-1, PR-1.

> **Read this first: data window and sample sizes.**
>
> - MLB regular season 2015–26, locked to MLBAM 592836. SEA/ARI/TOR/NYM years come from his pitcher-keyed file plus pitcher-id rows in other opponent files; Phillies years from the house log. Postseason excluded.
> - 2018 (56 PA) and 2019 (4 PA) are in the totals but out of every season-level chart and rank. 2026 is 115 PA.
> - Innings are outs from the log (OU-2) and reconcile exactly to public IP: 172.2 + 83.2 + 123.2 + 22.2 = 402.2. ERA, contract terms and the Angels timeline are labelled carry-ins (CI-1..CI-6), never computed on.
> - Ranks use the Phillies pitcher-season pool 2015–26 (≥100 PA, n = 198), not MLB.

---

## Bottom line
The Phillies bought a pitcher who allowed less than his strikeouts said he should: in 2021–22 his wOBA ran .027 below the Phillies line for his K% (KR-1). Over the contract the strikeouts fell 4.5 pts, the four-seamer lost 1.8 mph, the splitter's whiff rate fell 6.6 pts, and the contact got harder (xwOBA +.033). The kind luck of the Mets years also went away. The pre-registered ledger calls it **both, and the price was set on a residual**. Two of his four Phillies seasons are among the three worst by a Phillies pitcher since 2015 (2026 #1, 2024 #3 of 198).

1. **What they got:** 1,772 batters faced (#8 of 199 Phillies pitchers since 2015), 172.2+83.2+123.2+22.2 IP = 402.2, reconciled to the out. One average season (2023, .311 wOBA, #109 of 198 from the bottom), one swing year (2025, .335), and two of the three worst Phillies pitcher-seasons on record here.
2. **What they bought:** a contact manager. At 21.4% K in 2021–22 the Phillies line expects .323; he allowed .296. Statcast agreed it was mostly real (xwOBA .317, luck gap −.008).
3. **What broke:** the stuff (H-S STRONG). K% 21.4%→16.9%, whiff 23.6%→18.9%, four-seam 94.2→92.4 mph, splitter whiff 28.2%→21.6%. He threw the four-seamer 63% of the time in 2015 and not at all in 2026.
4. **And the luck (H-L STRONG):** the gap between results and contact quality moved +.021. Context the ledger did not grade: his tenure gap (+.013) sits below the Phillies pool median (+.019). The luck did not turn bad; it stopped being good. 2026 is the exception (+.069 in 115 PA).
5. **What it cost (AAV basis, CE-1):** $179K per inning over the deal; $794K per inning and $157K per batter in 2026. Released April 23; two Angels minor-league deals; never promoted, so the Phillies paid the full $18M.

## 1 · What the Phillies got
Four seasons, 1,772 batters, #8 among 199 Phillies pitchers since 2015 in batters faced. 2023 was a Phillies-median rotation year: 31 starts, 172.2 IP, .311 wOBA (the pool median is .318). Then 2024 (.412, #3 worst of 198), a swingman 2025 (21 starts in 34 games, .335) and a five-game 2026 that is the worst Phillies pitcher-season in the sample (.455).

| Season | Team | G (GS) | IP | BF | wOBA | Phillies rank (worst first) | xwOBA | K% | BB% | Whiff | Hard-hit | Barrel | Runs on watch / 27 outs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2015 | SEA | 29 (29) | 167.1 | 705 | .308 | — | .318 | 22.3% | 5.4% | 23.5% | 33.8% | 7.6% | 4.57 |
| 2016 | SEA | 25 (25) | 132.2 | 573 | .323 | — | .323 | 20.8% | 6.1% | 22.5% | 36.7% | 9.0% | 4.68 |
| 2017 | ARI | 28 (28) | 156.1 | 676 | .309 | — | .316 | 21.6% | 8.0% | 21.7% | 35.1% | 5.1% | 4.26 |
| 2020 | SEA/TOR | 11 (11) | 52.1 | 225 | .291 | — | .338 | 22.2% | 8.4% | 20.5% | 32.9% | 7.2% | 3.44 |
| 2021 | NYM | 30 (30) | 156.1 | 654 | .300 | — | .326 | 22.3% | 8.4% | 23.6% | 39.4% | 10.0% | 4.49 |
| 2022 | NYM | 29 (29) | 154.2 | 648 | .293 | — | .308 | 20.4% | 6.8% | 23.6% | 40.6% | 7.3% | 3.32 |
| **2023** | PHI | 31 (31) | 172.2 | 736 | **.311** | #109 of 198 | .322 | 18.8% | 9.5% | 20.5% | 40.9% | 6.8% | 4.27 |
| **2024** | PHI | 19 (15) | 83.2 | 382 | **.412** | #3 of 198 | .401 | 15.2% | 9.7% | 16.7% | 46.3% | 13.4% | 7.31 |
| **2025** | PHI | 34 (21) | 123.2 | 539 | **.335** | #68 of 198 | .337 | 16.0% | 7.8% | 18.5% | 41.4% | 7.4% | 4.29 |
| **2026** | PHI | 5 (4) | 22.2 | 115 | **.455** | #1 of 198 | .411 | 14.8% | 9.6% | 16.8% | 36.0% | 12.8% | 9.93 |

*House wOBA (K44 nresults) for wOBA and ranks; xwOBA is XW-1. Runs on watch include unearned runs scored during his PAs.*

![Where his Phillies seasons sit in Phillies history](out/dp_uc62_f8_rank.png)

![Every appearance by Game Score (GS-1), 2015–26](out/dp_uc62_f7_gs.png)

## 2 · What they bought
The client's chart, rebuilt on the governed pool. The Phillies line is wOBA = .414 − .426 × K% (R² 0.34, n = 194, Walker excluded). Every Walker season from 2015 to 2023 sits below it. 2021–22, the seasons that priced the contract, sat .027 below: a pitcher whose run prevention his strikeouts did not explain. Statcast's contact model said most of that was real (luck gap −.008), which is why it was easy to pay for.

![The client's chart, governed: wOBA allowed as a function of K%](out/dp_uc62_f1_k_woba.png)

![KR-1: how far below (or above) the Phillies K% line each season landed](out/dp_uc62_f2_kr1.png)

## 3 · What broke
Both pitches that carried the Mets years slipped. The four-seamer went from 94.2 mph in 2021–22 to 92.4 in the tenure, and from 30% usage to none in 2026. The splitter, his best pitch, lost 6.6 points of whiff rate. His three full Phillies splitters (2023–25) are the three lowest-whiff seasons among the 18 Phillies splitter-seasons since 2015 (≥150 thrown); 2024's was 16.3%. That year the sinker, his most-used pitch, allowed a .515 xwOBA on contact (78 balls in play).

![Velocity by pitch, every season](out/dp_uc62_f4_velo.png)

![Whiff rate by pitch, every season](out/dp_uc62_f5_whiff.png)

![The arsenal migrated away from the four-seamer](out/dp_uc62_f6_mix.png)

## 4 · Luck, measured
The pre-registered luck family is STRONG: his results-minus-contact gap rose +.021 from the Mets years. But the Phillies pool itself runs a +.019 median gap, and his tenure (+.013) is ordinary for a Phillie. The Mets years were the lucky ones. Only 2026 (+.069, 115 PA) was bad luck by Phillies standards, and it sat on the worst contact quality of his career (xwOBA .411).

![Results against contact quality: wOBA (Statcast basis) minus xwOBA](out/dp_uc62_f3_luck.png)

### The pre-registered ledger (PR-1, filed 20:19 ET before any *unseen* signature was computed)
| Family | Sig | Metric | Before | After | Bar | Verdict | Seen at T0 |
|---|---|---|---|---|---|---|---|
| H-S | S1 | krate | 21.4% (2021–22) | 16.9% (2023–26) | −3.0 pts | **PRESENT** | yes |
| H-S | S2 | whiff_rate | 23.6% (2021–22) | 18.9% (2023–26) | −3.0 pts | **PRESENT** | yes |
| H-S | S3 | ff_velo | 94.2 mph (2021–22) | 92.4 mph (2023–26) | −1.0 mph | **PRESENT** | no |
| H-S | S4 | fs_whiff | 28.2% (2021–22) | 21.6% (2023–26) | −5.0 pts | **PRESENT** | no |
| H-S | S5 | xwoba | .317 (2021–22) | .350 (2023–26) | +.025 | **PRESENT** | no |
| H-L | L1 | luck_gap | −.008 (2021–22) | .013 (2023–26) | +.015 | **PRESENT** | no |
| H-L | L2 | luck_gap | −.008 (2021–22) | .019 (2024) | +.020 | **PRESENT** | no |
| H-R | R1 | kr1 | .000 (0) | −.027 (2021–22) | −.025 | **PRESENT** | yes |
| H-R | R2 | luck_gap | .000 (0) | −.008 (2021–22) | −.010 | **WEAK** | no |
| H-R | R3 | kr1 | −.010 (2015–19) | −.027 (2021–22) | −.010 | **PRESENT** | yes |

**Roll-up:** H-S **STRONG** · H-L **STRONG** · H-R **SUPPORTED** → call: **both, and the price was set on a residual**. R2 is WEAK: at signing his contact was not lucky by the zero bar, so most of the gap the Phillies paid for was real weak contact. It aged with the stuff.

## 5 · What it cost
On the AAV basis the deal bought innings at $179K each. 2023 was the bargain ($104K); 2026 cost $794K per inning for 22.2 innings and 115 batters.

![CE-1: contract cost per inning, AAV basis](out/dp_uc62_f9_cost.png)

| Season | IP (OU-2) | BF | $ per inning | $ per batter |
|---|---|---|---|---|
| 2023 | 172.2 | 736 | $104K | $24K |
| 2024 | 83.2 | 382 | $215K | $47K |
| 2025 | 123.2 | 539 | $146K | $33K |
| 2026 | 22.2 | 115 | $794K | $157K |
| 2023-26 | 402.2 | 1772 | $179K | $41K |

*AAV basis: $18M a season, $72M total (CI-1). Cash timing, deferrals and tax are out of scope.*

## 6 · How it ended
| Date | Opp | Role | IP | Pitches | H | HR | BB | K | Runs on watch | Game Score |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-03-30 | vs WSH | Start | 4.2 | 99 | 10 | 0 | 3 | 2 | 7 | 23 |
| 2026-04-05 | @ COL | Start | 4.2 | 87 | 7 | 3 | 2 | 4 | 4 | 24 |
| 2026-04-11 | vs AZ | Start | 4.2 | 85 | 4 | 1 | 2 | 6 | 2 | 50 |
| 2026-04-17 | vs ATL | Start | 4.0 | 89 | 7 | 2 | 3 | 4 | 7 | 15 |
| 2026-04-22 | @ CHC | Bulk relief | 4.0 | 64 | 8 | 2 | 1 | 1 | 5 | 20 |

| When | What (carry-ins) |
|---|---|
| 2026-03-30 to 04-22 | Five appearances: four starts and one bulk outing behind opener Kyle Backhus at Chicago (log). 9.13 ERA, 8 HR in 22.2 IP (CI-1). |
| 2026-04-23 | Released to clear a rotation spot for Zack Wheeler's return (CI-1). Phillies owe the rest of the $18M. |
| 2026-05-23 | Minor-league deal with the Angels (CI-4). |
| 2026-06-08 | Opts out; released (CI-2, CI-4). |
| 2026-06-11 | Second minor-league deal with the Angels, assigned to AAA Salt Lake (CI-3). |
| 2026-06-21 | Released again. Five starts across the Arizona Complex League and Salt Lake: 21 IP, 3.86 ERA, 12 K, 7 BB (CI-4). Never promoted. |

## 7 · The client's claims, graded
| HP | Claim | Grade | Evidence |
|---|---|---|---|
| HP-01 | The client CSV reproduces (pitches, PA by season) | **CONFIRMED** | KF-1 frame matches the client CSV in 12/12 seasons; NF-1 dedup lost 483 pitches. Client vs governed pitches by season: {2015: -39, 2016: -35, 2017: -63, 2018: -11, 2019: 0, 2020: -5, 2021: -160, 2022: -122, 2023: 0, 2024: 0, 2025: 18, 2026: 0}. 2025 client row carries 18 postseason pitches (SRC-1). |
| HP-02 | Paid nearly $18 million this season | **CONFIRMED** | CI-1: $18MM, final year of 4/$72MM. The Angels owed only the prorated minimum for MLB time, offset against the Phillies' payment; he never reached the majors (CI-4), so the Phillies paid all of it. |
| HP-03 | To pitch in the Angels minor league system | **CONFIRMED (incomplete)** | Two minor-league deals (May 23, Jun 11), released Jun 8 (opt-out) and Jun 21; 5 starts, ACL + AAA Salt Lake, 21 IP (CI-4). Free agent after Jun 21; no later signing found. |
| HP-04 | 2026 worst, 2024 3rd-worst of 199 Phillies pitcher-seasons by wOBA | **CONFIRMED** | Governed pool n = 198 (regular season, >= 100 PA; turn 1 used games > 3 on the client frame, n = 199): 2026 #1, 2024 #3. Pool size restated 199 -> 198. |
| HP-05 | Career split .303 (2015-22) vs .350 (2023-26) | **PARTLY** | Governed pooled nresults: before 0.306, tenure 0.350. |
| HP-06 | 2015 ev_mu 88.9 is a tracking artifact | **PARTLY (bar met; cause misattributed)** | Registered bar met: 2015 BIP EV-null share 2.2% = 2.4x 2016-22. But nulls cannot move a mean 5 mph. The client's ev_mu is `inds` = mean launch_speed over EVERY pitch with a reading. Non-BIP rows with an EV: 2015 16%, 2016 39%, 2022 46% (fouls/tips). BIP-only mean EV is flat: 2015 89.4, 2022 89.1. The 2015 spike is a population change in which pitches carry EV, not a sensor error. |
| HP-07 | Code defects CR-1..CR-4 | **CONFIRMED (3 of 4); CR-4 WITHDRAWN** | CR-1 `games > 3` drops 18 Phillies pitcher-seasons with exactly 3 games that the title includes. CR-2 the CSV has no career rows (all 12 Walker rows carry a game_year). CR-3 `inds` and `leadoff_walk_rate` columns are merged then dropped by `z[level+kpis]`. CR-4 px.scatter(subtitle=...) on plotly 6.0.1: accepted. |

## Takeaways
1. **The contract was priced on a real but fragile skill.** Walker's 2021–22 run prevention beat his strikeouts by .027, and Statcast mostly agreed. That kind of edge rides on fastball velocity and a put-away splitter. Both declined from the first Phillies season.
2. **The tell was visible in 2023.** The 31-start, 172.2-inning season hid a K% of 18.8% (down from 20.4%), a four-seam usage cut to 17% and a 9.5% walk rate. KR-1 still read −.023 that year; in 2024 it flipped to +.062.
3. **Don't blame luck.** His tenure results-minus-contact gap (+.013) was ordinary for a Phillie (pool median +.019). The Mets years were the outlier.
4. **For the next contact-manager contract:** require KR-1 and the luck gap to point the same way, and price the fastball's velocity trend as hard as the ERA.

## Candid caveats
- **Ranks are Phillies-frame** (pitcher-seasons 2015–26, ≥100 PA, n = 198), not MLB-wide.
- **2026 is 115 PA.** It clears the 100-PA floor, but read direction, not decimals.
- **Two wOBA bases, labelled.** House wOBA (K44 nresults) for ranks and KR-1; Statcast-basis wOBA (WB-1) only beside xwOBA (XW-1).
- **KR-1 and CE-1 are provisional** (first use). KR-1's line explains 34% of the pool's wOBA spread; the rest is contact, sequencing and defense.
- **The luck context is post-hoc.** PR-1 graded the change from 2021–22; the pool-median comparison was added after scoring and is not graded.
- **Money is AAV basis.** No deferrals, signing-bonus timing or tax effects. ERA, ER and minor-league lines are carry-ins, never computed on.
- **No medical inference.** Velocity is reported, not explained; nothing here claims an injury.
- **The client frame undercounts him** by 483 pitches (O-26 name-dedup) and carries 18 NLDS pitches in 2025 (SRC-1). Governed numbers will not match the client CSV for 2015–22 or 2025.

*Receipts: `out/dp_uc62_*` (CSV/JSON/PNG). Governance trail: `Agents for Data Products/data-products/uc-pps-038-walker-phillies-career-recap-001/` (`00`–`07`, BID). DQ 15 PASS / 0 WARN / 0 FAIL.*
