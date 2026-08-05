# 07 — Certification & Publish Readiness

**Agents:** `certification-agent` → `version-controller` → `data-observability` → `cost-watchdog`
**Layer 4 — Certify** · UC #32 · `uc-pos-008` · `dp_uc31`

**Certification status: ✅ READY** — with one circulation gate (OI-1).

---

## 1. Artifact completeness audit (`certification-agent`)

| Required artifact | Present | Location |
|---|---|---|
| Use-case contract | ✅ | `uc-pos-008-Luis Arraez PHI 20260804.md` |
| Gap report / intake validation | ✅ | `01` §1 |
| Source fitness profile | ✅ | `01` §2 |
| Domain steward notes | ✅ | `01` §3 |
| Business glossary decisions | ✅ | `02` §2–3 |
| Metadata mapping | ✅ | `02` §4 |
| Classification & tagging | ✅ | `02` §5 |
| Privacy assessment | ✅ | `02` §6 |
| Data dictionary | ✅ | `03` §1–2 |
| Column-level technical lineage | ✅ | `03` §3 |
| Data model / architecture | ✅ | `04` §1 |
| KPI specifications (all new KPIs) | ✅ | `04` §2 — all 7 specified before use |
| DQ rule definitions | ✅ | `05` §1 — 24 rules |
| Join validation | ✅ | `05` §2–3 |
| DQ scorecard (executed) | ✅ | `out/dp_uc31_dq_scorecard.csv` — 24/24 |
| Independent verification | ✅ | `out/dp_uc31_verification_results.csv` — 368/368 |
| Freshness manifest | ✅ | `out/dp_uc31_freshness_manifest.csv` |
| Receipt index | ✅ | `out/dp_uc31_receipt_index.csv` — 30 CSVs + 6 figures |
| Reader report | ✅ | `.md` + branded `.pdf`, 12 pp |
| Interactive consumable | ✅ | `dp_uc31_arraez_acquisition_dashboard.html` |
| Persona onboarding | ✅ | `06` §2 |
| Query templates | ✅ | `06` §4 |
| Acceptance criteria / closure step | ✅ | `00` §Closure — three falsifiable projections |
| Version manifest | ✅ | §5 below |
| Monitoring / runbook | ✅ | §6 below |

**No missing artifacts.**

---

## 2. Internal consistency audit

The certification agent's job is to check that the artifacts agree with **each other**, not merely that each exists.

| Consistency check | Result |
|---|---|
| Every KPI in the report has a spec in `04` | ✅ 7/7 |
| Every spec in `04` appears in a receipt | ✅ 7/7 |
| Every table in the report names its receipt | ✅ |
| Every figure's numbers trace to a receipt | ✅ 6/6 |
| Report data window matches the freshness manifest | ✅ 2026-08-02 both |
| Report caveats match the open items in `00` | ✅ 9 caveats ↔ 6 open items, all cross-referenced |
| Glossary term count matches the report's KPI list | ✅ AR-1…AR-7 |
| DQ rule count in `05` matches the executed scorecard | ✅ 24 = 24 |
| Verification count in the report matches the results file | ✅ 368 |
| Dashboard values match the receipts | ✅ spot-checked; swap delta reproduces `f7` to 4 dp |
| Privacy classification consistent across artifacts | ✅ Internal — Restricted in `02`, `00`, report header, PDF footer, dashboard header |

---

## 3. Verification defect log

**This section exists because the harness failed on first run.** Both failure classes were investigated to root cause and neither was silenced.

### Run 1 — 330 / 351 PASS, 21 FAIL

**Failure class A (6 checks): season PA/AB/BA/SLG/OBP/K% for 2021 and 2025.**

| | Recomputed | Published | Δ |
|---|---|---|---|
| 2021 PA | 479 | 480 | 1 |
| 2025 PA | 675 | 677 | 2 |

