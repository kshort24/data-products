# 05 — DQ Rules & Join Validation
## `uc-pos-007` / `dp_uc27` · Layer 2 · Agents: `dq-rule-definer`, `join-validator`

---

## 1. DQ rule specifications

Sixteen rules across six dimensions. Nine are **blocking** — a failure stops the build. Seven are
**warning** — a failure is published on the scorecard and in the report caveats. Rules are written
in plain language first, then as the implemented predicate.

| ID | Dimension | Plain language | Predicate | Blocking |
|---|---|---|---|---|
| DQ-01 | Uniqueness | No pitch appears twice in the governed frame | `clean.duplicated(PITCH_KEY).sum() == 0` | **Yes** |
| DQ-02 | Validity | Every row belongs to one of the eleven rostered hitters | `set(clean.batter) ⊆ ROSTER_IDS` | **Yes** |
| DQ-03 | Validity | Regular season only | `set(clean.game_type) == {'R'}` | **Yes** |
| DQ-04 | Validity | Right-handed pitchers only | `set(clean.p_throws) == {'R'}` | **Yes** |
| DQ-05 | Consistency | Every venue code is an MLB club — no minor-league rows survive | `set(clean.home_team) ⊆ MLB_TEAMS` | **Yes** |
| DQ-06 | Accuracy | No Hurricane-Irma relocated game is counted as Miami | `clean[game_pk ∈ IRMA].empty` | **Yes** |
| DQ-07 | Accuracy | The Miami cohort contains only `MIA` home games | `set(clean[venue==MIAMI].home_team) == {'MIA'}` | **Yes** |
| DQ-08 | Completeness | wOBA is computable for every published hitter × venue cell | `split.woba.isna().sum() == 0` | **Yes** |
| DQ-09 | Completeness | xwOBA null share is within Statcast's expected range (populated on contact and strikeouts only) | `null_share < 0.90` | No |
| DQ-10 | Completeness | Exit velocity is present on at least 95% of balls in play | `launch_speed.notna().mean() >= 0.95` | No |
| DQ-11 | Validity | Every published hitter clears the PA gate (40 Miami / 100 elsewhere) | `venue_delta.qualified.all()` | No |
| DQ-12 | Timeliness | The Phillies cache is within 7 days of the build date | `(build − max_game_date).days <= 7` | No |
| DQ-13 | Timeliness | Alcantara's source cache carries 2026 data | `alcantara_max_date >= '2026-06-01'` | No |
| DQ-14 | Consistency | Balls-in-play denominators reconcile across `hard_hit_rate`, `barrel_rate` and `get_stats` | `split.bips == split.bip` elementwise | **Yes** |
| DQ-15 | Uniqueness | One MLBAM id per display name — no name collision | `len(ROSTER) == len(set(ROSTER.values()))` | **Yes** |
| DQ-16 | Completeness | Every rostered hitter has faced Alcantara at least once in the log | `alc.batter.nunique() == 11` | No |

**Why DQ-15 exists.** The house failure mode is name-based entity resolution: the Nola /
"Nolan Hoffman" contamination in `uc-pps-008`. This product locks on MLBAM id and asserts the
one-to-one mapping rather than assuming it.

**Why DQ-14 exists.** Four different KPIs divide by "balls in play." If any of them computed its
own denominator differently, hard-hit rate and barrel rate would not be comparable to each other or
to the batted-ball shares. The rule asserts they are the same number.

Results: `07_ §1`. Receipt: `out/dp_uc27_dq_scorecard.csv`.

---

## 2. Join validation report

`join-validator` was run against the model in `04_ §1.2`. **It found the defect that reshaped the
build**, so this section is longer than usual.

### 2.1 Joins in the model

There is exactly one relational join in the whole pipeline:

| Join | Type | Cardinality | Fan-out risk |
|---|---|---|---|
| governed frame `game_year` → `wOBA and FIP Constants.csv` `Season` | left | many-to-**one** | **None.** `Season` is unique in the constants file; the join is a dimension lookup |

Verified: row count is identical before and after the constants merge. No other join exists — the
union is a `concat`, not a join, and every published table is a `groupby` on a single frame.

### 2.2 The union is not a join, but it fans out anyway

