# 01 · Strategy & Intake — `uc-pos-014-turner-2026-recency-001`

**Department:** Strategy & Intake · **Agents:** `use-case-validator`, `source-system-profiler`,
`domain-steward-proxy`, `business-glossary-agent` (glossary output in `03`)
**Gate:** Layer 1 must close before Layer 2 design begins. **Status: CLOSED — GO with 3 non-blocking gaps.**

---

## 1.1 · `use-case-validator` — the ask, decomposed

The submitted prose is one paragraph with a delegation clause. It decomposes into eight answerable
questions. Each is bound to an acceptance criterion before any analysis is run.

| Q | Question as submitted | Answerable? | Acceptance criterion |
|---|---|---|---|
| **Q1** | "What is going on with him **recently**" | Yes, once "recently" is defined | A window ≥ 50 PA, its boundary declared before results are seen, and a sensitivity scan proving the finding is not an artifact of the boundary |
| **Q2** | "…and maybe this year in general" — high-level performance | Yes | 2026 season line vs his own career and vs a Phillies-hitter population benchmark, with percentile placement |
| **Q3** | "**defining where he has struggled** this year" | Yes | Struggle localised to at least one of: window, pitch group, handedness, count state, contact quality — each with a stated floor |
| **Q4** | "what **'good'** has looked like in the past… with the Phillies and in his prior career" | Yes | A per-season career panel 2015→2026 across both source systems, with era labels derived not assumed |
| **Q5** | "underlying **indicators** affecting his performance" | Yes | Process metrics (contact quality, bat tracking, expected outcomes) reconciled against results; luck vs skill separated |
| **Q6** | "potential **actions by personas** within the Phillies hitting department" | **Partially** | Answerable only as *observable → persona remit → testable hypothesis*. **Causation is not identifiable in this data plane** (no coaching, medical, or intervention log). This limit is stated in the deliverable, not buried |
| **Q7** | "Has his **approach changed**?" | Yes | Decision metrics (swing, chase, in-zone swing, first-pitch swing) compared across windows and seasons; "approach" is defined as *decisions*, distinct from *outcomes* and from *what pitchers do to him* |
| **Q8** | "certain **pitches or pitch groups**… trend against **lefties or righties**" | Yes | Pitch-group and pitch-type splits by window; platoon splits by window **and** by season; platoon exposure counterfactual (PL-1) to separate performance from scheduling |

### Premises detected and flagged for adjudication (C-1, `uc-pps-027`)

The ask contains three soft premises. Under the standing falsify-before-describe policy each is tested
before it is described, and each may come back FALSE.

| P | Premise | How it will be tested |
|---|---|---|
| **P1** | He *has* struggled this year | Season line vs his own 11 prior seasons and vs the Phillies hitter-season population |
| **P2** | Something is happening *recently* that differs from the season | Window split + breakpoint sensitivity scan |
| **P3** | His approach *has* changed | Decision metrics only; outcome and pitcher-behaviour metrics are reported separately so a change in what is *done to him* is never mis-read as a change in *his* approach |

**G8 compliance (`uc-pps-028`):** no superlative ("worst", "career-low", "best") may appear in the
deliverable without a named metric and an enumerated cohort. The parent product `uc-pos-006` was caught by
its own verification gate making exactly this error ("career-low" → corrected to "PHI-era low"); that
correction is inherited as a standing check here.

---

## 1.2 · DPO latitude — the three discretionary calls, declared up front

The requester delegated direction to the `data-product-owner`. Discretion exercised after seeing results is
indistinguishable from result-fitting, so all three calls are recorded here, before the build.

1. **"Recently" = 2026-08-01 → 2026-09-02 (W3).** Chosen as a calendar month boundary, not an outcome
   boundary, and set against **W1 early (Mar 26–Jun 30)** and **W2 July (Jul 1–31)**. July is broken out on
   its own because the parent product ended mid-July with July flagged as an unresolved surge — it is the
   claim under test, not a convenience bucket. A **breakpoint sensitivity scan** across candidate cuts is a
   mandatory receipt (RC-5).
2. **"Good" = three reference points, not one.** (a) his own peak seasons (defined by wOBA, cohort =
   his 12 qualified seasons); (b) his Phillies-era norm 2023–2025; (c) the Phillies hitter-season population
   2015–2026 (≥ 50 PA) for percentile placement. A single "career average" would hide that his WSN peak and
   his PHI norm are different animals.
