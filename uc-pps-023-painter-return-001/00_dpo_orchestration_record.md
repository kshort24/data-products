# 00 — DPO Orchestration Record

**Agent:** `data-product-owner` (orchestrator) · **Use Case:** `uc-pps-painter-return-001` · **Value stream:** `pps`
**Ledger IDs:** UC **#29** · contract `uc-pps-023` · build artifact `dp_uc28`
**Human DPO:** Kellen Short · **Date:** 2026-07-31
**Recommendation:** ✅ **Ready to publish** — pending human acknowledgment of 5 non-blocking open items.

This is the spine of the package: the sequenced delivery plan, the governance gates checked at each handoff, the capability-fulfillment map, and the publish recommendation. Department detail lives in files 01–07.

---

## The ask, in one line

> *"Painter starts tonight against Baltimore after being optioned. Did he adjust at Triple-A, and what should Painter, Realmuto, the pitching department, and the manager each do about it?"*

Four named personas, four different decisions, one pitcher. The deliverable is a decision aid, not a stat sheet.

---

## Delivery plan & layer status

| Layer | Departments | Status |
|---|---|---|
| 1 — Intake & Discovery | Strategy & Intake | ✅ complete (**GO**, 1 blocking gap resolved by descope, 4 non-blocking) |
| 2 — Design | Engineering (Design) ∥ Governance | ✅ complete |
| 3 — Build | Engineering (Build) | ✅ complete — 23 CSV receipts, 5 figures |
| 4 — Certify | Quality | ✅ **READY** (1 FAIL, reclassified non-blocking by scope) |
| 5 — Launch | Consumer Success ∥ Marketing | ✅ artifacts staged (PDF + interactive dashboard) |
| 6 — Operations | Platform (persistent) | ✅ backtest harness defined; monitoring is single-run scoped |

**Front door:** `visual-intake-agent` skipped — the request arrived as written prose. Sequence started at `use-case-validator`.

**Time-boxed delivery.** This use case has a hard expiry: first pitch tonight. The DPO ran Layers 2 and 3 with a single-pass design rather than the usual design/review/redesign loop, and recorded the compression here rather than hiding it. See 05.4.

---

## Governance gates checked at handoff

