# 02 · Engineering Design — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `data-architect`, `eda-agent`, `join-validator`, `metadata-mapper`, `data-dictionary`,
`dq-rule-definer`, `data-tagger`, `dashboard-specifier`

## Data model

Three grains, and the whole build turns on keeping them apart.

| Layer | Grain | Key | Source | Rows |
|---|---|---|---|---|
| L0 pitch (MLB) | one pitch | `game_pk` + `at_bat_number` + `pitch_number` | `phils_2026.parquet`, filtered `game_type=='R'` ∧ `phillies_role=='pitching'` | 22,021 |
| L0 pitch (AAA) | one pitch | same | `lhvp26.parquet`, filtered `game_type=='R'` | 20,319 (348 subject) |
| L0 pitch (opponent-facing) | one pitch | same | `phils_2026.parquet`, `phillies_role=='batting'` | 24,656 — used **only** for the opposing starter and the Braves order |
| L1 appearance | one pitcher × one game | `pitcher` + `game_pk` | `appearance_summary(L0)` | 632 |
| L2 arm-season | one pitcher × one season | `pitcher` + `game_year` | `pitcher_season_workload(L1)` | 26 relievers |
| L3 target-game ledger | one pitcher × one target date | `pitcher` + `target_game` | `ledger_for(T)` | 9 × 2 framings |

**A doubleheader produces two L1 rows** because `game_pk` differs — inherited behaviour, documented in the
governed kernel, and relevant here because the anchor game was an eleven-inning single game, not a twin bill.

### Joins and the fan-out check (`join-validator`)

| Join | Type | Fan-out risk | Result |
|---|---|---|---|
| L1 ← `mcgs(['pitcher','game_pk'])` | left, 1:1 on the composite key | duplicate (pitcher, game) rows would double-count | **0 duplicates** — verified, family B |
| L1 → L3 (`avg_pitches` from L2) | left on `pitcher` | a pitcher with no prior 2026 relief outing gets a null average | Holman is exactly this case; BS-1's null rule returns GREEN + `debut` rather than 0 |
| Braves order ← name map from `des` | left on `batter` | a batter with no parseable `des` row loses his name | 9 of 9 resolved; asserted in the build |
| L0 opponent ← `nresults(['batter_id'])` | — | **`nresults` cannot group on `batter`** (defect D-9) | aliased to `batter_id` build-locally |

### Why capacity sums over arms, not slots

The single most important modelling decision. A reliever assigned innings 3 and 4 does not make two
appearances; he makes one. Summing an arm's expected batters faced once per *inning* would have produced a
capacity of 38.6 BF for the client's script and no finding at all. Summing once per *arm* produces 29.7 and
the finding. This is asserted at build time and re-derived by a second code path in verification family B.

## EDA findings that shaped the build (`eda-agent`)

1. **`is_start` comes back as `pd.NA` for every reliever** on a single-team frame — 484 of 632 appearances.
   This is defect **D-8**, found here, and it is the reason the L2 layer silently returned an empty DataFrame
   on the first run. Remediated build-locally; the locked function is untouched. Full write-up in `05`.
2. **The anchor game went eleven innings.** The design initially assumed a nine-inning anchor; the extra-inning
   shape is why five relievers appear and why three of them threw nine pitches. Innings 10–11 also mean
   `innings_spanned` and `inning_exited` exceed 9, which the L1 grain handles but the regulation-game
   benchmark must exclude — hence `max_inn == 9` on the benchmark filter.
3. **The benchmark is not 27 batters.** 106 regulation Phillies games in 2026 took a median of 37 batters
   faced and 147 pitches from the staff, IQR 34.2–40.0. Pricing the script against 27 would have made it look
   comfortable. This single number is what turns a plausible plan into a measurable shortfall.
4. **Bullpen-game precedents disagree with the average.** The two 2026 games in which no Phillies pitcher
   faced more than 12 batters ran **5.0** and **7.1** BF per arm, against a season-average reliever outing of
   ~4.2. Relievers in bullpen games are asked for more than their norm. That observation is what forced the
   second capacity mode.
5. **Holman's arsenal is handedness-split, not handedness-adjusted.** The lead pitch inverts: splitter 44.1%
   vs LHB, four-seam 45.0% vs RHB. A pooled mix table would have shown a balanced three-pitch mix and hidden
   the plan entirely. Grain forced to `stand × pitch_type` throughout.
