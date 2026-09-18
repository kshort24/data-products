# 02 · Business Glossary & Data Domains
**`dp_uc46` · duplicate-checked against `Baseball Functions.ipynb` cells 49/55/57 and `contract/`**

## 1. Data domains

The O-11 separation applies: the **value stream** is the consumer axis, the
**data domain** is the source axis. They are not the same cut and they do not
have the same NULL regime.

| Data domain | Source axis | CDEs contributed | NULL regime |
|---|---|---|---|
| **Pitch Outcomes** | Statcast pitch record | Pitch Result Type (`type`) | Complete |
| **Batted Ball Classification** | Statcast derived classifier | Batted Ball Type (`bb_type`) | **Complete (0.00% on BIP)** |
| **Hit Coordinates** | Hit-location tracking | Hit Coordinate X/Y (`hc_x`,`hc_y`) | Incomplete, 0.08–0.14% |
| **Batted Ball Tracking** | Hawk-Eye sensor | Launch Angle, Exit Velocity, Hit Distance | Incomplete, 3 different rates |
| **Batter Identity** | Roster / game record | Batter Handedness (`stand`), Batter, Player Name | Complete |
| **Game Events** | Play-by-play | Plate Appearance Description (`des`) | Complete |

Value stream: **`pos`** (Phillies batting). The family is handedness-symmetric and
carries no Phillies-specific logic, so it runs unchanged on `nphl`. A pitcher-facing
application (`pps` — "what direction does this pitcher allow") is **out of scope** and
is a separate use case, not a parameter of this one.

## 2. Business glossary

New and promoted terms. Terms already governed elsewhere are listed with their
source and are **not** redefined here.

| Term | Definition | Synonyms / Abbreviations | Status |
|---|---|---|---|
| **hit direction** | The third of the field a batted ball travelled to, relative to the batter's own handedness: Pull, Straightaway, or Oppo. Assigned by a fixed ±4.7-slope wedge boundary on the batted ball's field coordinates. | spray direction, batted ball direction | **GOVERNED** (extracted from cell 56) |
| **pull** | A batted ball hit to the batter's pull side — the left side of the field for a right-handed batter, the right side for a left-handed batter. | pulled, pull side | GOVERNED |
| **oppo** | A batted ball hit to the batter's opposite field — the right side of the field for a right-handed batter, the left side for a left-handed batter. | opposite field, oppo side, "the other way" | **NEW** |
| **straightaway** | A batted ball hit up the middle, inside the wedge that is neither pull nor oppo. Handedness-independent by construction. | up the middle, middle third, straight | **NEW** |
| **classifiable ball in play** | A ball in play whose hit coordinates were recorded, and which can therefore be assigned a hit direction. The governed denominator for every directional rate. | classifiable BIP, tracked BIP | **NEW** |
| **oppo rate** | The ratio of balls hit to the opposite field to classifiable balls in play, at the stated level of granularity. | Oppo%, opposite-field rate | **NEW KPI** |
| **pull rate** | The ratio of balls hit to the pull side to classifiable balls in play, at the stated level. | Pull% | **NEW KPI** |
| **straightaway rate** | The ratio of balls hit up the middle to classifiable balls in play, at the stated level. | Straight%, middle rate | **NEW KPI** |
| **oppo line-drive rate** | The ratio of line drives hit to the opposite field to **opposite-field** balls in play, at the stated level. Reads as: when this hitter goes the other way, how often does he square it up? | oppo LD%, opposite-field line-drive rate | **NEW KPI** |
| **batted ball data profile** | The distribution summary of a measured batted-ball characteristic within a `bb_type` cell — minimum, maximum, mean, standard deviation, 5th and 95th percentile — each reported with the count of non-null observations behind it. | bb profile, batted ball profile | **NEW** |
| **pull air rate** | The ratio of pulled batted balls that are not ground balls to classifiable balls in play, at the stated level. | Pull AIR%, pull air rate | **AMENDED** — definition unchanged, denominator narrowed (see `08`) |
| **directional cell** | One published combination of level values and hit direction. The unit the FL-1 floor is applied to. | — | **NEW** |

### Terms NOT redefined here (already governed)
`bb_type`, `bips`, `total_level`, `share` — `Baseball Functions.ipynb` cell 49.
`total_bips` — cell 55. `barrel_rate`, `hard_hit_rate` — cells 57, 51.

### Duplicate / conflict check
- `oppo_rate` as a **column name** already exists in `dp_uc42_kernel` with an
  identical formula. Promoted, not duplicated. Confirmed numerically identical
  (verification family C, 7/7).
- No conflicting definition of "oppo" exists in the repo. The word appears in ten
  prior files, always as prose or as a column produced by the same cell-56 boundary.
- **Naming conflict, unresolved by design:** this build uses `mu_la` / `min_la` /
  `std_la`, the DPO's stated convention. The notebook's `inds` (cell 42) uses the
  reversed `la_mu` / `ev_mu` / `dist_mu`. Both now ship. Logged as **O-20**;
  recommendation is to align `inds` on a later pass, not here — `inds` has 74 call
  sites across 14 files and renaming its output in this build would break them all.

## 3. Semantic layer — what each KPI may and may not do

| KPI | Grain | Aggregation | Prohibited |
|---|---|---|---|
| `pull_rate`, `straight_rate`, `oppo_rate` | any `level` over classifiable BIP | Ratio of sums. Re-aggregate by summing `*_n` and `n_bip`, never by averaging rates. | Publishing `oppo_rate` without its two siblings (DR-3). Inferring `pull_rate` as `1 − oppo_rate`. |
| `oppo_ld_rate` | `level` × `hit_direction`, filtered to Oppo × line_drive | Ratio of sums within the direction | Comparing to a pull line-drive rate without noting the denominators are different populations. |
| `share` (bb_type) | `level` × `bb_type` | Ratio of sums | Mixing with the profile arm's `n_*` as if one denominator. |
| `mu_*`, `std_*`, `p5_*`, `p95_*` | `level` × `bb_type` | **Not re-aggregable.** A mean of means across cells is not the pooled mean. | Re-aggregating. Reporting without its `n_*`. |
| `min_*`, `max_*` | `level` × `bb_type` | Order statistics; re-aggregable by min/max only | Treating as a range estimate — they are single observations. Use `p5`/`p95` for that. |
| `pull_air_rate` | any `level` | Ratio of sums | Comparison to values published before 2026-09-17 (`08`). |

**Standing constraint on all of them:** a directional cell below FL-1 (25 classifiable
BIP) may be computed but may not be ranked, headlined, or shown unflagged.