*Root cause.* The harness used the strict PA basis; `a1_season_line` is produced by the locked `get_stats`, which counts `truncated_pa` as a plate appearance. Counts of `truncated_pa`: 2021 = 1, 2025 = 2 — **exactly the discrepancy.**

*Disposition.* **Not a defect. The harness was wrong to assert equality.** Rewritten to assert the *reconciliation* — `locked_PA − strict_PA == truncated_pa count` — and to add two new checks proving the fork cannot touch any forward-looking number:

- **V-009a:** the 2026 primary window contains **zero** `truncated_pa`. PASS.
- **V-009b:** `truncated_pa` occurs only in 2021 and 2025 — shadow years. PASS.

The locked kernel was **not** edited. It is shared with `dp_uc20`, `dp_uc22` and `dp_uc24`; patching it mid-build would silently fork a definition across four delivered products. Logged as open item **O5** for a coordinated version bump.

**Failure class B (15 checks): AR-6 SPRC reconstruction.**

| | Recomputed | Published | Δ |
|---|---|---|---|
| Arraez slot 1, RE24/162 | 24.900 | 24.890 | 0.010 |
| Arraez slot 2, RE24/PA | 0.0362 | 0.0361 | 0.0001 |

*Root cause.* The check reconstructs SPRC from its **published** inputs, which are stored at 4 decimal places. The build composes from unrounded values. Reconstructing from rounded inputs necessarily drifts.

*Disposition.* **Not a defect, but the tolerance was wrong.** Rather than loosen it silently, the check was renamed to state what it tests ("from published inputs"), given an explicit bounded tolerance (2e-4 on the rate; 0.05 runs on the per-162 total — under 0.2% of a ~25-run quantity), and documented in the source with the reason. **The raw-path check V-120, which recomputes RE24/PA directly from the parquet, carries the real burden and passes at 1e-4.**

### Run 2 — 361 / 361 PASS

### Run 3 — 368 / 368 PASS
Eight checks added after the premise conflict was discovered, covering both lineup framings and the observed-leadoff finding (V-130a…V-133d).

**Zero unexplained failures at certification.**

---

## 4. Verification coverage

| Area | Checks | Method |
|---|---|---|
| Source & entity lock | 10 | Direct assertion on raw parquet |
| Season line (8 seasons × 10) | 80 | Explicit boolean masks; no kernel reuse |
| Discipline & contact | 18 | Recomputed from `description`/`type` masks |
| Two-strike (AR-1/AR-2) | 40 | Independent per-PA index construction |
| Damage map (AR-3) | 36 | Per-cell mask recomputation |
| Scoring position (AR-4) | 29 | Independent `min()` conversion logic |
| Slot reconstruction (AR-5) | 43 | Independent cumcount; integrity assertions |
| SPRC model (AR-6) | 68 | Weights, profiles, composition, and raw-path RE24 |
| Table setting (AR-7) | 32 | OBP and supply recomputed from events |
| Report claims | 7 | Headline assertions tested as booleans |
| Artifact completeness | 5 | Filesystem and index integrity |
| **Total** | **368** | **368 PASS / 0 FAIL** |

**Design property.** The harness does not import the build module. It re-reads the raw parquet and, where the build used a groupby/apply kernel, uses explicit boolean masks and scalar arithmetic — so a shared bug cannot pass both paths.

**Claims tested as assertions, not prose.** Seven statements in the report are enforced by the harness, so the document cannot drift from the data:

| Check | Report claim |
|---|---|
| V-042 | Arraez has the best two-strike survival rate on the roster |
| V-133a | The Turner-framing swap is negative |
| V-133b | The Schwarber-framing swap is under 2 runs |
| V-133c | Scenario C beats both stated options |
| V-133d | The observed leadoff hitter is Turner |
| V-134 | Arraez's slot spread is under 5 runs per 162 |
| V-135 | Schwarber outproduces Arraez in every slot |

---

## 5. Version manifest (`version-controller`)

**Version 1.0.0** — initial release.

