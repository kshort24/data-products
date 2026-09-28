# 06 · Consumer Success: `uc-pps-034`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · The product forms, and who each is for

The ask was to explore different kinds of data products for one story. Each form below owns a part of the story no other form tells.

| Form | Owns | Best reader | File |
|---|---|---|---|
| **Narrative dashboard** | the season as an arc you walk, chapter by chapter | anyone; start here | `dp_uc49_luzardo_2026_dashboard.html` |
| **Game story** | 109 pitches in order; the "two game plans" | broadcast, content, pitching coach | dashboard ch. 6; figs 5–6 |
| **October card** | a falsifiable definition of "defining", written first | front office, writers, the player | dashboard ch. 8; `out/dp_uc49_october_card.csv` |
| **Feature report** | the long read with every caveat | front office, pitching department | `dp_uc49_luzardo_2026_recap_report.pdf` |
| **Context board** | "better than most", with the dataset named | analysts | dashboard ch. 3–4; figs 1–2 |
| **Notecard** | one image, one line | social, broadcast graphic | `out/dp_uc49_fig9_notecard.png` |
| **Postseason ledger** | the 2023 Wild Card at the Bank to last October | writers, broadcast | dashboard ch. 8; report §7 |
| Acquisitions board (not built) | "one of Dombrowski's best" | front office | needs a transaction source (E-8) |

## 2 · Reading paths

- **Five minutes:** dashboard hero → chapter 3 (the chase) → chapter 6 (Labor Day, step through the ninth) → chapter 8.
- **The pitching department:** report §2–3 (chase, zone), fig 7 (pitch map), ch. 6 fig 6 (changeup by time through), §6 (what the log shows before the IL).
- **Broadcast / content:** the notecard, ch. 6 stepper (every pitch of the shutout with count and velocity), the postseason ledger. Every sentence in the dashboard is safe to read on air as written; carry-ins are marked.
- **Your notebook:** report §9 or the dashboard appendix. Each of your 13 claims and chart choices with a verdict.

## 3 · Dashboard walkthrough (`dp_uc49_luzardo_2026_dashboard.html`, offline)

1. **Theme bar:** *Match my system* (default), *Brand light*, *Notebook dark* (your `plotly_dark`). The choice is remembered in this browser only.
2. **Chapter nav** stays at the top and highlights where you are.
3. **Chapter 3, drill-through:** click any dot to read that pitcher-season against Luzardo 2026. The panel also states the starter-workload result.
4. **Chapter 6, stepper:** ◀ ▶ or drag. The chart outlines the plate appearance's pitches in red; the chips list count, pitch, velocity and result; bold chips are whiffs.
5. **Chapter 8:** the card's four bars, its backtest (read it before you use the card), and his six postseason games with the card's verdict on each.

## 4 · How to read the October card

A postseason outing is **on-script** when at least 3 of these hold: four-seam velocity over the first 15 pitches ≥ 96.2 mph; chase rate ≥ 29.2%; ≥ 12.0 whiffs per 100 pitches; walk rate ≤ 10.7%. The bars are the edges of his own 2026 range, so on-script means *this season's pitcher showed up*. It does not mean he won, and in 2026 his off-script starts actually allowed fewer runs. A relief outing is graded the same way. The first pitch of Game 162 or the postseason makes this v1.1.0.

## 5 · FAQ

- **Why "runs on watch" and not ERA?** Statcast has no earned-run flag. Runs on watch (house `runs_created`) counts every run that scored during his plate appearances. His published ERA (2.87) is quoted as a carry-in.
- **Why is 2019 in the table?** It is his debut season (46 PA); shown for the arc, flagged as context.
- **Is "#1 whiff among starters" MLB-wide?** No. Phillies seasons 2015–2026 with ≥2,000 pitches (41). It holds at 1,500 and 2,500.
- **What about the shoulder?** The product reports the reported facts and what the log shows (velocity, workload). It does not model or infer an injury.
- **Why do your notebook's career numbers differ?** Your frame includes postseason pitches in season rows (380) and loses 230 regular-season pitches to the `nphl` loader's dedup (O-26). 2026 is identical.

## 6 · Catalog entry (`product-narrator`)

> **The Chase — Jesús Luzardo, 2026.** Eight chapters from his arrival to the question October will answer. He missed more bats than any Phillies starter of the Statcast era, stopped needing the zone to do it, and threw the best start of his career on Labor Day before the log went quiet. Includes a pitch-by-pitch replay of the shutout and a pre-registered October card. Internal · v1.0.0 · data through 2026-09-26 · verified 226/226.
