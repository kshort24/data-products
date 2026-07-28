# 01 — Intake Validation & Source Profile
## `uc-pos-007` / `dp_uc27` · Layer 1 · Agents: `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`

---

## 1. Use-case validator — gap report

Seven gaps found. One blocking, six non-blocking. All resolved before Layer 2 opened.

| # | Gap | Class | Resolution |
|---|---|---|---|
| G-1 | **"loanDepot park" has no identifier in the pitch log.** Statcast carries `home_team`, not `venue_id`. Using `home_team == 'MIA'` silently equates *the Marlins as home club* with *the ballpark* | **BLOCKING** | DPO ruling: accept `home_team == 'MIA'` as the venue proxy, but (a) publish the known-relocation exclusion, (b) publish a parallel visiting-club-only cohort so the tenure confound is visible rather than baked in. Recorded as CDE `VENUE_COHORT` in `02_` |
| G-2 | Requester's snippet uses `player_name` to select hitters. `player_name` is the *pitcher* name in team-level and pitcher-level pulls | Non-blocking | Entity lock moved to `batter` MLBAM id. 11 ids resolved, one id per display name, verified in DQ-15 |
| G-3 | Snippet does not filter `game_type`. Playoff and spring rows are present in `harper`, `schwarber`, `turner`, `edmundo` parquets | Non-blocking | `game_type == 'R'` filter added; 6,439 rows removed |
| G-4 | Snippet does not deduplicate the union | Non-blocking → escalated to `join-validator` | See `05_ §2`. This turned out to be the largest single data defect in the intake |
| G-5 | Minor-league rows are present in `nphl` for prospects (requester flagged this) | Non-blocking | Competition-level allow-list on `home_team`; 7,172 rows removed. Quantified in §3 below |
| G-6 | Bryan De La Cruz named in the request but has no parquet | Non-blocking | Excluded at requester's instruction; noted in the report caveats so the omission is not read as a finding |
| G-7 | No league-wide park baseline exists locally, so "does the park suppress offense" cannot be answered in the general case | Non-blocking | Scope narrowed: the product benchmarks the roster against itself and says so explicitly |

**Verdict: PROCEED.**

---

## 2. Entity lock

Locked on `batter` (MLBAM id). Never on `player_name`.

| MLBAM | Display name | Phillies-era source | Pre-Phillies source | Career MLB pitches (post-governance) |
|---|---|---|---|---|
| 607208 | Turner, Trea | `phils_2023..2026` | `turner.parquet` (2015–22) | 16,501 |
| 656941 | Schwarber, Kyle | `phils_2022..2026` | `schwarber.parquet` (2015–21) | 16,798 |
| 547180 | Harper, Bryce | `phils_2019..2026` | `harper.parquet` (2015–18) | 17,410 |
| 669016 | Marsh, Brandon | `phils_2022..2026` | `marsh.parquet` (2021–22) | 7,559 |
| 664761 | Bohm, Alec | `phils_2020..2026` | — | 8,573 |
| 681082 | Stott, Bryson | `phils_2022..2026` | — | 8,143 |
| 592663 | Realmuto, J.T. | `phils_2019..2026` | `realmuto.parquet` (2015–18, Marlins) | 16,123 |
| 687282 | Rincones Jr., Gabriel | `phils_2026` | `lhvb25`, `lhvo26`, `clwo26` (MiLB — **excluded**) | 289 |
| 702222 | Crawford, Justin | `phils_2026` | `lhvb25` (MiLB — **excluded**) | 924 |
| 656537 | Hill, Derek | `phils_2026` | `derek_hill.parquet` (2020–26; DET, WSH, MIA, TEX, SF, CWS) | 1,696 |
| 624641 | Sosa, Edmundo | `phils_2022..2026` | `edmundo.parquet` (2018–22, STL) | 3,219 |

Counts are pitches vs RHP after all four governance filters.

---

## 3. Source-system profile — fitness for purpose

### 3.1 Sources scanned

30 parquet files carry at least one roster hitter's pitch:

