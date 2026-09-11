# 02 · Engineering Design — `uc-pos-016-turner-whole-field-directional-001`

**Version: v1.1.0** — the v1.0.0 text below is unchanged; the v1.1.0 delta is the amendment section appended at the end of this file.

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

---

# v1.1.0 AMENDMENT — Engineering Design (`dp_uc42a`, 2026-09-10)

**Agents:** `data-architect`, `eda-agent`, `join-validator`, `metadata-mapper`, `dashboard-specifier`

## Data model (delta)

v1.0.0's single-entity BIP pipeline is unchanged and reproduced exactly. Three populations are added around
it, all from the same concat, all joined on keys that already exist.

```
phils_{2023..2026}.parquet
  ├─► [A] pos  = Phillies BATTING rows (phillies_role contract), game_type != S/E
  │            └─► merge wOBA weights per season (game_year → Season, row-count asserted)
  │            ├─► [A1] CONTEXT POOL   groupby(player_name, game_year) via governed
  │            │        nresults / runs_created / hard_hit_rate / barrel_rate, PA >= 50
  │            │        └─► RC-1 runs_created_per_600
  │            └─► batter == 607208
  │                 ├─► [B] PITCH FRAME   game_type=='R', all 9,485 pitches
  │                 │        + pitch_uid, is_bip, in_zone      ──► PM-1 profile + stability
  │                 └─► [C] BIP FRAME     v1.0.0 pipeline, verbatim, + pitch_uid
  │                          + plate_x/plate_z carried through ──► PM-2, DC-1, both charts
  └─► C ⊂ B, joined on pitch_uid  ──► the cross-highlight between spray chart and pitch map
```

**`join-validator` findings (three joins now exist where v1.0.0 had none):**

| Join | Risk | Result |
|---|---|---|
| wOBA weights → `pos` on `game_year → Season` | Fan-out if the constants file carries a duplicate season row (it has repeated blocks historically) | **Asserted**: weights de-duplicated on `Season`, and the merge asserts `len(out) == len(in)`. **PASSED**, 0 fan-out. |
| Context pool: 5 governed KPI frames merged on `[player_name, game_year]` | Row loss from `hard_hit_rate`'s inner merge (defect D-1) | **Merged `how='left'` at the pool level**, so the 3 affected player-seasons keep a NULL hard-hit rate instead of vanishing. The governed function itself is **not** patched — the defect is measured and disclosed, `out/dp_uc42a_defect_exposure.csv`. |
| BIP frame ↔ pitch frame on `pitch_uid` | Duplicate or non-unique key would silently mis-link the two charts | **Asserted**: `pitch_uid` unique across all 9,485 rows; BIP is a strict subset. **PASSED.** |

## EDA findings that shaped the revision

- **The plate-side coordinate convention was derived, not assumed.** For this RHB, Pull BIP have median
  `plate_x` = −0.110 and Oppo +0.231; zone cells 1/4/7 sit at ≈ −0.50 and 3/6/9 at ≈ +0.50. Negative
  `plate_x` is therefore **inside**, which is what licenses the Inside/Middle/Outside labelling in the
  in-zone decomposition. `uc-pos-014`'s bat-path addendum (O-15: `attack_direction` is pull-negative here,
  the *inverse* of the MLB glossary) is the standing reason this repo never takes a Statcast sign convention
  on trust.
- **The in-zone pull loss is uniform across the zone**: down 5.8–8.7 pp in every one of three zone rows and
  three zone columns, none clearing the band individually. A location-driven cause would concentrate. This
  observation is what motivated PM-1 — if it is not *where* the pitches are, is it *whether* the pitches
  moved at all?
- **PM-1's answer split cleanly on the in/out boundary**, and the whole-plate test would have hidden it. The
  out-of-zone shift is essentially two cells: zone 14 (down-and-away) −3.7 pp, zone 11 (up-and-in) +4.2 pp.
- **Every direction's production is down** (`slg_bip`, in-zone: pull .766→.632, straight .538→.447, oppo
  .454→.429). This is what forced `DC-1`: with all three falling, a mix-shift story could not be the whole
  explanation, and reporting the mix shift alone would have let a true finding do false work.

## Design decisions

1. **Two linked views, not one.** The spray chart answers *where the ball went*; the pitch map answers *where
   the pitch was*. Shipping either alone loses the question the finding actually turns on. They share
   `pitch_uid` and cross-highlight on hover — the interaction is the argument, not decoration.
2. **Season frames over grain descent.** The DPO's call (`01` G-6). A population→season→pitch descent was the
   org's recommendation; season frames were chosen, and season frames are what shipped.
3. **Hand-drawn SVG, no charting library.** A field-coordinate spray chart, a plate-side zone grid, and a
   cross-highlight link between two different coordinate systems are not shapes any library ships. It also
   sidesteps **O-19** (the Chart.js `merge()` defect that silently deletes tick callbacks, repo-wide) — which
   v1.0.0's Chart.js dashboard was exposed to.
4. **Both y-axes ship on the context chart.** `RC-1` is the default because the raw axis misleads (`03` §5),
   but the raw count is one toggle away. Replacing the DPO's own metric without offering it back would be
   correcting him rather than informing him.
5. **Grain of the rate tests unchanged from v1.0.0** — `game_year × zone_bucket`. The new decompositions
   (`PM-2`, zone rows/columns) are explicitly labelled diagnostic, with their small cell counts printed
   beside every rate, because they are exactly the sparse-cell grain v1.0.0's §Design-change note refused to
   compute rates on.

## Metadata mapping (delta)

| Physical field | Business term | Mapping |
|---|---|---|
| `plate_x`, `plate_z` | Pitch location at the front of home plate, catcher's-view feet | Exact — Statcast native, no transform |
| `launch_speed`, `launch_angle`, `launch_speed_angle` | Exit velocity, launch angle, Statcast batted-ball class (6 = barrel) | Exact — governed by `hard_hit_rate` / `barrel_rate` |
| `bat_score`, `post_bat_score` | Batting-team score before/after the plate appearance | Exact — governed by `runs_created` |
| `wBB … wHR` | Season wOBA linear weights | Exact — `wOBA and FIP Constants.csv`, per-season |
| `pitch_uid` *(derived)* | Statcast pitch identity: game × at-bat × pitch number | **New**, NEW-UC42a |
| `slg_bip` *(derived)* | Total bases per ball in play | **New**, NEW-UC42a — deliberately *not* named `slg`; the denominator is BIP, not at-bats |

**0 ambiguous or unmapped physical fields.** Four new derived terms proposed in `03` §5.
