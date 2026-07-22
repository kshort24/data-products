# 07 — Consumption & Observability · uc-pos-006 (dp_uc24)

**Agent roles:** analytics-enabler + consumer-onboarding-agent + data-observability · **Status: Delivered.**

## How to use this data product
The reader PDF is bottom-line-first; the KPI panel (report §1) is the single source of truth for the season line. Two consumables extend it:
- **Interactive HTML explorer** (`dp_uc24_turner_2026_review_interactive.html`) — self-contained; toggle the trajectory KPI (OPS / wOBA), read the season table, monthly 2026, and the indicator panels with hover. Opens in any browser, no server.
- **One-page persona action card** (`dp_uc24_turner_2026_persona_card.pdf`) — the three-persona "so-what," each action traced to an indicator. Meeting-ready.

## Persona onboarding
| Persona | What this answers for you | Start at | Key numbers |
|---|---|---|---|
| **Trea Turner** | Why is the slug down and what's the one lever? | §3–§4 + persona card | pulled-air .117 (PHI-era low), pull .352, in-zone swing .692; fastball wOBA .352 |
| **Manager** | Is the July run real; lineup/leverage call? | §5 + trajectory figure | July .980 (62 PA), rolling OPS .455→.973, post-ASB 14 PA; vs-LHP .632 |
| **Hitting staff** | Where are the fixable leaks? | §4 + §6 | offspeed .184 wOBA / 37.8% K; vs-LHP collapse; watch pulled-air + LD as leading indicators |
| **Analyst** | How was every number produced? | 03/04 + receipts | 16 CSV receipts; `dp_uc24_verification.py` 33/33 |

## Example questions → where answered
- "Is the down year bad luck?" → §2 (xwOBA .295 ≤ wOBA .303 — no) · `_results_by_season.csv`
- "What changed in his contact?" → §4 · `_spray_by_season.csv`, `_battedball_by_season.csv`
- "Which pitches hurt him?" → §4 pitch-group table · `_pitchgroup_by_season.csv`
- "Is he heating up?" → §5 · `_2026_monthly.csv`, `_2026_rolling_form.csv`, `_2026_half_split.csv`

## Observability (post-publish)
| Signal | Rule | Action on trip |
|---|---|---|
| Freshness | max `game_date` should advance ~daily in-season | if > T-2, restate staleness before quoting |
| Entity integrity | `batter.nunique()==1`, 0 dup keys | block refresh; re-lock entity |
| xwOBA null drift on BIP | alert if > 3% (baseline 0.94%) | investigate Savant export |
| Sample thresholds | July / post-ASB splits cross 50 / 100 PA | re-promote from "directional" to reportable |
| KPI drift | RF-1 endpoint must equal `get_stats` OPS each run | fail build if mismatch |

**Refresh cadence:** on-demand / daily in-season. This product is a snapshot as of 2026-07-20 — the trajectory and rolling lines are designed to be re-run as games are added. **Recommended follow-up:** August backtest on the July-recovery durability and the 90th-pct EV top-end.