| Gate (governance principle) | Where enforced | Result |
|---|---|---|
| **1 — No CDE inference** | All CDEs are Statcast-native physical fields with existing glossary entries; 3 new derived KPIs went through `kpi-calculator` spec → `business-glossary-agent` before appearing in the report (04.2, 03.1) | ✅ |
| **2 — No build without approved specs** | `data-engineer` implemented only what `data-architect` (02.1) and `technical-lineage-builder` (02.5) specified; locked KPI functions copied verbatim from `dp_uc11`, not re-derived | ✅ |
| **3 — No publish without certification** | `certification-agent` returned **ready** (05.3) before any consumer artifact was released | ✅ |
| **4 — No breaking change without notice** | `version-controller` (07.3): three new KPIs are **additive/non-breaking**; the `arm_angle` spread metric is flagged provisional pending ratification | ✅ |
| **5 — Privacy clears external publish** | `privacy-watchdog` (03.4): player performance data on identified public athletes; **internal-only** classification applied, external publish blocked | ✅ |
| Join strategy passes before build | `join-validator` (02.4) — the union is a **stacked concat with a level discriminator**, not a join; fan-out risk is structurally absent. Verified zero key collision across tiers | ✅ |
| **Multi-level blending guard** (UC#11 inheritance) | Enforced *by construction* in the build: every rate KPI is computed inside a `groupby(['level', ...])`. There is no code path that pools MLB and AAA into one rate | ✅ |

---

## The load-bearing orchestration thread

The intake gate caught something that would have wrecked the deliverable if it had reached the report unexamined.

`use-case-validator` (01.2) flagged **one blocking gap**: the request implies an opponent matchup ("his start against the Baltimore Orioles"), but `source-system-profiler` (01.1) found **zero Orioles hitter rows in the repo and zero prior Painter-vs-BAL pitches**. The standard `uc-pps` pattern builds a lineup-by-lineup attack plan; that was impossible here.

The DPO did not paper over this. Three options were put to the scope decision:

1. Fabricate a lineup plan from general knowledge — **rejected** (violates the "never publish a number the build didn't compute" rule).
2. Block the use case pending an Orioles cache build — **rejected** (the use case expires at first pitch).
3. **Descope the opponent dimension and re-anchor the use case as a self-scout.** — **adopted.**

Option 3 turned out to serve the actual ask better than the original framing. The requester's four named personas all want to know *what Painter should do*, not *what Baltimore does*. The opponent gap is carried as a visible FAIL in the DQ scorecard (05.2) and stated in the report's own warning box rather than buried.

**Second thread:** the descope freed the analysis budget to go deeper on delivery mechanics, which is where the finding actually lives. `eda-agent` (02.3) noticed a release-point discontinuity that a lineup-focused build would have skipped entirely. That became finding #4 of the report.

---

## Capability fulfillment

```json
{
  "capability_fulfillment": [
    { "capability": "Characterise Painter's stuff — velocity, spin, movement — across the AAA stint",
      "satisfied_by": "arsenal_by_level + stuff_delta (NEW KPI: Cross-Level Stuff Delta), 04.3",
      "status": "met" },
    { "capability": "Characterise location, chase, and whiff",
      "satisfied_by": "location_tiers + fastball_whiff_by_location + fastball_elevation (NEW KPI: Fastball Upper-Third Rate)",
      "status": "met" },
    { "capability": "Characterise release point and extension",
      "satisfied_by": "release_by_start (NEW KPI: Release Consistency Index) + release_by_level_pitch; surfaced the two-start release discontinuity",
      "status": "met — and became the headline finding" },
    { "capability": "Determine whether he made adjustments in the minor leagues",
      "satisfied_by": "stuff_delta (stuff barely moved) + arsenal usage shift (+16.1 pts four-seam) + aaa_arc (early vs late). Answer: the adjustment is a re-sequencing, not a stuff change",
      "status": "met" },
    { "capability": "Actions for Painter / Realmuto / pitching department / manager",
      "satisfied_by": "report section 'Game-plan takeaways', 13 numbered items across 4 persona blocks; consumer-onboarding personas in 06.2",
      "status": "met" },
    { "capability": "Opponent attack plan vs Baltimore",
      "satisfied_by": "NOT DELIVERED — no Orioles data exists in the repo",
      "status": "descoped, disclosed in report warning box and DQ scorecard" }
  ]
}
```

---

## Open items (human DPO to acknowledge at sign-off — none blocking)

```json
{
  "open_items": [
    { "issue": "The tipping hypothesis (13.8-degree arm-slot spread, 96th percentile) is the report's central causal claim and is CORRELATIONAL. It explains the data better than any alternative on hand, but it is not established. The report says so in its own voice.",
      "source_agent": "data-product-owner", "requires_human": true, "status": "open" },
    { "issue": "Benchmark pool is 31 RHP (23 for arm spread) drawn only from 2026 Phillies games, not league-wide. Percentiles are directional.",
      "source_agent": "source-system-profiler", "requires_human": true, "status": "open" },
    { "issue": "Cross-level spin deltas of +84 to +118 rpm on four pitch types, but +1 rpm on the curveball. Unexplained. No conclusion depends on spin.",
      "source_agent": "data-quality-engineer", "requires_human": true, "status": "open" },
    { "issue": "AAA tier is 101 PA, below the 100-BF publication convention for pitcher rate stats. Platoon splits rest on 65 PA (LHH) and 36 PA (RHH).",
      "source_agent": "use-case-validator", "requires_human": true, "status": "open" },
    { "issue": "Camden Yards park notes are carry-in domain knowledge, not repo-computed. Flagged as such in the report and carry no numbers.",
      "source_agent": "domain-steward-proxy", "requires_human": true, "status": "open" }
  ]
}
```

---

## Publish decision

```json
{
  "certification_recommendation": "ready_to_publish",
  "conditions": "Human DPO acknowledges the 5 non-blocking open items. The single DQ FAIL (opponent coverage) is reclassified non-blocking because the use case was formally descoped to exclude an opponent attack plan; the descope is disclosed in the report's own warning box.",
  "publish_surface": "INTERNAL ONLY — privacy-watchdog blocks external publish (03.4)",
  "publish_approved_by": "pending — human DPO (Kellen Short)"
}
```

> The DPO orchestrator does **not** self-approve publication. This package is handed to the human DPO for the final call.

---

## Ledger update required

The installed `pitcher-scouting-report` skill's `references/uc-ledger.md` is stale (it reads "Next available: UC #12"). It cannot be edited mid-session. **Append this row and set Next available to UC #30 / `dp_uc29` / `uc-pps-024` / `uc-pos-008`:**

| UC | ID | Subject | Status | Key artifacts |
|---|---|---|---|---|
| 29 | uc-pps-023 | Painter return read vs BAL (2026-07-31) | Delivered | `dp_uc28_painter_vs_orioles*` + `uc-pps-023-*.md`; **first self-scout variant** of the uc-pps pattern (opponent dimension formally descoped); adds 3 new KPIs and the benchmark-pool method |

---

## Deliverables index

| File | What |
|---|---|
| `README.md` | Package overview |
| `USE_CASE_uc-pps-painter-return-001.md` | The use-case contract (yml + business context) |
| `00`–`07` | Department artifact files (Strategy → Platform/Marketing) |
| *(MLB repo)* `dp_uc28_painter_vs_orioles.py` | Build script — the only place numbers are computed |
| *(MLB repo)* `dp_uc28_painter_vs_orioles_report.md` / `.pdf` | Reader report, 11 pages |
| *(MLB repo)* `dp_uc28_painter_vs_orioles_dashboard.html` | Self-contained interactive dashboard |
| *(MLB repo)* `dp_uc28_build_pdf.py` / `dp_uc28_build_dashboard.py` | Renderers |
| *(MLB repo)* `out/dp_uc28_*` | 23 CSV receipts, 5 figures, console receipt |
