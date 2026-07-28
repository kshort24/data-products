# 05 — DQ Rules & Join Validation
## UC #27 · `uc-pps-022` · Layer 2

Agents: `dq-rule-definer`, `join-validator`

`dq-rule-definer` specifies. `data-quality-engineer` executes (`07_`). The two are kept
separate on purpose — the agent that writes the rule does not grade the result.

---

## 1. Rule specifications

### Dimension: Uniqueness

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-01** | Every pitch appears once | `duplicated(['game_pk','at_bat_number','pitch_number']).sum() == 0` | **Blocking** |

### Dimension: Validity — entity integrity

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-02** | The slice contains exactly one pitcher | `pitcher.nunique() == 1 and pitcher.unique() == [662144]` | **Blocking** |
| **DQ-03** | Brad Keller is not in the slice | `641745 not in pitcher.unique()` | **Blocking** |
| **DQ-04** | Regular season only | `set(game_type) == {'R'}` | **Blocking** |

> **Why DQ-03 exists as its own rule.** `lhvp26.parquet` contains two pitchers named Keller.
> A `player_name.str.contains('Keller')` filter returns 561 rows instead of 533 and blends a
> second pitcher's arsenal into the profile. DQ-02 would catch it, but DQ-03 names the specific
> trap so that the failure message is diagnostic rather than merely negative. This is the
> generalisable lesson from the Nola / "Nolan Hoffman" incident: **assert against the specific
> near-miss entity, not just against cardinality.**

### Dimension: Completeness

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-05** | Location CDEs are present on every pitch | `plate_x, plate_z, sz_top, sz_bot, zone` all non-null ≥ 99% | **Blocking** |
| **DQ-06** | Velocity is present on every pitch | `release_speed` non-null ≥ 99% | **Blocking** |
| **DQ-07** | Contact-quality CDEs are present on batted balls | `launch_speed` and `estimated_woba_using_speedangle` non-null ≥ 95% **of `type=='X'` rows** | **Blocking** |
| **DQ-08** | Spin is present | `release_spin_rate` non-null ≥ 95% | Warning |
| **DQ-09** | Bat-tracking absence is documented, not silently tolerated | `bat_speed` populated rate recorded; product must have no dependency on it | Warning |

> **Why DQ-07 is scoped to `type=='X'`.** Measuring `launch_speed` completeness across all
> pitches returns ~35% and would trip a naive threshold, because a called strike has no exit
> velocity — correctly. The denominator must be balls in play. This is the completeness
> analogue of the UC#26 xwOBAcon grain fix and is the most common false-positive DQ failure
> in this repo.

### Dimension: Accuracy — reconciliation

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-10** | Innings reconcile to events | `sum(events → outs) / 3` within 0.34 IP of the sum of per-start IP | **Blocking** |
| **DQ-11** | Rate denominators reconcile | For every published rate, numerator ≤ denominator and denominator > 0 | **Blocking** |
| **DQ-12** | Splits sum to the whole | `PA(L) + PA(R) == PA(total)`; `sum(PA by start) == PA(total)`; `sum(pitches by pitch_name) == pitches(total)` | **Blocking** |

### Dimension: Consistency — interpretive guard rails

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-13** | No rate is published without its sample size | Every published rate line carries `n` (pitches, PA, or BIP as appropriate) | **Blocking** |
| **DQ-14** | No rate is published without a benchmark | Every headline rate has a same-league same-season comparison value | **Blocking** |

> DQ-13 and DQ-14 are unusual as *data*-quality rules — they govern presentation. They are
> here because this UC's dominant failure mode is not a wrong number, it is a **correct number
> read without context**. A `.268` wOBA on 146 batters faced is true and is meaningless
> without both the 146 and the `.343` baseline beside it. Treating that as a DQ requirement
> rather than an editorial preference is what makes it enforceable.

### Dimension: Timeliness

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-15** | Data window is stated and current | Cache max `game_date` recorded in the freshness manifest; subject's last outing within 14 days of report date | Warning |

### Dimension: Interpretability — provisional-KPI containment

| Rule | Plain language | Spec | Severity |
|---|---|---|---|
| **DQ-16** | SR-M1 is flagged wherever it appears | Every SR-M1 receipt carries a `STATUS` column reading `PROVISIONAL — NOT RATIFIED`; every prose mention carries the banner | **Blocking** |

---

## 2. Rules deliberately **not** specified

| Candidate rule | Why not |
|---|---|
| "wOBA allowed must fall in a plausible range" | A range check would encode an expectation about AAA offence that no approved source establishes. It would manufacture a threshold |
| "Velocity must not vary more than X mph within a start" | The observed 3.1 mph decay is a *finding*, not an error. A DQ rule here would suppress the signal the report is built on |
| "Minimum 100 BF before publishing any rate" | Applied as a **warning**, not a block. The convention exists to prevent overclaiming, and the correct mitigation for a 146-BF subject is disclosure (DQ-13), not suppression. Blocking would mean this product could never be built |

---

## 3. Join validation results (`join-validator`)

Only one join exists.

| Check | Result |
|---|---|
| Join: `lhvp26.game_year` → `wOBA constants.Season` (LEFT) | |
| Right-side key uniqueness | **PASS** — `Season` unique |
| Row count pre-join | 533 |
| Row count post-join | 533 |
| Fan-out / row multiplication | **NONE** — mathematically impossible on a unique right key |
| Unmatched left rows (null injection) | **0** — all 2026 rows matched |
| Grain drift | **NONE** — grain unchanged at pitch level |
| Key integrity | **PASS** |

**Additional grain assertions run at build time** (these are the checks that would catch a
silent fan-out anywhere else in the pipeline):

| Assertion | Expected | Observed | Result |
|---|---|---|---|
| `PA(stand=L) + PA(stand=R)` | 146 | 85 + 61 = 146 | **PASS** |
| `sum(BF across 8 starts)` | 146 | 146 | **PASS** |
| `sum(pitches by pitch_name)` | 533 | 230+128+97+72+6 = 533 | **PASS** |
| `sum(PA by TTO)` | 146 | 72 + 58 + 16 = 146 | **PASS** |
| `sum(PA by start-block)` | 146 | 66 + 80 = 146 | **PASS** |
| `BIP total` | 96 | 41+30+15+9+1 = 96 | **PASS** |

**Verdict: no join risk in this product.** The grain is preserved end-to-end.
