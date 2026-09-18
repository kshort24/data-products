# 05 · Data Quality Rules & Scorecard
**`dp_uc46` · 18 rules defined, 18 executed against Phillies `pos` 2024–2026 (`game_type=='R'`, 12,360 BIP)**
**Result: 17 PASS · 1 WARN · 0 FAIL.** Machine-readable: `out/10_dq_scorecard.csv`.

## 1. Dimensions covered

completeness · uniqueness · validity · accuracy · consistency · timeliness ·
conformity · **traceability**

Traceability is the dimension opened on uc-pos-016 (family F). Here it does real
work: DQ-14 asserts that a cell whose sensor count is *below* its population
**shows** that gap rather than quietly presenting a mean over fewer observations
than the reader assumes.

## 2. Scorecard

| ID | Dimension | CDE | Rule | Status | Observed |
|---|---|---|---|---|---|
| DQ-01 | completeness | `hc_x`,`hc_y` | Untracked BIP ≤ 2% of all BIP | **PASS** | 9 / 12,360 = 0.073% |
| DQ-02 | completeness | `bb_type` | Never NULL on a BIP (complete classifier) | **PASS** | 0 NULL |
| DQ-03.la | completeness | `launch_angle` | NULL share on BIP ≤ 2% | **PASS** | 26 / 12,360 = 0.210% |
| DQ-03.ev | completeness | `launch_speed` | NULL share on BIP ≤ 2% | **PASS** | 31 / 12,360 = 0.251% |
| DQ-03.dist | completeness | `hit_distance_sc` | NULL share on BIP ≤ 2% | **PASS** | 40 / 12,360 = 0.324% |
| DQ-04 | uniqueness | `PITCH_KEY` | No duplicate `game_pk`/`at_bat_number`/`pitch_number` | **PASS** | 0 duplicates |
| DQ-05 | validity | `launch_angle` | Within [−90, 90] | **PASS** | [−90.0, 89.0] |
| DQ-06 | validity | `launch_speed` | Within [5, 130] mph | **PASS** | [11.5, 117.2] |
| DQ-07 | accuracy | `hit_distance_sc` | `== 0` is a placeholder, not a measurement; count must be disclosed | **WARN** | 22 rows, all `ground_ball` |
| DQ-08 | validity | `hit_direction` | Every classifiable BIP gets Pull/Straightaway/Oppo | **PASS** | 0 `not grouped` |
| DQ-09 | validity | `stand` | Exactly `{'L','R'}` | **PASS** | `['L','R']` |
| DQ-10 | consistency | direction rates | Three rates sum to 1 in every cell (DR-3) | **PASS** | max \|dev\| = 0.00e+00 |
| DQ-11 | consistency | direction counts | `pull_n + straight_n + oppo_n == n_bip` | **PASS** | all cells |
| DQ-12 | consistency | `bb_type` share | Shares sum to 1 within each level cell | **PASS** | max \|dev\| = 0.00e+00 |
| DQ-13 | consistency | profile `n` | Each `n_*` ≤ `bips` in its cell | **PASS** | 0 violations |
| DQ-14 | **traceability** | profile `n` | Sensor gaps are visible, not zero-filled | **PASS** | 8 cells carry a visible gap |
| DQ-15 | timeliness | `game_date` | Source current within 7 days | **PASS** | max 2026-09-16 |
| DQ-16 | conformity | `below_floor` | FL-1 flag present on every published directional frame | **PASS** | 3 of 20 player cells suppressed |

## 3. The one WARN — DQ-07

22 ground balls across 2024–2026 carry `hit_distance_sc == 0`. Zero feet is not a
plausible measurement for a batted ball that reached the field of play; it is a
sensor placeholder living inside the non-null population, where `count()` will
include it and `min()`/`mean()` will be pulled toward it.

**Not remediated, deliberately.** Three reasons:

1. Filtering a published value on suspicion is a larger governance problem than
   reporting it with a flag. The Register's Principle 2 posture — implement the
   received definition, not the better one — applies to values as well as formulas.
2. The effect is bounded and one-directional: it can only depress `min_dist` and
   `mu_dist` on ground-ball cells, which are already the cells no one reads for
   distance.
3. Deciding it is a placeholder rather than a real zero requires domain
   adjudication this build has no standing to make.

**Escalated to the DPO** as the one open DQ item. Options if ratified as a
placeholder: (a) treat as NULL in the profile arm only, (b) add `n_dist_zero` as a
disclosed column, (c) leave as-is with the WARN standing. Recommendation: **(b)** —
it preserves the received value and makes the contamination countable.

## 4. Rules that would catch a future regression

These are the three worth carrying into the observability runbook:

- **DQ-08 + the `assert_spray_convention` control.** If Statcast ever flips the sign
  of `hc_x`, every directional KPI inverts and every rate stays plausible. Nothing
  else in the repo would notice. This pair is the only detector.
- **DQ-10.** A sum-to-1 violation means someone has added a fourth direction or
  changed the wedge boundary without updating the family.
- **DQ-13.** `n_* > bips` means a merge has fanned out — the failure mode that
  `join-validator` exists for, caught at the column level.
