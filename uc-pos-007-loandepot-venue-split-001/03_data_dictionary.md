# 03 — Data Dictionary
## `uc-pos-007` / `dp_uc27` · Layer 2 · Agents: `data-dictionary`, `metadata-mapper`, `data-tagger`

Every physical element published by this product, linked to its CDE from `02_`.

---

## 1. Physical source columns consumed

31 columns read from the parquet layer. All map to an approved glossary term; **0 unmapped**,
**1 ambiguous** (escalated and resolved — see `02_ §2 CDE-1`).

| Physical column | Type | CDE / role | Mapping class |
|---|---|---|---|
| `game_pk`, `at_bat_number`, `pitch_number` | int | Pitch identity (dedup key) | Exact |
| `batter` | int | `BATTER_ENTITY` (MLBAM id) — entity lock | Exact |
| `pitcher` | int | Pitcher entity (Alcantara lens) | Exact |
| `game_date`, `game_year` | date / int | Temporal grain; wOBA-constant join key | Exact |
| `game_type` | str | Competition context (`R` = regular season) | Exact |
| `home_team` | str | **`VENUE_COHORT` + `COMPETITION_LEVEL`** | **Ambiguous — resolved by DPO ruling** |
| `away_team` | str | Relocation detection (DS-2); batting-team derivation | Exact |
| `inning_topbot` | str | `VENUE_TENURE_CONTEXT` derivation | Exact |
| `p_throws` | str | Pitcher handedness filter | Exact |
| `stand` | str | Batter handedness (carried, not published) | Exact |
| `events` | str | Plate Appearance / At Bat / hit-type classification | Exact |
| `description` | str | Swing/whiff classification; row counter | Exact |
| `type` | str | Ball In Play (`X`) | Exact |
| `zone` | int | In-zone / out-of-zone for chase and z-swing | Exact |
| `balls`, `strikes` | int | Count context (carried) | Exact |
| `bb_type` | str | Batted-ball classification | Exact |
| `launch_speed` | float | Hard-Hit Rate, EV90, average EV | Exact |
| `launch_angle` | float | Carried for batted-ball context | Exact |
| `launch_speed_angle` | int | Barrel Rate (`== 6`) | Exact |
| `estimated_woba_using_speedangle` | float | Expected wOBA | Exact |
| `estimated_ba_using_speedangle` | float | Expected BA | Exact |
| `pitch_name` | str | Arsenal classification (Alcantara lens) | Exact |
| `release_speed`, `release_spin_rate`, `pfx_x`, `pfx_z` | float | Arsenal characterisation | Exact |
| `des` | str | Row counter in rate functions | Exact |
| `phillies_role` | str | Batting/pitching split in `phils_*` (source-layer only) | Exact |
| `wBB`, `wHBP`, `w1B`, `w2B`, `w3B`, `wHR`, `Season` | float / int | wOBA linear weights (joined dimension) | Exact |

### Derived columns created by the build

| Column | Derivation | CDE |
|---|---|---|
| `player` | `batter` mapped through the 11-entry `ROSTER` dict | `BATTER_ENTITY` display name |
| `venue` | `home_team == 'MIA'` → `loanDepot park` else `All other MLB parks` | `VENUE_COHORT` |
| `is_milb` | `home_team` not in the 31-code MLB allow-list | `COMPETITION_LEVEL` |
| `is_irma` | `game_pk` in {492302, 492317, 492332} or (MIA-home ∧ MIL-away ∧ date in 2017-09-15..17) | DS-2 enforcement |
| `park_era` | `game_year <= 2019` → pre-reconfig, else post-reconfig | DS-3 |
| `bat_team` | `home_team` if `inning_topbot == 'Bot'` else `away_team` | Batting-team identity |
| `miami_home_club` | `venue == loanDepot park` ∧ `bat_team == 'MIA'` | `VENUE_TENURE_CONTEXT` |

---

## 2. Published tables (CSV receipts under `out/`)

24 receipts. Every number in the reader report and the persona card traces to one of these.

