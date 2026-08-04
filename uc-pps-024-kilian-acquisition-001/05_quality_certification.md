# 05 — Quality & Certification

**Department:** Quality · **Agents:** `dq-rule-definer`, `data-quality-engineer`, `certification-agent`
**Layer 4 verdict:** ✅ **CERTIFY READY** — 205/205 independent checks, 32 DQ checks, **0 FAIL**, 2 WARN (both disclosed in the report)

---

## 5.1 `dq-rule-definer` — rule specifications

Rules written in plain language first, then handed to the engineer. The definer does **not** implement or score.

| # | Rule (plain language) | Dimension | Threshold |
|---|---|---|---|
| R1 | Every row must belong to the one pitcher we locked to | Validity | `nunique(pitcher) == 1 AND == 668873` |
| R2 | No pitch may appear twice | Uniqueness | 0 duplicates on natural key |
| R3 | Only regular-season rows | Validity | `game_type` set == {'R'} |
| R4 | 2025 must be absent and must never be filled in | Consistency | `count(game_year==2025) == 0` |
| R5 | Hawk-Eye tracking fields complete on tracked pitches | Completeness | ≥ 0.95 |
| R6 | Contact-quality fields complete **on balls in play** | Completeness | ≥ 0.95 of `type=='X'` |
| R7 | `events` is PA-terminal — low all-row completeness is expected, not a defect | Completeness | informational only |
| R8 | Location-metric orientation must be proven from the data, not assumed | Accuracy | sinker `pfx_x` < 0; slider `pfx_x` > 0 |
| R9 | Publishable rate cells must clear 100 BF, or be flagged directional | Accuracy | flag below threshold |
| R10 | Every null-tracking row must be explained, not silently dropped | Validity | all null `pitch_name` rows accounted for |
| R11 | Pitch-mix and location denominators must use the tracked population | Consistency | share denominator == printed denominator |
| R12 | Exit-velocity means must be computed on balls in play only | Accuracy | every EV aggregation filters `type=='X'` |
| R13 | xwOBAcon must use the BIP-only definition; the contaminated column must not be published | Accuracy | quarantined column never cited |

R10-R13 are **new this UC** and came directly out of the source profile and the verification failures.

---

## 5.2 `data-quality-engineer` — scorecard

**32 checks executed** (`out/dp_uc29_dq_scorecard.csv`). **0 FAIL · 2 WARN · 30 PASS.**

### Governance checks — all PASS

| Check | Value | Result |
|---|---|---|
| Entity lock `pitcher == 668873` | 1 distinct id | ✅ |
| Dedup on natural key | 0 duplicates | ✅ |
| Regular season only | `{R}` | ✅ |
| 2025 absent, not interpolated | 0 rows | ✅ |
| 2026 BF ≥ 100 publish threshold | 193 PA | ✅ |
| Prior-era BF ≥ 100 | 138 PA | ✅ (8 outings — directional) |
| Orientation: sinker `pfx_x` < 0 (arm side) | −1.100 | ✅ |
| Orientation: slider `pfx_x` > 0 (glove side) | +0.423 | ✅ |
| Untracked rows explained | 8, all `automatic_ball` | ✅ |
| Tracked population | 728 of 736 | ✅ |
| xwOBAcon BIP-only hardening applied | 118 BIP | ✅ |
| `launch_speed` on non-BIP rows identified | 114 foul rows | ✅ (all EV means filter `type=='X'`) |

### Completeness — all PASS

Tracking fields 98.9% (the 1.1% shortfall is exactly the 8 untracked rows). Contact fields **100% of balls in play**. `events` 26.2% — PA-terminal by design, correctly classified as informational rather than a defect. `bat_speed` 46.5% — excluded from every published KPI.

### The two WARNs

| WARN | Detail | Disposition |
|---|---|---|
| **Slider vs RHH cell size** | 61 pitches / 14 BIP, below the 100-BF convention | **Report as directional.** The report prints the denominator on every slider line and leads the finding with the home-run *count* (a hard number) and exit velocity (stable), not the xwOBAcon rate. Disclosed in the report's caveats |
| **Locked `in_zone_rate` inflated (O2)** | Locked 0.4860 vs strict 0.4808 — null-zone rows counted as in-zone | **Report publishes the STRICT variant.** Locked function left unmodified per the inheritance rule. Escalated as O2 for a repo-wide decision |

---

