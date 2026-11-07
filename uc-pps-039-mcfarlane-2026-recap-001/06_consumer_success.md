# 06 · Consumer Success
Agents: `consumer-onboarding-agent` · `analytics-enabler` · `query-builder`

## 1 · Product forms and readers
| Form | File | Reader |
|---|---|---|
| Report (10 pp) | `dp_uc63_mcfarlane_2026_recap_report.pdf` / `.md` | front office, pitching coaches, the client |
| Interactive dashboard | `dp_uc63_mcfarlane_2026_dashboard.html`; Artifact "Alex McFarlane 2026" | analysts, content |
| Slide content + Claude Design kit | `slides/` (= MLB `out/dp_uc63_design_kit/`) | the client, building the animated deck |

## 2 · Reading paths
- **Two minutes:** report page 1 (bottom line + F5b) or the dashboard's "The story" tab.
- **The client's narrative, checked:** each report chapter / dashboard tab opens with his paragraph (Commentary) and the governed read (The data). The ledger at the end lists every verdict.
- **Building the deck:** `slides/slide_content.md` → `slides/dp_uc63_claude_design_brief.md` → `slides/data/` + `slides/ref/`.

## 3 · Slide map (13 slides)
1 Title (Nasty stuff) · 2 Hand-in-hand · 3 Time to ascend · 4 333 pitches, 21 outings · 5 Bridge to Duran · 6 Overall year · 7 Pitch plot · 8 Pitch maps ·
9 By handedness · 10 Outlier fastball · 11 Down the stretch (org addition) · 12 Stretch S-1 · 13 The ledger. Each slide: commentary, registered on-screen numbers, visual + data, animation cue, speaker's data note.

## 4 · Persona notes
- **Pitching coach:** lefty plan worked (FF 63% / SL 28%, one walk). Righty plan leans on the sinker (45.6%), which draws contact (5.3% whiff) and most of the hard contact; 6 of 7 walks came to righties.
- **Manager / bullpen:** 4 bridge outings, all from 8/31; FF velocity dipped to ~98 over 9/22–9/27, back to 99.6 in the Wild Card.
- **Front office:** the four-seam is a 99th / 97th-percentile velo/spin pairing with no peer season in the Phillies frame since 2015.

## 5 · FAQ
- *Why do the client's tables include the Wild Card?* His `pps` does; the report reproduces his frame. Context percentiles use regular season only.
- *Why is whiff 29.1% in one place and 27.9% in another?* 29.1% = all 333 pitches (client frame); 27.9% = 313 regular-season pitches (context pool).
- *Is the slider a bullet slider?* Bullet-adjacent: drop qualifies, sweep is 0.7 in past the house line.

## 6 · Query templates (`query-builder`)
```python
import dp_uc63_kernel as K
ph = K.load_frame(); cf = K.client_frame(ph)                      # the client's frame, id-locked
K.nresults(["stand"], cf); K.whiff_rate(["stand", "pitch_type"], cf)  # client tables
fo = K.fo1_pool(ph); K.fo1_rank(fo)                                # FO-1
K.outing_ledger(cf, game_pitchers=ph[(ph.phillies_role == "pitching") & (ph.game_year == 2026)])  # BD-1
```

## 7 · Catalog entry
`uc-pps-039` · Alex McFarlane 2026 recap · Phillies Pitching · v1.0.0 · READY-CONDITIONAL · public · report, dashboard, slide kit.
