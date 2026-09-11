# 06 · Consumer Success — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

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

---

# v1.1.0 AMENDMENT — Consumer Success (`dp_uc42a`, 2026-09-10)

**Agents:** `analytics-enabler`, `consumer-onboarding-agent`, `dashboard-specifier`

## What the product answers now

Unchanged: *was my working theory about Turner's 2026 directional tendency right?* (No.)
**Added, and more useful:** *if the shift is real, was it him or the pitchers* (him, in-zone — `PM-1`) and
*how much of the down year does it actually explain* (about a fifth — `DC-1`).
**Still not answered:** why his contact is worth less in every direction. That is the swing-mechanics
question, and `uc-pos-014` v1.1.0's bat-path addendum is the tooling for it — flagged as the natural
follow-on, not started here.

## How to read the deliverables

| Artifact | Use it for |
|---|---|
| `dp_uc42a_turner_whole_field_dashboard.html` | **Start here.** Double-click; opens in any browser, offline. Five scenes in narrative order: the rug and what one tick contains → the linked spray chart and pitch map → the attack-stability control → the uncertainty bands and DC-1 → the receipts. |
| `dp_uc42a_turner_whole_field_report.md` | The written version, with the caveats spelled out. §7 is the V-1 defect in v1.0.0's paperwork. |
| `dp_uc42a_context_animation.py` | For JupyterLab. Your Plotly cell, governed and animated. `from dp_uc42a_context_animation import figures; figures()['context'].show()`. **Run it once before trusting it** — plotly could not be installed in the build session (`05` condition 5). |
| `out/dp_uc42a_turner_pitch_extract.csv` | All 9,485 pitches with plate location, if you want to cut it yourself. |
| `out/dp_uc42a_context_player_seasons.csv` | The 65-row rug population with RC-1. |
| `out/dp_uc42a_verification_results.csv` | All 155 checks, by family, with expected and got. |
| v1.0.0's files | Untouched and still runnable. `out/dp_uc42_fig1_facet_grid.png` is superseded, not deleted. |

## Dashboard spec (as delivered)

Five scenes, hand-drawn SVG, no charting library, no network:

1. **The rug** — 65 Phillies player-seasons, barrel rate × run creation, bubble area = games, rug ticks on the
   x margin. Season play/slider walks Turner's tick 2023→2026. Y-axis toggles RC-1 ↔ raw runs created.
2. **The linked pair** — spray chart (field coordinates, with the governed ±4.7-slope boundary drawn so the
   classification is auditable by eye) beside the pitch map (plate coordinates, Statcast zone grid). **Hovering
   either lights the same event on the other.** Filters: zone class, direction, pitcher hand, and a toggle for
   the faint backdrop of pitches that produced no ball in play. Direction-mix bars update beneath.
3. **The control** — PM-1's three tests and the zone-share shift bars (zone 14 down, zone 11 up).
4. **The bands** — z-scores for premise and finding on one axis; the in-zone decomposition table; the DC-1
   waterfall; `slg_bip` by direction and season.
5. **Receipts** — data position, kernel defects measured against this build, provisional objects, inherited
   objects, and the honest-limits list.

Scoped up from v1.0.0's single-toggle bar chart because the question grew two new arms (`PM-1`, `DC-1`) and
because the DPO asked for more interactivity by name. Still short of the six-tab full-season template — a
`dashboard-specifier` judgment call, disclosed.

## Query patterns for reuse

```python
# The two linked views, joined the way the dashboard joins them:
import pandas as pd
bip   = pd.read_csv('out/dp_uc42a_turner_bip_extract.csv')     # 1,832 balls in play
pitch = pd.read_csv('out/dp_uc42a_turner_pitch_extract.csv')   # 9,485 pitches
linked = pitch.merge(bip[['pitch_uid','hit_direction','loc_x','loc_y']],
                     on='pitch_uid', how='left')               # NaN direction = no ball in play

# Re-run PM-1 on a different subject or window:
from dp_uc42a_kernel import pitch_location_profile, load_pos, build_pitch_frame
# ...then chi-square the zone-share vector, conditionally on in/out — see dp_uc42a_build.py::_chi

# Re-run DC-1 on any BIP frame with `events` and `hit_direction`:
from dp_uc42a_kernel import directional_value_decomposition
directional_value_decomposition(bip)          # returns mix / rate / interaction, identity closes

# RC-1 on any context pool:
from dp_uc42a_kernel import runs_created_per_600
```

## Persona action note

**Still no causal actions proposed**, and `DC-1` is the reason to be firmer about that than v1.0.0 was: the
directional shift accounts for a fifth of the damage loss, so a coaching intervention aimed only at pull rate
would be aimed at the smaller share of the problem. The larger share — every direction producing less — is a
question this product cannot answer and should not be read as answering.
