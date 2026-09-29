# 02 · Engineering Design: `uc-pos-018`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model (`data-architect`): BF-1, one frame

```
phils_2015..2026  (prec 0) ─┐
subject files     (prec 1) ─┤   keep rows where batter ∈ LINEUP_IDS  or  pitcher == 519242
atlp26 / atlo26   (prec 2) ─┼─► (Phillies logs: + every Phillies batting row)
other MLB opp.    (prec 3) ─┘   sort(prec, src) → drop_duplicates(PITCH_KEY, keep='first') → apply_woba_weights
                                                  │
                    ┌─────────────────────────────┼──────────────────────────────┐
             batter_frame(H, id)            sale_frame(H, years)            H (lineup × Sale)
             game_type == 'R'               game_type == 'R'                lineup aggregate
```

- **Grain:** one row per pitch; key `(game_pk, at_bat_number, pitch_number)`.
- **Why one frame:** the client's three cells built three different frames three different ways (`po26`, `pos`+`nphl`, `bh`). Every table here is a groupby of the same frame, so the Schwarber number and the lineup aggregate cannot disagree (DQ-17).
- **Why precedence:** the same pitch can sit in a Phillies log, a batter file and a pitcher file with different `player_name`. The Phillies log wins, then the subject's own file, then the Braves file, then the rest. The result is deterministic. It does not depend on file-name order (the O-26 trap).
- **Minor-league tiers are never read** into the MLB frame.

## 2 · EDA (`eda-agent`): what shaped the product

| # | Finding | Consequence |
|---|---|---|
| E-1 | LHB vs Sale 2026: **24 PA, 1 hit, .066 wOBA**; career LHB .217 (52 PA) vs RHB .278 (111 PA) | Bottom line 2–3: the right side carries |
| E-2 | Sale's wOBA by time through the order is flat (.262 / .254 / .258); HR rate 1.2% → 2.4% | Bottom line 4; answers the client's "jump on him early" |
| E-3 | Sale's arsenal splits by side: LHB SL 39% / SI 33% / FF 27%; RHB FF 46% / SL 40% / CH 13% | Every card's Plan line reads the batter's side |
| E-4 | Turner: away-third BIP pulled 31%, oppo 37%, .241 wOBA; inner-third pulled 65%, .336 | HP-05 "does not hold as worded" |
| E-5 | Bohm ≥ .345 wOBA vs LHP in all 7 seasons with 40+ PA; away pitches oppo 42% | Bohm as "the matchup bat"; season chart |
| E-6 | Realmuto: 0 barrels in 74 PA vs LHP fastballs in 2026; xwOBA .320 vs wOBA .261 | "At people, not over them"; season chart |
| E-7 | Sosa: 48% chase vs LHP in 2026; 58% on LHP changeups 2024–26; .218 wOBA vs Sale | "Sale has figured him out"; pitch-group chart |
| E-8 | Hill: vs LHP fastballs .362 / 14% barrels; breaking 42% whiff; 5 of 6 BIP vs Sale hard-hit | "Fastball or nothing" |
| E-9 | Stott: 2026 vs LHP .325 (up from .274/.257) with 25% hard-hit; LHP breaking 2024–26 .223 / 11% HH; 0 PA vs Sale in 2026 | "Rebound without damage" |
| E-10 | De La Cruz: 41 PA vs LHP in 2026; pooled 2024–26 breaking .224 / 42% chase | Card built on the pooled split; THIN printed |

## 3 · Join validation (`join-validator`)

| Join | Keys | Cardinality | Check |
|---|---|---|---|
| IC-1: `nresults` ⋈ `xwoba_pa` ⋈ `whiff_rate` ⋈ `chase_rate` ⋈ `barrel_rate` ⋈ `hard_hit_rate` | the level keys | 1:1, LEFT | Row count of the card = row count of `nresults` at every level used (harness C recomputes without joins) |
| Sale arsenal: `groupby(pitch_type)` ⋈ `index_card(['pitch_type'])` | `pitch_type` | 1:1, LEFT | Harness D |
| Band × value: `direction_rate(['hitter','h_band'])` ⋈ `nresults(['hitter','h_band'])` | `h_band` | 1:1, LEFT | Harness E |

Known inherited behaviour, **measured and left alone** (standing rule: shipped kernels are not edited): `whiff_rate` inner-joins (D-1/D-2, drops zero-whiff groups → NaN whiff on a card, never 0); `hard_hit_rate` counts untracked BIP as not-hard-hit (O-8, 1 BIP for five hitters, ≤ 0.5 pp; `out/dp_uc50_method_variance.csv`).

## 4 · Metadata mapping (`metadata-mapper`)

| Physical | Meaning here | Note |
|---|---|---|
| `batter` | MLBAM id of the hitter | **D-50-1:** cannot be a `get_stats` level (renamed to `pitches` by `measure_calcs`). A display key `hitter` is used instead |
| `player_name` | Pitcher in pitcher-keyed files (`sale`, `atlp26`), batter in batter-keyed files | Never used to select |
| `n_thruorder_pitcher` | Statcast time through the order | TT-1 caps at "3+" |
| `plate_x` | + = first-base side, catcher's view (E-7) | HL-1 flips it for LHB |
| `hc_x`, `hc_y` | Hit coordinates | Only through `dp_uc46.derive_loc` (PA-L1) |
| `woba_value`, `woba_denom` | Savant's wOBA credit | Used only in XW-1's non-BIP arm and the MV-1 disclosure; published wOBA is house wOBA |
| `estimated_woba_using_speedangle` | xwOBA on contact | XW-1 BIP arm; 0 fallbacks in 2026 cards (DQ-11) |
| `arm_angle` | Statcast arm angle | Sale ≈ 11° median, printed on the release panel |

## 5 · Product specification (`dashboard-specifier`)

**Index card** (11 × 6.6 in, one per hitter): navy header (slot, name, bats, game) with a red rule; red one-line tag; five tiles (2026 vs LHP wOBA, xwOBA + K%, career vs Sale wOBA + PA/THIN, career vs Sale slash, last 30 days wOBA); a lede (≤ 6 sentences, every number bound to a receipt); a **SALE** line; a **PLAN** line; one chart chosen by story:

| Chart | Hitters | What it shows |
|---|---|---|
| `band` | Turner | 2026 vs LHP: where the pitch was (inner/middle/away) → where the ball went (pull/straight/oppo), with wOBA by third |
| `spray` | Schwarber | Every BIP vs Sale, hits coloured (the client's requested spray, governed) |
| `rank` | Harper | OPS vs every LHP faced 20+ times, Sale in red (the client's cut, as a picture) |
| `season` | Bohm, Realmuto | wOBA and xwOBA vs LHP by season, career-vs-Sale line |
| `pitchgroup` | Hill, De La Cruz, Stott, Sosa | His wOBA vs LHP by pitch group beside Sale's 2026 usage to his side; whiff and chase under each |

**Notecard** (Letter landscape): Sale strip (five tiles), the single rule, nine rows (slot, name, bats, 2026 vs LHP wOBA/xwOBA, vs Sale PA/slash/wOBA, tag, short plan), the lineup aggregate line.

**Sale section:** the client's three plots in one figure (movement in inches with the client's four-number subtitle, location by side sized by usage, release points with arm angle), a TTO chart, and an arsenal-by-side table.

**Render QA** (C-6, headless PNG review before shipping) caught three defects: the direction legend collided with the footer; the movement axis said arm side is "toward a RHB" (it is *away*, E-7); and the notecard's plan column took the first sentence of the plan, which was sometimes a fact rather than an instruction (a `short` plan field was added).
