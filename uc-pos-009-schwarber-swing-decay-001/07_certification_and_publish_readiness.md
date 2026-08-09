# 07 — Certification & Publish Readiness

**Layer 4 — Certify** · Department: Quality
**Agents:** `certification-agent` · `version-controller` · `data-observability` · `cost-watchdog`
**Use case:** `uc-pos-009-schwarber-swing-decay-001` · **Build:** `dp_uc32`

---

## 1. `certification-agent` — artefact completeness audit

| Required artefact | Present | Location |
|---|---|---|
| Use-case contract | ✅ | `uc-pos-009-Kyle Schwarber SWING 20260808.md` |
| DPO delivery spine | ✅ | `00_DPO_delivery_spine.md` |
| Intake validation + source profile | ✅ | `01_` |
| Business glossary + tagging + privacy | ✅ | `02_` |
| Data dictionary + technical lineage | ✅ | `03_` |
| Architecture + KPI specs | ✅ | `04_` |
| DQ rules + join validation + build notes | ✅ | `05_` |
| Consumer success (semantic layer, personas, dashboard spec, queries) | ✅ | `06_` |
| Certification (this document) | ✅ | `07_` |
| Build script | ✅ | `dp_uc32_schwarber_swing_decay.py` |
| Verification harness | ✅ | `dp_uc32_verification.py` |
| PDF builder | ✅ | `dp_uc32_build_pdf.py` |
| Dashboard builder | ✅ | `dp_uc32_build_dashboard.py` |
| Reader report (markdown) | ✅ | `dp_uc32_schwarber_swing_decay_report.md` |
| Reader report (PDF) | ✅ | `dp_uc32_schwarber_swing_decay_report.pdf` |
| Interactive dashboard | ✅ | `dp_uc32_schwarber_swing_decay_dashboard.html` |
| CSV receipts | ✅ | `out/` — **24** |
| Figures | ✅ | `out/` — **5** |
| DQ scorecard | ✅ | `out/dp_uc32_dq_scorecard.csv` — 24/24 |
| Verification results | ✅ | `out/dp_uc32_verification_results.csv` — 59/59 |
| Freshness manifest | ✅ | `out/dp_uc32_freshness_manifest.csv` |
| README index | ✅ | `README.md` |

**Package complete. No missing artefact.**

### Internal consistency checks

| Check | Result |
|---|---|
| Every KPI in the report has a spec in 04 §3 | ✅ 9/9 |
| Every spec in 04 appears in the lineage in 03 | ✅ |
| Every receipt in 03's register exists on disk | ✅ 24/24 |
| Every figure referenced by the report exists | ✅ 5/5 (V-F checks) |
| Every receipt cited in the report exists | ✅ (V-51) |
| Report header counts match the scorecards | ✅ 24/24 DQ, 59/59 verification |
| Glossary terms used in the report are defined in 02 | ✅ |
| No number in the report was computed outside the build | ✅ (V-37 … V-50 re-derive them) |
| No pre-sensor bat-speed value appears in the prose | ✅ (V-52) |

---

## 2. Independent verification — 59/59 PASS

`dp_uc32_verification.py` reloads from parquet by a **separate code path** — it does not import the build script and shares no helper functions. Its job is to catch the build being wrong, not to re-run it.

| Block | Checks | Result |
|---|---:|---|
| Entity & scope (V-01…05) | 5 | ✅ |
| Receipts vs independent recompute (V-06…15) | 10 | ✅ |
| **No-imputation policy enforcement (V-16…24)** | **9** | ✅ |
| Phase split integrity (V-25…36) | 12 | ✅ |
| Report-body claim audit (V-37…50) | 14 | ✅ |
| Figure & receipt existence (V-F…, V-51, V-52) | 7 | ✅ |
| Build DQ still green (V-53, V-54) | 2 | ✅ |
| **Total** | **59** | **✅ 0 FAIL** |

### Checks worth naming

- **V-20** — asserts 2023 bat-speed coverage is *exactly zero*, pinning the correction to the DPO's intake note so a future data refresh that backfills 2023 will trip the harness rather than silently change the report.
- **V-22 / V-23** — pin the imputation-harm figures (7,021 swings, 67.7%) that the report quotes as its governance argument.
- **V-35** — asserts the *paradox itself*: sweet-spot rate rose while barrel rate fell. If a future refresh breaks this relationship, the report's central metrological claim needs rewriting, and the harness will say so.
- **V-45 / V-47** — pin the honest caveats: Phase A exceeded 2025, and Phase A contact depth was the outlier. **These are checks on the report's humility, not on its findings.**
- **V-52** — regex-scans the prose for any pre-2024 bat-speed number. A policy violation in *narrative* is as bad as one in a table.

