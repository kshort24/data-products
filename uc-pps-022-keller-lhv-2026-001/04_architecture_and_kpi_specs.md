# 04 — Architecture & KPI Specifications
## UC #27 · `uc-pps-022` · Layer 2

Agents: `data-architect`, `kpi-calculator`, `eda-agent`, `join-validator`

---

## 1. Model blueprint (`data-architect`)

### Grain

**One row per pitch.** `(game_pk, at_bat_number, pitch_number)` is the natural key and is
unique across the Keller slice (0 duplicates, asserted).

### Physical model

```
lhvp26.parquet  (pitch grain, 14,960 rows)
        │
        ├── filter game_type == 'R'
        ├── drop_duplicates(game_pk, at_bat_number, pitch_number)
        ├── LEFT JOIN wOBA constants  ON game_year = Season      [1:1 dimension]
        │
        ├──▶  KELLER      = pitcher == 662144        (533 pitches)   ← primary
        └──▶  BASELINE    = pitcher != 662144        (14,427 pitches) ← benchmark
```

**Design rationale — why one table and no star schema.** The entire product answers questions
at a single grain from a single source. Introducing a fact/dimension split here would add
join risk with zero analytical benefit. The only dimension join is the season-level wOBA
constant table, which is 1:1 on `Season` and cannot fan out.

**Design rationale — why the baseline is a slice of the same table.** Keller and his benchmark
are drawn from *the same file, the same season, the same park mix, and the same tracking
installation*. That eliminates level, era, park, and calibration as confounders without a
single external join. The alternative — benchmarking against MLB rates — would have silently
compared a AAA pitcher to a major-league population, which is the exact error the level-
translation caveat exists to prevent.

**Aggregation strategy.** Every published rate is computed by a locked KPI function applied at
a stated `level`. No rate is ever averaged from a lower level up (no mean-of-means). Rate
denominators are always recomputed at the published grain.

---

## 2. `join-validator` report

| Join | Type | Cardinality | Fan-out risk | Result |
|---|---|---|---|---|
| `lhvp26.game_year` → `wOBA constants.Season` | LEFT, 1:1 | 533 → 533 | **None** — right side unique on `Season` | **PASS** |

Row-count assertion pre/post join: **533 = 533**. No other joins exist in this product.
Grain drift: **none possible**. Outer-join null injection: **none** (all 2026 rows match).

---

## 3. `eda-agent` findings that shaped the design

The EDA pass is reported here because two of its findings changed the report structure rather
than merely decorating it.

1. **A structural break in the season, not a trend.** Per-start walk rate reads
   `1, 3, 2, 2, 3, 0, 0, 0`. That is not noise around a mean — it is a step change after the
   6/18 start. The architect therefore added a **start-block dimension** (`half`: starts 1-4
   vs 5-8) as a first-class cut, and the report is organised around it. Splitting 8 starts
   into 4+4 was chosen *before* looking at outcome data, on the walk pattern alone, to avoid
   fitting the split to the answer.
2. **Bimodal contact quality by pitch.** Exit velocity allowed clusters hard on the four-seam
   and cutter (89-90 mph mean) and soft on the sinker and slider (75-79 mph mean). This is a
   large enough separation to survive the small sample and it motivated the per-pitch contact-
   quality receipt.
3. **Monotonic velocity decay by inning** (93.6 → 90.5 mph, innings 1→6) with no reversal. This
   is a clean enough signal to justify a workload recommendation, which would otherwise have
   been "vibes" (explicitly forbidden by the house rules).
4. **Outlier check.** One curveball home run at 103 mph on 6 total curveballs. Flagged: the
   curveball is excluded from all published rate tables (`n=6`) and appears only in the
   home-run receipt. A `1.480` xwOBAcon on one batted ball is not a finding.

---

## 4. Locked KPI register — inherited VERBATIM

The following functions were **copied without modification** from
`dp_uc25_nola_vs_dodgers.py`, which inherited them from `dp_uc15` ← `dp_uc11` ← `dp_uc8`.
None was re-derived this session. Any edit to these is a breaking change and goes to
`version-controller` before it ships.

| KPI | Function | Grain applied | Provenance |
|---|---|---|---|
| Counting stats + slash + wOBA | `get_stats` / `nresults` | population, stand, pitch, TTO, start-block | UC#8 |
| xwOBA on contact | `xwobacon` | population, stand, pitch, TTO | UC#8, **grain fix UC#26** |
| Whiff Rate | `whiff_rate` | population, stand, pitch, start-block | UC#8 |
| Chase Rate / In-Zone Rate | `chase_rate` | population, stand, pitch, start-block | UC#8 |
| Putaway Rate | `putaway_rate` | population, stand, pitch, start-block | UC#8 |
| First-Pitch Strike Rate | `fpsr` | population, stand, start-block | UC#8 |
| Hard-Hit Rate | `hard_hit_rate` | population, stand, pitch, TTO, start-block | UC#8 |
| Edge Rate | `edge_rate` | population, stand, pitch, start-block | UC#8 (glossary-approved) |
| OOZ Called-Strike Rate | `ooz_called_strike_rate` | population, stand, start-block | UC#8 (glossary-approved) |
| Air / GB Rate | `air_gb_rate` | population, stand, pitch, start-block | UC#8 (glossary-approved) |
| Chase-Up Rate | `chase_up_rate` | population, stand, start-block | UC#8 |
| Attack Zone partition | `_attack_zone` | pitch | UC#11 |

