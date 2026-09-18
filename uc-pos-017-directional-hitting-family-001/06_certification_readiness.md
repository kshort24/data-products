# 06 · Certification Readiness
**`dp_uc46` v1.0.0 · audited against the Function Certification Checklist (`07`) · 2026-09-17**

## 1. Gate audit, per function

| Function | G1 search | G2 glossary | G3 lineage | G4 dict | G5 DQ | G6 fixture | G7 sig/name | G8 census | G9 verdict | G10 binding |
|---|---|---|---|---|---|---|---|---|---|---|
| `hit_direction` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `derive_loc` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `classifiable_bip` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `assert_spray_convention` | ✅ | n/a | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `direction_rate` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `bb_type_profile` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |
| `pull_air_rate` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ |

**Gate 10 is ⚠ for the entire library, for one environmental reason (C-3), not seven.**

## 2. Evidence

| Gate | Artifact |
|---|---|
| 1 | `01` §1 — commands, scope, per-element disposition, alias reconciliation |
| 2 | `02` §2 — 12 terms, duplicate check, one named unresolved conflict (O-20) |
| 3 | `03` — column-level table + transformation chain |
| 4 | `04` — 10 consumed, 30+ published columns |
| 5 | `05` + `out/10_dq_scorecard.csv` — 18 rules, **17 PASS / 1 WARN / 0 FAIL** |
| 6 | `dp_uc46_verification.py` family A — **27 fixture checks**, expectations hand-derived in the module docstring before the code ran |
| 7 | `(level, df)` on all seven public functions; four aliases reconciled to two governed names |
| 8 | `01` §1 — prior-art table doubles as the census; three inline redefinitions logged |
| 9 | This document |
| 10 | `03` §4 — sources of truth named; hash mechanism absent (C-3) |

## 3. Verification

**130 / 130 PASS.** Families A–E: 49/49 (`dp_uc46_verification.py`) · Family F: 74/74 (`dp_uc46_family_f.py`) · Gate 7: 7/7 (`dp_uc46_notebook_reconcile.py`).

| Family | Checks | What it can detect |
|---|---|---|
| A — hand-computed fixture | 27 | A wrong formula. The only family that can. |
| B — real-data invariants | 7 | Sum-to-1 violation, fan-out, convention inversion, floor breach |
| C — parent reproduction vs `dp_uc42` | 7 | Silent drift from the promoted provisional |
| D — share arm vs cell 50 | 4 | Drift from the governed `bb_type_by_level` |
| E — sensor-boundary conduct | 4 | Zero-fill leakage, per-sensor `n` collapse, empty-input crash |
| F — narrative/receipt reconciliation | run separately | A figure in prose that no receipt supports |

Family A includes a **negative control**: `assert_spray_convention` is fed an
inverted frame and the test passes only if it *raises*. A control that cannot fail
is not a control.

## 4. Superseded implementations

| Superseded | Location | Disposition |
|---|---|---|
| `hit_direction` (embedded) | `Baseball Functions.ipynb` cell 56 | Patched — cell now imports the extracted function |
| `hit_direction` (transcribed) | `dp_uc37_kernel.py:461`, `dp_uc40_kernel.py:471`, `dp_uc42_kernel.py:87` | **Left in place.** Delivered, certified packages whose own verification runs against them. Logged as deprecated; migrate on their next revision, not retroactively. |
| `pull_air_rate_fix` | `dp_uc37_kernel.py:479`, `dp_uc40_kernel.py:489` | Promoted into `pull_air_rate`; the `_fix` name retires |
| `pulled_air(df, level)` | `dp_uc24:154`, `dp_uc31:208`, `marsh_breakout_analysis:151` | **Deprecated, inverted signature.** Not patched — see `00` §4 |
| `directional_rate_table` | `dp_uc42_kernel.py:144` | Promoted into `direction_rate`; numerically identical (family C) |

**Standing rule established:** a delivered package's code is not edited to adopt a
later governance decision. It is marked superseded and migrated at its next
revision. Silently changing a shipped artifact's behaviour breaks the only thing
its verification receipt was ever good for.

## 5. Privacy

**LOW.** Aggregate batted-ball outcomes for professional players, at or above a
25-BIP floor, derived entirely from publicly published Statcast tracking. No PII,
no quasi-identifiers beyond `player_name` (which is the subject, not an identifier
to be protected), no health or availability inference, no deployment or evaluation
framing. Classification: **Internal**. No external-publish block required, but the
library inherits whatever classification the consuming data product carries.

## 6. Open items

| ID | Item | Owner | Blocking? |
|---|---|---|---|
| **C-1** | Any grain finer than player×season must carry FL-1 suppression | consuming UC | No — conduct rule |
| **C-2** | `hit_distance_sc` ground-ball statistics WARN-flagged pending DQ-07 adjudication | DPO | No |
| **C-3** | `impl_hash` UNAVAILABLE — no mechanism in this environment. F1. Closed by the `get_function_source` MCP tool (`MCP_SERVER_DESIGN` §4.5) | DPO / engineering-lead | No — environmental |
| **O-20** | `mu_la` (this build) vs `la_mu` (`inds`, cell 42) naming conflict; 74 call sites | DPO | No |
| **O-21** | `(level, df)` lint rule specified in `00` §4 but **not built** | engineering-lead | No |
| **O-22** | Three deprecated `pulled_air(df, level)` copies awaiting migration | consuming UCs | No |
| **N-2** | Bat-path columns (`bat_speed`, `swing_length`, `attack_angle`) deferred to v1.1.0 pending O-14 sign resolution | DPO | No — scoped out |

