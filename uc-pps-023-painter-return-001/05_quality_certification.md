# 05 — Quality & Certification

**Department:** `coa-dept-quality` · **Lead:** `quality-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `dp_uc28`
**Layer 4 verdict:** ✅ **READY TO PUBLISH** (internal only) — 1 FAIL, reclassified non-blocking by formal descope.

Agents run: `dq-rule-definer` → `data-quality-engineer` → `certification-agent`.

---

## 5.1 `dq-rule-definer` — rules specified

| # | Rule (plain language) | Dimension | Threshold | Blocking? |
|---|---|---|---|---|
| R1 | Every row belongs to Andrew Painter and nobody else | Accuracy | `pitcher` set == `{691725}` exactly | 🔴 **yes** |
| R2 | No pitch appears twice | Uniqueness | 0 duplicates on `(game_pk, at_bat_number, pitch_number)` | 🔴 **yes** |
| R3 | Only regular-season games count | Validity | `game_type == 'R'` only | 🔴 **yes** |
| R4 | Core stuff CDEs are essentially complete in both tiers | Completeness | ≥99% PASS, ≥90% WARN, else FAIL | 🔴 **yes** |
| R5 | Batted-ball CDEs are known-sparse and must be flagged | Completeness | WARN expected; must not appear as a headline rate | 🟡 no |
| R6 | No rate KPI pools MLB and AAA | Consistency | no denominator spans `level` | 🔴 **yes** |
| R7 | Pitch tagging drift between feeds is surfaced | Consistency | SL/SW boundary verified by horizontal break | 🟡 no |
| R8 | Opponent data exists for the named opponent | Completeness | ≥1 BAL hitter row | 🟡 no — **descoped**, see 5.3 |
| R9 | Sources are fresh relative to game day | Timeliness | AAA cache ≥ T-1 | 🔴 **yes** |
| R10 | Samples meet the publication convention, or the shortfall is disclosed | Validity | 100 BF, else WARN + mandatory PA disclosure | 🟡 no |

---

## 5.2 `data-quality-engineer` — scorecard executed

Full receipt: `out/dp_uc28_dq_scorecard.csv` (25 checks).

| Check | Dimension | Result | Status |
|---|---|---|---|
| Entity lock | Accuracy | `pitcher` set == `{691725}` | ✅ **PASS** |
| Deduplication | Uniqueness | MLB 1,141 / AAA 396 rows after dedup; 0 duplicate keys survive | ✅ **PASS** |
| Game type filter | Validity | 52 spring-training pitches excluded | ✅ **PASS** |
| `release_speed` | Completeness | 100% / 100% | ✅ **PASS** |
| `release_spin_rate` | Completeness | 100% / 100% | ✅ **PASS** |
| `pfx_x`, `pfx_z` | Completeness | 100% / 100% | ✅ **PASS** |
| `plate_x`, `plate_z`, `sz_top`, `sz_bot` | Completeness | 100% / 100% | ✅ **PASS** |
| `release_pos_x`, `release_pos_z` | Completeness | 100% / 100% | ✅ **PASS** |
| `release_extension` | Completeness | 100% / 100% | ✅ **PASS** |
| `arm_angle` | Completeness | 100% / 100% | ✅ **PASS** |
| `zone` | Completeness | 100% / 100% | ✅ **PASS** |
| `launch_speed` | Completeness | 35.9% / 36.9% | ⚠️ **WARN** — directional only |
| `estimated_woba_using_speedangle` | Completeness | 25.9% / 25.0% | ⚠️ **WARN** — barred from report |
| Cross-level blending guard | Consistency | no pooled rate published | ✅ **PASS** |
| Pitch-tag drift | Consistency | SL/SW boundary differs by tagging model | ⚠️ **WARN** — verified distinct by HB (−6.3/−6.9 vs −15.7/−15.8) |
| **Opponent coverage** | Completeness | **0 Orioles rows; 0 prior Painter-vs-BAL pitches** | 🔴 **FAIL** |
| Freshness — MLB | Timeliness | max `game_date` 2026-06-17 (file current to 07-29) | ✅ **PASS** |
| Freshness — AAA | Timeliness | max `game_date` 2026-07-26 (cache current to 07-30) | ✅ **PASS** |
| Sample size — MLB | Validity | 1,141 pitches / 299 PA | ✅ **PASS** |
| Sample size — AAA | Validity | 396 pitches / 101 PA | ⚠️ **WARN** — below 100 BF convention; PA disclosed on every AAA rate |

**Tally: 21 PASS · 3 WARN (+ per-CDE WARNs) · 1 FAIL.**

---

## 5.3 `certification-agent` — readiness audit

### Artifact completeness

| Required artifact | Present? | Where |
|---|---|---|
| Use-case contract | ✅ | `USE_CASE_uc-pps-painter-return-001.md` |
| Intake gap report | ✅ | 01.2 |
| Source profile & fitness ruling | ✅ | 01.1 |
| Domain steward rulings | ✅ | 01.3 (5 rulings) |
| Glossary status | ✅ | 01.4 |
| Data model blueprint | ✅ | 02.1 |
| KPI specs — new | ✅ | 02.2 (3 full specs) |
| KPI inheritance — locked | ✅ | 02.2 (7 functions, verbatim) |
| Union/join validation | ✅ | 02.4 (8 checks, PASS) |
| Column-level lineage | ✅ | 02.5 (≤3 hops, all CDEs traced) |
| Semantic layer | ✅ | 03.1 |
| Metadata mapping | ✅ | 03.2 |
| Tagging proposal | ✅ | 03.3 |
| Privacy assessment | ✅ | 03.4 (4 rulings) |
| Build artifact | ✅ | `dp_uc28_painter_vs_orioles.py` |
| DQ scorecard | ✅ | `out/dp_uc28_dq_scorecard.csv` |
| Freshness manifest | ✅ | `out/dp_uc28_freshness_manifest.csv` |
| Reader report + PDF | ✅ | `dp_uc28_painter_vs_orioles_report.md` / `.pdf` |
| Interactive dashboard | ✅ | `dp_uc28_painter_vs_orioles_dashboard.html` |
| Consumer enablement | ✅ | 06 |
| Versioning / observability | ✅ | 07 |

### Internal consistency audit

| Audit | Result |
|---|---|
| Does every number in the report trace to a receipt? | ✅ verified — see 05.5 |
| Does the dashboard agree with the PDF? | ✅ **structurally guaranteed** — the dashboard reads the same CSVs; it does not recompute |
| Are all 19 starts accounted for in both the log and the level summary? | ✅ 14 MLB + 5 AAA = 19 |
| Does any AAA rate appear without its sample size? | ✅ no — spot-checked all 14 AAA rate mentions in the report |
| Does any expected-outcome metric appear? | ✅ **no** — grep confirms zero `xwoba`/`xba` in the report body (privacy/DQ ruling 01.3-Q3 upheld) |
| Does the report make any health or injury claim? (privacy ruling R2) | ✅ **no** — mechanical framing only; grep confirms no injury/fatigue/health language attached to the drift findings |
| Is the tipping hypothesis labelled as a hypothesis? | ✅ yes — stated twice, once in the bottom line ("This is a hypothesis, not a proof") and once in its own section ("This is not proof") |
| Is the opponent gap disclosed to the reader, not just to governance? | ✅ yes — in the report's own warning box, in a dedicated section, and in the caveats |
| Does every finding terminate in a persona action? (acceptance criterion G4) | ✅ 13 numbered takeaways across 4 persona blocks |
| Do figure subtitles match the data? | ✅ regenerated from data after the "15 starts" defect (04.4) |

### The FAIL, adjudicated

**R8 — opponent coverage — FAIL.**

`certification-agent` does not have authority to waive a FAIL. It escalates with a recommendation:

> The FAIL is real and correctly recorded. However, the use case was **formally descoped at intake** (01.2 / 00) to exclude an opponent attack plan, and the descope is disclosed to the reader in the report's own warning box rather than buried in governance. The failing capability is not claimed as delivered anywhere in the package — the capability-fulfillment map at 00 marks it `descoped`.
>
> **Recommendation: reclassify non-blocking.** A FAIL against a capability the product explicitly does not claim is a scope record, not a quality defect.

**DPO adjudication (00): accepted.** The FAIL stands in the scorecard as a permanent record that Orioles data does not exist in this repo — which is itself useful, and is carried forward as a platform backlog item (07.1).

---

## 5.4 Process honesty note

This use case ran under a hard deadline (first pitch tonight). Layers 2 and 3 were executed **single-pass** rather than through the usual design → review → redesign loop. `quality-lead` records this because a compressed process is a risk factor even when the output passes:

- **Mitigated:** the locked-KPI inheritance rule means the highest-risk logic was not written under time pressure — it was copied from an already-certified build.
- **Mitigated:** the entity lock is a runtime assertion, so the single largest failure mode in this repo's history cannot pass silently.
- **Residual:** the arc-boundary choice (2026-07-10) and the benchmark thresholds (≥40 four-seams, ≥15 per type) received one pass of judgment each, not a sensitivity sweep. The arc finding was spot-checked against the alternative split and survives; the benchmark thresholds were not swept. **Recorded as residual risk, not hidden.**

---

## 5.5 Verification pass

Independent re-derivation of every headline number from the CSV receipts, performed after the report was written. Method and full output: `dp_uc28_verification.py` and `out/dp_uc28_verification_log.txt`.

The verification script reads the **receipts**, not the build's in-memory objects, so a receipt/report mismatch is detectable. Nine checks (group A) go further and re-read the raw parquet to confirm the receipts are themselves faithful to source.

**Result: 76 / 76 checks passed.**

| Group | Checks | What it verifies |
|---|---|---|
| **A** | 9 | Source fidelity — row counts, start counts, entity lock, spring exclusion, `game_pk` disjointness, freshness, all re-read from parquet |
| **B** | 7 | Benchmark percentiles behind bottom-line finding #1 |
| **C** | 7 | Arm-slot spread behind bottom-line finding #2 (the tipping hypothesis) |
| **D** | 10 | Usage-vs-stuff separation behind finding #3, incl. the SL/SW tag-distinctness proof |
| **E** | 11 | Delivery mechanics behind finding #4, incl. the **same-park control** (6/28 and 7/10 both at LHV) and the monotonicity of the extension and arm-angle declines |
| **F** | 6 | Platoon weapon shelving behind finding #5 |
| **G** | 14 | Supporting sections — elevation bands, both arcs, times-through-order, location tiers |
| **H** | 12 | **Governance rules upheld in the report text itself**, not just in the receipts |

Group H is the unusual one and is worth naming, because it audits the prose rather than the numbers:

- **H1** — xwOBA may be *named* as a caveat but never *published* as a value. Test: every line mentioning it must contain a negation and must carry no decimal number.
- **H2** — privacy ruling 03.4 R2. Regex over the whole report for injury/fatigue/health language attached to the mechanical-drift findings. Zero matches.
- **H3** — the tipping claim is labelled a hypothesis in the report's own voice, twice.
- **H4** — the opponent gap is disclosed to the *reader*, not just recorded in governance.
- **H12** — no rate-KPI receipt exists without a `level` column, i.e. the blending guard holds at the artifact layer, not only in the code.

A defect this pass caught in an earlier draft: figure 1's subtitle read "15 starts" against a true regular-season count of **14**. Fixed at source by generating the subtitle from the data (04.4).

---

## 5.6 Certification decision

```json
{
  "certification_status": "READY",
  "blocking_failures": 0,
  "dq_summary": { "pass": 21, "warn": 3, "fail": 1, "fail_reclassified_non_blocking": 1 },
  "verification": "76/76 checks passed — headline numbers re-derived from receipts, source fidelity re-read from parquet, governance rules audited in the report text",
  "publish_surface": "INTERNAL ONLY — external publish blocked by privacy-watchdog (03.4 R1)",
  "distribution": "need-to-know: Painter, Realmuto, pitching department, manager, human DPO",
  "conditions": [
    "Human DPO acknowledges the 5 open items at 00",
    "arm_spread_deg remains PROVISIONAL and correlational until the ratification study at 03.1 is run",
    "No health or injury inference is drawn from the extension and arm-angle drift findings"
  ],
  "recommended_to": "human DPO (Kellen Short)"
}
```