## 5.3 Independent verification

**`dp_uc29_verification.py` — 205/205 PASS.**

This is a **separate code path**, not a re-run of the build: it re-loads the raw parquet and recomputes every published number with plain boolean masks, importing nothing from the build module. The design intent is to defeat the shared-bug failure mode where a wrong helper agrees with itself.

| Group | Checks | Covers |
|---|---|---|
| A | 13 | Entity lock, dedup, game type, era counts, 2025 gap, freshness |
| B | 21 | Every headline conversion number in the Bottom Line and era table |
| C | 18 | Velocity, arsenal composition, usage, movement, whiff by pitch |
| D | 36 | Platoon splits, pitch × hand, tracked-population findings |
| E | 20 | **NEW KPI** Slider Finish Rate + vertical half |
| F | 14 | **NEW KPI** Fastball Elevation Rate |
| G | 9 | Sinker vs LHH (the recommendation to shelve it) |
| H | 5 | Damage log — all 5 HR, side, pitch, date window |
| I | 22 | Deployment, leash, rest, inherited runners |
| J | 6 | Stability — monthly velo, two-inning velo hold |
| K | 7 | Count-state usage cited on the battery card |
| L | 34 | Receipts exist and agree with the independent recompute |

### What verification caught

The first run returned **199/205**. Six failures, of which **three were real defects in the published draft**, not test errors:

1. **Exit-velocity means contaminated by foul balls.** The slider vertical-half table read 80.8 / 92.4 mph. The correct BIP-only figures are **86.8 / 99.1**. The draft numbers came from an exploratory pass that averaged `launch_speed` without filtering `type=='X'` — and `launch_speed` is populated on 114 foul rows in this feed. → **O3**, and the report now carries the correction and the warning.
2. **Zone rate inflated by untracked rows.** Published 48.6%, correct strict value **48.1%**. → **O2**.
3. **Usage denominators inconsistent.** The count-usage table computed shares over rows with a known pitch type while printing the full row count beside them. Both now use the tracked population. → resolved in build.

The remaining three were expected-value updates flowing from those same fixes. **Every one of these would have shipped without the independent recompute.** That is the argument for the check existing.

---

## 5.4 `certification-agent` — readiness

| Artifact | Required | Present |
|---|---|---|
| Use-case contract | ✅ | `uc-pps-024-Caleb Kilian PHI 20260804.md` |
| Intake gap report | ✅ | `01_strategy_intake.md` §1.1 |
| Source profile & fitness | ✅ | `01_strategy_intake.md` §1.2 |
| Data model blueprint | ✅ | `02_engineering_design.md` §2.1 |
| KPI specs (incl. all new KPIs) | ✅ | `02_engineering_design.md` §2.2 |
| Glossary entries + provenance | ✅ | `03_governance.md` §3.1 |
| Metadata mapping | ✅ | `03_governance.md` §3.2 |
| Data dictionary | ✅ | `06_consumer_success.md` §6.1 |
| Tagging proposal | ✅ | `03_governance.md` §3.3 |
| Privacy assessment | ✅ | `03_governance.md` §3.4 |
| Column-level lineage | ✅ | `04_engineering_build.md` §4.1 |
| DQ scorecard | ✅ | `out/dp_uc29_dq_scorecard.csv` (32 checks) |
| Freshness manifest | ✅ | `out/dp_uc29_freshness_manifest.csv` |
| Independent verification | ✅ | `dp_uc29_verification.py` — 205/205 |
| Acceptance criteria met | ✅ | 7 of 7 consumer questions answered with receipts (`00` §capability map) |

**Internal consistency check:** ✅ every number in the report traces to a CSV receipt; every receipt traces to a lineage entry; every KPI traces to a spec written before use; every spec traces to approved CDEs.

### Certification verdict

> ✅ **READY — cleared for internal advance use.**
>
> Zero FAIL. Two WARNs, both sample-size or locked-function disclosures that the report itself surfaces in its caveats section. Three new open items (O2, O3, O4) plus one carried forward (O1) — none blocking, and **two of them are repo-wide improvements this UC discovered rather than problems it created**.
>
> The certification agent does **not** make the publish decision. Returned to the human DPO with a recommendation to publish internally.

**Post-publication closure step:** re-read at **150 PA in Phillies uniform** — re-test the reverse platoon split (O4) and measure Slider Finish Rate against the 70% glove-side target.