| Change class | Count | Notes |
|---|---|---|
| Breaking | 0 | New data product; no consumers to break |
| Additive | 7 | AR-1 … AR-7, all **provisional** |
| Locked-KPI modifications | **0** | `get_stats`, `discipline`, `batted_ball`, `pulled_air`, `PITCH_GROUP`, `wrc`, `ppa`, `bat_tracking` inherited byte-identical from `dp_uc24` |
| Deprecations | 0 | — |

**Gate 4 satisfied.** No existing definition was changed. The `truncated_pa` fork is an *additional* basis used only by new KPIs, not a redefinition of the existing one — and it is reconciled in verification rather than left implicit.

**Consumer communication.** None required (no existing consumers). When O4 and O5 are resolved in a coordinated bump across `dp_uc28`–`dp_uc31`, that **will** be a breaking change for anyone who has cached `xwoba_con` counts or shadow-year PA totals, and will require notice under Gate 4.

---

## 6. Observability & runbook (`data-observability`)

This is a point-in-time analytical product, not a running pipeline. Monitoring is therefore about **staleness and invalidation**, not job health.

| Signal | Threshold | Action |
|---|---|---|
| Source cache age | `arraez.parquet` max date > 14 days behind today | Re-pull; the product's forward-looking claims weaken as his Phillies sample grows |
| Phillies PA accumulated | ≥150 PA in a Phillies uniform | **Trigger the closure re-read** (`00` §Closure) |
| Two-strike survival | Sustained below .85 over 100+ PA | **Invalidate the acquisition thesis.** Supersede, do not amend |
| Lineup card change | Manager moves him out of slots 2–4 | Re-run `f5`/`f7`; the model already prices all nine slots |
| wOBA − xwOBA gap | Closes toward 0 | **Expected.** Confirms the projection; no action |
| Schema drift | New Statcast fields or renamed columns | Build asserts on the fields it uses; a rename surfaces as a DQ-11/DQ-20 failure |

**Runbook: re-running this product.**
```bash
python dp_uc31_arraez_acquisition_read.py          # ~15 s → out/
python dp_uc31_verification.py                     # must report 0 FAIL
python dp_uc31_build_pdf.py                        # → report.pdf
python dp_uc31_build_dashboard.py                  # → dashboard.html
```
Data root resolves via `MLB_DATA_ROOT`, `argv[1]`, or a portable candidate list. **The build refuses to run without a reachable data root** rather than emitting an unfilled harness — the `uc-pps-010` failure mode.

---

## 7. Cost review (`cost-watchdog`)

| Item | Observation |
|---|---|
| Runtime | ~15 s build, ~10 s verification, on a local laptop-class machine |
| Peak memory | Two parquet files, ~31 k retained rows; trivially small |
| Storage | 30 CSVs + 6 PNGs + PDF + HTML ≈ 1.3 MB total |
| Recompute waste | `pa_frame()` and `slot_opportunity()` are recomputed several times inside `main()` and inside DQ checks. **Measurably wasteful; deliberately not optimised** — recomputation from source is a correctness property here, and at this scale caching would trade auditability for milliseconds |
| Recommendation | **No action.** If this pattern is ever applied to a full-league population (~700 hitters rather than 11), the AR-6 cross product should be vectorised and `pa_frame` memoised. Not before |

---

## 8. Certification decision

**READY TO PUBLISH.**

All required artifacts present and mutually consistent. 24/24 build DQ. 368/368 independent verification, zero unexplained failures. All seven new KPIs specified before use. No locked definition modified. Privacy assessed and classified. Every published number traced to a receipt.

**One gate applies to circulation, not to certification:** **OI-1**, the leadoff-hitter premise conflict. The lineup recommendation changes sign between framings, so the human DPO must confirm the current lineup card before this reaches the manager or coaching staff. It does not block release to the analytics group, for whom both framings are informative.

The remaining five open items are disclosures, not defects.