6. **Statcast horizontal-break sign flips with the pitcher's hand.** Derived empirically per standing rule
   O-15, not assumed: for this RHP the splitter carries the most negative `pfx_x` (−12.0") and the slider the
   least (−1.2/−2.4"), so **negative is arm-side**; for LHP Mayza the sinker is **+14.4"**, the mirror. Every
   break figure in the report is labelled with the batter side it applies to.
7. **AAA tracking is thinner than MLB tracking, but not by as much as feared.** 67 of 73 batted balls carry
   exit velocity (91.8%). Still enough O-8 exposure to keep `hard_hit_rate` out of the deliverable.
8. **`launch_speed` is populated on 61 non-batted-ball rows** (fouls) — standing defect O-3. Every
   exit-velocity filter in the build is gated on `type == 'X'`.

## Design change forced by EDA

The first design shipped a single BS-2 number: 29.7 vs 37, "2.4 innings short." Finding 4 above showed that
relievers in bullpen games routinely exceed their season average, which makes the single-number framing an
overstatement dressed as precision. **BS-2 was re-specified with two modes** — average and ceiling — and the
headline was rewritten from "the script is short" to "the script is ceiling-dependent, and its largest ceiling
belongs to the debutant." The second framing is smaller, more defensible, and more useful. (This is the
`uc-pos-016` DC-1 lesson — size a finding before amplifying it — applied at design time rather than after
delivery.)

## Metadata mapping (`metadata-mapper`)

| Physical column | Glossary term | Status | Note |
|---|---|---|---|
| `pitcher` | Pitcher (MLBAM id) | exact | the entity lock; never a name |
| `batter` | Batter (MLBAM id) | exact | aliased to `batter_id` in this build (D-9) |
| `game_pk` | Game | exact | doubleheader-safe |
| `pitch_number`, `at_bat_number` | Pitch, Plate Appearance | exact | |
| `inning`, `inning_topbot` | Inning, Half-inning | exact | `inning_topbot` drives `phillies_role` upstream |
| `n_thruorder_pitcher` | Times Through the Order | exact | constant 1 for every Mayza pitch in 2026 — OP-1 cannot discriminate |
| `release_speed`, `release_spin_rate`, `release_extension` | Velocity, Spin Rate, Extension | exact | |
| `pfx_x`, `pfx_z` | Horizontal Break, Induced Vertical Break | exact **with a sign caveat** | reported ×12 as inches; sign is hand-relative (O-15) |
| `plate_x`, `plate_z` | Plate Location | exact | catcher's view |
| `zone` | Statcast Zone | exact | >9 is out-of-zone; NULL counts as in-zone (D-7/O-13) |
| `description`, `events`, `type` | Pitch Result, Play Outcome, Pitch Class | exact | |
| `stand`, `p_throws` | Batter Side, Pitcher Hand | exact | **per plate appearance**, not a fixed attribute — one Braves hitter flips |
| `launch_speed` | Exit Velocity | exact, **conditional** | valid only where `type=='X'` (O-3) |
| `wBB`…`wHR` | wOBA weights | exact on MLB, **absent on AAA** | DQ-5; not imported |
| — | `bullpen_availability_tier` | **NEW, provisional** | no prior glossary term for "an arm is down" |
| — | `script_capacity` / `script_coverage_risk` | **NEW, provisional** | |
| — | `multi_inning_propensity` | **NEW, provisional** | |
| — | `opener_tto_delta` | **NEW, provisional, could not execute** | |

## DQ rules specified (`dq-rule-definer` — implemented and scored in `05`)

| Rule | CDE | Dimension | Threshold |
|---|---|---|---|
| R1 | `pitcher` | validity | every subject resolves to ≥1 row by MLBAM id; zero name filters in the build |
| R2 | `game_pk`+`at_bat_number`+`pitch_number` | uniqueness | 0 duplicates |
| R3 | `game_type` | consistency | `{'R'}` only on both frames |
| R4 | `pitch_type` | completeness | null rate < 0.5% |
| R5 | `game_date` max | timeliness | ≥ target − 1 day |
| R6 | wOBA weights | comparability | present on MLB, **absent** on AAA, never imported across |
| R7 | `launch_speed` | validity | read only where `type=='X'` |
| R8 | opponent identity | accuracy | flagged WARN unless independently confirmed |
| R9 | every report figure | traceability | recomputable from a shipped receipt (family F) |

## Dashboard specification (`dashboard-specifier`)

**Judgment: build it.** The question is a what-if ("does this script hold?"), and a what-if needs a control
surface. Spec as delivered:

- **Primary surface: the inning rail.** Nine slots, 1–9, each showing its arm, his availability tier as a
  top-edge stripe, and the batters his outing is expected to deliver. Innings are a genuine sequence, so the
  numbering carries information rather than decorating.
- **Two toggles that change the arithmetic, not the styling.** *Which night was "last night"* (D+1/D+2)
  re-tiers every arm; *price each arm at* (average outing / season high) switches BS-2 capacity mode. Both
  are the escalations from `01` made operable instead of merely disclosed.
- **Live coverage meter** with the 37-BF requirement drawn as a fixed mark, so a script that does not reach
  it reads at a glance rather than requiring arithmetic.
- **Presets:** the client's script, the revised script, and empty — so the two can be compared in one click.
- **Holman pitch map** as hand-drawn SVG with handedness and pitch-type filters. No charting library:
  a plate-view scatter with a strike-zone overlay is not a library shape, and vendoring nothing sidesteps the
  standing **O-19** (merge() deletes Chart.js tick callbacks) and the vendor-don't-CDN rule at once.
- **No external code.** Google Fonts is the only external host; the assertion is checked, not assumed
  (verification family E).
