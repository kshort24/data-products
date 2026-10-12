# 06 · Consumer Success: `uc-pps-035`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · The product forms, and who each is for

| Form | Owns | Best reader | File |
|---|---|---|---|
| **Feature report** (PDF) | the long read, every caveat, the notebook graded | front office, pitching department | `dp_uc51_wheeler_2026_recap_report.pdf` |
| **Narrative dashboard** | the season as eight chapters; the start drill | anyone; start here | `dp_uc51_wheeler_2026_dashboard.html` · Artifact "Still Zack Wheeler" |
| **Stretch forensics** | the six-start slide: walks, misses, release point, what the log cannot see | pitching coach, front office | dashboard ch. 4; figs 4–5; `stretch_windows.csv` |
| **Swing-timing board** | tied-up / centered / flail with the population named; the sinker in on righties | analysts, catchers | dashboard ch. 5; figs 7–8 |
| **Still-Wheeler card** | 2027 bars registered before a pitch | front office, writers, the pitcher | dashboard ch. 8; fig 12; `still_wheeler_card.csv` |
| **Notecard** | one image, one line | social, broadcast graphic | `out/dp_uc51_fig13_notecard.png` |
| **Postseason ledger** | WC G3 relief beside his Phillies Octobers | writers, broadcast | dashboard ch. 8; report §8 |
| Contract-value board (not built) | "one more year left on his deal" priced | front office | needs salary/WAR sources (E-8) |

## 2 · Reading paths

- **Five minutes:** dashboard hero tiles → chapter 2 (fig 1) → chapter 4 (pick 8/7 and 8/24 in the start drill) → chapter 8 card.
- **Pitching department:** report §3 (zone), §4 (the slide, misses vs release point), §5 (sinker to righties), §7 (splitter), card table.
- **Front office:** report bottom line → §2 (rank and population) → §8 (2027 card, contract carry-in) → §10 caveats.
- **Broadcast / content:** the notecard; report §8 WC G3 line; every dashboard sentence is safe to read on air as written, and carry-ins are tagged.
- **Your notebook:** report §9 or the dashboard appendix, 18 rows.

## 3 · Dashboard walkthrough (`dp_uc51_wheeler_2026_dashboard.html`, offline)

1. **Theme bar:** *Match my system* (default), *Brand light*, *Notebook dark* (your `plotly_dark`). Remembered in this browser only.
2. **Chapter nav** stays at the top and highlights where you are.
3. **Chapter 4, start drill:** choose any of the 28 starts from the list, or click a bar in the walks/xwOBA chart. The panel shows the line, walks per PA, xwOBA, Game Score, in-zone, edge, chase, first-15 velocity, arm-side share of clear misses and the four-seam release point. Slide starts carry a red pill.
4. **Chapter 8:** the card's four bars (red = 2027 bar, dotted navy = same rule on 2021–25), every 2026 start coloured by period, and the WC G3 outing as a diamond.

## 4 · How to read the Still-Wheeler card

A 2027 start is **on-script** when at least three of these hold: four-seam velocity over the first 15 pitches ≥ 95.3 mph; chase rate ≥ 30.8%; ≥ 13.0 whiffs per 100 pitches; walk rate ≤ 12.0%. The bars are the edges of his own 2026 range, so on-script means *this season's pitcher showed up*. In 2026 that mattered: on-script starts allowed 2.16 runs per 27 outs and off-script starts 4.96. The card is not a forecast; it is the definition the 2027 log will be graded against (v1.1.0).

## 5 · FAQ

- **Your notebook says 7.6% walks; the report says 7.3%. Which is right?** Both. 7.6% is your frame, which includes his 17 Wild Card plate appearances (3 walks). Rates here are regular season only.
- **Why not Savant's 42.4% edge rate?** Savant draws its edge band differently from the house ER-1 (one baseball either side of the zone line). The two numbers measure different areas. On ER-1 his edge rate did not change.
- **Why "the slide" and not "August"?** The reported 8.51 ERA matches exactly one six-start window, 7/27–8/24. Calendar August (8/2–8/30) gives 6.26.
- **Did the dropped glove cause the walks?** The log cannot say. It shows his misses drifting arm side during those starts and returning after, with his release point unchanged. The glove is reporting.
- **Is "#6 of 41" MLB-wide?** No. Phillies seasons with ≥2,000 pitches, 2015–2026.
- **Why "runs on watch" and not ERA?** Statcast has no earned-run flag. Runs on watch counts every run scored during his plate appearances; his 3.00 ERA is a carry-in.

## 6 · Catalog entry (`product-narrator`)

> **Still Zack Wheeler — 2026.** Eight chapters from a rib resection to a Wild Card relief outing. Six of the ten best Phillies starter seasons by xwOBA since 2015 are his, 2026 included. His walk rate is one six-start slide, and the report shows what the log can and cannot say about why. Includes a start-by-start drill, a tied-up board and a 2027 card registered before the first pitch. Internal · v1.0.0 · data through 2026-09-27 (+ WC G3) · verified 204/204.
