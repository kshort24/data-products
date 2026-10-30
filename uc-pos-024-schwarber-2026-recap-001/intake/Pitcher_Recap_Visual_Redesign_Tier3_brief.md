# Brief: Pitcher Recap Visual Redesign (Tier 3)

## Purpose
Redesign the weakest visuals in the 2026 pps recap reports (uc-pps-033 to 037) so the reports converge on one visual standard. Animation of the Tier 1 visuals is handled separately; do not animate anything here. Changes must pass governance review like any other data product change.

## Governance constraints
- Locked KPIs keep their definitions. A visual change is not a metric change. If a redesign needs a new or redefined metric, flag it as a versioned change and route it to the Data Product Owner.
- Follow the existing UC ledger, naming, and report/governance templates. Each redesign is traced to the use case it modifies.
- Every new comparison set, era boundary, or threshold must be documented, not hardcoded in a notebook.
- Source PDFs are in the data-products repo: uc-pps-033-bowlan, 034-luzardo, 035-wheeler, 036-mayza, 037-alvarado.

## Visual standards (acceptance criteria)
1. **No connected lines for discrete observations** (seasons, starts, games). Use dots/shapes, sized by a stated variable (PA, BF, pitches), with an optional sketched trendline. Exception: cumulative-by-PA, one line per season.
2. **Context before highlight.** Every featured pitcher visual is plotted against a defined comparison set (Phillies SP seasons, Phillies LHP relief seasons, or the house log). The pitcher is the highlighted mark.
3. **Show distribution.** Box plots shade the middle 50% and carry that treatment to every metric, not just velocity.
4. **Trendline scatters report R² and n.** Say whether the pitcher sits above or below the line.
5. **No stacked or single-bar proportion charts.**
6. **Time on the x axis. Axis labels and units always visible.** Small multiples must stay readable at PDF size.
7. **No dual-metric charts on shared axes** unless the units are the same.

## Shared dependencies (build once, first)
- **Comparison sets:** definitions, min-sample rules, and source for Phillies SP seasons, Phillies LHP relief seasons, and house log.
- **Era definitions:** the "slide" start/end and All-Star break dates for Wheeler, documented and reusable.
- **Helpers:** trendline + R² function, box plot with IQR shading, and a discrete-time-series dot plot.

## Redesign items
| # | Visual (report) | Problem | Decision the agents must resolve | Proposed default |
|---|---|---|---|---|
| 1 | wOBA / xwOBA line trends (Alvarado, Mayza, Wheeler) | Lines imply continuity; too small in Wheeler | Replace vs restyle; sizing variable | Dots sized by PA with dotted trendline; Alvarado replaces the trend with cumulative wOBA against |
| 2 | Zone expansion (Wheeler) | Connected points, no context | Comparison set; zone-expansion definition | Pitcher seasons as dots against Phillies SP seasons; drop connections |
| 3 | Walk rate by start (Wheeler) | Busy, lots of shading and lines | Era boundaries; min sample per era | Reduce opacity; show BB% and xwOBA aggregates as shapes above each era (pre-slide / slide / post) |
| 4 | Hard hit rate over time (Wheeler) | Line chart, no distribution | Pitcher framing of exit velocity allowed; 95 mph line | Season box plots of EV allowed with 95 mph reference and hard-hit % labels. The Harper code in the notes is a pattern prototype only |
| 5 | Release point scatters (Wheeler, Mayza) | Story unclear | What question the visual answers | Pitch map of locations, or release point against a Phillies context set |
| 6 | Release extension (Mayza) | Box plot does not convey "further down the mound" | Framing of extension | Horizontal box against context, or a mound schematic with extension distance |
| 7 | Clear misses share (Wheeler) | Proportional box | Alternative encoding | Animated-ready pitch map of misses by location |
| 8 | Pitch of Outing velocity (Bowlan) | Lines connect three segments | Segment definition | Velocity distribution (box or strip) per segment |
| 9 | Weapons by side (Mayza) | Does not capture single-pitch performance | Which single-pitch metric(s) | Dots per pitch type by batter side, sized by usage, with whiff/xwOBA on the axes. Propose options, don't assume |
| 10 | K rate + wOBA against shared axes (Bowlan) | Mixed units | Separate or combine | Two aligned panels, or K% vs wOBA scatter against context |
| 11 | Game Score + early FF velocity (Luzardo) | Connected dots, bars | Shared x axis | FF velocity box per start above, Game Score dots below, shared axis |
| 12 | Proportional bars: swing timing (Wheeler), others | Hard to compare | Alternative encoding | Dot or dumbbell rows by pitch type; flag every instance across the five reports |
| 13 | Four bar charts in a row (Luzardo) | Lukewarm | Layout only | 2x2 grid, keep current coloring |

Also add R² to Luzardo walk rate vs IZR. Note that other Phillies LHP seasons sit near his walk rate.

## Deliverable per item
1. A short design note: decision made, rationale, and rejected alternative.
2. Prototype figure (PNG or HTML) against real data, reviewed against the seven standards.
3. Governance entry: comparison set, thresholds, and any metric impact.
4. Open questions escalated to the Data Product Owner instead of silently assumed.

## Sequencing
1. Shared dependencies (comparison sets, eras, helpers).
2. Items 1, 2, 3, and 4 (Alvarado and Wheeler, highest repeat feedback).
3. Items 8, 10, 11, and 13 (smaller scoped changes).
4. Items 5, 6, 7, 9, and 12 (framing needs the most judgment).

## Out of scope
Animation, Tier 1 and Tier 2 visuals, and any changes to locked KPI definitions.

## Review gate
The Data Product Owner reviews each prototype before it replaces a visual in a published report.