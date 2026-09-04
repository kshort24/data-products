# 05a · Quality & Certification — bat-path addendum
### `uc-pos-014` v1.1.0 · `dp_uc40a` · addendum to `05_quality_certification.md`

| | |
|---|---|
| Independent verification | **180 / 180 PASS** (`dp_uc40a_verification.py`, `out/dp_uc40a_verification_results.csv`) |
| Convention assertions | **12 / 12 PASS** — the build refuses to publish if any hard check fails |
| DQ scorecard | **10 PASS · 3 WARN · 0 FAIL** (`out/dp_uc40a_bp_dq_scorecard.csv`) |
| Reconciliation with v1.0.0 | popup rate agrees to **< 1×10⁻⁹** on both bat-path seasons |
| New open items | **4** — O-15, O-16, O-17, O-18, all disclosed, none silently patched |
| Certification | **READY** — v1.1.0 is additive; v1.0.0 is unchanged and unretracted |

---

## 1 · Verification design

Same contract as v1.0.0: the harness re-reads the parquet with different column-availability handling and
a different batting-side derivation order, re-implements BP-0 by hand, and imports nothing from
`dp_uc40a_kernel` for any value it verifies.

| Block | Checks |
|---|---|
| Sensor boundaries and coverage (2023–2026) | 15 |
| Convention assertions, recomputed independently | 12 |
| BP-1 subject panels (2 seasons × 9 measures) | 20 |
| BP-2 pitch-group panels (2 seasons × 3 groups × 5) | 30 |
| PU-2 popup rates (4 seasons × 3 groups × 3) | 38 |
| PB-1 peer control (5 metrics × 4) | 26 |
| Population placement | 6 |
| Breaking-ball popup pool | 11 |
| PU-1 popup signature | 14 |
| **Report claim audit** — every "largest", "flattest", "not a bat-speed story" re-derived | 12 |
| **Report text scan** — required disclosures present in the prose | 11 |
| **Total** | **180** |

### What the harness pins that prose alone would not

- `report claim: Turner has the flattest plane in the pool` is verified as
  `pool.tilt.min() == pool.loc[Turner]` — not as a percentile that could drift.
- `report claim: popups are NOT a bat-speed story` asserts the popup-vs-other bat-speed gap is **under
  1.0 mph**. If a future refresh reopens that gap, the check fails and the sentence cannot ship.
- `report does not claim a bat-speed collapse on popups` explicitly guards against the pre-BP-0 number
  (63.6 mph) reappearing without its correction note.
- `O-15: attack_direction is pull-NEGATIVE` is re-derived from raw spray geometry, not read from the
  build's own assertion file.

---

## 2 · DQ scorecard

| Status | Rules |
|---|---|
| **PASS (10)** | A-1 path columns absent pre-2025 · A-2 `bat_speed` absent in 2023 · A-3 2026 path coverage 96.1% · A-4 coverage stable 2025↔2026 (Δ 0.010) · A-7 12/12 conventions asserted · A-8 v1.0.0 reconciliation < 1e-9 · A-9 peer control applied to all 7 metrics · A-10 `hyper_speed` used nowhere · A-12 `pitch_group` map verbatim from the data plane |
| **WARN (3)** | **A-5 O-18 bunts excluded** — 0 bunt swings in Turner's 2026 (the rule is still applied and counted; it bites on other hitters) · **A-6 O-18 degenerate swings** — 3 tracked 2026 swings under 25 mph excluded from central tendencies and counted (report-only) · **A-11 swing floor** — one published cell in a bat-path season (Aug–Sep offspeed, 17 tracked swings) is below the 25-swing floor; it is NULL on every measure and carries `below_swing_floor = True`. The six pre-2025 pitch-group cells are the sensor boundary, not a floor breach, and are split out as A-11b |
| **FAIL (0)** | — |

---

## 3 · Defect and open-item register after this addendum

| ID | State | Note |
|---|---|---|
| D1–D4, D6/O-8 | open (inherited) | `_fix` variants used; unchanged by this addendum |
| D5/O-7 (pull-air) | remediated, ratification pending | unchanged |
| D-7/O-13 (`in_zone_rate` NULL zone) | **opened by v1.0.0**, remediated, ratification pending | unchanged |
| **O-15** `attack_direction` inverted vs the published glossary | **NEW — HIGH** | Mitigated by shipping `pull_direction` beside the raw column. **Not** patched at source. A Savant methodology check is the resolution path |
| **O-16** team-wide `swing_path_tilt` drift 2025→2026 | **NEW — MEDIUM** | Mitigated by PB-1 peer-netting, which is now a **standing requirement** for any instrumented year-over-year bat-path claim |
| **O-17** `hyper_speed` = `max(EV, 88)` | **NEW — LOW** | Column excluded from the product; flagged for the glossary |
| **O-18** bat path degenerate on bunts / checked swings | **NEW — MEDIUM** | BP-0 population rule; exclusions counted on every panel |
| O-5, O-11, O-12, F1 | open | untouched |