* `data/phillies/phils_2015..2026.parquet` (12 files, `phillies_role == 'batting'`) — Phillies-era rows
* Hitter-specific pulls: `turner`, `schwarber`, `harper`, `marsh`, `realmuto`, `edmundo`, `derek_hill`
* Team-level "outfielder" pulls that incidentally carry roster hitters as the batter:
  `marlins-of-24-25`, `nats-of-23`, `giants-of-rangers-of-24`, `white-sox-of-25-26`, `tigers-of-20-22`
* Opposing-pitcher pulls that carry roster hitters as the batter: `alcantara`, `luzardo`, `pop`,
  `buehler`, `morton`, `taillon`, `wheeler`, `senzatela`, `mikolas`, `moore`, `hand`, `joe_ross`,
  `kimbrel`, `giles`, `estevez`, `strahm`, `alvarado`, `hoffman` and others
* MiLB affiliate frames: `lhvb25`, `lhvo26`, `clwo26` — **excluded by competition-level rule**

### 3.2 Naive-union inflation (the defect in the intake snippet)

`pd.concat([pos, nphl])` with no dedup. A single pitch can appear in `pos`, in the hitter's own
parquet, in a team-level pull, and in the opposing pitcher's parquet simultaneously.

| Hitter | Miami pitches, naive | Miami pitches, deduped | Inflation | Governed (RHP only) |
|---|---|---|---|---|
| Realmuto, J.T. | 4,836 | 4,567 | **+5.9%** | 3,497 |
| Harper, Bryce | 1,560 | 1,402 | **+11.3%** | 1,042 |
| Turner, Trea | 1,109 | 989 | **+12.1%** | 800 |
| Schwarber, Kyle | 927 | 798 | **+16.2%** | 578 |
| Bohm, Alec | 733 | 625 | **+17.3%** | 441 |
| Stott, Bryson | 642 | 552 | **+16.3%** | 381 |
| Hill, Derek | 541 | 541 | 0.0% | 297 |
| Marsh, Brandon | 456 | 385 | **+18.4%** | 293 |
| Sosa, Edmundo | 193 | 169 | **+14.2%** | 96 |
| Crawford, Justin | 50 | 50 | 0.0% | 42 |
| Rincones Jr., Gabriel | 0 | 0 | — | 0 |

Inflation is not uniform, so it does not cancel in a ratio — it biases hitter-to-hitter comparison
as well as the level. Receipt: `out/dp_uc27_source_profile.csv`, `out/dp_uc27_source_provenance.csv`.

### 3.3 Competition-level contamination

MiLB frames use affiliate `home_team` codes (`LHV`, `SWB`, `IND`, `CLR`, `DUN`, `TAM`, …), none of
which is `MIA`. So MiLB rows never entered the *Miami* cohort — they entered the **"all other
ballparks" baseline**, which is worse, because that is the comparison term.

| Hitter | MiLB pitches in the naive baseline | Share of that hitter's non-Miami pitches |
|---|---|---|
| Rincones Jr., Gabriel | 1,178 | **45.4%** |
| Crawford, Justin | 1,005 | **33.4%** |
| Bohm, Alec | 64 | 0.5% (2025 rehab/option) |
| Marsh, Brandon | 32 | 0.3% (2025 rehab) |

Note the two "quiet" cases: Bohm and Marsh are established big leaguers whose baselines would have
been contaminated at a level small enough to go unnoticed. The rule is applied to the whole roster,
not just the prospects.

### 3.4 Fitness by CDE

