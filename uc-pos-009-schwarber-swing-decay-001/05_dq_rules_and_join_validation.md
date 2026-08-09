# 05 — DQ Rules, Join Validation & Build

**Layers 2–3** · Departments: Quality ∥ Engineering (Build)
**Agents:** `dq-rule-definer` · `join-validator` · `data-engineer` · `data-quality-engineer`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

---

## 1. `dq-rule-definer` — 24 rules across six dimensions

Written in plain language first, then as executable assertions. Rules DQ-08 through DQ-11 are the **no-imputation gate** and are the reason this section exists in the form it does.

| Rule | Dimension | Plain language | Assertion |
|---|---|---|---|
| DQ-01 | uniqueness | No pitch appears twice after the concat | `duplicated(PITCH_KEY).sum() == 0` |
| DQ-02 | validity | Only Schwarber is in the locked frame | `set(batter) == {656941}` |
| DQ-03 | validity | A name filter would not have pulled anyone else | contamination id list is empty |
| DQ-04 | validity | Regular season only | `set(game_type) == {'R'}` |
| DQ-05 | consistency | He bats left-handed in every row | `set(stand) == {'L'}` |
| DQ-06 | completeness | Launch angle is present on essentially every ball in play | coverage > 0.97 |
| DQ-07 | completeness | 2026 bat speed is measured on essentially every swing | coverage > 0.95 |
| **DQ-08** | **accuracy** | **The source has no bat-speed value before 2024** | `count == 0` |
| **DQ-09** | **accuracy** | **The source has no attack-angle value before 2025** | `count == 0` |
| **DQ-10** | **accuracy** | **No bat-speed aggregate is published for any pre-sensor season** | `a1[year<2024].bat_speed_mu.isna().all()` |
| **DQ-11** | **accuracy** | **No attack-angle aggregate is published for any pre-sensor season** | `a1[year<2025].attack_angle_mu.isna().all()` |
| DQ-12 | validity | Derived plate speed is physically plausible | 99%+ in [60, 105] mph |
| DQ-13 | accuracy | Plate speed sits the right distance below release speed | mean gap in (5, 12) mph |
| DQ-14 | validity | Squared-up percentage is in range | 99%+ in [0, 1.15] |
| DQ-15 | consistency | Season receipts reconcile to the source BIP total | equal |
| DQ-16 | consistency | Phase receipts reconcile to the 2026 BIP total | equal |
| DQ-17 | timeliness | Data is no more than 3 days stale | `today − max(game_date) ≤ 3` |
| DQ-18 | completeness | Enough 2026 contact to publish a phase split | BIP ≥ 150 |
| DQ-19 | validity | Exit velocity is within physical bounds | 99.9%+ in [5, 125] |
| DQ-20 | consistency | Exactly 2024/2025/2026 are marked measured | set equality |
| DQ-21 | uniqueness | The peer pool has one row per player-season | no fan-out |
| DQ-22 | completeness | At least 20 receipts written | count |
| DQ-23 | accuracy | Zero-coverage seasons carry a null mean, not a filled one | `isna().all()` |
| DQ-24 | validity | The rolling window size never drifts | `min(window_n) == 60` |

### Why four rules for one policy

The DPO's decision — *no imputation, coverage gate* — is a **policy**, and policies erode. DQ-08/09 assert the **source** has no pre-sensor values (catching an upstream data change that silently backfills). DQ-10/11 assert the **output** publishes none (catching a code change that removes the suppression pass). Source and output are checked separately because either can fail without the other.

**This is the mechanism that makes the governance decision durable rather than aspirational.** A future maintainer who deletes the suppression loop gets a red build, not a plausible-looking chart.

---

## 2. `data-quality-engineer` — scorecard

**Result: 24/24 PASS, 0 FAIL, 0 WARN.**

| Dimension | Rules | Pass |
|---|---:|---:|
| Uniqueness | 3 | 3 |
| Validity | 7 | 7 |
| Consistency | 4 | 4 |
| Completeness | 5 | 5 |
| **Accuracy** | **6** | **6** |
| Timeliness | 1 | 1 |

Selected evidence:

| Rule | Observed |
|---|---|
| DQ-01 | 0 duplicate pitch keys |
| DQ-03 | name-filter contamination ids: **none** |
| DQ-06 | launch-angle coverage on BIP: **0.995** |
| DQ-07 | 2026 bat-speed coverage on swings: **0.981** |
| DQ-08 | pre-2024 bat-speed values in source: **0** |
| DQ-09 | pre-2025 attack-angle values in source: **0** |
| DQ-13 | release − plate speed: **7.18 mph** |
| DQ-15 | season-spine BIP 3,285 == source BIP 3,285 |
| DQ-16 | phase-split BIP 242 == 2026 BIP 242 |
| DQ-17 | max `game_date` 2026-08-07, **1 day** stale |
| DQ-18 | 2026 BIP available: **242** (min 150) |

