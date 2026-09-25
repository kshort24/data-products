# 02 · Engineering Design: `uc-pps-033`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model

```
phils_2015..2026.parquet ──┬─ role=pitching, pitcher=680742 ─(PHI)──┐
                           └─ role=batting,  pitcher=680742 ─(VS_PHI)┤  CF-1 career_frame
data/opponents/bowlan.parquet ─ pitcher=680742 ────────────(FILE)────┤  precedence PHI > FILE > VS_PHI
                                                                     │  game_type == 'R'; 1,818 pitches; 0 dup keys
                                                                     ▼
            ┌──────────── pitcher-season (SR-1 recap, AR-2 arsenal, rate tests)
   pitch ───┼──────────── appearance (US-1 log → usage summary, RC by entry state)
   grain    ├──────────── pitch-of-outing bucket (VE-1)
            └──────────── count state (CS-1)

phils_* role=pitching (all RHP) ── KP-1 population (pitcher-season, ≥100 PA, n=198)
                                └─ staff four-seam frame (ex-2017) → ride rank, centroids, drill densities
out/dp_uc47_population_graded.csv ── read-only inheritance (2025, 2026 grades; rank recomputed on efc_score)
```

**One frame, many groupbys.** Every Bowlan number is a groupby of CF-1, so the recap, arsenal, usage and ledger cannot drift apart. The comparison populations (KP-1, staff four-seams) are separate frames with their own declared filters, and they are never joined to CF-1.

**Joins.** The only merges are the client's own recap merges (1:1 on `player_name, game_year, p_throws`) and display names onto pitcher ids (m:1). `join-validator`: fan-out-free by construction. Family B rebuilds CF-1 with plain pandas and matches its row counts per season.

## 2 · EDA findings that changed the build

| # | Finding | Consequence |
|---|---|---|
| E-1 | Every pitch type gained velocity 2025 → 2026 (FF +1.5, SI +1.0, SL +1.0, CH +2.1) | PC-1 is a whole-arsenal hypothesis, not a four-seam one |
| E-2 | 2026 outings are shorter (16.4 vs 21.4 pitches), which could explain velocity by itself | **VE-1**: velocity by pitch of outing. Pitches 1–10 are +1.5 mph, so the gain is in the arm |
| E-3 | First-pitch strikes **fell** (67% → 60%) while walks fell | CA-2 added as a hypothesis that the data **contradicts** |
| E-4 | Four-seam whiff fell (.435 → .370) while its xwOBA on contact collapsed (.446 → .321) | The report's "the four-seam changed jobs" framing |
| E-5 | Sinker whiff .176 → .055, xwOBAcon .187 → .393; sweeper −6.1 RV/100 on 77 pitches | WA-1 / WA-2 watch items |
| E-6 | Runs per PA rose while wOBA fell | Decomposed by entry state: 15 dirty entries produced 13 of 30 runs |
| E-7 | 2017 Phillies RHP four-seam ride is 17.3 in against 14.8–15.9 in every other season (z = 5.1) | DQ-11. The client's 2017 exclusion is kept and justified |
| E-8 | `pitch_mix` rounds `pfx_*` to 0.1 ft → vert in 1.2-inch steps | **O-25**. SR-1 governed mode reads unrounded means |

## 3 · Metadata map (physical → CDE)

| Physical column | CDE | Map | Note |
|---|---|---|---|
| `pitcher` | Pitcher (MLBAM) | exact | entity lock |
| `player_name` | **AMBIGUOUS** | — | batter on batting-role rows (uc-pps-032 NR-1); display only |
| `game_type` | Game Type | exact | 'R' only |
| `phillies_role` | Phillies Role | exact | source tag PHI / VS_PHI |
| `release_speed` / `release_spin_rate` | Pitch Velocity / Spin Rate | exact | |
| `pfx_z`, `pfx_x` | IVB ("ride/carry/vert") / Horizontal Break | exact ×12 → in | unrounded (O-25) |
| `description` | Swing / Whiff | exact | SWINGS/WHIFFS inherited |
| `zone` | Strike Zone (1–9 in, 11–14 out) | exact | in-zone FF whiff uses `zone < 10` (client) |
| `events` | PA outcome | exact | PA / K / BB / HR |
| `bat_score`, `post_bat_score` | Runs Created inputs | exact | house term |
| `delta_run_exp` | Run Value | exact, sign flipped | RV/100 pitcher POV |
| `estimated_woba_using_speedangle` | xwOBA on contact | exact, BIP only | pitch-level use quarantined |
| `balls`, `strikes` | Count State (CS-1) | derived | |
| `on_1b/2b/3b` (first pitch) | Entry runners (US-1) | derived | first pitch by sort, not `first()` |
| `inning`, `outs_when_up` (first pitch) | Entry inning / outs | derived | |
| `pitcher_days_since_prev_game` | Rest days | exact | |
| `stand` | Batter hand | exact | platoon mix |
| `game_pk` | Appearance | exact | games = nunique |

## 4 · DQ rule design (handed to `05`)

19 rules, each with its grain declared. Three are designed to WARN permanently: DQ-07 (house frame is not MLB-wide), DQ-16 (one NULL zone, so the in-zone rate has D-7/O-13 exposure), and DQ-17 (2023/2024 are 14 and 17 PA).

## 5 · Dashboard specification

| Element | Question it answers | Control | Failure mode it guards against |
|---|---|---|---|
| Box line (header) | What was his season? | — | burying the result under the method |
| Persona lens | What does this mean for *my* job? | 7 chips; remembered per viewer | one narrative that fits nobody |
| Ch. 1 The buy | What did the Phillies acquire? | — | reading the trade through ERA |
| Ch. 2 The tick and a half | Is the velocity real, and is it arm or role? | Gemini grid in a detail panel | role effect mistaken for arm gain |
| Ch. 3 The carry that stayed + **drill-through** | How rare is the ride on this staff? | click a centroid or pick a pitch | the client's "DT" left unbuilt |
| Ch. 4 Rebuilt by platoon | What changed in the arsenal? | table | single-pitch RV read at face value (note printed) |
| Ch. 5 Fastball when it matters | How did pitch calling change? | rate-test table | "elite" asserted on an unsettled change |
| Ch. 6 The eighth-inning job + **timeline** | How was he used, and was there a warning before 9/17? | hover every appearance | the injury read as data |
| Your notebook, graded | Which of my claims held? | verdict filter | overwriting the client instead of grading him |
| Persona action ledger | Which actions leave a signature? | follows the lens | hypotheses presented as facts |
| Receipts | Can I trust it? | — | — |

Theme: follows the viewer, and the toggle stamps `data-theme`. Charts re-template on every change (`plotly_white` ↔ `plotly_dark`), with navy swapped to a light blue on dark for contrast. The browser computes nothing; the drill-through draws receipt centroids and pre-binned densities only.
