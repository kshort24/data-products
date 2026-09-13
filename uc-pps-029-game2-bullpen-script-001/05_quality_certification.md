# 05 · Quality & Certification — `uc-pps-029-game2-bullpen-script-001`

**UC #43 · `uc-pps-029` · `dp_uc43` · v1.0.0**
**Agents:** `data-quality-engineer`, `certification-agent`, `version-controller`

## 1 · Scope disclosure (read this first)

This is a **pre-game decision-support build on a T-1 log**, not a season study. Three things follow:

1. Every availability figure is a snapshot taken against a specific target date, and the target date is not
   fully resolved (`01` G-1). Both framings ship; one of them is not certifiable.
2. The debutant's entire evidence base is Triple-A. It is labelled as a supporting tier on every surface and
   no rate from it is blended with an MLB rate.
3. The opposing starter's identity is **inferred**. The Statcast frame carries no name for opponent pitchers.

## 2 · DQ scorecard

Receipt: `out/dp_uc43_dq_scorecard.csv`. 12 checks across 8 dimensions.

| Dimension | Check | Result | Status |
|---|---|---|---|
| completeness | PHI pitching rows with null `pitch_type` | 0 / 22,021 | **PASS** |
| completeness | Holman AAA rows missing velo / break / location | 0 / 348 | **PASS** |
| validity | entity lock — every subject by MLBAM id, zero name filters | 9 / 9 ids | **PASS** |
| uniqueness | duplicate `(game_pk, at_bat_number, pitch_number)` | 0 | **PASS** |
| consistency | `game_type` — regular season only on both frames | `['R']` | **PASS** |
| timeliness | PHI log vs target D+1 | 2026-09-11 vs 2026-09-12 (T-1) | **PASS** |
| timeliness | PHI log vs session date D+2 | 2026-09-11 vs 2026-09-13 (T-2) | **FAIL** |
| timeliness | AAA log vs target; subject's last logged pitch | T-6; T-13 | **WARN** |
| comparability | AAA wOBA suppressed (LV-1 / DQ-5) | weights absent, MLB constants not imported | **PASS** |
| accuracy | opposing-starter identity | inferred from 4 constraints, not independently confirmed | **WARN** |
| traceability | every report figure recomputable from a shipped receipt | family F, 54 checks | **PASS** |
| volume | Holman AAA sample | 104 PA / 348 pitches / 20 outings | **PASS** |

**One FAIL, deliberately shipped.** The D+2 timeliness check fails by construction: under the session-date
framing the cache may be missing a game. Rather than suppress the framing or pretend the check passes, the
D+2 ledger ships with the failure attached and the report says in its first paragraph that it is not
certifiable. This follows the `uc-pos-015` precedent of a DQ FAIL shipping under an explicit
READY-CONDITIONAL rather than being rounded away.

## 3 · Defect register

### Found in this build (both **NEW**, both repo-wide)

| ID | Severity | Summary |
|---|---|---|
| **D-8** | **High** | `appearance_summary` returns `is_start = pd.NA` for every non-starter on a single-team frame (484 of 632 here). `pitcher_season_workload(relievers_only=True)` consequently returns an **empty DataFrame, silently, with no error**. Any prior analysis that called the governed bullpen pipeline and got "no relievers" got a bug, not a result. |
| **D-9** | Medium | `measure_calcs` unconditionally renames a column named `batter` to `pitches`, so `nresults(['batter'], df)` raises `KeyError`. Blocks every per-batter results table through the governed path. |

Both are reproduced as live assertions in verification family D, so a future run detects the day they are
fixed upstream. Both are remediated **build-locally**; the locked functions are untouched, per standing
policy.

### Known defects, exposure measured (not assumed inapplicable)

`out/dp_uc43_defect_exposure.csv`, summarised in `03` §5. Net effect on this deliverable: **D-1 zero**,
**D-7/O-13 ≤0.22% on MLB and nil on AAA**, **O-3 respected**, **O-8 avoided by not shipping the KPI**,
**O-14 disclosed in the wording**, **O-10 is the reason the opponent identity is a WARN**.

