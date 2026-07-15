# 07 — Consumption & Observability · uc-pos-005 (dp_uc22)

**Agent roles:** analytics-enabler + consumer-onboarding + data-observability · **Status: Delivered**

## How to consume this product
| Consumer | Artifact | What it gives you |
|---|---|---|
| Anyone (start here) | `dp_uc22_harper_own_the_zone_interactive.html` | 6-figure interactive: shadow-band pitch map (every 2026 edge decision, hover for pitch detail), OZ trends, damage panels, platoon, monthly |
| Manager / Hitting dept | `dp_uc22_harper_own_the_zone_report.md` | Governed narrative + persona actions |
| Analyst | `out/dp_uc22_*.csv` (16 receipts) | Season/dim-grain aggregates + 2026 pitch-level shadow-band and punished logs |
| Analyst (rebuild) | `dp_uc22_harper_own_the_zone.py . out` | Deterministic rebuild from parquet cache |

## Reading the OZ family (interpretation FAQ)
- **OZ-1 up = good** (taking the borderline ball). **OZ-2 down is NOT bad** — read it with OZ-4: fewer edge swings at higher damage is the 2026 profile.
- **Never quote OZ-3 alone** (03 guardrail): it fell to .099 in 2026 *because* selectivity improved on both sides of the line.
- Sub-50-pitch or sub-40-BIP splits are labeled small-sample; the 2026 vs-LHP OZ-4 (24 BIP) is indicative only.
- Region shares move with pitcher behavior too: Harper saw fewer shadow_in pitches per pitch seen in 2026 (250/1,590) than 2025 (402/2,172) — pitchers are living further off the plate against him; that context belongs in any second-half comparison.

## Observability & refresh
| Monitor | Rule | Action |
|---|---|---|
| Freshness | parquet cache `max(game_date)` < last completed Phillies game − 2 days | refresh cache via `mlb_data.py` before any re-run |
| Schema drift | Statcast field rename/removal in {plate_x, plate_z, sz_top, sz_bot, launch_speed_angle, estimated_woba_using_speedangle} | block re-run; escalate to DPO |
| Volume anomaly | new-season pitch count for entity deviates >20% from games-played expectation | investigate role/injury before interpreting trends |
| Constant drift | FanGraphs 2026 constants finalized post-season | re-run wOBA-dependent receipts; expect ≤ ±0.002 |
| Re-run triggers | end of 2026 regular season (full-year view); any Harper IL stint > 15 days (window annotation) | DPO decides |

## Watch list carried out of the first half
1. Fastball barrel rate (.092, tenure low) — does the spin-hunting profile hold up when pitchers adjust back to velocity?
2. vs-LHP average EV (88.0, tenure low) — contact quality, not approach.
3. July fade (.251 wOBA, 48 PA) — fatigue vs noise; September will tell.
4. OZ-1 durability — .411 held through three good months; the mantra's proof is a full season.
