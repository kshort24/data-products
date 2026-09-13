# 00 · DPO Orchestration Record — `uc-pps-030-painter-vs-braves-001`

**UC #44 · contract `uc-pps-030` · build `dp_uc44` · v1.0.0 · 2026-09-13**
Value stream: Phillies Pitching (`pps`) · Human DPO: Kellen Short
Status: **READY-CONDITIONAL** · independently verified **247 / 247**

---

## 1 · The ask and framing

A Game 3 advance on Andrew Painter at Atlanta with wild-card seeding stakes, delivered against three inputs
the client supplied himself: a hand-sketched index card carrying three specific numbers, a speculative
20-80 scouting-scale KPI, and a working notebook cell that cuts the season at 2026-07-21.

The organization read the ask as **three jobs stacked in one sentence**, and sequenced them in this order:

1. **Falsify the card.** Three checkable claims arrived with the ask. Anything built on top of an unchecked
   claim inherits its error.
2. **Specify the scale before computing it.** "Normally distributed around 50" is a distributional assumption,
   not a formatting choice. It gets a population, a floor, and a test.
3. **Then build the advance.** Only after 1 and 2 is there anything worth putting in front of a catcher.

That order is the whole engagement. Reversing it produces a beautiful card that repeats a stale number.

## 2 · Delivery plan (departments actually engaged)

| Layer | Agent / capability | What it actually did here |
|---|---|---|
| Strategy & Intake | `use-case-validator` | 6 gaps, 5 client premises stress-tested. Two did not survive |
| | `source-system-profiler` | F1–F4 fitness gate over 12 seasons; `arm_angle` failed and forced a descope |
| | `domain-steward-proxy` | Atlanta hitter resolution by `des`-parse; opponent-starter identity check |
| Engineering Design | `data-architect` | Two-frame model (subject window / benchmark pitcher-seasons), no join fan-out |
| | `eda-agent` | 8 findings; two of them changed the build (see `02` §EDA) |
| | `join-validator` | Population join is a groupby, not a merge — fan-out impossible by construction; verified anyway |
| | `metadata-mapper` | 23 physical columns mapped to CDEs; 2 unmapped and surfaced |
| | `dashboard-specifier` | Three-control spec (window × handedness × pitch) with a stated failure mode |
| Governance | `business-glossary-agent` | 7 new terms drafted; all **provisional**, none ratified |
| | `kpi-calculator` | SG-1…SG-5, AR-1, PM-1 specified in plain language before any code |
| | `technical-lineage-builder` | Column-level trace for every published number |
| | `privacy-watchdog` | Public-performance data, no PII beyond published player identity — CLEAR |
| | `data-tagger` | Internal — Restricted; external publish blocked |
| | `version-controller` | v1.0.0; breaking-change policy on the population definition |
| Engineering Build | `data-engineer` | `dp_uc44_kernel.py` + build + 30 receipts |
| Quality & Certification | `dq-rule-definer` / `data-quality-engineer` | 19 DQ checks; 1 FAIL (forced the descope), 1 WARN |
| | `certification-agent` | 7-family verification harness, 247 assertions |
| Consumer Success | `consumer-onboarding-agent` / `analytics-enabler` | Persona routing, re-run recipe, the single attack rule |
| Platform & Marketing | `cost-watchdog` / `token-economist` | Bid vs actual, 5 calibration findings, 6 tripwires |

**Not engaged:** `machine-learning-engineer` (no forecasting in scope), `data-observability` (this is a
point-in-time advance, not a published pipeline).

## 3 · Governance gate checks

| Gate | Result |
|---|---|
| G1 · Entity locked to an MLBAM id before any computation | **PASS** — `pitcher == 691725`, single `player_name`, asserted at build time and re-verified independently |
| G2 · Opponent identity resolved, not assumed | **PASS** — 656550 confirmed externally. Improvement on `uc-pps-029`, where O-10 forced an inference |
| G3 · Rule-1 search before declaring any KPI new | **PASS** — 7 candidates searched against the repo; 0 collisions, 1 near-miss (`cross_level_stuff_delta`, `uc-pps-023`) documented |
| G4 · Locked KPIs inherited verbatim, not re-derived | **PASS** — Section A byte-identical to `dp_uc43_kernel` Section A |
| G5 · Known-defect exposure measured against this build | **PASS** — 6 defects read; 1 exposed (O-5), 3 not exposed, 2 not applicable |
| G6 · No published rate below its declared floor | **PASS** — curveball ungraded at 16 pitches, by design and by assertion |
| G7 · Small samples print their denominators | **PASS** — verified as a narrative assertion, not a style rule |
| G8 · Cross-level evidence never blended | **PASS** — AAA loaded unweighted, used for context only |
| G9 · Every published number reconciles to a receipt | **PASS** — family E, 40 narrative assertions |
| G10 · Distributional assumption of a new KPI tested | **PASS** — and it **failed on three populations**, which is disclosed in the report body rather than a footnote |

