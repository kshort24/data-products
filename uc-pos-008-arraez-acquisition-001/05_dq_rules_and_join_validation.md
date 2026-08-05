# 05 — DQ Rules & Join Validation

**Agents:** `dq-rule-definer` → `join-validator` → `data-quality-engineer`
**Layer 2 design → Layer 3 execution** · UC #32 · `uc-pos-008` · `dp_uc31`

---

## 1. Rule specification (`dq-rule-definer`)

24 rules across the six standard dimensions. Written in plain language first, then as executable assertions; specified **before** the build ran.

| ID | Dimension | Plain-language rule | Why it matters | Severity |
|---|---|---|---|---|
| DQ-01 | Uniqueness | The Arraez source contains exactly one batter id | A multi-player cache would silently pool other hitters | **Blocking** |
| DQ-02 | Validity | That id is MLBAM 650333 | Entity lock; the Nola/"Nolan Hoffman" failure mode | **Blocking** |
| DQ-03 | Uniqueness | No duplicate (game_pk, at_bat_number, pitch_number) | Duplicates inflate every count | **Blocking** |
| DQ-04 | Validity | Only `game_type == 'R'` survives filtering | Postseason has different run environments | **Blocking** |
| DQ-05 | Completeness | `stand == 'L'` on every row | A right-handed row would mean contamination | **Blocking** |
| DQ-06 | Timeliness | Cache max date is 2026-08-02 | The freshness claim in the report must be true | **Blocking** |
| DQ-07 | Consistency | Zero Phillies plate appearances for Arraez | The "pre-arrival dossier" framing depends on it | **Blocking** |
| DQ-08 | Completeness | Primary window ≥ 400 PA | Below this the headline is not publishable | **Blocking** |
| DQ-09 | Validity | `truncated_pa` is absent from the strict PA spine | The fork must be real, not accidental | **Blocking** |
| DQ-10 | Completeness | `delta_run_exp` present on ≥98% of primary-window PAs | AR-6 is unsupportable below this | **Blocking** |
| DQ-11 | Completeness | Base-state fields present on every PA | AR-4/AR-5/AR-6 all key on them | **Blocking** |
| DQ-12 | Accuracy | PA-spine BA reconciles to locked `get_stats` within 0.006 | Detects grain drift between the two kernels | **Blocking** |
| DQ-13 | Accuracy | PA-spine wOBA reconciles to locked `get_stats` within 0.006 | As DQ-12 | **Blocking** |
| DQ-14 | Consistency | Every Phillies game yields nine distinct slots | Slot reconstruction precondition | **Blocking** |
| DQ-15 | Consistency | First nine PAs of every game are nine distinct batters | The stronger slot precondition | **Blocking** |
| DQ-16 | Validity | Slot PA counts decline monotonically 1→9 | A structural property of batting orders; violation means the mapping is wrong | Warning |
| DQ-17 | Consistency | RISP share is higher in slot 4 than slot 1 | The consumer's own hypothesis, tested as a rule | Warning |
| DQ-18 | Validity | SPCR is bounded in [0, 1] | A rate outside this means the `min()` guard failed | **Blocking** |
| DQ-19 | Accuracy | Runs on a PA never exceed runners on base + 1 | Catches scorekeeping or arithmetic errors | **Blocking** |
| DQ-20 | Completeness | ≥97% of classified pitches map to a pitch group | Unmapped pitches silently shrink AR-3 cells | Warning |
| DQ-21 | Consistency | Comparison set is 2026 regular season only | Prevents era mixing in the benchmark | **Blocking** |
| DQ-22 | Timeliness | Comparison set max date equals the cache max | Subject and benchmark must share a window | **Blocking** |
| DQ-23 | Validity | `xwoba_con_n ≤ bip` everywhere | O4 guard — the honest denominator can never exceed the count | Warning |
| DQ-24 | Consistency | Slot context weights sum to 1.0 per slot | AR-6 arithmetic precondition | **Blocking** |

---

## 2. Join validation (`join-validator`) — part 1: the constants join

| Join | Test | Result |
|---|---|---|
| Arraez × `wOBA and FIP Constants.csv` on `game_year = Season` | Row count before vs after | 15,228 → 15,228 · **no fan-out** |
| | `Season` unique in the constants file | ✅ unique |
| | Every `game_year` finds a match | ✅ 2019–2026 all present |
| Phillies × constants | Row count before vs after | 16,269 → 16,269 · **no fan-out** |

