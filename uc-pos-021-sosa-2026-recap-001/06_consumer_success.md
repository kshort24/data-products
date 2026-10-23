# 06 · Consumer Success
**consumer-onboarding-agent · analytics-enabler · query-builder · product-narrator**

## 1 · Forms and readers
| Form | Reader | Use |
|---|---|---|
| `dp_uc56_sosa_2026_recap_report.pdf` (8 pp) | Front office, DPO | the decision document; §8 walkaway |
| `dp_uc56_sosa_2026_dashboard.html` / Artifact "Love Sosa" | Hitting & bench coaches, analysts | hover the scatter and cumulative lines |
| `out/dp_uc56_hp_grades.csv` | Client (notebook author) | which notebook claims held |

## 2 · Reading paths
- **Two minutes (GM):** Bottom line (6 items) → F9 walkaway.
- **Ten minutes (hitting coach):** F2 card → F4 over the hump → F5 approach → F6 pitch groups. The two coachable items: pulled air balls (16.6%, his lowest) and offspeed chase (66%).
- **Analyst:** `headlines.json`, then the harness log.

## 3 · FAQ
- **Why is 2026 "down" when xwOBA is his best?** wOBA is what happened; xwOBA is what his contact usually produces. They split by .023 in 2026 (BABIP .281, more grounders).
- **Isn't the late surge proof he figured something out?** The surge is in results only. After the break his xwOBA fell (.344 → .305).
- **Why not use Statcast's EV50?** You defined EV50 as the median; we kept your definition and labelled it.
- **Where does $6.0M come from?** The top AAV among four 2025–26 utility deals ($6.4M, W. Castro) rounded down; the data set the term (0 decline flags → up to 2 years).
- **Why are the pooled wOBA numbers slightly different from an older package?** WB-2: this package weights each season with its own wOBA constants.

## 4 · Query templates (query-builder)
```python
import sys; sys.path.insert(0, r"<this folder>")
import dp_uc56_kernel as K
ph = K.load_house(); w = K.woba_weights(); pos = ph[ph.phillies_role == "batting"]
s = K.subject_rows(pos)                                   # any MLBAM id: change K.SUBJECT_ID
K.oz1(["game_year"], s)                                   # OZ-1 by season
K.ev_profile(["game_year"], s)                            # EV50 (median) / EV90 / max
K.pull_air(["game_year"], s)                              # K46 v1.1.0 pull-air
K.nresults_unrounded(["p_throws"], s[s.game_year.isin(K.BASELINE)], w)   # pooled wOBA, WB-2-safe
```

## 5 · Catalog entry
**uc-pos-021 · Edmundo Sosa 2026 recap ("We Really Do Love Sosa")** — results-down season on an undiminished bat; bench/platoon value; WA-1 walkaway $6.0M × ≤2 yrs. READY-CONDITIONAL · 161/161 · v1.0.0 · 2026-10-23.
