# 03 · Governance: `uc-pos-018`

Agents: `kpi-calculator` · `technical-lineage-builder` · `business-glossary-agent` · `privacy-watchdog` · `data-tagger` · `version-controller`

## 1 · Rule-1 search (before anything new was written)

| Need | Search | Found | Decision |
|---|---|---|---|
| Slash line, wOBA, K/BB | `def nresults` | `dp_uc44_kernel` (verbatim notebook) | **Import** |
| Whiff, chase | `def whiff_rate`, `def chase_rate` | `dp_uc44_kernel` | **Import** |
| Barrel, hard-hit | `def barrel_rate`, `def hard_hit_rate` | `barrel_rate.py` (MLB root), `dp_uc44_kernel` | **Import** |
| Pull / straight / oppo, AIR% on pulls, LD by direction | `hit_direction`, `direction_rate`, `pull_air_rate`, `bb_type_profile` | `dp_uc46_kernel` (uc-pos-017, certified) | **Import from the control plane**, sha-pinned |
| xwOBA on contact | `def xwobacon` | `dp_uc48_kernel` | **Import** (re-export) |
| xwOBA per PA | `xwoba`, `woba_denom` | none (only `xwobacon`; `xwobas` in the notebook is UNUSED/legacy) | **New: XW-1** |
| Location thirds | `zone_cell`, `location`, `horizontal` | `dp_uc42a` PM-2 (in-zone Statcast cells only) | **New: HL-1** (needs out-of-zone pitches too) |
| Pitcher rank among a hitter's LHP | `lhp_rank`, the client's cell 151 | client code only | **New: LR-1** (the client's method as a function) |
| Time through the order | `thruorder`, `tto` | none | **New: TT-1** |
| Client name frame | `nphl_name_frame` | `dp_uc49` NF-1 (one name, fixed column set) | **Generalised: NF-2** (many names, one pass) |

## 2 · KPI specifications (`kpi-calculator`), written before code

### XW-1 · `xwoba_pa(level, df)`: PA-denominated expected wOBA
- **Plain language:** what a hitter's wOBA "should" be given how he hit the ball, counting strikeouts and walks at face value.
- **Formula:** Σ over PA ends with `woba_denom > 0` of (`estimated_woba_using_speedangle` if BIP and present, else `woba_value`) ÷ Σ `woba_denom`.
- **Population:** PA-ending pitches; `woba_denom` excludes IBB and sacrifice bunts (Savant convention).
- **Edge cases:** a BIP without an expectation falls back to its actual `woba_value` and is counted in `xw_fallback` (0 in every 2026 card, DQ-11). Empty group → NaN, never 0.
- **CDEs:** `estimated_woba_using_speedangle`, `woba_value`, `woba_denom`, `type`.
- **Note:** wOBA and xwOBA therefore have slightly different denominators (house PA vs `woba_denom`). A card compares them as levels, not as a difference to three decimals.

### HL-1 · `horizontal_band(df)`: Inner / Middle / Away
- **Formula:** `x_rel = plate_x` (RHB) or `-plate_x` (LHB); Away if `x_rel > 0.83/3`, Inner if `< -0.83/3`, else Middle. Out-of-zone pitches keep their side.
- **Grain:** pitch; used on classifiable BIP. **Floor:** FL-1 (25 BIP) per published cell; cells below the floor carry an asterisk and are never quoted as findings.
- **CDEs:** `plate_x`, `stand`. **Sign convention:** + = first-base side (E-7), asserted indirectly by `dp_uc46.assert_spray_convention` on the same frame.

### LR-1 · `lhp_rank(df, target, min_pa=20, metric='ops')`
- **Plain language:** among every lefty this hitter has faced at least 20 times, where does Sale rank (1 = the worst OPS for the hitter)?
- **Population:** regular-season PAs vs LHP, 2015–2026, `nresults(['pitcher'])`, `plate_apps ≥ 20` (the client's `> 19`).
- **Returns:** rank, population size, the target's value, the population median. If the target is under the floor, rank is NaN and the card prints "— (n PA < 20)".

### TT-1 · `tto_split(level, df)`
- `nresults` with an added `tto` dimension from `n_thruorder_pitcher` (1, 2, 3+), plus XW-1. No new arithmetic.

### IC-1 · `index_card(level, df)`
- A composition only: `nresults ⋈ xwoba_pa ⋈ whiff_rate ⋈ chase_rate ⋈ barrel_rate ⋈ hard_hit_rate`, LEFT on level keys. Missing counts fill to 0; rates stay NaN.

### NF-2 · `nphl_name_frames(names)` and `client_pos()`
- Reproduce `nphl[nphl.player_name == name]` exactly as `get_nphillies_data()` builds it (all opponent files, sorted, keep-first dedup), and `pos` exactly as `get_phillies_data()` returns it (all game types). **HP family only.**

### BF-1 · `load_house()`
- The model in `02` §1. Precedence dedup; minor-league tiers excluded; wOBA weights applied after dedup.

## 3 · Technical lineage (`technical-lineage-builder`)

| Published object | Source columns | Transform chain | Receipt |
|---|---|---|---|
| Card tiles: 2026 vs LHP wOBA / xwOBA / K% | events, weights, `woba_*`, `estimated_woba…` | BF-1 → `batter_frame` → `year==2026 & p_throws=='L'` → IC-1 | `dp_uc50_by_hand.csv` |
| Career vs Sale line | same + `pitcher` | BF-1 → `batter_frame` → `pitcher==519242` → IC-1 | `dp_uc50_sale_career.csv` |
| LR-1 rank | events, `pitcher`, `p_throws` | BF-1 → `p_throws=='L'` → `nresults(['pitcher'])` → floor → sort | `dp_uc50_rank.csv`, `dp_uc50_rank_pop.csv` |
| Pitch-group splits | `pitch_type` | group map → IC-1 by `pitch_group`, windows 2024–26 and 2026 | `dp_uc50_pitch_group.csv` |
| Direction by third | `hc_x`, `hc_y`, `stand`, `plate_x`, `bb_type` | `dp_uc46.build_bip` → HL-1 → `direction_rate` ⋈ `nresults` | `dp_uc50_band.csv`, `dp_uc50_lhp26_bip.csv` |
| Last 30 days | `game_date` | `game_date ≥ 2026-08-28` → IC-1 | `dp_uc50_last30.csv` |
| Sale arsenal / by side | `pitch_type`, `release_*`, `pfx_*`, `plate_*`, `arm_angle` | `sale_frame([2026])` → groupby ⋈ IC-1 | `dp_uc50_sale_arsenal*.csv`, `dp_uc50_sale_pitch_extract.csv` |
| Sale TTO | `n_thruorder_pitcher` | TT-1 | `dp_uc50_sale_tto.csv` |
| Lineup aggregate | `stand` | lineup × Sale → IC-1 by LHB/RHB/all, career and 2026 | `dp_uc50_lineup_agg.csv` |
| Every prose number | the receipts above | `dp_uc50_headlines.json` → `dp_uc50_narratives.py` | harness F |

## 4 · Defects and dispositions

| ID | What | Disposition |
|---|---|---|
| **D-50-1** (new) | `measure_calcs` renames `batter` → `pitches`, so `nresults(['batter'], df)` raises | Worked around (display key `hitter`); upstream fix proposed (E-1) |
| **O-26** (second exposure) | Name-filtered `nphl` loses 10 Sale 2026 pitches (469 all-years) to keep-first dedup | HP-10; E-2 |
| **MV-1** (new) | Savant `woba_value` credits reached-on-error (0.9) and catcher's interference; house wOBA does not. Gap ≤ .002 on the Sale lines, up to .029 on 2026 vs LHP (Sosa, 4 ROE) | House wOBA published; gap receipted in `dp_uc50_method_variance.csv`; E-4 |
| **O-8** (carried) | Untracked BIP counted as not-hard-hit | 1 BIP for five hitters; ≤ 0.5 pp; receipted |
| **D-1/D-2** (carried) | `whiff_rate` inner join | Zero-whiff groups show NaN, never 0 |
| **E-7** (carried) | `plate_x` sign in PM-1's docstring | Used correctly in HL-1; caught the same mistake in our own axis label during render QA |
| **Harness defects** (found and fixed before certification) | nullable-Float comparison in my own hard-hit recompute; oppo classifier not excluding pull; a hardcoded .538 | Fixed in `dp_uc50_verification.py`; noted in `05` §4 |

## 5 · Privacy & tagging (`privacy-watchdog`, `data-tagger`)

Public Statcast performance data on professional players. No health, injury or availability inference. The Harper quote is the client's carry-in. **Classification: Internal** (advance meeting). External publication would be permissible after DPO review. No other club's hitters are ranked; Braves appear only as Sale.

## 6 · The client's cards, graded (HP family)

| # | Claim (client) | Client value | Client method today | Governed | Verdict |
|---|---|---|---|---|---|
| HP-01 | Turner vs LHP 2026 "pretty bad" | printed | .266 wOBA / .581 OPS / 249 PA | .275 wOBA / .324 xwOBA / 235 PA | Holds on results; process is league-average. His frame keeps S/E rows |
| HP-02 | AIR% on pulls | 44% | 43.0% | 43.0% | Holds; value moved |
| HP-03 | LD rate, straightaway | 30% | 28.8% | 28.8% | Holds; value moved |
| HP-04 | BA oppo | .196 | .192 | .192 | Holds; value moved |
| HP-05 | "Too many pulls on pitches away from him" | narrative | — | away third: 31% pull, 37% oppo (68 BIP); inner third 65% pull | **Does not hold as worded** |
| HP-06 | Schwarber vs Sale .327 / .779 / 27 / .520 | same | same | same | **Reproduced** |
| HP-07 | 1 in 5 barrels; < half hard-hit; 5 hits | 20% / <50% / 5 | 20.0% / 46.7% / 5 | same | **Reproduced** (15 BIP, answering "(or 15 BIP?)") |
| HP-08 | Harper .100 OPS, by far the worst (20+ PA) | .100 | .190 (next worst .538) | .190, #1 of 20 (next worst .478) | Holds in direction; value corrected |
| HP-09 | Sale subtitle | cell | 96.1 / 38.4% / 18.00 in / 30.3% | 96.1 / 38.2% / 18.0 in / 30.3% | Reproduced; SI run quantised (pitch_mix rounds pfx_x before ×12) |
| HP-10 | Name-filtered Sale 2026 frame is complete | implicit | 2,565 pitches | 2,575 | **O-26 exposure** |
| HP-11 | Sosa vs Sale (cell 137) | 23 / .451 / .218 | same | same | **Reproduced** |
| HP-12 | Hill 2026 barrel rate (cell 152) | .108 (14/130) | .108 (14/130) | .105 (14/133) | Reproduced (client method); governed differs by 3 BIP |

HP-08's second-worst differs between frames (.538 client, .478 governed: Kershaw, 23 PA). The ranking of Sale is the same in both.

## 7 · Versioning (`version-controller`)

- **v1.0.0**, anchor 2026-09-27 (Game 162). The build refuses any other regular-season anchor.
- **Parents pinned:** `dp_uc44_kernel.py` `a2c119096db2`, `dp_uc46_kernel.py` `a45ac9a76395`, `dp_uc48_kernel.py` `0f63857a1032`, `barrel_rate.py` `6282f090394a`.
- **Build files** (sha256, first 12): kernel `8084cb172d0c` · build `08d728d51efa` · narratives `2e2072cab5d8` · figs `2c8922ebfc24` · report `688b25481342` · pdf `6d271de49072` · verification `a3b64cde59c4`.
- **v1.1.0 trigger:** any postseason PA vs Sale (Game 1 itself) → the H2H lines gain a postseason row (never blended into regular season) and the plans are graded against what happened.