`pd.concat` of overlapping sources produces exactly the pathology a join fan-out produces: the same
fact counted more than once. **This is the defect present in the requester's source snippet**
(`vs = pd.concat([pos, nphl])` with no deduplication).

**Mechanism.** A single pitch — say Bryce Harper facing Sandy Alcantara at loanDepot park in 2023 —
is physically present in up to four cached parquets simultaneously:

| Source | Why it holds the row |
|---|---|
| `data/phillies/phils_2023.parquet` | Phillies batting row |
| `data/opponents/alcantara.parquet` | Alcantara pitcher pull |
| `data/opponents/marlins-of-24-25.parquet` | Marlins outfielder pull, if the ball was hit to an outfielder |
| `data/opponents/harper.parquet` | (not in this case — Harper's pull stops in 2018) |

`get_nphillies_data()` deduplicates *within* `nphl`, but `pd.concat([pos, nphl])` re-introduces
every `pos`/`nphl` overlap. Measured duplication of Miami rows, by contributing source:

| Hitter | Contributing sources for duplicated Miami rows |
|---|---|
| Schwarber | `pos`, `alcantara`, `schwarber`, `marlins-of-24-25`, `luzardo`, `pop` |
| Turner | `pos`, `turner`, `alcantara`, `marlins-of-24-25`, `luzardo`, `pop` |
| Realmuto | `pos`, `realmuto`, `luzardo`, `taillon`, `joe_ross`, `hand`, `buehler`, `senzatela`, `mikolas`, `moore`, `morton`, `pop`, `wheeler`, `marlins-of-24-25`, `alvarado`, `giles`, `hoffman`, `kimbrel`, `estevez`, `strahm` |
| Stott | `pos`, `alcantara`, `marlins-of-24-25`, `luzardo`, `pop` |
| Sosa | `pos`, `luzardo`, `marlins-of-24-25` |

**Impact, quantified.** Miami pitch counts inflate by 5.9% (Realmuto) to 18.4% (Marsh) — see
`01_ §3.2`. Because the inflation is uneven, it biases hitter-to-hitter comparison, not just the
overall level. A hitter who happens to have faced more separately-cached pitchers in Miami gets more
duplication.

**Remediation.** `drop_duplicates(subset=['game_pk','at_bat_number','pitch_number'], keep='first')`
applied to the union before any filtering.

**Key sufficiency proof.** Statcast's `(game_pk, at_bat_number, pitch_number)` triple is unique per
pitch by construction. Post-dedup the governed frame contains **0 duplicate keys** (DQ-01), and the
row count is stable across re-runs regardless of source ordering (`keep='first'` on a deterministic
`sorted(glob(...))` file order).

### 2.3 Grain drift check

| Check | Result |
|---|---|
| Does any published table mix grains? | No. Every table is a `groupby` on the pitch-level frame |
| Does the constants join change the grain? | No — many-to-one dimension lookup, row count invariant |
| Do the three cohort frames overlap in a way that could double-count in a pooled figure? | No. Cohort B (visitors) is a strict subset of Cohort A; cohort C (Alcantara) is a strict subset of A. **They are never summed together** — they are reported side by side as alternative populations |
| Are BIP denominators consistent across rate KPIs? | Yes — asserted by DQ-14 |

### 2.4 Null-introduction check

No outer joins are used, so no nulls are introduced by join mechanics. Nulls present in the output
come from three legitimate sources, all handled explicitly:

| Null source | Handling |
|---|---|
| `estimated_woba_using_speedangle` on non-contact pitches | Statcast design. Aggregated as a mean over populated rows; 80.2% null share is expected and asserted by DQ-09 |
| `launch_speed` on 0.6% of balls in play | Tracking gaps. Excluded from the quantile and the hard-hit numerator; DQ-10 asserts the coverage floor |
| A cohort with zero balls in play | Guarded — rate returns `NaN`, never a divide-by-zero. VD-2 uses `nanmean` so a hitter missing one process component is still classified |

### 2.5 Verdict

**PASS after remediation.** The one true join is safe. The union fan-out was found, quantified,
fixed, and is now asserted by a blocking DQ rule. Any future venue or park study in this repo should
inherit the dedup and competition-level filters from `dp_uc27` rather than re-derive them.
