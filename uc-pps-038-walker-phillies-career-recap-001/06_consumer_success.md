# 06 · Consumer Success
Agents: `consumer-onboarding-agent` · `analytics-enabler` · `query-builder`

## 1 · Product forms
| Form | For | Where |
|---|---|---|
| PDF report, 8 pages | front office, pro scouting; reading on paper | MLB `dp_uc62_walker_phillies_career_recap_report.pdf` (copy here) |
| Interactive dashboard, 8 tabs + season inspector | analysts, pitching department | MLB `dp_uc62_walker_phillies_career_dashboard.html` (copy here); Artifact "Taijuan Walker, Phillie" |
| Receipts | anyone checking a number | MLB `out/dp_uc62_*` |

## 2 · Reading paths
- **Two minutes:** dashboard masthead tiles → "The story" tab, or PDF page 1.
- **The contract question:** "What they bought" → "Luck, measured" (PR-1 ledger) → "What it cost".
- **The pitching question:** "What broke" (velocity, whiff, mix by pitch).
- **The audit:** "Receipts" tab, then `05`.

## 3 · Persona notes
- **Front office:** the lesson is in Takeaway 4: price a contact manager on KR-1 *and* the luck gap together, and on the fastball's velocity trend.
- **Pro scouting:** KR-1 is a cheap screen for free-agent pitchers: a large negative KR-1 with a near-zero luck gap is real contact management; check its velocity dependence.
- **Pitching department:** the four-seamer went 63% (2015) → 30% (2022) → none (2026); the splitter's whiff fell with it. The cutter (30% in 2025) did not replace the lost misses.

## 4 · Worked example: KR-1 for any pitcher-season
```python
import json, numpy as np, pandas as pd
fit = json.load(open("out/dp_uc62_kr1_fit.json"))
def kr1(krate, woba): return woba - (fit["intercept"] + fit["slope"] * krate)
kr1(0.214, 0.296)   # Walker 2021–22 pooled → about −.027
```
Use house `nresults` K% and wOBA, ≥ 100 PA. Refit when the pool changes.

## 5 · FAQ
- **Why don't the 2015–22 numbers match the client CSV?** The client frame drops 483 of his pre-Phillies pitches (O-26). Governed 2015–22 wOBA is .306; the turn-1 PA-weighted read was .303 (HP-05 PARTLY).
- **Is this "bad luck"?** Partly, and less than it looks: his tenure luck gap (+.013) is below the Phillies pool median (+.019). 2026 is the exception.
- **Why no ERA?** ER is not in the log. ERA is a labelled carry-in (5.12 over the deal).
- **Why is 2018–19 missing from the charts?** 56 and 4 PA: below the 100-PA floor. They remain in pooled totals.

## 6 · Catalog entry
`uc-pps-038` · Taijuan Walker, Phillie · Phillies Pitching · player evaluation / contract review · 2015–26 regular season · PDF + dashboard · READY-CONDITIONAL · owner Kellen Short.
