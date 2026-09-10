# 06 · Consumer Success — `uc-pos-016-turner-whole-field-directional-001`

**Agents:** `analytics-enabler`, `consumer-onboarding-agent`, `dashboard-specifier`

## Primary persona: Kellen (as requester / hitting-analytics owner)

**What this product answers:** was my working theory about Turner's 2026 directional tendency right?
**What it doesn't answer:** why any observed shift is happening (no swing-mechanics data joined here — see
`uc-pos-014`'s bat-path addendum, `03a_bat_path_semantics_and_lineage.md`, for that angle if a follow-on is
wanted) and whether it's predictive of anything going forward (no tripwire/monitor armed for this UC — see
`07`).

## How to read the deliverables

| Artifact | Use it for |
|---|---|
| `dp_uc42_turner_whole_field_report.pdf` | The verdict, first page. Sections 4-5 are the visuals; 6 is the finding; 7 is the two decisions flagged for your confirmation. |
| `dp_uc42_turner_whole_field_dashboard.html` | Toggle between outside-zone and in-zone views of the pull/oppo trend interactively; open directly in any browser, no network needed. |
| `out/dp_uc42_fig1_facet_grid.png` | The exact layout from your sketch description — hit_direction columns, game_year rows, p_throws colored, outside-zone pitches ringed. |
| `out/dp_uc42_turner_bip_extract.csv` | Every BIP, row-level, if you want to re-slice it yourself (e.g., by month, by specific pitcher). |

## Dashboard spec (as delivered)

Single-page, 4 sections: verdict banner, KPI stat cards (4), an interactive pull/oppo bar chart with an
outside-zone/in-zone toggle (Chart.js, vendored inline — opens with no network), and the full counts table.
Scoped down from the 6-tab pattern used on full season-review UCs (`uc-pos-014`) to match this UC's single
narrow question — a `dashboard-specifier` judgment call, disclosed here rather than silently matching the
bigger template's tab count for its own sake.

## Query patterns for reuse

```python
# Re-slice the BIP extract by month instead of season:
import pandas as pd
bip = pd.read_csv('out/dp_uc42_turner_bip_extract.csv')
bip['month'] = pd.to_datetime(bip.game_date).dt.month
bip.groupby(['month', 'ooz']).hit_direction.value_counts(normalize=True)

# Re-run the significance test on a different year split:
from dp_uc42_kernel import pooled_two_prop_z
# x1,n1 = 2026 count/total; x2,n2 = comparison-window count/total
```

## Persona action note

**No causal actions are proposed.** This is a description-of-outcome product (where did BIP go, by year and
zone), not a swing-mechanics or approach diagnostic. If Kellen wants the "why" behind the in-zone shift this
UC surfaced, the natural next step is a bat-path pull (per `uc-pos-014` v1.1.0's precedent: contact point,
swing plane) scoped to in-zone-only BIP in 2026 — flagged as a possible follow-on UC, not started here.