## 4 · Capability fulfilment

| Client capability requested | Delivered as | Where |
|---|---|---|
| "Pitch maps by stand on the left with a one-stat callout" | The notecard figure, and the live card | `out/dp_uc44_fig1_notecard.png`, dashboard |
| "A few lines to describe his pitches" on the right | The arsenal rail, six pitches, one line of shape + one of volume each | same |
| "Assess his pitches on a 20-80 scouting scale" | SG-1…SG-5, with population, floors, and a normality test | `03` §2, `out/dp_uc44_grades.csv` |
| "Consult prior work done on Andrew Painter" | `uc-pps-023` findings carried forward and **re-tested**, not restated | `01` §prior art, report §4 |
| The notebook cell's First/Second-Half cut | Adopted as the *reconciliation* frame and replaced by the option-date cut as the *analysis* frame, with the reason stated | `02` §design change |
| "Other additions driven by the organization" | AR-1 arsenal turnover; the tag-drift control; the four-seam elevation grade; the by-stand leak table | report §3, §4, §6 |
| PDF report | 10 pp, branded | `dp_uc44_painter_vs_braves_report.pdf` |
| "Explore an interactive dashboard" | Self-contained card, three controls, four receipt tables | `dp_uc44_painter_scouting_card.html` |

## 5 · The finding, in the DPO's words

The client's card is right three times out of three. Every number on it reconciles to the pitch log exactly —
21.8% four-seam whiff, 16.97 inches of ride, 39.5% splitter whiff to left-handed hitters, and a breaking-ball
in-zone rate that does grade out above average (55, 68th percentile). This shop did not find an error.

What it found is that **the three numbers are not about the same pitcher**. The four-seam line describes the
arm that will start tonight. The splitter line describes the arm that got optioned in June: Painter has thrown
**zero splitters in eight starts back**, and the pitch that replaced it is a changeup that is three miles an
hour harder, three inches flatter and three inches more run — and, by expected damage, better (.160 xwOBA
against, a 75 on the results grade). The whiff difference to left-handed hitters (.395 → .301) does not clear
significance at 76 versus 73 swings.

That one substitution reorganizes the entire advance. It explains why the platoon has flipped (29.7% strikeout
rate against right-handed hitters, 18.1% against left-handed); it explains why 47 plate appearances of April
head-to-head history against Atlanta cannot be used as a plan (arsenal turnover between that sample and
tonight: 0.33); and it puts the actual, actionable leak in a cell nobody would have looked at — the **sweeper
to left-handed hitters**, thrown in the zone 64.5% of the time, missing 20.0% of swings, allowing .523 xwOBA
on nine tracked plate appearances. Atlanta will run six left-handed bats out of its nine most-used.

The four-seam is the second finding and it is a *trade*, not a decline. He moved it up — elevation rate .307 →
.349 against a population mean of .200, a 70 — and doubled its whiff rate from a 35 to a 50. The price is a
command grade of 25 and ninety pitches for twenty-three batters. His overall strike-throwing improved over the
same window, so this is design, not deterioration, and the bullpen should be planned for six innings rather
than seven for that reason and not because of Houston.

## 6 · Where the organization argued with itself

**Which window gets graded.** `eda-agent` wanted the full 2026 season for sample size (484 PA). `kpi-calculator`
refused: a full-season grade averages two arsenals that differ by 37% of their pitches, and the resulting
number describes nobody. The DPO agent sided with the specifier. **Resolution:** grade the post-option window
(185 PA), publish the pre-option card beside it, never blend. This costs statistical power and buys meaning,
and the report says so in the data-window box rather than in a footnote.

**Whether to publish grades on non-normal populations.** `data-quality-engineer` flagged three populations
failing Shapiro-Wilk (sweeper whiff p = .015; changeup and sinker in-zone p = .006 / < .001) and proposed
suppressing those three grades. `certification-agent` objected that suppression is a heavier claim than
disclosure: the question is not whether the population is normal but whether the grade *moves*. **Resolution:**
compute both the z-derived and the rank-derived grade for every metric and publish the disagreement. Eleven of
twelve came back identical; the twelfth (slider command) differs by five points, half the flag threshold. Both
are in the report. Nothing was suppressed and nothing was hidden.

