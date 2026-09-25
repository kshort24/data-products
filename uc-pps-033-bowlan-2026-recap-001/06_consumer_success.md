# 06 · Consumer Success: `uc-pps-033`

Agents: `consumer-onboarding-agent` · `analytics-enabler` · `product-narrator`

## 1 · Personas and reading order

| Persona | Start with | Then | The one thing to take away |
|---|---|---|---|
| **DPO (Kellen)** | Report §8 (your notebook, graded) | `00` §7 escalations | Your claims held (17 of 22). The two that need fixing upstream are the vert rounding (O-25) and the `gy` leak |
| **Front Office** | Dashboard lens *Front Office* → ch. 1 | ch. 3 drill-through | The trade bought ride and whiff. Velocity turned them into the #2 four-seam of 405 |
| **Pitching Coach** | lens *Pitching Coach* → ch. 2 | ch. 4 sinker watch | The whole arsenal gained speed from pitch one. The sinker is the 2027 problem |
| **Pitching Analyst** | lens *Pitching Analyst* → ch. 3–4 | `03` §2 specs | Platoon arsenal (FF+CH vs L, sweeper vs R); the four-seam became a weak-contact pitch |
| **Catcher** | lens *Catcher* → ch. 5 | the rate-test table | Four-seam at two strikes and when behind: that is the usage change that is significant |
| **Manager** | lens *Manager* → ch. 6 | the appearance timeline | One late inning, 59 times. No velocity warning before 9/17. The 2027 question is frequency |
| **Pitcher** | lens *Pitcher* | ch. 2, ch. 5 | Harder from the first pitch, and hitters chased more |

## 2 · Dashboard walkthrough (`dp_uc48_bowlan_2026_dashboard.html`, offline)

1. **The box line** at the top is the season in eight numbers.
2. **Read as…** re-reads the page for one chair. Chapters that don't concern that persona fold to their headline ("Read this chapter anyway" opens them). Callouts name the ledger hypothesis, its strength and what would confirm it. The ledger table at the bottom filters to that persona. The choice is remembered in this browser only.
3. **Ch. 2** has the Gemini 2×2 behind a *details* toggle, governed (inches, n, imports).
4. **Ch. 3 drill-through.** The left chart shows every Phillies RHP pitch-type centroid since 2015 (2017 excluded), with Bowlan's 2026 arsenal outlined and labelled. **Click any dot**, or use the pitch buttons, to redraw the right chart as that pitch, Bowlan's 2026 pitches over the density of every other Phillies right-hander's. The red band is the middle 50% of his ride.
5. **Ch. 6 timeline.** Each 2026 appearance is plotted by date and four-seam velocity; dot size is pitches and red means a run scored while he pitched. Hover shows entry inning, runners on and rest. The dotted line is the 9/17 exit (carry-in).
6. **Your notebook, graded:** filter by verdict. **Persona action ledger:** follows the lens; expand for all 27 signatures. **Receipts:** DQ and freshness.
7. **Notebook dark / Brand light** flips the page and every chart. With no choice made, the page follows the viewer's system theme.

## 3 · How to read a persona ledger row

A row says: *if this person did this, the log should show these changes, and here is whether it does.* **STRONG** means every predicted change is there at its declared size (and significant where a test applies). **SUPPORTED** means most are and none contradicts it. **UNSUPPORTED** means the data does not carry the signature, or carries the opposite. No row claims the action happened. Only the confirmation column (the scouting file, the lab notes, the pitch calls) could establish that.

## 4 · FAQ

- **Is the 31.5% K rate elite?** It is the 92nd percentile among 198 Phillies pitcher-seasons since 2015, and second on the 2026 staff behind Duran. The jump from 25.4% is not statistically settled on 181 and 232 PA (p = 0.18).
- **Why does the notebook say 18.0" of vert in both years?** `pitch_mix` rounds to 0.1 ft first (O-25). The unrounded values are 17.7 and 18.0.
- **Why .272 and not .269?** .272 is the anchored log. No season-end version of the log gives .269; it appears only on a cut through July 4.
- **Why 59 games and not 60?** The log has 59 regular-season appearances; the three spring outings are excluded.
- **He gave up 30 runs, one every other outing. Is that good?** "Runs created" counts inherited runners who scored. 13 of the 30 came in the 15 outings he started with men on. 38 of 59 outings were scoreless.
- **Was he hurt before 9/17?** Nothing in the log says so. His last five outings averaged 96.9 mph against 97.0 for the season. The injury itself is a news report (right groin strain, no IL), not data.
- **What would change the story?** A postseason (v1.1.0), his 2027 sinker, and a real season of sweepers.

## 5 · Catalog entry (`product-narrator`)

| Field | Value |
|---|---|
| Product | Season Recap: Jonathan Bowlan 2026 ("The Tick and a Half") |
| Value stream | `pps` |
| Purpose | Explains what changed between a results-only 2025 Royals four-seam and an elite 2026 Phillies four-seam, and which actions in the pitching value stream leave the signatures of that change |
| KPIs | client recap set (19) · KP-1 house percentile · AR-2 arsenal · CS-1 count mix · US-1 usage · VE-1 arm-vs-role · PA-1 ledger |
| Grain | pitch → pitcher-season / appearance / count / bucket |
| Refresh | point-in-time, anchor 2026-09-23; a postseason or refresh is v1.1.0 |
| Owner | Kellen Short (DPO) |
| Certification | READY-CONDITIONAL (C1–C6) |

**Executive summary.** Jonathan Bowlan's four-seam fastball had plus ride and elite swing-and-miss when the Phillies acquired him, but ordinary run prevention. In 2026 he threw it about a mile and a half an hour harder from the first pitch of every outing. The pitch became the second-best right-handed four-seam in the club's 405-season comparison frame. The club used it more with two strikes and when behind, and gave him a defined late-inning role. His strikeout rate ranked in the 92nd percentile of Phillies pitcher-seasons since 2015. Two watch items carry into 2027: the sinker and the new sweeper.