## 4 · Independent verification — 171 / 171 PASS

`dp_uc43_verification.py`. Receipt: `out/dp_uc43_verification_results.csv`.

| Family | Checks | What it proves |
|---|---|---|
| **A** source & entity integrity | 21 | Frames are regular-season, role-correct, de-duplicated, dated as claimed; all 10 entity locks resolve by MLBAM id; Holman has zero MLB pitches and zero 2025 AAA pitches; **no name-based filtering appears anywhere in the build script**. |
| **B** KPI recomputation, second code path | 63 | Pitch mix recomputed with `value_counts`, whiff and chase recomputed from raw `description`/`zone` masks, the appearance ledger recomputed by `groupby`, rest days recomputed by `diff`, BS-2 capacity and the 37-BF benchmark recomputed from the raw frames — none of it through the kernel functions that produced the receipts. |
| **C** cross-receipt consistency | 14 | The sensitivity table matches both ledgers; exactly five tiers move; Alvarado is AMBER under both; the anchor game has five relievers and one starter and Alvarado is flagged un-named; three of the first four Braves hitters bat left against a lefty; the opposing starter reached the 6th all three times; all four AAA home runs were to LHB. |
| **D** defect exposure | 9 | D-8 and D-9 both **reproduce live** (484 `<NA>`; the empty frame; the `KeyError`); D-1 dropped no group here; `hard_hit_rate` is genuinely absent from the AAA deliverables; no wOBA column exists anywhere on the AAA tier. |
| **E** deliverable integrity | 18 | Every file and figure present; PDF non-trivial; **the dashboard loads no external code** (regex over every `src`/`href`; fonts-only allowance); data is inlined; both themes are declared at token level and `body` paints an explicit background. |
| **F** narrative / receipt reconciliation | 54 | Every headline figure in the report prose, the README and the dashboard markup is recomputed from the shipped receipts **and** string-matched against the text — 29.7, 37, 7.3, 2.4, 147, 106, 38.1, 37.4, "1 of 56", "1 of 61", "15 of 40", "16 of 50", "8 of 20", the per-arm 7-day loads, the anchor pitch counts, Holman's usage/velo/FPSR, the splitter drift, the platoon split, the zero-HR-in-70-PA claim. The harness's **own size claim** is checked last, against the size it actually reached. |

Family F exists because of **V-1** (`uc-pos-016` v1.1.0), where a superseded draft figure survived into the
README and the ledger patch while the receipts and report agreed. It cost ~4k output tokens there and caught
the defect. It cost about the same here and found nothing — which is the outcome you pay for.

## 5 · Certification decision

**READY-CONDITIONAL.** Publish internally now. Five conditions travel with it:

1. **The target game must be confirmed before the ledger is acted on.** Five of nine availability tiers move
   between D+1 and D+2. If the target is 2026-09-13, refresh the cache first — the D+2 column as shipped is
   computed from a log that may be a game short, and the build says so rather than hiding it.
2. **The opposing-starter section is conditional on the identity inference.** Everything in the report's §8
   is correct *for MLBAM 641816*. If that is not Mahle, §8 describes the wrong pitcher; nothing else changes.
3. **BS-1, BS-2 and BS-3 are provisional and unratified.** Do not promote them to APPROVED until an
   independent second use. BS-1's cut-points in particular are this build's judgment, not a governed standard.
4. **The AAA tier must not be re-quoted out of context.** Holman's rates describe International League
   hitters. The mix and the shape travel; the rates do not.
5. **The recommended revision (report §6) is judgment, tagged as judgment.** It follows from the measurements
   but it is not itself a measurement, and it should not propagate downstream as one.

**Not blocked on:** privacy (LOW, `03` §6), volume (Holman clears the sample floor), or lineage completeness.

## 6 · Versioning

**v1.0.0 — initial release.** No prior version; no breaking change. Change semantics for the next release are
registered in `03` §8. One note specific to this product: a cache refresh is **not** a patch in the usual
sense, because the anchor game moves and every availability figure changes. A refreshed run is a new game.
