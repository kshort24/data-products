# 02 · Engineering Design — `uc-pps-032`

Agents: `data-architect` · `eda-agent` · `join-validator` · `metadata-mapper` · `dashboard-specifier`

## 1 · Data model

```
phils_2015..2026.parquet ─┐                          ┌─ population mask   n ≥ 100 FF, 2018–26, RHP   (405)
                          ├─ FR-1 universe U ── AF-2 ─┤
data/opponents/*.parquet ─┘   (pitch grain,           │  pitcher-season frame g (grain: game_year × pitcher)
  128 files, level gate,       1,219,975 rows,        ├─ subject mask      n ≥ 50 FF   (graded, THIN if < 100)
  precedence dedup)            0 dup keys)            ├─ cohort mask       pitcher ∈ COHORT (6 ids)
                                                      ├─ staff mask        pitched for PHI in 2026 (volume = PHI rows only)
                                                      └─ candidate mask    ¬staff, 2025–26; RANKED n ≥ 100 / WATCH 50–99
```

**One grain, several masks.** Every grade is computed once, on `g`, against the population mask. Cohort,
staff, board and watch list are *filters* of the same graded frame — so the cohort's grades and the board's
grades cannot drift apart, and the population a subject is graded against is identical for all of them.

**No joins across grains.** The only merges are (a) pitcher-season totals onto pitcher-season FF aggregates
(1:1 on `game_year, pitcher`), and (b) display names onto ids (m:1). `join-validator` confirmed both are
fan-out-free by construction; family B re-derives the universe via an independent concat-then-dedup path and
gets the same row count.

**Precedence dedup.** Phillies logs win over `nphl`; within `nphl`, a pitcher-keyed row (FILE/TEAM) wins over
an INCIDENTAL copy of the same pitch — so `row_frame` reflects the most complete source that holds the pitch.

## 2 · EDA findings that changed the build

| # | Finding | Consequence |
|---|---|---|
| E-1 | League four-seam velocity rises **+0.164 mph/season** (p = .0001) and spin **+8.26 rpm/season** (p = .003) across the population; ride, whiff, run value flat | SG-6: drift-adjust velo and spin to 2026 terms; leave the rest |
| E-2 | Run value per 100 has split-half reliability **0.21** at ~581 pitches (k ≈ 1,084); whiff 0.78 on swings (k ≈ 56); shape metrics > 0.99 (k < 1) | SG-7: shrink whiff and RV toward the population; do not shrink shape |
| E-3 | Ride and run value are non-normal (Shapiro p < .001); velo, spin, whiff normal | Rank-derived twin grades published; skew flag never fires |
| E-4 | Duran's four-seam: velocity z ≈ +2.5, ride and spin z ≈ −1 to −2 (2026 grades 40 and 30) | Axes must be graded separately before combining — the case for AF-3's two-axis design |
| E-5 | A single start (Misiorowski, 69 FF) tops the first ungated board | CB-1 board evidence floor (100 FF); watch list for 50–99 |
| E-6 | Several pitcher-seasons carry mid-season club changes (Kilian 392 FF, 31 as a Phillie) | Staff volume for EFS uses **Phillies-log pitches only** (DQ-16) |
| E-7 | RHP arm-side is negative `pfx_x` (median −0.64 ft) | Asserted as DQ-10; horizontal break shipped as context only |

## 3 · Metadata map (physical → CDE)

| Physical column | CDE | Map | Note |
|---|---|---|---|
| `release_speed` | Pitch Velocity | exact | |
| `pfx_z` | Induced Vertical Break (IVB, "ride/carry/vert") | exact ×12 → inches | client aliases: ride, carry, vert |
| `release_spin_rate` | Spin Rate | exact | |
| `pfx_x` | Horizontal Break | exact ×12 | context only |
| `release_extension` | Extension | exact | context only |
| `description` | Swing / Whiff (SWINGS/WHIFFS lists) | exact | lists inherited from `Baseball Functions.ipynb` via dp_uc44 |
| `delta_run_exp` | Run Value (batting-team POV) | exact, **sign flipped** | RV/100 is pitcher POV (+ good) |
| `estimated_woba_using_speedangle` | xwOBA (PA grain) | exact | PA-ending rows only (DQ-09) |
| `player_name` | **AMBIGUOUS** | — | batter on batting-role and batter-keyed rows → NR-1 resolves pitcher names |
| `home_team`, `away_team` | Competition Level (derived) | derived | both MLB clubs ⇒ MLB |
| `game_type` | Game Type | exact | 'R' only |
| `pitcher` | Pitcher (MLBAM) | exact | entity lock |
| `phillies_role` | Phillies Role | exact | `pitching` ⇒ Phillies pitcher |
| (derived) `row_frame`, `coverage`, `role` | Sampling Frame / Coverage / Role | new | FR-1 / AF-2 |

## 4 · DQ rule design (handed to `05`)

19 rules across uniqueness, validity, completeness, consistency, accuracy, distribution, comparability and
timeliness — all grain-declared (the uc-pps-028 D-1 lesson). Three are **designed to WARN permanently**:
unresolved names (DQ-06), non-normal metrics (DQ-12), and the bounded frame (DQ-14).

## 5 · Dashboard specification

| Tab | Question it answers | Controls | Failure mode it guards against |
|---|---|---|---|
| Archetype map | Where does any pitcher-season sit? | season range, tier, coverage, find | THIN seasons drawn hollow so they can't pass for population members |
| The room | Who's best among the six — by what? | weight on shape, best vs 2026 | the "best" depending silently on a weight |
| Out there | Who outside grades well, on what evidence? | weight, ranked/watch, role | a one-start sample topping the board |
| The needle | What would move 2026's share? | — | reading "replaces Nola" as a roster call (ledger language) |
| Your notebook, graded | Which client claims held? | — | — |
| Receipts | Does the answer survive the method? | — | — |

The weight slider is the only live computation, and it is the AF-4 formula on receipt columns; at 0.5 it
reproduces `efc_score` to 0.002 (verification family D). Theme toggle: brand `plotly_white` ↔ notebook
`plotly_dark`.
