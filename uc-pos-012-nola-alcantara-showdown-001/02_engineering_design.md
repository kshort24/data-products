# 02 · Engineering Design
**data-architect · join-validator · kpi-calculator · eda-agent**

## Logical model

One pitch-level fact population per analysis entity, all conforming to the same KPI grain contract:

| Entity | Source | Filter | Row meaning |
|---|---|---|---|
| `Noles` | `pps` | `pitcher==605400 & bat_team=='MIA'` | a pitch Nola threw to a Marlin |
| `Wheeler vs MIA` | `pps` ∪ `wheeler.parquet` | `pitcher==554430 & bat_team=='MIA'` | a pitch Wheeler threw to a Marlin (2017–19 NYM years from cache) |
| `Phillies Hitters` | `pos` | in-population per HD-1 floor | a pitch to a Phillies batter |
| `Harper vs MIA` | `pos` | `batter==547180 & opponent=='MIA'` | a pitch to Harper from a Marlin |
| `PHI vs Alcantara` | `pos` | `pitcher==645261` | a pitch Alcantara threw to a Phillie |

`bat_team` (pitching frames) = `away_team if inning_topbot=='Top' else home_team`.
`opponent` (batting frame) = `away_team if home_team=='PHI' else home_team`.

**Grains published:** `entity` (career) · `entity × stand` · `game_year` · `game_year × stand` ·
`player_name × batter × game_year(× stand)` for the Phillies population. Every grain gets the full
KPI family (KF-1) so the box plot, scatter, cards and tables all read from the same shape.

## Join / concat validation

| Check | Result |
|---|---|
| `pos` ∩ `pps` on `(game_pk, at_bat_number, pitch_number)` | disjoint by construction (`inning_topbot` split); dup count asserted **0** in build and verification |
| Wheeler cache × `pps` season overlap | **∅** — cache carries 2017–2019 only; asserted in build (`overlap == set()`) and verification check 22 |
| Column intersection on the Wheeler concat | concat restricted to shared columns (cache has 93 of 114); all KF-1 CDEs present in both |
| KF-1 internal merges | all `on=level, how='left'` onto the `nresults_unrounded` spine → no fan-out possible (spine is unique per grain by groupby construction); `rc_per_pa × plate_apps == runs_created` identity asserted on the box population |
| `alcantara.parquet` | **excluded from all joins** (stale); entity-lock read only |

## KPI calculation specs

All inherited functions are consumed from `dp_uc35_kernel.py` (transcription authority:
`Baseball Functions.ipynb`; `_fix` provenance: uc-pos-010/011). New this UC:

### KF-1 `kpi_family(level, df, woba_w)` — NEW-PROVISIONAL (composition)
Left-merge chain: `nresults_unrounded` (slash, wOBA, K%) ⟵ `whiff_rate_fix` (D1) ⟵ `chase_rate_g`
⟵ `hard_hit_rate_fix` (D2) ⟵ `barrel_rate_g(suffix='_barrel')` ⟵ `runs_created` (verbatim).
Derived: `rc_per_pa = runs_created / plate_apps` (unrounded components — D4 avoided by
construction; `runs_created` filled 0 only as a genuine count). Population: all pitches at the
grain; PA-denominated rates use governed `NON_PA` terminal rows. Edge cases: zero-swing grain →
whiff NULL; zero-OOZ → chase NULL; zero-BIP → hard-hit/barrel NULL (never a measured 0).

### SB-1 `synthetic_batter(df, label, opponent, pitcher)` — NEW-PROVISIONAL
Selects the pitches a locked pitcher threw, optionally vs one batting team, and tags the frame as a
composite batting entity. **Semantic guard:** output is a claim about the *pitcher's allowed
production*, never about an individual opposing batter; consumers must keep the entity label.

### Floor derivation (HD-1) — spec
`floor(grain) = min(plate_apps of Noles at that grain)`, computed after KF-1, receipted in
`dp_uc35_floor_derivation*.csv`, applied as `plate_apps > floor` (strict, matching the submitted
snippet's `> criteria` semantics). Never hand-keyed; changes automatically if the data window moves.

## EDA notes that shaped design

- Nola has **no 2025 Marlins meeting** → season grain is 11 rows, not 12; the constant (career
  aggregate) is unaffected but P5 is falsified.
- Harper-vs-Alcantara season cells are all <15 PA → season receipt ships, but the design pins the
  54-PA career line as the only citable H2H number.
- The 7/28/2026 game (823838) contains **both** subjects' starts — receipted as the duel anchor.
- 2020 (60-game season) is a structural small sample at every grain; flagged, not excluded.

## Figure/dashboard design contract

Fig 1 box plot: population = `boxplot_population.csv` only; constants = career receipts; stars =
`harper_mia_seasons.csv`. Fig 2 facets: per-stand floors from `floor_derivation_stand.csv`.
Figs 3–4: id-keyed rankings; names only per O-10 rules. Dashboard: same receipts inlined at build,
Chart.js vendored, `chart()` degradation helper, cards render from full-precision career receipts
(not the 4dp headlines — double-rounding is a D4-family failure and was caught in QA).
