# 02 · Layer 2 — Design: Data Model, KPI Specs, Technical Lineage

Agents: `data-architect` · `kpi-calculator` · `technical-lineage-builder` · `metadata-mapper`

---

## A · Data model blueprint (`data-architect`)

**Source grain:** one row per pitch. **Output grains:** three, all derived from one pitch log.

| Grain | Key | Purpose |
|---|---|---|
| G-CAREER | `catcher_id × resolved_name` | Q3 — the career battery panel |
| G-SEASON | `catcher_id × resolved_name × game_year` | Q3 — trend |
| G-WINDOW | `window × catcher_id × resolved_name` | Q1/Q2 — recency |
| G-BASE | `player_name` (Nola, all catchers) | the self-referential benchmark every delta is measured against |
| G-START | `game_pk` | confound panel + per-start receipts |

**Benchmark design (important).** Every battery number is compared to **Nola's own
all-catcher mean**, not to a league or staff population. Rationale: the question is whether
*this pitcher's* plan changed, and a cross-pitcher benchmark would import arsenal
differences the question does not care about. This mirrors `uc-cat-001` KPI-2's
self-referential design.

**Join strategy and fan-out risk.** There is exactly one join that can multiply rows: the
catcher-name resolution. It is a many-to-one lookup on a **de-duplicated** id→name frame
(`drop_duplicates('batter')` after modal ranking), so fan-out is structurally impossible.
The `join-validator` check is folded into `dp_uc38_verification.py` Tier B as
`catcher_slot_coverage`, which asserts the built panel and the DPO-path panel cover the same
catcher slots.

**Grain-drift guard.** `events` is populated on only ~26% of rows (PA-terminal). Every
outcome KPI aggregates from PA-terminal rows; every approach KPI aggregates from pitch rows.
The two are never divided into each other. The locked `nresults`/`get_stats` functions
enforce this by construction.

---

## B · KPI calculation specs (`kpi-calculator`)

### B.0 · Inherited — DO NOT RE-DERIVE

| KPI | Function | Provenance |
|---|---|---|
| Slash line, wOBA, K%, BB%, HR/PA | `get_stats` / `nresults` | UC8 → UC25, verbatim |
| Whiff rate | `whiff_rate` | verbatim |
| Chase rate, in-zone rate | `chase_rate` | verbatim |
| Putaway rate | `putaway_rate` | verbatim |
| First-pitch strike rate | `fpsr` | verbatim (= `uc-cat-001` KPI-4) |
| Hard-hit rate | `hard_hit_rate` | verbatim |
| Edge rate | `edge_rate` | UC8 glossary-approved, verbatim |
| OOZ called-strike rate | `ooz_called_strike_rate` | UC8 glossary-approved, verbatim |
| Air / GB rate | `air_gb_rate` | UC8 glossary-approved, verbatim |
| xwOBAcon | `xwobacon` | `uc-pps-021` DQ fix, verbatim |

Any edit to these breaks comparability with the entire Nola advance file. They are copied,
not adapted.

### B.1 · CS-1 · Count state *(supporting definition)*

**Plain language.** From the pitcher's point of view: he is *ahead* when he has more strikes
than balls, *behind* when more balls than strikes, *even* otherwise.

**Formula.** `ahead if strikes > balls · behind if balls > strikes · else even`
**Grain.** pitch · **Population.** all pitches · **Nulls.** `balls`/`strikes` are complete.
**Edge cases.** 0-0 is *even* (not "ahead"), 3-2 is *even*. This is the conventional read and
is stated because a reasonable person could define 0-0 differently.

### B.2 · BAT-1 · Pitch-mix share *(NEW-PROVISIONAL)*

**Plain language.** What share of the pitches in this group were each pitch type?
**Formula.** `n(pitch_type) / n(group)`
**Grain.** any level × `pitch_type` · **Population.** pitches with non-null `pitch_type`
**Nulls.** null `pitch_type` (0.030%) excluded from numerator *and* denominator.
**Edge cases.** Zero-count pitch types are **absent rows**, not zero rows — consumers
needing the full support must reindex. `group_n` rides along so the denominator is always
printable.

### B.3 · BAT-2 · First-pitch group mix *(NEW-PROVISIONAL)*

**Plain language.** How does this battery start a hitter — fastball, breaking, or offspeed?
**Formula.** `n(pitch_group | pitch_number==1) / n(pitch_number==1)`
**Grain.** level × `pitch_group` · **Population.** `pitch_number == 1`
**Constants.** `PITCH_GROUP` dict, canonical from `dp_uc18_marsh_breakout.py`; unmapped
types → `other` (never silently dropped).
**Edge cases.** `pitch_number` restarts each PA, so this is one row per PA by construction.