## 7. Verdict

> **CONDITIONALLY CERTIFIED** — all seven functions, conditions C-1 through C-3.
>
> Gates 1–9 pass for every function. Gate 10 is open for the library as a whole on
> a single environmental cause with a designed remedy already on the roadmap.
>
> The library is publishable and consumable now. **O-7 is CLOSED**: the guidebook's
> directional function executes against the live schema for the first time since it
> was written.

**Publish decision is the human DPO's.** This document is a readiness report, not
an approval.

---

## 8. What family F caught (addendum, post-reconciliation)

Family F ran 74 checks recomputing every headline figure in the report and the
notecards from the shipped receipts. It failed five on the first pass. All five
are recorded because each is a different defect class and two of them were in the
verification harness itself.

| ID | Class | Finding | Remediation |
|---|---|---|---|
| **V-2** | display rounding | Receipts stored at 4dp, then re-rounded to 1dp for prose, diverged from the raw value: 2025 oppo rate reads 29.2% from the receipt and 29.3% from the underlying 1,238/4,232. | **Receipts re-emitted at 6dp.** Same class as the uc-pos-013 headline-JSON lesson, different mechanism — there it was the JSON, here the CSV receipts themselves. **Recommend 6dp as the repo-wide receipt standard**, not just for headline JSON. |
| **V-3** | rounding-flattered claim | The report asserted two hitters were "over 39%" oppo. One was **38.97%**. The claim was true only at 0 decimal places. | Prose now states both exact rates. |
| **V-4** | harness self-blindness | V-3 **initially passed**, because the family F check formatted its recomputed value at the same precision the prose used. A reconciliation check formatted at the prose's own precision cannot detect a rounding-flattered claim — it reproduces the error and confirms it. | Checks now assert exact values; prose states exact values. |
| **V-5** | harness bug | Two family F checks compared the report's *oppo* rate claim against the recomputed *pull* rate. Wrong column, and it would have failed a correct report. | Fixed. |
| **V-6** | prose/harness form | "more than four times" (word) vs `more than 4 times` (harness). | Prose uses digits where a figure is checked. |

**V-4 is the one worth carrying forward.** The lesson from uc-pos-016 was that
narrative and receipts drift. The lesson here is one level up: **the reconciliation
harness is not automatically correct, and it can be wrong in a way that certifies
the error it was built to catch.** Two of five first-pass failures were the
harness's own. It needs the same fixture discipline as the functions it checks
(Gate 6), and a check that formats at the prose's precision is not a check.

Final: **49/49 (families A–E) + 74/74 (family F) = 123/123 PASS.**

---

## 9. Gate 7 reconciliation — the patched notebook vs the certified module

`dp_uc46_notebook_reconcile.py` executes the **guidebook's own new code cells**
against real data and asserts their output is byte-identical to `dp_uc46_kernel`.

```
executed notebook cells 58 and 56 -- no exception
  [PASS] build_bip frame
  [PASS] direction_rate['game_year']
  [PASS] direction_rate['game_year', 'stand']
  [PASS] direction_rate['player_name', 'game_year']
  [PASS] bb_type_profile[game_year]
  [PASS] bb_type_profile[game_year, hit_direction]
  [PASS] pull_air_rate[game_year]
GATE 7 RECONCILIATION: 7/7 PASS
```

The notebook independently reproduces the report's headlines: 2026 pull 45.7% /
straightaway 24.5% / oppo 29.8%, `oppo_ld_rate` 25.17%.

### V-7 — the defect this gate caught, on its first run

The first patch application put **two of seven functions** into the notebook cell.
The extraction helper that sliced the kernel into cell-sized pieces searched for
each section's end-marker **from the top of the file** rather than from the section's
own start, so every section whose terminator appeared earlier in the file collapsed
to an empty string. The notebook received `hit_direction` and
`assert_spray_convention` and nothing else — no constants, no `direction_rate`, no
`bb_type_profile`.

**Nothing else in this build would have caught it.** Families A–E test the *module*,
and the module was correct. Family F tests *prose against receipts*, and both were
correct. The notebook — the artifact the DPO actually opens — was the only thing
wrong, and it was wrong silently: the cell parsed, and a reader skimming it would
see a governed-looking function with a long docstring.

This is the same failure mode as the original O-7 defect, reproduced in one build
by the tooling meant to fix it: **a definition that looks certified in the guidebook
and is not what the guidebook says it is.** Remediated by restoring the backup,
fixing the slice, and embedding the payload in the patch script so there is one
file and no cross-file version skew.

**Recommendation, repo-wide:** Gate 7 becomes an executable reconciliation, not a
declaration. Any build that edits the notebook must run its cells and diff them
against the certified module before certifying.

Final: **49/49 (A–E) + 74/74 (F) + 7/7 (Gate 7) = 130/130 PASS.**
