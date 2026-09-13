# 01 · Strategy & Intake — `uc-pps-030-painter-vs-braves-001`

**UC #44 · `uc-pps-030` · `dp_uc44`** · Strategy & Intake department (`coa-dept-strategy`)
Agents: `use-case-validator`, `source-system-profiler`, `domain-steward-proxy`, `business-glossary-agent`

---

## The ask

> *"Andrew Painter needs to step up for a Phillies team that should leave Atlanta with a win… Can Painter
> deliver after a rough outing against the Astros during the week? … I sketched out a scouting report on a
> notecard. Pitch Maps by stand on the left side of the card with maybe a one-stat callout for how he performs
> against each side of the plate. Then on the right a few lines to describe his pitches. 'High-Ride FF' (21%
> Whiff and 16.8 in. Vert) and 'Plus FS' (39.5% Whiff to LHB) and 'Lands Breaking Balls' (Above Average IZR).
> An interesting twist to this could be assessing his pitches on a 20-80 scouting scale…"*

Decision the product serves: **the game plan for one start**, specifically the pitch-selection plan by
handedness, and the bullpen's expectation of how deep the start goes.

Stakes as stated by the client (carry-in, unverified in the log): the Phillies are three games clear of
Arizona for a wild-card berth and one game back of the Cubs for the top seed and home field in a three-game
series. Atlanta is out of reach.

## Prior art (mandatory retrieval before scoping)