> **UC#26 inheritance note.** The `xwobacon` correction is carried forward: the pitch-level
> `xwoba` column produced by `nresults` is a mean over *all* pitches including non-batted-ball
> rows, and must never be cited as xwOBAcon. Both columns are present in the receipts;
> the report cites only `xwobacon`. This is the third UC to carry the fix.

---

## 5. §SR-M1 — PROVISIONAL KPI ratification packet

**KPI id:** `SR-M1` · **Working name:** Mayza Success Rate · **Recommended ratified name:** Quick At-Bat Rate (`qab_rate`)
**Status: PROVISIONAL — NOT RATIFIED — NOT INHERITABLE**
**Owner of the ratification decision: the human DPO.**

### 5.1 Business intent as supplied

> From his *On Pattison* interview, Tim Mayza said that being a reliever with only two
> pitches in his repertoire, his goal is for quick at-bats. He defines that as **getting to
> two strikes or a ground ball within 3 pitches**.

This is a genuinely good metric idea. It captures something the existing pps glossary does
not: *efficiency of arriving at leverage*, as distinct from FPSR (pitch 1 only) or Putaway
Rate (conditional on already being at two strikes). It is worth ratifying. The work below is
about ratifying it **precisely**, not about second-guessing it.

### 5.2 The supplied implementation, read carefully

```python
calc_df = df[df.pitch_number < 4]
s2  = calc_df.groupby(['game_pk','at_bat_number']).agg(max_strikes=('strikes','max'))
s2w = s2[s2.max_strikes == 2]
...
z['is_success'] = np.where((z.max_strikes == 2) | (z.bips == 1), 1, 0)
```

**The author's own two concerns are both correct, and both resolve cleanly:**

| Author's concern | Verdict |
|---|---|
| "I could double-count PAs where he gets to two strikes *and* the third pitch is a grounder" | **Correct, and it is not a bug.** `np.where` with `|` evaluates to a single boolean per row, and `z` is one row per PA, so a PA satisfying both conditions contributes exactly 1. The `total_pas = ('game_pk','size')` denominator counts PA groups, not pitches. **No double-count exists.** |
| "This was all for naught" | **Not for naught — but the implementation measures something narrower than the sentence says.** See below. |

**The finding — a one-pitch lag.** `strikes` is the **pre-pitch** count (`01_ §C.3`). It
records the state the batter walked into, not the state after the pitch. Consequently
`max_strikes` over pitches 1-3 is the count *displayed on pitch 3*, which requires:

1. the second strike to have accrued on pitch **1 or 2** (not 3), **and**
2. the plate appearance to have **survived to a third pitch**.

So the supplied function measures *"reached two strikes within the first **two** pitches and
the PA continued"* — not *"reached two strikes within three pitches."* A batter who takes
strike two on pitch 3 shows `strikes == 2` only on pitch 4, which the `pitch_number < 4`
filter excludes.

### 5.3 Three candidate readings, reconciled against real data

Computed by `sr_m1_variants()` in the build script, at PA grain, strike accrual counted as
any pitch with `type != 'B'`.

| Variant | Definition | Keller (146 PA) | LHV staff ex-Keller (3,714 PA) |
|---|---|---|---|
| **A — as written** | 2nd strike accrued by pitch 2 **and** PA reached pitch 3, OR ground ball in pitches 1-3 | **.411** | **.366** |
| **B — two strikes by pitch 2** | 2nd strike accrued on or before pitch 2 (no survival condition), OR ground ball in pitches 1-3 | **.452** | **.408** |
| **C — two strikes by pitch 3** | 2nd strike accrued on or before pitch 3, OR ground ball in pitches 1-3. *The literal reading of the stated intent* | **.637** | **.604** |

**Spread: 22.6 percentage points** between A and C on the same pitcher and the same data.

**Sanity anchor.** The DPO's original note reported ~40% for Mayza's career across ~1,500 PA
using variant A. Variant A on this population returns .366 for a full AAA staff and .411 for
Keller — consistent with that scale. Variant C returns ~.60, which is a different and much
less discriminating statistic (60% of all plate appearances reaching two strikes within three
pitches is close to a league constant).

**That is the substantive argument for ratifying A, not C.** The literal sentence produces a
metric with little spread between pitchers; the as-written implementation produces one that
separates a staff from .30 to .43. If the goal is to *identify* quick-at-bat pitchers rather
than to *define* the phrase, A is the better instrument. But A should then be **named for
what it measures** — "two strikes within two pitches, or an early ground ball" — rather than
inheriting the interview's "within 3 pitches" phrasing.

