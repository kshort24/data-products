# 03 · Governance — `uc-pos-016-turner-whole-field-directional-001`

**Agents:** `business-glossary-agent`, `kpi-calculator`, `technical-lineage-builder`, `data-tagger`,
`privacy-watchdog`, `domain-steward-proxy`

## Rule-1 grep (mandatory before any KPI/function is declared new — `repo-search-before-declaring-kpi-new.md`)

```
grep -rn "def hit_direction"        -> Baseball Functions.ipynb cell 56 (as `pull_air_rate`'s inline logic);
                                        extracted verbatim as a standalone fn in dp_uc40_kernel.py (PA-F1 lineage)
grep -rn "def derive_loc"           -> dp_uc40_kernel.py line 455 (PA-L1)
grep -rn "def in_zone"              -> dp_uc40_kernel.py line 167
grep -rli "sort_rank"               -> 0 matches anywhere in either repo
ls data-products/ | grep -i turner  -> uc-pos-006-turner-2026-offense-001, uc-pos-014-turner-2026-recency-001
```

**Findings applied:**
- `hit_direction`, `derive_loc`, `in_zone` are all governed and reused verbatim — **0 KPIs re-derived that
  already existed.**
- `sort_rank` is genuinely absent from the repo. The requester's own instruction ("as currently defined is
  valid only for a right-handed batter's field orientation") describes a function this organization has
  never shipped. Per Rule 3 (a notebook alias is not a name) and the spirit of Rule 1, this is declared
  **NEW-UC42**, not "the existing `sort_rank`, fixed" — because there is no existing governed `sort_rank` to
  fix. See `01_strategy_intake.md` G-2.
- Two prior Turner UCs exist (`uc-pos-006`, `uc-pos-014`) — both reviewed (see `00` and this UC's report
  §3) for the MLBAM id, the coordinate convention, and the schema notes (asymmetric pre-PHI/PHI columns),
  all of which carried forward cleanly.

## New governed objects (provisional — E-1, pending ratification before a third reuse)

| Object | Definition | Status |
|---|---|---|
| **`sort_rank(direction, stand)`** | Facet-column order: R → Pull=0, Straightaway=1, Oppo=2; L → Oppo=0, Straightaway=1, Pull=2. Keeps physical field left-right reading consistent across batter sides. | NEW-UC42, provisional |
| **`WF-1 oppo_rate_ooz`** | `(BIP with hit_direction=='Oppo') / (all BIP)`, restricted to BIP whose pitch was out of the strike zone (`zone >= 10`), grouped by `game_year`. | NEW-UC42, provisional — diagnostic use only, not locked (see `00` §6) |
| **`WF-2 pull_rate_ooz`** | Same construction, `hit_direction=='Pull'`. | NEW-UC42, provisional |
| **`P_THROWS_COLORS`** | `{'R': '#002D72', 'L': '#E81828'}` — locked dict, Phillies Navy/Red. | NEW-UC42; candidate for promotion to a shared brand-center constant — it is currently redefined ad hoc per script across the repo, which is exactly the instability the requester flagged |

**Why diagnostic, not locked (kpi-calculator recommendation, ratified by the DPO):** WF-1/WF-2 are built on
71-99 BIP per year — well below the volume this repo's rate-stat conventions treat as comfortable (the
standing 50-PA batter floor is itself a *plate-appearance* floor for full-season rates; a per-year,
zone-filtered BIP count in the double digits is a materially smaller population). Locking a KPI whose first
measurement is a null result, on a population this size, risks a false sense of settled-ness. Recommendation:
revisit locking after either a full 2026 season close-out (more BIP) or a second-subject reuse (tests
whether the WF-1/WF-2 construction generalizes).

## Technical lineage (column-level, abbreviated — full trace in `out/dp_uc42_turner_bip_extract.csv`)

```
hc_x, hc_y (Statcast raw)
  -> derive_loc()          -> loc_x, loc_y
  -> hit_direction(loc_x, loc_y, stand)  -> hit_direction {Pull, Straightaway, Oppo, not grouped}
zone (Statcast raw)
  -> in_zone() / ooz flag  -> zone_bucket {in_zone, outside}
hit_direction x zone_bucket x game_year
  -> directional_rate_table()  -> WF-1, WF-2 (pull_rate, oppo_rate, straight_rate) per (game_year, zone)
WF-1/WF-2 (2026) vs WF-1/WF-2 (2023-2025 pooled)
  -> pooled_two_prop_z()   -> z-scores published in §6 of the report
```

## Privacy assessment

**LOW.** Single public MLB player's own publicly-reported on-field performance data (Statcast, MLB's own
public data feed). No PII beyond a public figure's professional statistics; no combination of fields creates
a re-identification risk that does not already exist in the public record (his name and MLBAM id are already
public). No external publication surface is proposed for this diagnostic build — internal Baseball
Operations use only, consistent with `uc-pos-014`'s precedent.

## Data tagging

`sensitivity: public-professional-stats` · `domain: player-performance` · `subject-area: hitting/plate-discipline`
· `data-product: uc-pos-016-turner-whole-field-directional-001` · `value-stream: pos`
