# 07 — Consumption & Observability · uc-pos-004 (dp_uc20)

**Agent roles:** analytics-enabler + consumer-onboarding + data-observability

## How to consume this product
- **Read first:** `dp_uc20_schwarber_first_half_report.pdf` (bottom line up top; §7 caveats before extrapolating).
- **Re-query:** every table is a CSV in `MLB/out/dp_uc20_schwarber_first_half_*` — load with pandas, no recompute needed. To refresh after the break: `python dp_uc20_schwarber_first_half.py <MLB_root> <out_dir>` (extends automatically as `phils_2026.parquet` grows; the "1H" framing in figure labels would then be stale — re-label before re-publishing).
- **Interpretation guardrails:** xwOBA = BIP-weighted proxy, not full Statcast xwOBA; wRC not wRC+ (no park/league adjustment); P/PA is an approach descriptor, not a value metric; sub-50-PA splits are directional.

## Persona quick cards
- **Manager:** platoon table (`_platoon_by_season`) — .415 wOBA vs LHP ends the rest-vs-lefty case; count-state table shows why pinch-hitting him behind in counts is fine (.663 even-or-behind).
- **Hitting dept:** discipline + spray receipts are the leading-indicator panel — watch breaking-ball chase (`_pitchgroup`) monthly; the walk rate (13.5%) is the canary.
- **Player:** `_earlycount_pa` + `_2026_hr_log` — the ≤2-pitch plan is producing .643 wOBA; two-strike PA are accepted losses.
- **DPO/Content:** measurables table (§1) + HR log feed Derby-adjacent storytelling; carry-in labels must travel with any excerpt.

## Second-half watch list (observability rules)
| Signal | Rule | Action if tripped |
|---|---|---|
| Walk-rate erosion | BB% < 11% over any 100-PA window | Hitting dept review — the profile's safety net is thinning |
| Breaking-ball counter | chase vs breaking > .33 over 150 pitches | Expect spin-heavy attack; revisit take/swing map |
| Top-end EV aging flag | no batted ball ≥ 114 EV by 2026-09-01 | First true aging indicator at 33 — flag to FO |
| Pulled-air regression | pulled-air rate < .26 over 100 BIP | HR pace will follow; re-read §5 before panicking about BA |
| K% ceiling | K% > 38% over 100 PA | Profile still playable only if barrel ≥ 17%; check both |
| Cache freshness | `phils_2026.parquet` max date > 3 days stale in-season | Re-pull before any second-half quote |

## Versioning
v1.0.0 (2026-07-14, first half). A post-season refresh is a MINOR bump (window extension, same logic); promoting SC-1/SC-2 to locked is metadata-only; any kernel change would be MAJOR and needs version-controller review.