**Column-collision handling.** The constants file shares column names with the parquet (`wOBA`, `wBB`, …). The locked pattern drops the parquet's copies before merging and suffixes any residual as `_bad`, so the season weights always win. Inherited verbatim from `dp_uc24`; verified by DQ-13 (a wrong weight would break the wOBA reconciliation).

---

## 3. Join validation — part 2: batting-slot reconstruction

This is the highest-risk derivation in the build and received the most attention.

### 3.1 JV-03 — slot integrity

| Test | First run | After fix |
|---|---|---|
| Games with nine distinct slots | 112 / 112 | 112 / 112 |
| Games whose first nine PAs are nine distinct batters | **111 / 112** | **112 / 112** |
| Mean distinct batters per (game, slot) | 1.125 | 1.125 |
| (game, slot) cells with exactly one batter | 87.7% | 87.7% |

### 3.2 Root cause of the single exception

Game `823294`, 2026-05-26:

| at_bat_number | batter | events |
|---|---|---|
| 1 | Schwarber | field_out |
| 2 | Turner | field_out |
| 3 | Harper | home_run |
| 4 | Marsh | single |
| **5** | **Bohm** | **`truncated_pa`** |
| **9** | **Bohm** | **field_out** |
| 10 | Stott | field_out |

Bohm's plate appearance was interrupted (third out on the bases) and resumed in the next inning. Statcast records the interruption as `events == 'truncated_pa'` and the resumption as a second row. Under the locked PA rule this is **two** plate appearances, which puts Bohm in the first nine twice and shifts every subsequent slot in that game by one.

**Fix.** The strict PA spine excludes `truncated_pa`. 112 / 112 clean.

**This is why the definitional fork exists.** It was not a stylistic preference — the lineup model is *incorrect* without it. Documented in 01 §3.4, specified in 04 §1.3, reconciled in verification V-009.

### 3.3 Residual grain notes

- **12.3% of (game, slot) cells contain more than one batter.** These are genuine substitutions. AR-5 measures the *slot*, so this is correct behaviour, not drift.
- **Slot PA counts decline monotonically** (512, 498, 482, 477, 466, 451, 440, 427, 415) — exactly the structural signature a correct mapping should produce. DQ-16.
- **No cross-team leakage.** The comparison frame is filtered on `phillies_role == 'batting'` before slot assignment, so opponent PAs (which share the `at_bat_number` sequence) cannot enter the cycle.

### 3.4 AR-6 cross product

The AR-6 composition is an intentional many-to-many join (slots × contexts × hitters).

| Test | Expected | Actual |
|---|---|---|
| Weight rows | 9 slots × 3 contexts | 27 ✅ |
| Profile rows | 11 hitters × 3 contexts | 33 ✅ |
| Output rows | 11 hitters × 9 slots | 99 ✅ |
| Weights sum to 1.0 per slot | 9 × 1.0 | ✅ DQ-24, V-100 |

No unintended fan-out: the cross product's dimensions are asserted rather than assumed.

---

## 4. Execution results (`data-quality-engineer`)

**Build-time scorecard: 24 / 24 PASS.** Full detail in `out/dp_uc31_dq_scorecard.csv` and rendered in the dashboard's Governance tab.

| Dimension | Rules | Pass |
|---|---|---|
| Completeness | 5 | 5 |
| Validity | 7 | 7 |
| Consistency | 6 | 6 |
| Accuracy | 3 | 3 |
| Uniqueness | 2 | 2 |
| Timeliness | 2 | 2 |

### Selected results worth reading

| Rule | Value observed |
|---|---|
| DQ-08 | 464 PA in the primary window (gate: 400) |
| DQ-10 | `delta_run_exp` present on 99.07% of PAs (gate: 98%) |
| DQ-12 | PA-spine BA .3238 vs locked .3238 — exact |
| DQ-15 | 0 exceptions after the strict-spine fix |
| DQ-17 | Slot 1 RISP .1758 vs slot 4 RISP .2495 — **the consumer's hypothesis confirmed** |
| DQ-20 | 1,708 of 1,712 classified pitches mapped (99.8%) |
| DQ-23 | `xwoba_con_n ≤ bip` in all 8 season rows |

### Non-blocking observations recorded, not failed

1. **`xwoba_con_n` runs 0–16 below `bip` per season** — the O4 gap made visible. 2026: 408 estimates on 414 balls in play. Rates unaffected; the honest denominator is published.
2. **One AR-3 cell below the publication gate** — offspeed vs LHP, 4 balls in play. Retained, flagged `thin`, and marked unusable in the report rather than dropped, so a reader cannot conclude the cell was never examined.
3. **`bat_speed` absent before 2023.** Era limitation, disclosed; no imputation.
