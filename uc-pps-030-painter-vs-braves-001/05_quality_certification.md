# 05 · Quality & Certification — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Quality & Certification department
Agents: `data-quality-engineer`, `certification-agent`

---

## 1 · Scope disclosure (read this first)

This package grades **185 plate appearances**. That is a deliberate choice, not an accident of the cache: the
full 2026 season offers 484, and 62% of the sample was given up because the arsenal changed by 37% of its
pitches in the middle of it. Everything below should be read against that number.

Three things this package does **not** do, each with cause:

- **No arm-slot or release-point analysis.** `arm_angle` is 54% null (DQ-6 **FAIL**). The `uc-pps-023`
  arm-spread finding is not refreshed and must not be quoted as current.
- **No Holmes season profile.** The repo holds 260 Holmes pitches, all against Philadelphia. Every Holmes
  number carries that bound.
- **No claim of league-relative standing.** The grades are relative to a Phillies-schedule population (SG-2).

## 2 · DQ scorecard

19 checks. **17 PASS · 1 WARN · 1 FAIL.**

| # | Dimension | Rule | Result | Detail |
|---|---|---|---|---|
| DQ-1 | Uniqueness | No duplicate `(game_pk, at_bat_number, pitch_number)` | **PASS** | 1,861 rows, 0 duplicates |
| DQ-2 | Validity | Entity lock is an MLBAM id resolving to one `player_name` | **PASS** | 691725 → Painter, Andrew |
| DQ-3 | Validity | `game_type == 'R'` only | **PASS** | 52 spring pitches excluded upstream |
| DQ-4.plate_x | Completeness | populated on every post-option pitch | **PASS** | 0 / 720 null |
| DQ-4.plate_z | Completeness | " | **PASS** | 0 / 720 |
| DQ-4.zone | Completeness | " | **PASS** | 0 / 720 |
| DQ-4.release_speed | Completeness | " | **PASS** | 0 / 720 |
| DQ-4.pfx_x | Completeness | " | **PASS** | 0 / 720 |
| DQ-4.pfx_z | Completeness | " | **PASS** | 0 / 720 |
| DQ-5 | Completeness | `release_extension` populated | **WARN** | 1 / 720 null — excluded from the mean, never imputed |
| DQ-6 | Completeness | `arm_angle` populated | **FAIL** | **387 / 720 null (54%)** — arm-slot analysis descoped |
| DQ-7 | Completeness | xwOBA populated on every PA-ending pitch | **PASS** | 2 nulls (`truncated_pa`, `sac_bunt`) |
| DQ-8 | Consistency | xwOBA on K == 0, on BB == season wBB | **PASS** | Confirms the field is PA-grain xwOBA, not xwOBAcon |
| DQ-9 | Accuracy | Every population meets the minimum or is stamped THIN | **PASS** | FF 232 · ST 29 THIN · CH 56 · SL 92 · SI 138 · CU 45 |
| DQ-10 | Validity | No grade below the subject pitch/swing floor | **PASS** | CU (16 pitches) ungraded |
| DQ-11 | Accuracy | z-grade and rank-grade agree within 10 | **PASS** | Max divergence 5 (slider command). No flag fired |
| DQ-12 | Timeliness | Log current through anchor; target D+1 | **PASS** | 2026-09-12 → 2026-09-13 |
| DQ-13 | Validity | Opponent starter id confirmed, not inferred | **PASS** | 656550 = Grant Holmes, externally confirmed |
| DQ-14 | Consistency | AAA carries no wOBA weights, enters no MLB rate | **PASS** | 396 AAA rows loaded unweighted, context only |

**The FAIL is load-bearing and was honoured.** DQ-6 did not produce a caveat; it produced a descope. A 54%-null
biomechanical field cannot carry a distributional claim, and the `uc-pos-009` sensor-boundary rule forbids
imputing across an instrument gap. The prior UC's most distinctive finding is therefore **absent** from this
package rather than restated at lower confidence.

## 3 · Defect register

**No new kernel defects found.** Six known defects were read against this build and measured, not assumed
inapplicable:

| Defect | Exposed | Reading | Remediation |
|---|---|---|---|
| D-1 / D-2 | **NO** | Every post-option pitch type recorded ≥1 whiff, so the inner join loses nothing *here*. It still drops the curveball on a handedness split — asserted in verification family F so the defect stays visible | build-local `wr_safe()`; kernel untouched |
| D-7 / O-13 | **NO** | 0 null `zone` in the graded window | `in_zone_rate` computed as `(zone<=9).mean()` |
| O-8 | **NO** | 0 of 123 post-option BIP untracked | Hard-hit still printed as hits / **tracked** BIP with both counts |
| O-5 | **YES** | 1 `truncated_pa` in 185 PA | Disclosed; effect < 1 part in 185 |
| O-3 | N/A | No exit-velocity KPI | — |
| O-7 | N/A | No directional KPI | — |

## 4 · Independent verification — 247 / 247 PASS

`dp_uc44_verification.py` reloads from the parquet rather than trusting the build's receipts, then reconciles
everything the report and the card publish. Log: `out/dp_uc44_verification_log.txt`.