### 5.4 Formal spec — the recommended ratification (variant A, renamed)

| Field | Specification |
|---|---|
| **KPI id** | `SR-M1` |
| **Name** | Quick At-Bat Rate |
| **Column** | `qab_rate` |
| **Plain-language definition** | The share of plate appearances in which the pitcher either reached a two-strike count within the first two pitches, or induced a ground ball within the first three pitches |
| **Formula** | `qab_rate = qab_successes / total_pa` |
| **Numerator** | Count of PAs where `(max(strikes) over pitches 1-3 == 2) OR (any pitch 1-3 with type=='X' and bb_type=='ground_ball')` |
| **Denominator** | Distinct `(game_pk, at_bat_number)` in the population |
| **Grain** | Plate appearance. Aggregated to any **PA-invariant** level |
| **Valid levels** | `pitcher`, `player_name`, `game_pk`, `game_date`, `stand`, `p_throws`, `home_team`, and any pitcher-attribute dimension |
| **INVALID levels** | `pitch_name`, `pitch_type`, `balls`, `strikes`, `zone`, `description`, `inning` — any within-PA-varying column. Grouping on these splits a single PA across multiple rows and inflates the denominator. **Guard rail required at ratification** |
| **CDEs consumed** | `game_pk`, `at_bat_number`, `pitch_number`, `strikes`, `type`, `bb_type` |
| **Population filter** | Regular season (`game_type=='R'`), deduplicated on the pitch key |
| **Null handling** | `bb_type` null on non-batted-ball rows is expected; the `type=='X'` predicate gates it. `fillna(0)` after the merges is safe *for this construction only* because both merged columns are counts |
| **Edge cases** | PAs ending on pitch 1-2 without reaching two strikes and without a ground ball → failure (correct). Intentional walks → counted as PAs, always failures (recommend excluding at ratification). Foul balls at two strikes cannot advance the count, so no correction needed. HBP → PA, failure |
| **Minimum sample for publication** | **40 PA** — the threshold used for the leaderboard receipt |
| **Direction** | Higher is better |

### 5.5 Code changes recommended before ratification

None of these change the numbers under variant A; they harden the function.

1. **Rename** `success_rate` → `qab_rate`, `total_success` → `qab_successes` (glossary
   naming compliance, `02_ §2`).
2. **Add a level guard** that raises if `level` contains a within-PA-varying column. This is
   the highest-value change — the function silently produces wrong denominators otherwise.
3. **Replace `('des','size')` with `('description','size')`** in the two internal aggregations.
   Both count rows so the result is identical, but `des` is null on ~73% of rows and reads as
   if it were counting narratives. This is a legibility fix, not a correctness fix.
4. **Narrow the `.fillna(0)`** to the two merged count columns rather than the whole frame, so
   the function stays safe if a future `level` carries nullable values.
5. **Document the pre-pitch-count semantics in the docstring**, so the next reader does not
   re-derive §5.2.
6. **Optionally exclude intentional walks** from the denominator.

### 5.6 Keller's PROVISIONAL SR-M1 values

Reported under variant A. All flagged PROVISIONAL in the receipts.

| Cut | SR-M1 | Baseline | Read |
|---|---|---|---|
| Overall (146 PA) | **.411** | .366 | 5th of 28 LHV pitchers with ≥40 PA |
| vs LHB (85 PA) | **.365** | .364 | Exactly league-average |
| vs RHB (61 PA) | **.475** | .368 | Large edge — same direction as every other RHB split |
| Starts 1-4 (66 PA) | **.318** | — | Below baseline |
| Starts 5-8 (80 PA) | **.488** | — | The approach change shows here too |

The metric independently reproduces the two central findings of this report — the
right-handed advantage and the mid-June inflection — from a completely different construction
than the whiff/chase/contact panel. That convergence is the strongest argument that the
findings are structural rather than an artefact of one metric family.

### 5.7 Ratification decision requested of the DPO

| # | Decision | Recommendation |
|---|---|---|
| R1 | Which variant is ratified: A, B, or C? | **A** — best discrimination; matches the original ~40% anchor |
| R2 | Ratified name and column? | **Quick At-Bat Rate / `qab_rate`**; retire "success_rate" |
| R3 | Apply the six code hardenings in §5.5? | **Yes** — 2 is required, the rest recommended |
| R4 | Minimum publication sample? | **40 PA** |
| R5 | Ratify alongside the QR-1…QR-3 family from `uc-pps-019` to prevent a namespace clash? | **Yes** |
| R6 | Does SR-M1 apply to starters, or is it a reliever-only construct as Mayza framed it? | **DPO call.** Keller is a starter; the metric behaved sensibly. Recommend ratifying it as role-agnostic with a note that the interview framing was reliever-specific |

**Until R1-R6 are answered, SR-M1 remains PROVISIONAL and no downstream UC may inherit it.**