| CDE | Fit | Evidence |
|---|---|---|
| `VENUE_COHORT` | **Adequate with a caveat** | `home_team` non-null on 100% of rows; the field is a club identifier, not a venue identifier — see G-1 |
| `COMPETITION_LEVEL` | **Good** | Derivable with certainty from the `home_team` allow-list; zero ambiguous codes |
| `BATTER_ENTITY` | **Good** | 11 ids, 11 names, no collisions, no nulls |
| `PITCHER_HANDEDNESS` | **Good** | `p_throws` non-null on 100% of rows |
| Slash-line inputs (`events`, `type`, `description`) | **Good** | Non-null and in the expected domain across the window |
| Contact quality (`launch_speed`, `launch_speed_angle`) | **Good** | `launch_speed` present on **99.4%** of balls in play |
| Expected quality (`estimated_woba_using_speedangle`) | **Adequate** | Populated only on batted balls and strikeouts by Statcast design — 80.2% of pitch rows are null and that is correct, not a defect. Aggregated as a mean over the populated rows, consistent with the inherited kernel |
| Bat-tracking (`bat_speed`, `attack_angle`) | **Not used** | Statcast 2024+ only; the window is 2015–2026, so it would fracture the cohort. Deliberately out of scope |

### 3.5 Freshness

| Source | Max `game_date` | Days behind build (2026-07-27) | Verdict |
|---|---|---|---|
| `data/phillies/phils_2026.parquet` | 2026-07-22 | 5 | **Acceptable** (T-5; DQ-12 PASS) |
| `data/opponents/alcantara.parquet` | 2025-04-12 | 471 | **WARN — DQ-13.** Alcantara's 2026 season is visible only through the 103 pitches Phillies hitters saw on 2026-06-17 |
| Governed union | 2026-07-22 | 5 | — |

Receipt: `out/dp_uc27_freshness.csv`.

---

## 4. Domain steward proxy — findings

Three domain rules that no agent could have derived from the data alone. All three changed the design.

### DS-1 · The Marlins-tenure confound *(materially changed the product)*

`home_team == 'MIA'` collects two populations. **J.T. Realmuto caught for the Marlins 2015–2018
(783 PA at loanDepot as the home club) and Derek Hill played there in 2024 and 2025 (80 PA).**
Together they supply **863 of 1,901 Miami plate appearances — 45% of the cohort.** A "venue effect"
computed over that cohort is substantially an aging-curve and team-quality effect.

Consequence: every Miami number in the product is published twice, all-rows and visiting-club-only.
The visiting-club cohort is the one that describes 2026-07-28.

### DS-2 · The 2017 Hurricane Irma relocation

Three games carry `home_team == 'MIA'` but were played at Miller Park, Milwaukee: **2017-09-15,
-16, -17 vs MIL** (`game_pk` 492302, 492317, 492332). Announced 2017-09-13 after Irma; the Marlins
remained the nominal home club. 44 roster pitch-rows affected, all Realmuto's.

Consequence: hard exclusion, enforced and tested (DQ-06).
Source: [MLB.com — Brewers-Marlins series moved to Milwaukee](https://www.mlb.com/news/brewers-marlins-series-is-moved-to-milwaukee/c-254081146).

### DS-3 · loanDepot park is not a constant park across the window

The centre-field home-run sculpture was removed after 2018 and the outfield walls were brought in
for the 2020 season. A career-spanning "Miami" cohort therefore mixes at least two park
configurations.

Consequence: a park-era split was computed (`out/dp_uc27_park_era.csv`,
`out/dp_uc27_park_era_visitors.csv`). It shows a 24-point wOBA improvement post-2020 in the
all-rows series — **which vanishes in the visitors-only series** (`.343` pre vs `.334` post). The
apparent park-era effect is DS-1 in disguise, because Realmuto's Marlins years all sit pre-2020.
The report states this explicitly so the hypothesis is not revived downstream.

### DS-4 · Non-blocking domain notes carried forward

* `pitches_per_pa` computed as total pitches ÷ PA slightly overstates the absolute level (a PA can
  begin against one pitcher and end against another within the RHP filter). Identical across
  cohorts, so venue deltas are unaffected.
* The Phillies are the road club on 2026-07-28, which is why the visiting-club cohort — not the
  all-rows cohort — is the decision-relevant frame.
* Alcantara returned from Tommy John surgery in 2025, which is why a 2025–26 arsenal window is
  reported separately from the career-vs-this-roster mix.