| Artefact | What was inherited | What was re-tested |
|---|---|---|
| `uc-pps-023-painter-return-001` (UC #29, 2026-07-31) | The subject, the entity lock, the "four-seam is the anomaly" thesis, the multi-level evidence pattern, the descope-the-opponent precedent | **The four-seam thesis** — it holds, but the numbers have moved a full grade. **The splitter finding** (.395 whiff to LHH, usage collapse 21.4% → 10.6%) — the collapse continued to zero |
| `_scratch_painter_lhv_scouting_20260709.md` | Dev-scratch AAA read; the "fastball finish" watch item | The watch item resolved in an unexpected direction: he did not improve fastball finish, he moved the fastball up and changed what it is for |
| `uc-pps-029` (UC #43, 2026-09-12) | The kernel, the receipt architecture, the BID format, the tag-drift instinct | — |
| `uc-pos-009` | The sensor-boundary rule (never impute pre-instrument data) | Applied to `arm_angle`, and it is why that analysis is descoped rather than partially reported |
| `uc-pps-025` | "Assert the coordinate convention" | Asserted from the data: negative `plate_x` is the third-base side |

**Retrieval finding worth recording:** `uc-pps-023`'s finding #5 was *"the lefty weapon was shelved."* Eleven
weeks later it is not shelved, it is **replaced**. A prior UC's finding aged into a different finding. This is
the argument for re-testing inherited conclusions rather than restating them, and it is the single most
valuable thing in the intake.

## Gap report (`use-case-validator`)

| # | Gap | Blocking? | Resolution |
|---|---|---|---|
| G-1 | The ask does not say which window to grade. The client's own notebook cuts at 2026-07-21; the roster event is 2026-07-31 | **Blocking** | Resolved by DPO discretion: **grade the post-option window (07-31 →)**, reconcile the card against the client's 07-21 cut so his numbers are reproducible, publish both. See `02` §design change |
| G-2 | "Above Average IZR" has no stated population | **Blocking** | Resolved by SG-2. Pooled breaking-ball in-zone rate graded against RHP pitcher-seasons with ≥100 breaking pitches: **.477 → grade 55**, 68th percentile. The claim is confirmed on its own terms |
| G-3 | The 20-80 scale is requested but not specified — no population, no floor, no handling of the normality assumption | **Blocking** | Resolved by SG-1/SG-2/SG-3 before any grade computed. `03` §2 |
| G-4 | The opponent lineup is not supplied and no Braves cache exists in the repo | Non-blocking | Resolved: Atlanta bats reconstructed from Phillies **pitching** rows across 12 head-to-head games, names by `des`-parse, ids by MLBAM. 17 bats, 9 over 13 PA |
| G-5 | Grant Holmes is named but the repo has no opponent-pitcher name field (standing defect O-10) | Non-blocking | Resolved: id 656550 confirmed externally and locked. 260 pitches available — **against Philadelphia only**, which bounds what may be said |
| G-6 | Standings, seeding and probable starters are asserted by the client and exist nowhere in the data | Non-blocking | Logged as manual carry-ins in the freshness manifest and reprinted in the report's data-window box. No conclusion in this package depends on them |

## Premises stress-tested (falsify-before-describe — standing policy)

| # | Client premise | Verdict | Evidence |
|---|---|---|---|
| P-1 | "High-Ride FF — 21% Whiff and 16.8 in. Vert" | **SURVIVES** | 24 whiffs / 110 swings = **.218**; IVB **16.97"** on 218 pitches, on the client's own 07-21 cut. Full-season equivalents are .148 and 16.52" — the cut is doing real work and the client chose it correctly |
| P-2 | "Plus FS — 39.5% Whiff to LHB" | **SURVIVES AS ARITHMETIC, FAILS AS A PLAN** | 30/76 = **.395**, exact. Every one of those 76 swings came before 2026-06-18. **Zero splitters** in the eight starts since the option. This is the engagement |
| P-3 | "Lands Breaking Balls — Above Average IZR" | **SURVIVES** | Pooled breaking in-zone **.477** vs a population mean of **.446** (sd .064, n = 179) → **grade 55**, z = +0.49, 68th pctile. Stable across both windows (.4769 / .4777) |
| P-4 | "A rough outing against the Astros" | **SURVIVES, WITH THE CAUSE RELOCATED** | 2026-09-08: 27 BF, .438 xwOBA, **.550 xwOBA on contact**, 2 HR, 8 of 19 tracked BIP hard-hit. But 6 K / 2 BB and a CSW of 27.6% that ranks fifth of eight — his process was normal. The two starts over .400 xwOBA are the only two with multiple home runs |
| P-5 | "He did not face them in the big wraparound series last weekend" | **SURVIVES** | Atlanta at Philadelphia 09-04 → 09-07; Painter started 09-02 and 09-08. Confirmed from the game log, not from the schedule |

Two of five premises carry a material qualification. Neither is an error by the client; both are the
difference between a number and a decision.

## Source-system fitness (`source-system-profiler`, F1–F4 gate)

| Gate | Check | Result |
|---|---|---|
| F1 · Existence | Does the CDE set exist at the required grain? | **PASS** — pitch-level, 120 columns, all 23 required CDEs present |
| F2 · Volume | Is there enough of it to answer the question? | **CONDITIONAL PASS** — 720 pitches / 185 PA in the graded window. Above the floor for pitch-level rates, **below** it for by-stand × by-pitch cells, which is why those carry denominators instead of grades |
| F3 · Quality | Null rates, value ranges, duplicates | **PASS with one FAIL** — `plate_x/z`, `zone`, `release_speed`, `pfx_x/z` are 100% complete; `release_extension` 1 null; **`arm_angle` 54% null → FAIL** |
| F4 · Freshness | Is the cache current enough for a D+1 decision? | **PASS** — through 2026-09-12, T-1 |

**F3 failure consequence:** arm-slot / release-point analysis — the signature angle of `uc-pps-023` — is
**descoped**. The sensor-boundary rule from `uc-pos-009` forbids imputing across an instrument gap, and a
54%-complete field cannot carry a distributional claim. This is recorded as a descope with cause, not as an
oversight, and the report explicitly declines to restate the prior UC's arm-spread finding as current.

**Benchmark-frame fitness:** the 2015–2026 pull yields 393,126 right-handed pitches. Pitcher-season counts at
a 100-pitch floor: FF 232, SI 138, SL 92, CH 56, CU 45, FC 37, FS 25, **ST 14**. Only the sweeper fails the
25-pitcher-season minimum, and the floor-lowering rule exists because of it.

## Opponent resolution (`domain-steward-proxy`)

**Atlanta hitters.** No Braves cache exists. Built from `phillies_role == 'pitching'` rows across the 12
Philadelphia–Atlanta games in the 2026 log. Batter identity is the MLBAM `batter` id; display names come from
a modal parse of the `des` free-text field (the `uc-pps-011` method — never hand-keyed). 17 distinct bats
resolved, 9 above 13 PA. `stand` is the modal value per batter, which correctly renders switch-hitters as the
side they take against a right-handed pitcher.

**Grant Holmes.** MLBAM 656550. The repo carries no opponent-pitcher name field (standing defect O-10), so the
id was fixed two ways: (a) the arsenal fingerprint in the log — a six-pitch right-hander starting 2026-04-19,
04-24 and 09-07 against Philadelphia — and (b) an external identity lookup. Both agree. **This is an
improvement on `uc-pps-029`**, which had to ship an inferred opponent id and escalate it; the same class of
gap cost nothing here because the identity was confirmed rather than reasoned.

Bound on what may be said: the 260 Holmes pitches in this repo are **all against Philadelphia**. Every Holmes
number in the report carries that qualification. His season profile is not available and is not estimated.

## Glossary position (`business-glossary-agent`)

Seven new terms drafted, all **provisional**, none ratified:

| Term | Status | Nearest existing term | Why it is not that term |
|---|---|---|---|
| `scouting_grade_20_80` (SG-1) | Provisional | — | No existing repo term maps a metric to an ordinal scouting scale |
| `benchmark_population` (SG-2) | Provisional | `uc-pps-023` "benchmark pool" | That pool was 2026-only, one pitch type, one purpose. SG-2 is a parameterised constructor with declared floors |
| `grade_divergence_flag` (SG-3) | Provisional | — | New concept: disagreement between a parametric and a rank-based grade |
| `pitch_grade` (SG-4) | Provisional | — | Composite; deliberately excludes shape, which is the governed decision worth recording |
| `grade_label` (SG-5) | Provisional | — | Controlled vocabulary so reports cannot invent adjectives |
| `arsenal_turnover_index` (AR-1) | Provisional | `cross_level_stuff_delta` (`uc-pps-023`) | **Near-miss.** That measures *shape* change in one pitch across levels. AR-1 measures *composition* change across time. Different grain, different question. Documented in `03` §1 |
| `pitch_map_centroid` (PM-1) | Provisional | house pitch-map convention | Formalises what the house charts already draw, and adds dispersion so a tight centroid on a wide cloud cannot pass as a location |

## Declared DPO discretion

1. **Grading window = post-option, not full season.** Costs 62% of the sample. Buys a number that describes a
   real pitcher. Disclosed at the top of the report.
2. **The client's 07-21 cut is preserved for reconciliation only.** His numbers reproduce on his cut; the
   analysis runs on the roster date. Both are published so neither is a surprise.
3. **Head-to-head retained but disarmed.** Printed with plate appearances and with the turnover index that
   makes it unusable, rather than cut — because a cut table gets re-derived and believed.
4. **Grades published on non-normal populations, with the disagreement published too.** Suppression would have
   been the larger unstated claim.
5. **No clarifying questions asked before building.** The ask was specific, the client asked the organization
   to drive the additions, and a bidder that interviews the client mid-build has not understood the RFP. Every
   judgment call above is disclosed here instead.