**No verification failures were encountered.** Unlike `uc-pos-008` (330/351 on first run), this harness passed on first execution.

---

## 3. Governance gate review

| Gate (CLAUDE.md) | Where enforced | Result |
|---|---|---|
| **1. No CDE inference** | 02 | ✅ Nine report-local terms (SW-1…SW-9), all composed from existing physical CDEs or published Statcast definitions with the source named. Zero business meanings invented. Returned as promotion candidates |
| **2. No pipeline build without approved specs** | 04 §3 → build | ✅ All nine specified before appearing in any output. SW-8 emerged from analysis and was specified before publication |
| **3. No publish without certification** | this document | ✅ READY — 24/24 DQ, 59/59 verification |
| **4. No breaking changes without notice** | §5 below | ✅ n/a — new product, no consumers. Locked kernel inherited byte-identical |
| **5. Privacy flags block external publish** | 02 §6 | ✅ Assessment complete. **Internal — Restricted.** PW-2 blocks external publication |

---

## 4. Open items for the human DPO

| # | Item | Severity | Ask |
|---|---|---|---|
| **OI-1** | **Sensor-boundary NULL standard.** This build establishes that missing-because-the-instrument-did-not-exist is *out-of-scope data*, not missing data, and enforces it with four DQ rules | **Non-blocking, high value** | **Promote to a repository-wide governance principle** in `CLAUDE.md`. It generalises past baseball to any sensor-era field in any data product. Strongest single output of this UC |
| **OI-2** | **SW-1 Sweet-Spot Rate is unsafe alone for power hitters.** It rose 6.4% while SLG fell 27.2%. SW-8 Damage-Band Rate and SW-2 Ideal-Contact Rate are the proposed replacements | **Non-blocking** | Ratify SW-2, SW-7 and SW-8 for promotion (strongest candidates — all roster-general). Decide whether SW-1 carries a standing warning label in the glossary |
| **OI-3** | **SW-4 / SW-9 are provisional.** The 1.23 / 0.2306 constants are published approximations. The plate-speed derivation is exact; the constants are not | Non-blocking | Ratify as directional, or commission a calibration against a known squared-up reference |
| **OI-4** | **SW-8 band boundaries validated for one hitter only.** 20–32° is where *Schwarber's* value concentrates (xwOBAcon 1.243) | Non-blocking | Validate per-archetype before roster-wide use, or accept as a power-hitter-specific band |
| **OI-5** | **O4 carry-forward** (`xwobacon` `size` semantics, opened in `uc-pps-025`). Still unpatched repo-wide | Non-blocking | This build avoids it (uses `mean`, publishes `xwobacon_n`). Schedule the coordinated version bump |
| **OI-6** | **Nullable-dtype masking defect (B-1)** will hit any future agent masking a Statcast numeric column | Non-blocking | Add `coerce_numeric` guidance to `references/data-quality.md` in the MLB repo |
| **OI-7** | **No opponent-quality adjustment.** The breaking-ball finding may partly reflect who he faced — the largest unmodelled confounder | Non-blocking | Accept as a stated limitation, or commission a follow-on |
| **OI-8** | **Intake note corrected.** The DPO's statement that 2023 bat speed had "very limited availability" is contradicted by the source (0.0% for this batter) | Non-blocking, informational | Acknowledge. Pinned by V-20 |

**Nothing blocks publication.** OI-1 and OI-2 are the two worth acting on.

---

## 5. `version-controller`

**Version: v1.0.0** — initial release.

| Change class | Present | Note |
|---|---|---|
| Breaking | **none** | New data product, no existing consumers |
| Non-breaking additive | 9 KPIs (SW-1…SW-9), 24 receipts, 2 consumables | All new |
| Locked-kernel modifications | **none** | `whiff_rate`, `chase_rate`, `barrel_rate`, `hard_hit_rate`, `ev90`, `inds` inherited byte-identical |
| Deprecations | none | |

**Forward-compatibility notes for the next maintainer:**

