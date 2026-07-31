# 01 — Strategy & Intake

**Department:** `coa-dept-strategy` · **Lead:** `strategy-lead`
**Use Case:** `uc-pps-painter-return-001` · UC #29 · `uc-pps-023` · `dp_uc28`
**Layer 1 verdict:** ✅ **GO** — 1 blocking gap resolved by descope, 4 non-blocking carried forward.

Agents run: `use-case-validator` → `source-system-profiler` → `domain-steward-proxy` → `business-glossary-agent`.
`visual-intake-agent` not invoked (request arrived as written prose, not an image).

---

## 1.1 `source-system-profiler` — fitness for purpose

Run **before** the validator's final verdict, because the blocking question was empirical: does the data exist?

### Entity resolution

| Step | Result |
|---|---|
| Candidate | "Andrew Painter" |
| Resolved MLBAM id | **691725** |
| Method | id lookup in `data/opponents/painter.parquet` (2022 A/A+ log, single-pitcher file), cross-confirmed against `phils_2026.parquet` and `lhvp26.parquet` |
| **Lock applied** | `pitcher == 691725` in every load path. **No name filtering anywhere.** |

> Entity-lock rationale is not academic here. The repo's canonical failure is the Nola / "Nolan Hoffman" contamination from name-substring matching. `player_name` never appears in a filter in this build.

### Tier inventory

| Tier | Source | Filter | Rows | Window | Starts | Fitness |
|---|---|---|---|---|---|---|
| **MLB** | `data/phillies/phils_2026.parquet` | `phillies_role=='pitching' & pitcher==691725 & game_type=='R'` | **1,141** | 2026-03-31 → 06-17 | 14 | **FIT** |
| **AAA (supporting)** | `data/opponents/lhvp26.parquet` | `pitcher==691725` | **396** | 2026-06-28 → 07-26 | 5 | **FIT** for stuff/usage/whiff; **LOW** for EV/xwOBA |
| **Benchmark pool** | `phils_2026.parquet`, both roles | `game_type=='R' & p_throws=='R'`, ≥150 four-seams | 31 pitchers | 2026 | — | **FIT, narrow** |
| Opponent (BAL) | — | — | **0** | — | — | **ABSENT** |
| 2022 minor-league log | `data/opponents/painter.parquet` | `pitcher==691725` | 415 | 2022-04-09 → 06-04 | — | **NOT USED** — pre-injury, four years stale, different pitcher |

**Freshness:** `lhvp26.parquet` is current through **2026-07-30** (T-1 from game day). `phils_2026.parquet` is current through 2026-07-29, but Painter's last MLB pitch is 2026-06-17, so the MLB tier is complete regardless.

**52 spring-training pitches** (`game_type=='S'`) were found in the MLB tier and excluded. Left in, they would have contaminated the velocity baseline and the usage mix.

### CDE completeness — the decisive finding

The whole use case turns on whether the minor-league feed carries real tracking data. It does.

| CDE | MLB | AAA | Verdict |
|---|---|---|---|
| `release_speed`, `release_spin_rate`, `spin_axis` | 100% | 100% | ✅ |
| `pfx_x`, `pfx_z` (movement) | 100% | 100% | ✅ |
| `plate_x`, `plate_z`, `sz_top`, `sz_bot`, `zone` | 100% | 100% | ✅ |
| `release_pos_x`, `release_pos_z`, `release_extension`, `arm_angle` | 100% | 100% | ✅ |
| `effective_speed` | 100% | 99.2% | ✅ |
| `launch_speed`, `launch_angle` | 35.9% | 36.9% | ⚠️ balls in play only |
| `estimated_woba_using_speedangle` | 25.9% | 25.0% | ⚠️ **restricted** |

**Fitness ruling:** Lehigh Valley carries a full Hawk-Eye install. Cross-level comparison of **stuff, release, and location** is defensible. Cross-level comparison of **contact quality** is not, and expected-outcome metrics are barred outright (see 01.3-Q3).

---

## 1.2 `use-case-validator` — gap report

| # | Gap | Class | Resolution |
|---|---|---|---|
| **G1** | Request names an opponent ("against the Baltimore Orioles") but **zero Orioles rows exist** in the repo and Painter has never faced them (2026 opponents: ATH ATL AZ BOS CIN CLE CWS LAD MIA MIL PHI SF WSH) | 🔴 **BLOCKING** | **Descoped.** Use case re-anchored as a self-scout. Escalated to DPO → resolved at 00. Carried as a visible DQ FAIL and disclosed in the report's warning box. |
| G2 | AAA tier is 101 PA — below the repo's 100-BF convention for publishing pitcher rate stats | 🟡 non-blocking | Accepted with mandatory disclosure: every AAA rate prints its PA or swing count. |
| G3 | "Make adjustments" is not operationally defined in the request | 🟡 non-blocking | Operationalised by `kpi-calculator` as three testable axes: **stuff** (Cross-Level Stuff Delta), **sequencing** (usage by level/count/stand), **mechanics** (Release Consistency Index, extension, arm angle). |
| G4 | No acceptance threshold given for "what should we look out for" | 🟡 non-blocking | DPO set the bar: every finding must terminate in a named action for at least one of the four personas. Report section "Game-plan takeaways" is the acceptance surface. |
| G5 | Park effects requested implicitly (venue named) but no Camden Yards data in repo | 🟡 non-blocking | Carry-in only, flagged in-text, **no numbers attached**. |