**The sweeper population floor.** Only 14 right-handed pitcher-seasons in twelve years of Phillies games clear
100 sweepers — the pitch is too new. `data-architect` proposed pooling sweepers with sliders. `business-glossary-agent`
refused: a sweeper and a slider are different governed terms with different expected shapes, and pooling them to
fix a sample problem corrupts both. **Resolution:** a mechanical floor-lowering rule (below 25 pitcher-seasons,
drop the floor from 100 to 50 and stamp the grade THIN), applied automatically rather than by judgment, and
disclosed on the card itself. The sweeper's grades are the only THIN ones in the package.

**Whether the splitter→changeup swap is a pitcher decision or a Statcast tagging change.** `eda-agent` raised
it; nobody could answer it from Painter's own rows. **Resolution:** build the control. League splitter share
across every pitcher in the Phillies log went 4.14% in June to 5.39% in September with six arms still throwing
165 of them — the classifier did not move. It is a pitcher decision. This control is now a standing
requirement for any future AR-1 reading (`03` §2).

**Whether to keep the head-to-head table at all.** `consumer-onboarding-agent` wanted it cut — 47 plate
appearances, maximum 7 per hitter, against a retired arsenal, and a coach who sees a table will use it.
`analytics-enabler` argued that cutting it guarantees someone re-derives it in a notebook next week and
believes it. **Resolution:** keep it, print the plate appearances, and put the reason it is unusable in the
same row. The report says so in three places.

## 7 · Escalations to the human DPO

1. **The card needs re-dating, not correcting.** "Plus FS — 39.5% whiff to LHB" is a true statement about a
   pitch that is out of the arsenal. Recommend it stays in the file with a date stamp, because if the splitter
   comes back it is the best single number this shop has on it. **Decision needed:** does the card get
   re-issued with the changeup line, or does it keep both with dates?
2. **Seven new governed objects, all provisional.** SG-1…SG-5, AR-1 and PM-1 are specified, executed and
   verified but **not ratified** — ratification requires an independent second use. The 20-80 family is
   general: it will grade any pitcher against any declared population. The cheapest ratification is the next
   uc-pps advance. **Decision needed:** ratify on second use, or hold for a formal review?
3. **`arm_angle` is 54% null and the `uc-pps-023` arm-spread finding cannot be refreshed.** That finding
   (13.8° of arm-slot spread against a 4.25° pool median, 96th percentile) was one of the five headline
   findings of the last Painter UC. It is now unverifiable on this cache. **Decision needed:** is this a cache
   problem worth fixing upstream, or is `arm_angle` simply not a field this repo can build on?
4. **The slider is the quiet one.** It grades 50 overall and is the only metric on the card where the z-grade
   and rank-grade disagree. It is also the pitch whose usage fell hardest (21.4% → 13.5%) without an obvious
   reason. Not escalated as a problem — escalated as the most likely subject of the next UC.
5. **Standings and probable starters are carry-ins.** Nothing in the parquet confirms who starts tonight or
   where anyone sits in the wild-card race. Every strategic framing in this package rests on the client's
   statement of them.

## 8 · Publish recommendation

**READY-CONDITIONAL — internal, need-to-know.**

Conditions:
- **C1** The package is valid for the 2026-09-13 start only, anchored to a log ending 2026-09-12. The build
  refuses to run against a different anchor. A refreshed cache is a new use case.
- **C2** The 20-80 grades are relative to a **Phillies-schedule population**, not a league population. Any
  external use of the number "60" must carry that sentence with it.
- **C3** The sweeper grades are THIN (population n = 29 at a lowered floor). Read ±1 grade.
- **C4** The platoon split is directional (p = 0.075). It is published because it aligns with a mechanism and
  with tonight's lineup, not because it clears a threshold.
- **C5** Arm-slot analysis is descoped with cause; the `uc-pps-023` finding must not be restated as current.
- **C6** All seven new governed objects are provisional. No downstream build may treat SG-1 as ratified.

External publication: **blocked**. Distribution: manager, pitching coach, catcher, pitching analyst.

Closure step: post-game backtest, 8 checks, `07_platform_marketing.md` §4.