**Policy held.** No governed function was patched inside a use-case build; no source column was
corrected in place. Every correction ships as a derived sibling (`pull_direction`) or a population rule
(BP-0), with the raw value retained.

---

## 4 · The finding that the governance caught

Worth recording because it is the second consecutive build in which a control changed the headline:

> An early pass over an **ungoverned swing population** showed Turner's breaking-ball popups arriving at
> **63.6 mph** of bat speed against 70.5 on his other breaking-ball contact — a 7-mph collapse, and by
> far the most quotable number in the addendum. Applying **BP-0** (O-18: exclude bunts, flag sub-25 mph
> checked swings) removed a handful of degenerate rows and the gap fell to **−0.5 mph**, inside noise.
>
> **The population rule killed the story.** The report says so in §5 rather than quietly shipping the
> corrected number, and the verification harness now blocks the ungoverned version from reappearing.

In v1.0.0, ST-1 killed a plausible bat-speed decline. In v1.1.0, BP-0 killed a plausible bat-speed
collapse. **Both times the discarded story was about bat speed, and both times the surviving finding was
geometric.** That consistency is itself evidence for the mechanism this addendum reports.

---

## 5 · `version-controller`

| Change | Class | Consumer impact |
|---|---|---|
| v1.0.0 → **v1.1.0** | **additive, non-breaking** | No v1.0.0 number changes. The popup rate reconciles exactly. `uc-pos-014` v1.0.0 remains valid and is not retracted |
| New kernel `dp_uc40a_kernel.py` | additive | Imports and re-exports `dp_uc40_kernel` unchanged |
| **O-15** | **breaking for any future consumer of `attack_direction`** | Anyone reading the MLB glossary convention onto this column inverts their conclusions. Raised to the DPO as **E-8** |
| **O-16** | **process-breaking** | Any prior or future year-over-year bat-path comparison without a peer control is unsafe. No prior UC published one, so there is no retro-correction to make |
| BP-0/1/2, PU-1/2, PB-1 | new, provisional | Ratification required before a third reuse |

## 6 · Certification

| Requirement | State |
|---|---|
| Semantic definitions sourced, not inferred | ✅ `03a` §1, six terms, five cited glossary pages |
| Technical definitions (units, grain, population, null policy) | ✅ `03a` §4 |
| Conventions asserted against data, not assumed | ✅ `03a` §2, 12/12, build-blocking |
| Column-level lineage for every KPI | ✅ `03a` §6 |
| Independent verification | ✅ 180/180 |
| Reconciliation with the parent version | ✅ < 1e-9 |
| Floors flagged wherever they appear | ✅ one below-floor cell, NULL and flagged |
| New defects disclosed on the consumable surface | ✅ report §7, dashboard "Bat path" tab |
| Privacy re-assessed | ✅ `03a` §7, unchanged |

**Certification status: READY.** Publish decision belongs to the human Data Product Owner.

## 7 · Escalations added to `00` §7

| # | Item | Decision needed |
|---|---|---|
| **E-8** | **O-15** — `attack_direction` sign is inverted vs the published MLB glossary | Confirm against Savant methodology, then ratify either the corrected `pull_direction` or a source-level fix. **Until then, no one should use the raw column without reading `03a`.** |
| **E-9** | **O-16** — team-wide tilt drift | Decide whether peer-netting becomes a permanent standing rule for all instrumented bat-path comparisons (recommended: yes) |
| **E-10** | **O-18 / BP-0** — bunt and checked-swing exclusion | Ratify the population rule so future builds inherit it rather than re-deriving it |
| **E-11** | **BP-1 / BP-2 / PU-1 / PU-2 / PB-1** provisional | Ratify before a third reuse |
| **E-12** | **O-17** — `hyper_speed` | Add a deprecation note to the glossary so no future UC treats it as independent |
| **E-13** | **Open-item IDs have no allocator.** A concurrent session claimed O-14 for an unrelated `bbrate` defect while this addendum was in flight; these four items were renumbered +1 before publication | Adopt a single allocator for the O-series (suggest: the ledger patch file is the claim, and an ID is only live once the row is pasted) |