**Verdict: GO.** The blocking gap is a scope problem, not a feasibility problem. Everything the four personas actually need is computable from the two tiers on hand.

---

## 1.3 `domain-steward-proxy` — domain rules and quirks

No human domain steward for `pps`. Standing in from repo documentation and prior UC history.

**Q1 — Is the AAA tier comparable to the MLB tier at all?**
Partially. Velocity, spin, movement, release, and extension are physical measurements from equivalent Hawk-Eye installs and compare directly. **Pitch classification does not** — the tagging model is fit per level. The slider/sweeper boundary is the known hazard.
*Steward ruling:* comparisons of **shape** are permitted; comparisons of **tags** require verification. The build verifies it — sliders average −6.3" (MLB) and −6.9" (AAA) horizontal break, sweepers −15.7" and −15.8". Distinct in both feeds. The usage shift is real, not an artifact.

**Q2 — Can outcome quality be compared across levels?**
**No.** Triple-A hitters are not major-league hitters. Any rate that depends on hitter quality (whiff, chase, wOBA, hard-hit) is interpretable *within* a level and *directionally* across levels, never as an equivalence.
*Steward ruling:* the report must state the level, the sample, and the caveat every time it crosses the boundary. It does — the four-seam whiff comparison explicitly notes that .212 vs AAA hitters equals the *median MLB* four-seam rate.

**Q3 — Is `estimated_woba_using_speedangle` usable?**
**No.** Standing repo fix from **UC-PPS-021 (Nola)**: pitch-level `get_stats.xwoba` was deprecated as a DQ defect. That ruling is inherited here and extended — no expected-outcome metric appears anywhere in this report, at either level.

**Q4 — What is the known history on this pitcher?**
Prior scratch analysis exists (`_scratch_painter_lhv_scouting_20260709.md`, 2 AAA starts, `pp26_milb_np.csv`). It is **superseded** by this UC: different source file (`lhvp26.parquet`), 5 starts instead of 2, and a governed build. Two of its conclusions are **contradicted** by the fuller sample and the contradiction is deliberate:
- Scratch said *"extension recovered to 2022 form."* This build shows extension **declining monotonically** across all five AAA starts (6.451 → 6.293 ft).
- Scratch said *"stuff is MLB-ready right now, this is a build-up assignment."* This build agrees on the stuff and disagrees on the diagnosis — the MLB-tier evidence (26th-percentile four-seam whiff on ordinary shape) says there was a real problem to solve, not just innings to accumulate.

*Steward ruling:* the scratch note is dev-scratch, never certified, and is superseded. Recorded here so the contradiction is on the record rather than a silent overwrite.

**Q5 — Rubber position and release point.**
Release coordinates shift when a pitcher moves on the rubber, and also when a park's camera calibration differs. Distinguishing them requires a **same-park control**.
*Steward ruling:* the build has one. Starts 6/28 and 7/10 were both at Lehigh Valley and their four-seam release differs by 5.6 inches. Calibration cannot produce that. The finding is mechanical.

---

## 1.4 `business-glossary-agent` — term status

All physical CDEs used in this build are Statcast-native and already carry approved glossary entries from prior UCs. **No new physical terms.**

Three **derived** terms were drafted for the three new KPIs, submitted by `kpi-calculator` (02.2), and approved for use in this UC:

| Term | Status | Note |
|---|---|---|
| **Release Consistency Index (RCI)** | ✅ approved, UC-scoped | Within-start dispersion of four-seam release, inches. Direction: lower is tighter. |
| **Fastball Upper-Third Rate (FUTR)** | ✅ approved, UC-scoped | Share of four-seams at or above the upper third of the batter's own zone. **Explicitly not a quality score** — direction is context-dependent. |
| **Cross-Level Stuff Delta (XLSD)** | ✅ approved, UC-scoped | Signed AAA-minus-MLB difference in velo/spin/ride/horizontal break, per pitch type, with a mandatory noise guard. |

**Promotion candidate:** `arm_spread_deg` (max-minus-min mean arm angle across a pitcher's pitch types) was used as a **tipping proxy** and is *not* yet a glossary term. It is drafted but held at provisional pending a wider population study — see 03.1 and 07.3. Flagged to the human DPO because it carries the report's central causal claim.

**No CDE meaning was inferred by any agent.** Every derived term traces to physical CDEs with an explicit formula recorded in 02.2.
