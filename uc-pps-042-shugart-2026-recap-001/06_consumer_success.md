# 06 · Consumer Success
Agents: `consumer-onboarding-agent` · `analytics-enabler` · `query-builder`

## 1 · Product forms and readers
| Form | File | Reader |
|---|---|---|
| Report (11 pp) | `dp_uc66_shugart_2026_recap_report.pdf` / `.md` | front office, pitching coaches, the client |
| Interactive dashboard | `dp_uc66_shugart_2026_dashboard.html` (needs internet for plotly.js from the pinned CDN) | analysts, content |
| Figures | `figures/` — 11 PNGs at 2× (F1–F9, F4a/F4b, S1) | slides, posts |

## 2 · Reading paths
- **Two minutes:** report page 1 (Bottom line + how he was calibrated) or the dashboard's tiles + bottom-line box.
- **Pitching coach:** §5 pitch × hand scorecard (F8), §4 density grid (F4b), §11 what to watch; dashboard Pitch × Hand Explorer.
- **Front office / role:** §1 (F1), §8 role (F9), S-1 stints.
- **The client:** §10 claims graded — 8 supported, 3 partly, 1 not, each with legs and evidence.

## 3 · How to read the new visuals
- **F1/F2/F8/S1** — every panel has its own axis, and **right is always better for the pitcher** (rows where lower is better are flipped and say so).
  Gray = the comparison set; red (or the pitch's color in F8) = Shugart.
- **F4b** — each square is 4 inches; darker = more pitches; each panel is scaled to its own maximum, so compare *where*, not *how many*, across panels.
- **F5** — cumulative lines move slowly by design: a line that keeps sliding late in the year is a real, sustained change.
- **F6** — the gray band is the middle 50% of Phillies RHP relief seasons; wOBA (red) vs xwOBA (dashed) tells you whether results matched contact.

## 4 · Query templates (`query-builder`)
```python
import dp_uc66_kernel as K
ph = K.load_frame(); gf = K.governed_frame(K.client_frame(ph))            # Shugart 2026, regular season
K.nresults(['stand', 'pitch_type'], gf)                                   # results by hand x pitch (K44)
K.inner_third_share(gf, 'L', 'FC')                                        # IN-1
K.cumulative_usage(gf, by=['stand'])                                      # CU-1
seasons = K.pitcher_seasons(ph[ph.game_type == 'R']); A = K.cs_a(seasons) # CS-A pool for any RHP reliever
K.house_percentile(A[A.pitcher != K.SUBJECT_ID], 'woba', 0.312, higher_is_better=False)
```
To run for another righty reliever: change `SUBJECT_ID` / `SUBJECT_NAME` in a successor kernel (never edit this one), rerun the T1–T5 chain.