| Family | Checks | What it proves |
|---|---|---|
| **A** · Lock / scope / freshness | 14 | Entity lock is an id and resolves to one player; **the build source contains no `player_name ==` filter anywhere**; regular season only; no duplicates; anchor matches the pin; windows partition the season; 8 and 14 starts |
| **B** · SG-1 transform correctness | 14 | Grade at the mean is 50; +1σ is 60; −2σ is 30; clips at 20 and 80; direction flip inverts; NaN in → NaN out; n<5 → NaN; zero-variance → NaN; **rounding is half-up, not banker's**; the divergence flag fires at 10 and not at 9; a genuinely skewed population trips it; `pitch_grade` is the mean and is NaN if either input is; the label vocabulary is monotone |
| **C** · SG-2 population construction | 43 | Every population size reproduces; the floor rule is honoured; the THIN flag is set **iff** the floor was lowered; every member clears the floor; the pool is RHP-only; pitcher-season grain has no duplicates; the pool spans both roles; **all twelve Shapiro-Wilk p-values reproduce**; the report names exactly the three populations that fail normality; 11 of 12 grades are identical z-derived and rank-derived; the one divergence is slider command at 5 points; no grade trips the flag |
| **D** · Receipt consistency | 64 | Every grade-table figure recomputes from the frame; every stuff grade re-derives from its own population; every pitch grade is the mean of its two inputs; the gates hold; usage sums to 1; the arsenal grade is the usage-weighted mean; every platoon cell recomputes; the start log's BF and pitches sum to the season; `mix_by_stand` sums per window × stand; turnover usages each sum to 1; AR-1 index = added + dropped; added is exactly `[CH]` and dropped exactly `[FS]`; H2H is 47 PA from exactly the two April dates |
| **E** · Narrative reconciliation | 40 | **Every number asserted in the report markdown**, recomputed and string-matched: the four-seam trade (.218 / 17.0" / .349 / .422 / .106); the splitter (.395 on 76 swings, last thrown 06-17, zero since); the changeup (.301 on 73 swings, .160 / .178 / .452 / .130); the sweeper leak (.645 / .200 / .523 on 9 PA); the platoon (.322 / .238, 29.7% / 18.1%, z = −1.78, p = .075); the FS-vs-CH test (z = 1.20, p = .23); Houston (27 BF / 6 K / 2 BB / 2 HR / .438 / .550 / 8 of 19); **the figure-5 title claim**; the four-of-five home-run claim; breaking IZR .477 → 55; efficiency (90.0 pitches, 23.1 BF, .612 → .638); six of nine Atlanta bats left-handed; Acuña .447 / Harris .436 / Riley .374; Holmes 260 / 69 / .372 and 87% two-pitch vs RHH; the tag-drift control; the arsenal grade 50 vs 45; both turnover indices; max H2H PA = 7 |
| **F** · Defect exposure | 8 | Every exposure claim in `03` §5 and `05` §3 is true; D-1 still reproduces as a live defect on a handedness split; the xwOBA field is PA-level; the arm-slot descope is warranted; AAA rows carry no weight columns |
| **G** · Deliverables | 64 | All 24 receipts, 5 figures, payload and log present; all 8 deliverables present; the PDF is non-trivial; **the dashboard contains no external `src=` or `<link>`**; every figure the report references exists; the report declares the entity lock, the population bias, and prints the 9-PA denominator |

Family E is the one that matters. It exists because a report is a set of claims, and a claim that no longer
reconciles to its receipt is the failure mode that governance is for. Four assertions in family E **failed on
the first run** and each one was a real error in the draft report:

1. A Shapiro-Wilk p-value quoted for the sweeper (.833) was computed at the 100-pitch floor, while the
   population actually used sits at the lowered floor — where it is **.015 and fails**. The report now names
   the three populations that fail normality, which is a materially better disclosure than the one it
   replaced.
2. "Five of nine Atlanta bats are left-handed" — it is **six**.
3. "Divergences of 0.0 across the board" — eleven of twelve, not twelve.
4. A precedence bug in the harness itself (a chained `==`), which was masking a defect-exposure check.

Three of the four were errors the prose would have shipped. That is the return on the harness.

## 5 · Certification decision

**READY-CONDITIONAL.** Certified for internal, need-to-know distribution for the 2026-09-13 start.

| Condition | Statement |
|---|---|
| **C1** | Valid for the 2026-09-13 start only, anchored to a log ending 2026-09-12. The build refuses a different anchor |
| **C2** | Grades are relative to a **Phillies-schedule population**. Any external use of a grade must carry that sentence |
| **C3** | Sweeper grades are **THIN** (n = 29 at a lowered floor). Read ±1 grade |
| **C4** | The platoon split is **directional** (p = 0.075), published because it aligns with a mechanism and tonight's lineup — not because it clears a threshold |
| **C5** | Arm-slot analysis is **descoped with cause**; the `uc-pps-023` arm-spread finding must not be restated as current |
| **C6** | All seven new governed objects are **provisional**. No downstream build may treat SG-1 as ratified |

Blocking issues: **none**. External publication: **blocked** (`data-tagger`, Internal — Restricted).

## 6 · Versioning

v1.0.0. Breaking-change policy in `03` §8. The four changes that silently move every grade — population scope,
floors, the shape-exclusion rule, and the rounding/clip — are all major-version changes by policy.