| File | Grain | Purpose |
|---|---|---|
| `dp_uc27_venue_split.csv` | hitter × venue cohort | **Primary answer.** Full KPI panel — the corrected version of the requester's snippet |
| `dp_uc27_venue_split_visitors.csv` | hitter × venue cohort, visiting club only | Same panel with `VENUE_TENURE_CONTEXT` applied |
| `dp_uc27_venue_delta.csv` | hitter | VD-1 deltas + VD-2 classification + qualification flag |
| `dp_uc27_pooled_venue.csv` | venue cohort | Roster-pooled panel, all rows |
| `dp_uc27_pooled_venue_visitors.csv` | venue cohort | Roster-pooled panel, visiting club only — **the decision-relevant frame** |
| `dp_uc27_park_era.csv` | venue × park era | DS-3 test, all rows |
| `dp_uc27_park_era_visitors.csv` | venue × park era | DS-3 test, visiting club only |
| `dp_uc27_miami_home_club.csv` | hitter × tenure context | The confound, quantified per hitter |
| `dp_uc27_bbtype_venue.csv` | venue × batted-ball type | Ground-ball / fly-ball shape by cohort |
| `dp_uc27_discipline_venue.csv` | hitter × venue | Chase, whiff, z-swing, zone-seen |
| `dp_uc27_alcantara_h2h.csv` | hitter | Career head-to-head panel vs Alcantara |
| `dp_uc27_alcantara_venue.csv` | venue | Roster vs Alcantara, Miami vs elsewhere |
| `dp_uc27_alcantara_hitter_venue.csv` | hitter × venue | Head-to-head split by venue |
| `dp_uc27_alcantara_total.csv` | — | Roster-total line vs Alcantara |
| `dp_uc27_alcantara_mix.csv` | pitch type | Arsenal vs this roster: usage, velo, movement, outcomes |
| `dp_uc27_alcantara_recent.csv` | hitter | 2025–26 window head-to-head |
| `dp_uc27_alcantara_recent_mix.csv` | pitch type | 2025–26 usage, for the arsenal-shift claim |
| `dp_uc27_alcantara_by_year.csv` | season | Year-by-year vs this roster |
| `dp_uc27_source_profile.csv` | hitter | Naive-union vs deduped vs governed pitch counts |
| `dp_uc27_source_provenance.csv` | hitter × source file | Which parquet supplied which rows, pre-dedup |
| `dp_uc27_exclusion_audit.csv` | governance rule | Rows removed by each filter |
| `dp_uc27_freshness.csv` | source | Max `game_date` per source with staleness note |
| `dp_uc27_dq_scorecard.csv` | check | 16 DQ checks with blocking flag and verdict |
| `dp_uc27_verification_results.csv` | check | 256 independent-recompute reconciliations |

### Shared panel columns

All panel tables carry the same 17 columns, so any two cohorts are directly comparable:

`plate_apps` · `pitches_per_pa` · `ba` · `obp` · `slg` · `ops` · `woba` · `xwoba` ·
`hard_hit_rate` · `barrel_rate` · `ev90` · `krate` · `bbrate` · `hr_rate` · `chase_rate` ·
`whiff_rate` · `bips`

---

## 3. Published figures

| File | Content | Every number traces to |
|---|---|---|
| `dp_uc27_fig1_woba_dumbbell.png` | Per-hitter wOBA, Miami vs elsewhere, PA labelled | `venue_split.csv`, `venue_delta.csv` |
| `dp_uc27_fig2_signal_quadrant.png` | VD-2 quadrants: results delta vs process composite | `venue_delta.csv` |
| `dp_uc27_fig3_park_era.png` | Pooled wOBA by park era | `park_era.csv` |
| `dp_uc27_fig4_alcantara_h2h.png` | Career wOBA/xwOBA vs Alcantara, PA labelled | `alcantara_h2h.csv` |
| `dp_uc27_fig5_confound_reveal.png` | Four cohorts: baseline, Miami all-rows, Miami visitors, Miami vs Alcantara | `pooled_venue.csv`, `pooled_venue_visitors.csv`, `alcantara_venue.csv` |

---

## 4. Classification tags (`data-tagger` proposal — DPO approved)

| Dimension | Value |
|---|---|
| Sensitivity | **PUBLIC-DERIVED** — all inputs are publicly published Statcast tracking data |
| PII | **None.** Player names and MLBAM ids are public professional identifiers, not personal data |
| Domain ownership | Phillies Baseball Operations — Offense |
| Subject area | Hitter performance · Venue analysis · Opponent scouting |
| Data product membership | `uc-pos-007` |
| Distribution | Internal |
| Retention | Retain with the package; supersede on re-run rather than overwrite |
