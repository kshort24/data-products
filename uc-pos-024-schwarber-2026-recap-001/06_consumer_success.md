# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder**
`uc-pos-024-schwarber-2026-recap-001` · UC #60 · `dp_uc60` v1.0.0

## 1 · Personas and deliverables
| Persona | Deliverable | Read it like this |
|---|---|---|
| Front office / DPO | **PDF** `dp_uc60_schwarber_2026_recap_report.pdf` (6 pp) | Bottom line → the three graded questions (§4–§6) → three things for 2027 |
| Hitting coach | **Dashboard** `dp_uc60_schwarber_2026_dashboard.html` (7 chapters) | Ch. 4 and 6. Hover the bat-speed boxes and the dumbbells; righty fastballs and chase are the coachable items |
| Video / content (UC58 consumer) | `out/dp_uc60_season_card.png` + F5/F6 | The "pop" story in one image, and consistent with the animation's numbers |
| Analysts | `out/dp_uc60_*` receipts + SD-1/2/3 | Reuse `recap_viz` and the registries; don't hardcode pools or eras |
| Pitcher-recap redesign (Tier 3 owners) | SD-1/2/3 | Start the 13 items from these helpers; SP and LHP-relief sets need DPO ratification first |

## 2 · Reading the numbers
- **"Not visible in the log" is not "not hurt".** The log saw an unchanged swing and worse contact.
- **xwOBA ran ahead of wOBA in August and September** (.352 / .364 vs .333 / .321). Some late-season results were worse than his contact.
- **The K–chase scatter's R² is near zero.** That is a finding, not a failed chart: chase and strikeouts are separate levers for him.

## 3 · Query templates
```python
import pandas as pd, json
sp = pd.read_csv("out/dp_uc60_season_panel.csv")                       # one row per season, 2015-26
pool = pd.read_csv("out/dp_uc60_context_pool_200.csv")                 # CS-1 context set
H = json.load(open("out/dp_uc60_headlines.json")); H["bk1"]            # BK-1 pre/post, scan result, grade
from phillies_dp import recap_viz as RV
RV.trendline_r2(pool.chase_rate, pool.krate); RV.era("asb_2026")       # SD-3 / SD-2
```

## 4 · FAQ
- **Why 702 PA, not 701?** The K57 spine counts the 1 `truncated_pa` as a PA; UC58's PA-X1 does not. No carry-in gives his PA, so neither count is confirmed externally.
- **Why is OPS .855, not .853?** The log's .232/.354/.502 sums to .855 (unrounded); CI-2's .853 is a print.
- **Can the dashboard be shared?** Yes. `_artifact.html` is the body-only variant for an Artifact publish. Plotly loads from the pinned CDN.
