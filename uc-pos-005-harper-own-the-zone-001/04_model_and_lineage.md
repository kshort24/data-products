# 04 — Model & Lineage · uc-pos-005 (dp_uc22)

**Agent roles:** data-architect + technical-lineage-builder · **Verdict: PASS**

## Grain & keys
- Base grain: **pitch** (one row per pitch). Natural key: `(game_pk, at_bat_number, pitch_number)` — dedup enforced on load.
- Entity lock: `batter == 547180`; population: `game_type == 'R'`; `phillies_role == 'batting'` at source select.
- No joins across grains except the wOBA-weights merge (`game_year == Season`, many-to-one, validated: 0 null weights post-merge). Join-validator: fan-out impossible (constants keyed uniquely by Season).

## Layered lineage (source → receipt)
```
data/phillies/phils_{2019..2026}.parquet          (Baseball Savant via mlb_data.py)
  └─ filter: phillies_role=='batting' & batter==547180 & game_type=='R'
  └─ dedup: (game_pk, at_bat_number, pitch_number)
  └─ merge: wOBA and FIP Constants.csv on game_year==Season
      ├─ get_stats(...)      → results_by_season / platoon_results / 2026_monthly
      ├─ discipline(...)     → discipline_by_season          [locked, zone<=9]
      ├─ batted_ball(...)    → battedball_by_season / _pitchgroup / _pitchtype / platoon_battedball
      └─ tag_regions(...)    [NEW: geometry per 03; excludes 10 null-location rows]
          ├─ region_profile(...) → region_profile_by_season
          ├─ oz_kpis(...)        → oz_kpis_by_season / oz_2026_by_{platoon,pitchgroup,countstate}
          ├─ shadow-band log     → 2026_shadow_band_pitchlog   [consumable feed]
          └─ punished log        → 2026_punished_log
```
All receipts written to `out/dp_uc22_harper_own_the_zone_*` (16 CSV + 4 PNG + buildlog). The interactive HTML reads **receipts only** — no raw recompute in the consumption layer.

## Derived columns (build-time, spec'd here)
| Column | Logic |
|---|---|
| `season` | `game_year` |
| `pitch_group` | dp_uc18 PITCH_GROUP map; unmapped → 'other' (excluded from group receipts) |
| `count_state` | two_strike (`strikes==2`) / ahead (`balls>strikes`) / even_or_behind — dp_uc20 convention |
| `region` | shadow_in / heart / shadow_out / waste per 03 geometry |
| `swing`, `whiff` | locked SWINGS/WHIFFS description lists |
| `outcome` (band log) | xbh / single / swing_other / take — display classification only |

## Implementation constraint honored
data-engineer implemented only what 03/04 specify; locked kernel functions copied verbatim from dp_uc20 (diff-checked). Verification (06) recomputes independently of both.
