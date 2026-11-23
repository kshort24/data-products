# 06 · Consumer Success
Agents: `consumer-onboarding-agent` · `analytics-enabler` · `query-builder`

## 1 · Product forms
| Form | For | Where |
|---|---|---|
| PDF report, 7 pages | front office, hitting department; reading on paper | MLB `dp_uc67_bohm_career_retrospective_report.pdf` (copy here) |
| Interactive dashboard, 8 tabs + season inspector | analysts; the LD spray chart lives here | MLB `dp_uc67_bohm_career_retrospective_dashboard.html` (copy here) |
| Receipts | anyone checking a number | MLB `out/dp_uc67_*`; key copies in `data/` |

## 2 · Reading paths
- **Two minutes:** dashboard tiles → "The story", or PDF page 1.
- **"Was uc-pos-013 right?"** → "The 2026 finish" (F2 + window table) → Receipts (PR-1 ledger).
- **"Was it the line drives?"** → "The line-drive question" (F3 gate, then the F4 spray chart).
- **"What do we lose?"** → "Run creation and RISP" (leaderboard, 2026 deciding-run log) → "The Phillies career, closed".

## 3 · Persona notes
- **Front office:** what leaves is a 3,575-PA contact hitter who was at the plate for 63 deciding runs. The RISP number is real history, not a forecast (RS-1). Price the contact profile, not the RISP split.
- **Hitting department:** the September in-zone whiff (15.3% on 120 PA) is the one signature that went the wrong way while contact quality rose. That is the thing to watch in his next club's April.
- **Pro scouting (if he signs elsewhere):** read him on xwOBA vs RHP (.312–.342 every season since 2022; .323 in 2026), not on 2026 results vs RHP breaking balls.

## 4 · Worked example: GW-1 for any Phillies hitter
```python
import pandas as pd
gw = pd.read_csv("out/dp_uc67_phillies_leaderboard_2020_26.csv")
gw[gw.pa >= 1000].sort_values("gw1", ascending=False)[["player_name", "pa", "gw1", "gw1_per_600"]]
# per 600 PA (receipt): Schwarber 11.9, Bohm 10.6, Harper 9.0. The count ranks Bohm #2; so does the rate
```
For another window, rebuild with `dp_uc67_kernel.game_table(ph)` → `pa_table(bat)` → `deciding_pa(...)`; it asserts one PA per win.

## 5 · FAQ
- **Why does 2026 not match my Baseball Savant export?** It now does (.249/.315/.383). Before TP-1 the house rule counted 3 `truncated_pa` rows as at-bats.
- **Why isn't the spray chart in the PDF?** The filed rule required the LD angle to pass a pool gate (R² ≥ .05); it got .007. The chart is in the dashboard as context, in the house field outline.
- **Is GW-1 the same as game-winning RBI?** Close, not identical: it credits the batter at the plate when the deciding run scores, including on an out or an error (7 of his 63), and needs no RBI field (which the log does not have).
- **Why "runs on watch", not runs created?** K48 `runs_created` counts every run that scored during his PA. It is a context measure, not Bill James RC.
- **Is he clutch?** He has the best RISP results of any Phillies regular since 2020. In 3 of his 7 seasons he was worse with RISP than without. That is the profile of a good hitter with a noisy split.

## 6 · Catalog entry
`uc-pos-026` · Alec Bohm, Phillie · Phillies Offense · player evaluation / career retrospective · 2020–26 regular season · PDF + dashboard · READY-CONDITIONAL · owner Kellen Short.
