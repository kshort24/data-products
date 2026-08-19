# 06 · Consumer Success
**analytics-enabler · consumer-onboarding-agent · query-builder · dashboard-specifier**

## How to use this data product

Open order for a first-time consumer: **dashboard** (cards + tabs, self-contained HTML, works
offline) → **PDF report** (the argued read, premises adjudicated in §2) → **receipts** (`out/`)
when you need to cite or recompute a number.

## Persona guides

### Hitting coach / offensive coordinator (pre-game, 2026-08-19)
The actionable surface is **§5–6 of the report**: Alcantara's 2026-vs-PHI line (.226 wOBA / 55 PA)
is two starts against a career book of .303/612 — prepare for regression toward the book, not the
shutout. His seam is **LHB contact quality** (.294 wOBA allowed to PHI lefties, 18.8% K over 340 PA)
versus a righty K rate of 23.5%. Harper's 54-PA book (.409 wOBA, 64.9% hard-hit) is the single best
H2H edge on the card. Ignore every per-season H2H cell — all <15 PA, flagged.

### Manager / front office
The Noles constant answers "does Nola still own Miami" with a decade of PA behind it: **yes —
0.090 RC/PA allowed career, 0.022 in 2026 (45 PA)**, with the lefty split intact *against this
club* despite the league-wide 2026 lefty leak (uc-pps-021). The exposure table is the institutional-
memory read: no active arm has seen this offense more (2,278 pitches). Premise corrections matter
for anything repeated publicly: Scherzer, not Alcantara, leads the era; Harper's "3rd-most-faced"
is a full-career claim this plane can't verify.

### Analyst
Start from `dp_uc35_kernel.py` (KF-1 gives you the whole KPI family at any grain in one call) and
`out/dp_uc35_headlines.json` (single source of truth for every card). The floor is **derived** —
if you re-run after new games, `floor_derivation.csv` may change; never hard-code 27.

### Broadcast / content
Safe lines, receipt-backed: "Since 2015, Aaron Nola has turned the Marlins into a .239/.278/.381
hitter — a bat you'd bench" · "Harper vs Alcantara: .319/.389/.574 across 54 PA, hard-hit on 65%
of his batted balls" · "July 28: Alcantara 1, Nola 0 — tonight is the rematch."
**Do not use:** any single-season H2H cell; any sub-50-PA rate without saying the PA; the "most
pitches ever" line (it's Scherzer's).

## Query patterns (against the receipts or the kernel)

```python
# Full KPI family for any entity/grain (kernel):
from dp_uc35_kernel import load_frames, woba_weights, kpi_family, synthetic_batter, NOLA
pos, pps = load_frames(); w = woba_weights()
noles = synthetic_batter(pps, 'Noles', opponent='MIA', pitcher=NOLA)
kpi_family(['game_year'], noles, w)            # season grain
kpi_family(['game_year','stand'], noles, w)    # the facet grain

# Receipt-only (no data plane needed):
import pandas as pd
box = pd.read_csv('out/dp_uc35_boxplot_population.csv')
box.groupby('game_year').rc_per_pa.median()    # the box medians under the constant
```

## Dashboard spec (as implemented)

Five KPI cards (full-precision career receipts) · Tab 1 constants-vs-population scatter with
hover-to-name · Tab 2 stand facets with per-stand floors in the panel notes · Tab 3 exposure +
Harper book + H2H season table · Tab 4 raw season receipts · Tab 5 governance summary. Vendored
Chart.js 4.4.1; degradation helper; no network calls. Drill-down beyond hover is intentionally out
of scope — the receipts are the drill-down.

## FAQ

**Why is the floor 27 and not 50?** Human-DPO ruling HD-1: the comparison is *about Nola*, so his
own minimum season PA vs MIA sets the bar. Sub-50 cells stay flagged and out of rankings.
**Why does the career wOBA say "2026 constants"?** Kernel behavior at non-season grains, disclosed
since dp_uc34; season receipts use true seasonal constants and reconcile in verification.
**Why do some bars say "MLBAM 571578"?** No governed local source maps opposing-pitcher ids to
names (O-10). Ids are exact; names are only shown where a cache or logged carry-in vouches for them.
**Where did "Noles" come from?** The DPO's own label in the submitted snippet (`nola_color =
"Noles"`). It is now a provisional glossary term (SB-1).
