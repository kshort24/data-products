# 03 — Governance · uc-pos-marsh-breakout-001

## business-glossary-agent — term status

| Term | Status | Note |
|---|---|---|
| wOBA, XBH, Chase Rate, Whiff Rate, Hard-Hit Rate, Barrel | Approved (existing) | Locked mechanics, no drift |
| Cumulative XBH / XBH Pace | Approved (uc-pos-marsh-xbh-001) | Reused conceptually for per-600 pace |
| **Pulled-Air Rate** | **Candidate** | Spray-angle threshold ±15°, stand-aware; needs DPO ratification (PD-2) |
| **Two-Strike Funnel %** | **Candidate** | Distinct-PA grain confirmed; no conflict with putaway_rate (pitcher-side) |
| **Early-Count Damage wOBA** | **Candidate** | `balls+strikes<=1` boundary (PD-3) |
| "Approach" | **Not a term** | Deliberately NOT defined as a CDE; report uses the indicator panel and labels narrative as inference |

## Provisional definitions held for DPO sign-off

- **PD-1** First half = regular season through 2026-07-11 (cache boundary = All-Star break).
- **PD-2** Pull threshold = |spray angle| > 15° toward pull side; air = FB + LD.
- **PD-3** Early count = PA resolved within first two pitches.
- **PD-4** July 2026 (40 PA) shown below the 50-PA floor, flagged, because recency is material to the use case.

## metadata-mapper (condensed)

All physical fields map exact to glossary/Statcast reference: `events`, `description`, `zone`, `balls/strikes`, `launch_speed`, `launch_angle`, `launch_speed_angle`, `bb_type`, `hc_x/hc_y`, `p_throws`, `stand`, `estimated_woba_using_speedangle` (mapped to *xwOBA proxy*, fuzzy — flagged in every consumable footnote), wOBA weight columns from constants CSV (exact).

## data-tagger proposal

`domain: phillies/pos` · `sensitivity: public` · `subject: player-performance/marsh` · `product: uc-pos-marsh-breakout-001`. No PII beyond public identity — privacy-watchdog: no flags, external publish not blocked.