3. **This is an EXTENSION of `uc-pos-006`, not a fresh study.** Therefore the standing
   **parent-reproduction check** applies: the parent's published figures are recomputed on the parent's own
   window and its own definitions before any new claim is made. Divergence is a defect to report — in the
   data plane *or* in this organization's own kernel — not a rounding note.

---

## 1.3 · `source-system-profiler` — fitness for purpose

Detail in `02_engineering_design.md` §Source profile. Headline: **fit for purpose on Q1–Q5, Q7, Q8; Q6
structurally limited.**

| Source | Rows | Cols | Coverage | Verdict |
|---|---|---|---|---|
| `data/opponents/turner.parquet` | 15,279 | 93 | 2015-08-21 → 2022-10-15, WSN + LAD, single batter id | **FIT** for career results, approach, contact quality. **UNFIT** for bat tracking (columns absent) |
| `data/phillies/phils_{2023..2026}.parquet` | 9,759 (subject rows) | 123 | 2023 → **2026-09-02** | **FIT** for everything, incl. bat tracking from 2024 |
| `wOBA and FIP Constants.csv` | — | — | seasonal weights incl. 2026 | **FIT** |

---

## 1.4 · Gap report

### Blocking gaps
**None.** Layer 2 may begin.

### Non-blocking gaps — carried into the deliverable as declared limits

| ID | Gap | Disposition |
|---|---|---|
| **G-1** | **No coaching / medical / intervention log exists in this data plane.** Q6 asks what personas *could have done*; nothing in the data can attribute an outcome to an action | Answer Q6 as hypotheses mapped to persona remit. State the limit in §1 of the report and in `07`. Do **not** soften it into implied attribution |
| **G-2** | **No batting-order / lineup-slot column.** Any "top of the order" framing is unavailable | Out of scope, declared. Nearest governed proxies (PA volume, base-out state) are reported instead |
| **G-3** | **Bat tracking is structurally absent before 2024 and absent from the pre-PHI source entirely.** "Has his swing changed vs his WSN peak?" cannot be answered on measurables | NULL, never imputed (uc-pos-009 sensor boundary). Bat-tracking comparisons are confined to 2024–2026 and labelled as such |

### Watch items (not gaps — risks to the finding)

| ID | Risk |
|---|---|
| **W-1** | September 2026 is **9 PA** at build time — far below the 50-PA floor. It must never be a bucket anyone ranks; the recency window is Aug 1 → Sep 2 as a whole |
| **W-2** | The recency window (~129 PA) is above floor but is five weeks. Sub-splits inside it (platoon, pitch group) fall below floor fast and must carry ⚠ |
| **W-3** | 2021 contains a **midseason WSN → LAD trade**. Era must be derived per row from the batting side of the half-inning, never carried in from a roster assumption |
| **W-4** | The two sources have **asymmetric schemas** (30 PHI-only columns). Any career-spanning metric must be checked for column availability on the pre-PHI side before it is charted, or 2015–2022 will silently render as zero |

---

## 1.5 · `domain-steward-proxy` — inherited domain rules applied to this build

| Rule | Source | Application here |
|---|---|---|
| 50-PA floor for batter rate stats | `repo-search-before-declaring-kpi-new` | Sept (9 PA ⚠), sub-splits inside W3 |
| Sensor-boundary NULLs are never imputed | `uc-pos-009` | bat tracking, untracked BIP |
| `xwOBAcon ≠ xwOBA` (O-4) | `uc-pps-025` | shifts compared, levels never cross-compared to wOBA |
| `estimated_woba_using_speedangle` is per-PA in this schema | `uc-pps-028` | asserted as a DQ rule at build, not assumed |
| Breakpoint scan required when the window is outcome-selected | `uc-pos-011` RC-5 | mandatory receipt |
| Coordinate convention must be asserted, not assumed | `uc-pps-025` | pull-air build refuses to publish if RHB pulled grounders do not sit on the expected side |
| Parent-reproduction check | `uc-pps-028` | 15 parent figures recomputed before any new claim |
| Say "the data product organization", not "Company of Agents" | DPO preference, `uc-pps-026` | applied throughout |

---

*Gate decision: **GO.** 0 blocking, 3 non-blocking, 4 watch items. Signed off by `data-product-owner`
2026-09-03.*
