# 02 · Engineering Design — `uc-pos-016-turner-whole-field-directional-001`

**Agents:** `data-architect`, `eda-agent`, `join-validator`, `metadata-mapper`

## Data model

Single-source, single-entity pull — no joins required.

```
data/phillies/phils_2023.parquet
data/phillies/phils_2024.parquet     ─┐
data/phillies/phils_2025.parquet      ├─► concat ─► filter batter==607208
data/phillies/phils_2026.parquet     ─┘         ─► filter game_type=='R'
                                                 ─► filter type=='X' (BIP)
                                                 ─► derive_loc (hc_x/hc_y -> loc_x/loc_y)
                                                 ─► hit_direction (governed, verbatim)
                                                 ─► filter zone.notna() (governed in_zone convention)
                                                 ─► ooz flag (zone >= 10)
                                                 ─► sort_rank (NEW-UC42)
```

`join-validator` finding: **no join to validate** — single-entity, single-frame-family pull. The only
structural risk (fan-out from a multi-source concat) does not apply, unlike hitter UCs that blend
`turner.parquet` (pre-PHI) with the Phillies frames; this UC is Phillies-era only by design (the premise is
about a 2023-2025→2026 drift, entirely inside the PHI frame family).

## EDA findings that shaped the build

- **0 untracked BIP** (`hc_x`/`hc_y` both non-null on every one of Turner's 1,832 regular-season BIP,
  2023-2026) — the D6/O-8 untracked-BIP caveat that affects most hitter UCs does not apply here.
- **0 null `zone`** on Turner's BIP in this window — the governed `in_zone()` NULL-exclusion rule has zero
  rows to exclude for this subject; disclosed rather than silently assumed to be zero.
- **Turner is 100% `stand=='R'`** across all four seasons (9,485 regular-season pitch rows) — expected (he
  is not a switch hitter), but verified rather than assumed, because `hit_direction` and `sort_rank` are
  both stand-branching functions and a silent stand-mix would change the read of every downstream number.
- **Outside-zone BIP share is declining**: 20.2% (2023) → 17.2% (2024) → 14.7% (2025) → 15.8% (2026). This
  directly affects the power of the outside-zone-specific test (§05) and is reported as an EDA-forced
  disclosure, not folded silently into the headline rate.

## Design change forced by EDA

The original grain in the request ("sliced by game_year x p_throws x hit_direction") would, if used as the
*rate-computation* grain rather than the *visual* grain, produce cells as small as single digits (e.g.
2026 x LHP x Oppo x outside-zone). **Design decision:** compute rates and significance tests at
`game_year x zone_bucket` (in/out) — the grain the premise is actually about — and use the full
`game_year x hit_direction x p_throws` cut only for the visual (Fig. 1), where a scatter tolerates sparse
cells that a rate table cannot. This is disclosed in `01` as declared DPO discretion #2 and does not
silently narrow what was asked for — the full three-way cut still ships, as the figure.

## Metadata mapping

| Physical field | Business term | Mapping type |
|---|---|---|
| `hc_x`, `hc_y` | Raw batted-ball coordinates (Statcast scoreboard-pixel frame) | Exact — governed by `derive_loc()` |
| `loc_x`, `loc_y` | Batted-ball horizontal/vertical location, centered feet-from-plate | Exact — `cbp-spray_AI.md` |
| `zone` | Statcast strike-zone region code (1-9 in zone, 11-14 out) | Exact — governed `in_zone()` |
| `hit_direction` | Pull / Straightaway / Oppo, stand-relative | Exact — `Baseball Functions.ipynb` cell 56 |
| `p_throws` | Pitcher handedness | Exact |
| `batter` | MLBAM player id | Exact — entity lock, not name-matched |

**0 ambiguous or unmapped fields.** No new glossary term required for any *physical* field; two new
*derived* terms are proposed in `03_governance.md` (WF-1, WF-2).