Receipt: `dq_scorecard`.

---

## 3. `join-validator` — short by design

This product performs **one concat and a set of 1:1 left-merges onto a self-built spine.** There is no cross-entity join, no lineup reconstruction, no external cache, no manual carry-in. The fan-out and grain-drift failure classes that dominated `uc-pos-007` (union fan-out) and `uc-pos-008` (slot reconstruction) are **structurally absent**.

| Operation | Keys | Expected | Observed | Verdict |
|---|---|---|---|---|
| `concat(schwarber.parquet, pos)` | — | year-disjoint, 0 overlap | 11,449 + 13,442; **0 duplicates dropped** | ✅ |
| KPI blocks → season spine | `game_year` | 1:1 | 12 rows in, 12 out | ✅ |
| KPI blocks → phase spine | `phase` | 1:1 | 2 in, 2 out | ✅ |
| KPI blocks → `phase × pitch_group` | 2 keys | 1:1 | 8 in, 8 out | ✅ |
| KPI blocks → `phase × velo_band` | 2 keys | 1:1 | 8 in, 8 out | ✅ |
| Peer pool → `player_name × game_year` | 2 keys | 1:1, no fan-out | 83 rows, 0 duplicates (DQ-21) | ✅ |
| Row-count reconciliation | — | totals preserved | DQ-15, DQ-16 both equal | ✅ |

**Zero exceptions.** The only nulls introduced by a merge are the deliberate coverage-gate nulls (03 §3), which are asserted rather than tolerated.

**Note for the roster.** The absence of joins is a *design* achievement — the architect chose a single-grain model with no intermediate materialisation (04 §1.2). It is worth preserving in future single-entity products.

---

## 4. `data-engineer` — build notes

**Artefact:** `dp_uc32_schwarber_swing_decay.py` — 24 receipts, 5 figures, 1 headline JSON.

### Specs implemented, nothing invented

Every KPI in the build maps to a spec in 04 §3. The locked kernel (`whiff_rate`, `chase_rate`, `barrel_rate`, `hard_hit_rate`, `ev90`, `inds`) is inherited **byte-identical** from `Baseball Functions.ipynb`. The counting kernel is a slim local re-implementation of `nresults` with the identical event classification, kept local so the build has no notebook dependency.

### Defects encountered and fixed during build

**B-1 — Nullable-dtype masking failure.** `TypeError: boolean value of NA is ambiguous` on the first `np.where` over `launch_angle`. Statcast parquet stores several columns as pandas extension dtypes (`Int64`/`Float64`); `pd.NA` short-circuits boolean evaluation.
*Fix:* `coerce_numeric()` casts 27 numeric columns to numpy `float64` once at hop 3, before any masking. Applied to the peer pool as well as the locked frame so the two paths cannot diverge.
*Why it matters beyond this build:* any future agent masking on a Statcast numeric column will hit this. It belongs in `references/data-quality.md`.

**B-2 — Categorical `groupby` length mismatch.** `pd.cut` returns an ordered Categorical; `groupby` over a multi-key level containing one then emits all category combinations, and the merge against a non-categorical spine raised `ValueError: Length of values (7) does not match length of index (8)`.
*Fix:* `.astype(str)` on all three binned columns, with `observed=True` on the single-key path. Bin ordering is reasserted explicitly where display order matters.

**B-3 — Plate-speed derivation.** First implementation used `release_speed` in the squared-up formula. Statcast's constants are calibrated on **plate** speed; the substitution would have inflated max-EV by ~7 mph and systematically depressed SW-4. *Fix:* exact kinematic solve from the 9P trajectory fit, gated by DQ-12/13/14. Caught at spec review, before it reached a receipt.

**All three were fixed at build time, not after publication.**

### Receipt discipline

`receipt()` is the only path to disk. No number reaches the report, PDF or dashboard except through a CSV. The dashboard builder **computes nothing** — it reads receipts and inlines them. This is asserted by V-51 (every receipt cited in the report exists) and by the dashboard's own footer.

### Figures

Five, Phillies brand (`#E81828` / `#002D72` / `#7A99C2`), matplotlib Agg, 150 dpi. Every figure's series is drawn from a named receipt:

| Figure | Receipt | Point |
|---|---|---|
| `fig1_rolling_damage` | `b3_rolling_bip_2026` | Sweet spot held, damage did not |
| `fig2_speed_vs_output` | `b4_rolling_swings_2026`, `b3_rolling_bip_2026` | The engine is intact; the transfer is not |
| `fig3_la_distribution` | `c1_la_distribution` | Contact moved out of the damage band |
| `fig4_imputation_harm` | `x1_imputation_harm` | Imputation would have drawn a nine-season trend never measured |
| `fig5_swing_path` | pitch spine (distributions) | Swing shape is unchanged |

### Exit behaviour

The build exits non-zero on any DQ failure. A red build cannot silently produce a PDF.
