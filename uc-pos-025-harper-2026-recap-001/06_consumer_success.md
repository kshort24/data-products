# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder**
`uc-pos-025-harper-2026-recap-001` · UC #61 · `dp_uc61` v1.0.0

## 1 · Personas and deliverables
| Persona | Deliverable | Read it like this |
|---|---|---|
| Client / DPO (designer) | **Design kit** `MLB/out/dp_uc61_design_kit/` (copy in `design-kit/`) + `dp_uc61_claude_design_brief.md` | Attach the whole folder to Claude Design. The brief's §1 non-negotiables override taste; §3 has motion ideas for the animation pass |
| Front office | `ref_notecard_reference.png` | Headline → four bullets → platoon map → spray. Every number traces to `headlines.json` |
| Hitting coach | TR panels + `tr_hand_by_pitch_group_2026.csv` | Lefty fastballs (.320 xwOBA vs .410) and lefty low-away breaking balls are the coachable items |
| Content / video | F1–F3 PNGs + the kit | The card is built for motion: 2026 draws over 11 seasons; hits land in date order |
| Analysts | `out/dp_uc61_*` receipts + kernel | Reuse `load_career(…)`, `cum_slash`, `career_envelope` for any hitter with an opponent file |

## 2 · Reading the numbers
- **"Inside his Phillies range 89% of the time"** is measured on PA 25–620, where at least two 2019–25 seasons exist. No earlier Phillies season reached 693 PA.
- **The halves tell the headline.** H2 OPS held (.862 → .868) on walks (14.7% → 16.5%) while hard-hit fell (46.2% → 37.4%) and xwOBA fell (.392 → .363).
- **"Mostly earned" vs LHP:** wOBA .299, xwOBA .314. The gap is small; the June read of "luck" (.303 / .383 in 95 PA) did not survive the season.
- **Spray points are where the ball was fielded** (HR: bearing × distance). Doubles down the line can sit in foul ground.

## 3 · Query templates
```python
import pandas as pd, json
cs  = pd.read_csv("out/dp_uc61_cum_slash_2015_26.csv")        # one row per PA, 12 seasons
c26 = cs[(cs.game_year == 2026) & ~cs.below_floor][["pa_n", "ops"]]   # switch the card to OPS
hg  = pd.read_csv("out/dp_uc61_hand_group_2026.csv")           # TR callouts
H   = json.load(open("out/dp_uc61_headlines.json")); H["hand"]["L"]
import dp_uc61_kernel as K; d = K.load_career(); K.cum_slash(K.pa_ledger(d, K.woba_weights()))
```

## 4 · FAQ
- **Why 162 G when the log shows 161?** 5/9 vs COL was a defensive-only appearance (no PA); it is in the fielding columns.
- **Why does the wOBA differ from Savant's?** The house uses FanGraphs season weights (`wOBA and FIP Constants.csv`); Savant uses its own scale. Every season on the card uses the house weights, including 2015–18.
- **Can I add another metric to the TL chart?** Yes: `tl_cumulative_by_pa.csv` carries BA, OBP, SLG, OPS, wOBA and HR for every PA of every season.