### B.4 · BAT-3 · Putaway-pitch mix *(NEW-PROVISIONAL)*

**Plain language.** When a two-strike plate appearance ends, what kind of pitch ended it?
**Formula.** `n(pitch_group | strikes==2 AND events non-null) / n(strikes==2 AND events non-null)`
**Population.** PA-terminal rows in two-strike counts — **including terminal contact**, not
just strikeouts.
**Relationship to `putaway_rate`.** Different questions, deliberately shipped together:
BAT-3 = *what was the finish pitch*; `putaway_rate` = *how often the finish was a strikeout*.
**Edge cases.** A PA that reaches two strikes and ends on a walk (3-2 ball four) is included
— the finish pitch was still thrown in a two-strike count.

### B.5 · BAT-4 · Two-strike fastball rate *(inherited definition, first build)*

**Plain language.** Of all two-strike pitches, how many were fastballs?
**Formula.** `n(pitch_group=='fastball' AND strikes==2) / n(strikes==2)`
**Provenance.** `uc-cat-001` KPI-1, specced 2026-08-09, never built. Definition verbatim.
**Interpretation.** High = strength exploitation ("trust the stuff"). Low = weakness
exploitation ("make him chase"). This is one axis of the `uc-cat-001` philosophy scorecard.

### B.6 · BAT-5 · Repeat-pitch rate *(NEW-PROVISIONAL)*

**Plain language.** Within a plate appearance, how often does the battery throw the same
pitch type twice in a row?
**Formula.** `n(pitch_type[n] == pitch_type[n-1]) / n(consecutive pairs)`
**Grain.** any level · **Population.** consecutive pitch pairs within `(game_pk, at_bat_number)`
**Denominator.** `Σ over PAs (pitches_in_PA − 1)`. Single-pitch PAs contribute **nothing to
either side** — this is why the denominator is *pairs*, not pitches.
**Nulls.** A null `pitch_type` breaks the chain; the pair spanning it is dropped from both
sides. Enforced by requiring `pitch_number − prev_pitch_number == 1`.
**Interpretation.** Conviction vs mixing. High = willing to show the same shape twice.
**Known limit.** First-order only — it cannot distinguish FF→FF from KC→KC.
**Test.** Fixture PA `FF FF KC` → 2 pairs, 1 repeat. `KC KC KC` → 2 pairs, 2 repeats, rate 1.0. **PASS.**

### B.7 · BAT-6 · Arsenal entropy *(NEW-PROVISIONAL)*

**Plain language.** A single number for how predictable the pitch mix is.
**Formula.** `H = −Σ p_i · ln p_i` (nats); `H_norm = H / ln(K_global)`, bounded [0, 1].
**`K_global`** = distinct pitch types in Nola's arsenal across the **whole frame**.
**Why global, not per-group:** normalising by each group's own active-type count would score
a two-pitch 50/50 group at 1.0 — nonsense for a comparability question. Groups must be
comparable to each other, so the denominator must be constant. *(This is the design decision
most likely to be challenged; it is stated explicitly so it can be.)*
**Nulls.** Zero-probability types contribute 0 (`0·ln0 := 0`). A single-type group returns
exactly `0.0`, not `−0.0`.
**Interpretation.** 0 = one pitch only. 1 = every pitch in the arsenal equally likely.
**Known limit.** Sequence-blind. Must be read with BAT-5 and BAT-7.
**Test.** `KC KC KC` → 0.0 exactly; four-type group → `active_types == 4`, `H_norm ∈ [0,1]`. **PASS.**

### B.8 · BAT-7 · Ahead-vs-behind divergence *(NEW-PROVISIONAL)*

**Plain language.** Does the battery throw a different arsenal when ahead than when behind?
**Formula.** Jensen-Shannon divergence, base 2 (bounded [0,1]) between the ahead-count and
behind-count pitch-type distributions:
`JSD(P‖Q) = ½·KL(P‖M) + ½·KL(Q‖M)`, `M = ½(P+Q)`, `0·log0 := 0`.
**Support.** The union of pitch types in the parent frame, so both vectors are aligned and
absent types are genuine zeros.
**Nulls / edge cases.** If **either** side has zero pitches, returns **NaN** — not 0. A
group with no behind-count pitches is *unmeasured*, not *maximally consistent*. This
distinction is the most likely misreading and is enforced in code.
**Interpretation.** 0 = one plan regardless of count. Toward 1 = two different pitchers.
**Explicitly NOT a quality metric.** A pitcher who abandons his best pitch when behind
scores as "adaptive" and is worse for it. Read beside BAT-4.
**Test.** identical → 0; disjoint → 1; symmetric; empty side → NaN. **PASS (4/4).**

### B.9 · BAT-8 · Zone rate by count state *(NEW-PROVISIONAL)*