1. **The suppression loop in `bat_tracking_block()` is load-bearing.** Removing it silently violates the DPO's recorded decision. DQ-10/11 and V-16…V-18 will fail — do not silence them.
2. **`split_date` is computed, not hard-coded.** Re-running after more games shifts it. That is intended; the report prints the date and both denominators. Any consumer quoting "since May 27" must re-read after a refresh.
3. **Sensor boundaries will move.** When a 2027 season arrives, the windows extend but the boundaries (2024, 2025) do not. DQ-08/09/20 encode them.
4. **SW-8 band boundaries are a versioned decision.** Changing 20–32° is a **breaking** change to any downstream comparison.

---

## 6. `data-observability` — monitoring & runbook

This is a point-in-time analytical product, not a live pipeline. Monitoring is therefore about **re-run validity**, not uptime.

| Signal | Rule | Action on trip |
|---|---|---|
| **Freshness** | `today − max(game_date) > 3` | DQ-17 fails, build exits non-zero. Refresh the parquet cache before re-running |
| **Sensor backfill** | Any pre-2024 `bat_speed` or pre-2025 `attack_angle` appears in the source | DQ-08/09 fail. **Do not override.** Investigate — an upstream backfill changes the evidence-window architecture and this UC must be re-designed, not re-run |
| **Coverage drop** | 2026 `bat_speed` coverage < 95% | DQ-07 fails. Check for a sensor outage window before publishing any SW-3/4/9 figure |
| **Sample floor** | 2026 BIP < 150 | DQ-18 fails. Phase splits are not publishable |
| **Entity contamination** | Name filter resolves to > 1 `batter` id | DQ-03 fails. A second Schwarber has entered the dataset; re-verify the lock |
| **Window drift** | `min(window_n) != 60` in the rolling receipt | DQ-24 fails. Rolling series is malformed |
| **Report drift** | Any V-37…V-52 claim check fails after a refresh | The prose no longer matches the data. **Re-write the affected passage — never relax the check** |

**Runbook — re-running this product:**

```bash
python dp_uc32_schwarber_swing_decay.py    # exits non-zero on any DQ failure
python dp_uc32_verification.py             # exits non-zero on any check failure
python dp_uc32_build_pdf.py                # only after both are green
python dp_uc32_build_dashboard.py
```

The order is mandatory. The PDF and dashboard builders do not check DQ status — they trust that the two harnesses above ran green.

---

## 7. `cost-watchdog`

| Item | Observation |
|---|---|
| Input volume | 13 parquet files, ~75 MB; 272,903 `pos` rows before the entity lock |
| Peak working set | Full Phillies batting frame is loaded to filter one batter — 272,903 rows to reach 13,442 |
| Runtime | Single-digit seconds end to end |
| Output footprint | 24 CSVs + 5 PNGs + 500 KB PDF + 104 KB HTML |
| Recompute waste | The peer pool (§E) reloads and re-features the entire LHB population for two receipts |

**Recommendations (ranked, none implemented — findings only):**

1. **Push the entity filter into the parquet read.** `pd.read_parquet(f, filters=[('batter','==',656941)])` would cut the working set ~20× at zero cost to correctness. **Highest value, lowest risk.**
2. **Column projection.** The build reads 121 columns and uses ~40. A `columns=` list would roughly halve I/O.
3. **The peer pool is the most expensive section for the least report weight** — two receipts, one secondary table, `pool_n = 5`. Consider making it opt-in via a flag.
4. **Figures re-render on every run.** Fine at this scale; would matter if this became a scheduled job.

**No cost concern blocks publication.** At this scale the product is cheap; the recommendations matter only if the pattern is templated across the roster.

---

## 8. Certification verdict

> ## ✅ **READY TO PUBLISH**
>
> 24/24 build DQ · 59/59 independent verification · 24 receipts · 0 manual carry-ins · 0 numbers computed outside the build.
>
> **Classification: Internal — Restricted.** Cleared for internal circulation. **Blocked for external publication** (02 §6, PW-2 — the mirror-view section is a live vulnerability disclosure).
>
> Eight open items, none blocking. OI-1 (sensor-boundary NULL standard) and OI-2 (SW-1 warning label + SW-2/7/8 promotion) are recommended for action at the next glossary review.

**Signed:** `certification-agent`, 2026-08-08. Publish decision rests with the human DPO.