**Plain language.** When behind in the count, does he attack the zone or nibble?
**Formula.** `n(zone ≤ 9) / n(located)` within each `count_state`
**Nulls.** Rows with null `zone` (0.031%) fall out of **both** sides — matches the governed
`chase_rate` convention. *Repo-wide open item **O-2** (null-zone handling) applies here too
and is inherited, not silently re-decided.*
**Interpretation.** The direct process read on the `uc-pps-021` free-pass diagnosis (D-4).

### B.10 · BAT-9 · In-zone whiff rate *(inherited definition, first build)*

**Plain language.** When hitters swing at strikes, how often do they miss?
**Formula.** `n(WHIFFS ∧ zone ≤ 9) / n(SWINGS ∧ zone ≤ 9)` — **identical filter on both sides**.
**Provenance.** `uc-cat-001` KPI-3, including its explicit fix of the intake doc's B-5/B-6
label mismatch. Definition verbatim.

---

## C · Technical lineage (`technical-lineage-builder`)

**Source → target, column level.** Base: `data/phillies/phils_2015..2026.parquet`,
`pitcher==605400`, `game_type=='R'`, deduped on `game_pk+at_bat_number+pitch_number`.

### C.1 Filter pipeline

| Step | Filter | Columns |
|---|---|---|
| A-1 | Regular season | `game_type == 'R'` |
| A-2 | Dedup | `game_pk`, `at_bat_number`, `pitch_number` |
| A-3 | Entity lock | `pitcher == 605400` |
| A-4 | Role split | `phillies_role == 'pitching'` (fallback: `home_team`/`inning_topbot`) |
| A-5 | Weight join | `game_year` → `wOBA and FIP Constants.csv[Season]` |

### C.2 Infrastructure CDEs

| CDE | Source | Transform | Constant |
|---|---|---|---|
| `catcher_id` | `fielder_2` | cast Int64 | — |
| `resolved_name` | `fielder_2` → `pos.batter` | modal `player_name` per batter id; cross-checked against `CATCHER_DICT_2020_26` | `uc-cat-001` 01b dict |
| `pitch_group` | `pitch_type` | `PITCH_GROUP` map; unmapped → `other` | `dp_uc18` canonical dict |
| `count_state` | `balls`, `strikes` | CS-1 | — |
| `is_swing` / `is_whiff` | `description` | `SWINGS` / `WHIFFS` membership | `Baseball Functions.ipynb` cell 21 |
| `in_zone` | `zone` | `zone <= 9` | boundary 9, codebase canonical |
| `is_edge` | `plate_x/z`, `sz_top/bot` | `_dist_to_zone_edge ≤ BALL_FT` | `PLATE_HALF=0.83`, `BALL_FT=2.94/12` |
| `window` | `game_pk` → `start_index_desc` | last-N-starts membership | `RECENT_N_STARTS=5` (DV-1) |
| `ip_computed` | `events` | `EVENT_OUTS` schedule ÷ 3 | out-credit map (UC8) |

### C.3 KPI lineage

| KPI | Source columns | Transform |
|---|---|---|
| BAT-1 | `pitch_type` | count ÷ group count |
| BAT-2 | `pitch_type`, `pitch_number` | group share on `pitch_number==1` |
| BAT-3 | `pitch_type`, `strikes`, `events` | group share on two-strike terminal rows |
| BAT-4 | `pitch_type`, `strikes` | fastball share at `strikes==2` |
| BAT-5 | `pitch_type`, `game_pk`, `at_bat_number`, `pitch_number` | lag-1 equality over consecutive pairs |
| BAT-6 | `pitch_type` | Shannon entropy ÷ `ln(K_global)` |
| BAT-7 | `pitch_type`, `balls`, `strikes` | JSD(ahead mix, behind mix), base 2 |
| BAT-8 | `zone`, `balls`, `strikes` | `zone≤9` share within count state |
| BAT-9 | `description`, `zone` | whiffs ÷ swings, both `zone≤9` |
| Outcome layer | see §B.0 | locked functions, unmodified |

### C.4 External / manual dependency register

| Dependency | Location | Risk |
|---|---|---|
| `wOBA and FIP Constants.csv` | MLB repo root | 2026 weights are mid-season estimates; a post-season update requires a full re-run (join happens pre-aggregation) |
| `CATCHER_DICT_2020_26` | hardcoded in build | If MLBAM reassigns an id, the cross-check FAILs loudly rather than going silently null — deliberate improvement on the `uc-cat-001` risk note |
| Tonight's battery / lineup | DPO prose | Manual carry-in; confirm pre-game |
| **Data plane mount** | `C:\...\Python Scripts\MLB` | **The realised risk.** Now a standing pre-flight check |
