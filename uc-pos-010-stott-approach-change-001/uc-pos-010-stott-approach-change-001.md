```yml
# Identity
name: Bryson Stott 2026 Approach-Change Diagnostic
id: uc-pos-010-stott-approach-change-001
description: >
  Bryson Stott's 2026 batting results have improved steadily since an atrocious April.
  This use case establishes the month-to-month factual record of that improvement, then
  tests whether it is accompanied by a measurable change in plate approach — as opposed to
  a change in outcomes alone. Delivers a governed monthly curated dataset (the `z` frame),
  a results panel, an approach panel, and a results-vs-process divergence read.

# Classification
value_stream: Phillies Offense
value_stream_code: pos
status: Draft — pending Use Case Validator intake
priority: High

# People
personas: Hitting Coach, Manager, Performance Analyst, Player (Bryson Stott), Data Product Owner
owner: Kellen Short

# Relationships
parent_use_case: null
sub_use_cases: []
related_use_cases:
  - uc-pos-stott-qab-001              # PRIOR UC ON THIS SUBJECT PLAYER — QAB Rate; physical field names
  - uc-pos-006-turner-2026-offense    # hitter down-year diagnosis; RF-1 trajectory / RF-2 rolling form
  - uc-pos-009-schwarber-swing        # sensor-boundary NULL standard; bat-tracking measurables
  - uc-pos-005-harper-own-the-zone    # OZ decision family; shadow-band geometry
  - uc-pos-004-schwarber-first-half   # wRC / P-per-PA (SC-1, SC-2); 50-PA floor in practice
  - uc-pos-002-risp-2out              # composite-vs-independent index precedent; 20-PA situational exception
  - uc-pps-017-luzardo-first-half     # SOURCE OF THE EXISTING `fpsr` IMPLEMENTATION
  - uc-pps-rangel-scouting-001        # `cde.fpsr` approved in contract
  - uc-cat-001-catcher-game-calling   # canonical is_swing / is_whiff / is_in_zone lineage

# Metadata
created: 2026-08-15
last_updated: 2026-08-15
uc_ledger_number: 34 (PROVISIONAL — verify via `ls dp_uc*` in the MLB repo before claiming)
build_artifact_prefix: dp_uc33 (PROVISIONAL — same verification required)

# Data References
kpis:
  inherited: plate_apps, woba, ops, ba, obp, slg, runs_created, hard_hit_rate, whiff_rate,
             barrel_rate, ev90, chase_rate, bbrate, krate
  inherited_approved: fpsr (First-Pitch Strike Rate) — ALREADY GOVERNED, see AP-1
  new_candidates: AP-2 swing_rate, AP-3 swing_rate_first_pitch (srfp),
                  AP-4 Approach Delta Panel, AP-5 Results-Process Divergence
data_domains: Player Identity & Season Aggregates, Pitch-Level Event & Description,
              Plate Discipline / Swing Decision, Batted-Ball Contact Quality,
              Count & Sequence State, Calendar / Season Time
```

# UC-POS-010: Bryson Stott 2026 Approach-Change Diagnostic

> **Reading order note.** Business Context names KPIs and intent. Data Specification is the
> single source of truth for how each is computed, at what grain, and from which CDEs. Any KPI
> named in Business Context without a row in *Derived Metrics and Data Functions* is an open item
> for the Use Case Validator.

---

## Business Context

### Problem Statement

Bryson Stott opened the 2026 season badly. His April was, in the requester's words, atrocious.
His batting results have grown steadily in the four months since. The Phillies coaching staff now
faces a question that recurs for every mid-season turnaround and that outcome statistics alone
cannot answer: **did the player change something, or did the results change around him?**

Those two explanations imply opposite decisions. If Stott altered his approach — swinging at
different pitches, in different counts, with different intent — the staff should identify what
changed, reinforce it, and protect it through the stretch run and into 2027 planning. If the
approach is unchanged and only the results moved, the improvement is a regression-to-the-mean
artifact riding on contact luck, sequencing, and opponent mix. Reinforcing a coaching cue that
did not cause the improvement is worse than doing nothing: it manufactures a false causal story
that gets re-applied to the next slumping hitter.

This use case deliberately separates the two questions and sequences them. **First** establish
the facts — how did month-to-month performance actually move this season. **Then**, and only
against that established baseline, test the approach hypothesis. The order matters because the
approach panel is only interpretable against a results record the staff has already agreed on.

The data product's job is not to declare a verdict. It is to make the results record and the
approach record legible side by side at the same grain, so a Hitting Coach can see whether they
move together.

### Personas

| Persona | Description | Primary Business Questions / Actions |
| ------- | ------------ | ------------------------------------- |
| Hitting Coach | Owns mechanical and approach intervention. Decides what cue to give, what to reinforce, and what to leave alone. | BQ-2, BQ-3, BQ-4, BQ-6 · Actions A-1, A-2, A-5 |
| Manager | Owns lineup construction, batting-order slot, and platoon deployment. Needs to know whether the improvement is durable enough to bet lineup position on. | BQ-1, BQ-5, BQ-6 · Actions A-3, A-4 |
| Performance Analyst | Builds and interprets the diagnostic. Owns the reliability read — whether a monthly move is signal or sample. | BQ-1, BQ-2, BQ-5, BQ-6 · Actions A-5, A-6 |
| Player (Bryson Stott) | The subject. Consumes a simplified read of what changed in his own approach, in language that maps to intent at the plate rather than to metric names. | BQ-3, BQ-4 · Actions A-1, A-2 |
| Data Product Owner | Kellen Short. Owns scope, KPI ratification, and every open decision flagged in this document. | All · Governance decisions |

### Business Questions

**Phase 1 — Establish the facts (must be answered before Phase 2 is interpretable):**

- **BQ-1.** How did Stott's results move month-to-month in 2026 — April through the current
  partial month — across rate outcomes (BA/OBP/SLG/OPS/wOBA), volume (plate appearances), and
  run production (runs created)?
- **BQ-2.** Is the month-to-month movement monotonic ("grown steadily"), or is the "steady
  improvement" narrative an artifact of comparing endpoints against an unusually bad anchor?

**Phase 2 — Test the approach hypothesis:**

- **BQ-3.** Has Stott changed *what he swings at*? Specifically: chase rate, overall swing rate,
  and first-pitch swing rate month-to-month.
- **BQ-4.** Has Stott changed *what happens when he swings*? Whiff rate, hard-hit rate, barrel
  rate, and EV90.
- **BQ-5.** Has the *pitcher's* approach to Stott changed — is he seeing more or fewer first-pitch
  strikes, which would move his outcomes without any change on his part?
- **BQ-6.** Do the results and the underlying contact quality move together, or has the results
  line outrun the process line — indicating the improvement is not yet earned?

> **BQ-5 is the confound question and is not optional.** A hitter's outcome line can improve
> entirely because opposing pitchers started attacking him differently. First-Pitch Strike Rate is
> the cheapest available read on that, which is why it is specified as a first-class KPI rather
> than a supporting statistic.

### Key Metrics or Key Performance Indicators (KPIs)

**Results panel** (inherited, already in circulation across pos-side use cases):
`plate_apps` · `ba` · `obp` · `slg` · `ops` · `woba` · `runs_created`

**Contact-quality panel** (inherited):
`hard_hit_rate` · `barrel_rate` · `ev90`

**Approach panel** (partly inherited, partly new):
`chase_rate` · `whiff_rate` · `bbrate` · `krate` · **`swing_rate` (AP-2, new)** ·
**`swing_rate_first_pitch` / `srfp` (AP-3, new)**

**Pitcher-intent panel** (new):
**`fpsr` — First-Pitch Strike Rate (AP-1, new)**

**Diagnostic composites** (new, candidate — see open decisions):
**AP-4 Approach Delta Panel** · **AP-5 Results-Process Divergence**

### Actions

- **A-1.** Reinforce a specific, identified approach change with the player (Hitting Coach → Player).
- **A-2.** Withhold a coaching cue where the data shows no approach change — avoid manufacturing a
  false causal story.
- **A-3.** Adjust batting-order slot to reflect a durable change in on-base or damage profile.
- **A-4.** Adjust platoon deployment if the approach change is handedness-conditional.
- **A-5.** Escalate to a deeper diagnostic (bat-tracking, zone/region profile, pitch-type splits)
  where the monthly panel identifies a change but cannot explain its mechanism.
- **A-6.** Flag the case as a reusable template for in-season turnaround diagnosis on other hitters.

### Required Capabilities

- **RC-1.** Ability to view results and approach metrics side by side at a single, common monthly
  grain — not in separate reports at different grains.
- **RC-2.** Ability to distinguish a partial (in-progress) month from a complete month at a glance,
  so it is never compared as an equal.
- **RC-3.** Ability to see the sample size (`plate_apps`, and pitch/BIP counts for rate denominators)
  adjacent to every rate metric, so reliability is never inferred separately from the number.
- **RC-4.** Ability to separate *hitter approach* metrics from *pitcher intent* metrics visually and
  semantically, so the confound in BQ-5 cannot be read as a hitter behavior change.
- **RC-5.** Ability to compare each month against a declared anchor (April) rather than only against
  the adjacent month.
- **RC-6.** Ability to trace every number on the delivered visual back to a governed KPI definition
  and its source CDEs.

### Expected Outcomes

- **Objective:** Correctly classify the 2026 Stott improvement as approach-driven, process-driven,
  or outcome-only — so coaching intervention is applied where it will hold.
  <br>**Key Result:** The `swing_rate_first_pitch` (AP-3) and `chase_rate` monthly series each show
  a directional move from their April baseline — *baseline to be established from `pos` 2026, April
  bucket* — of a magnitude the Analyst can classify as inside or outside monthly noise, delivered
  before the end of the 2026 regular season.

- **Objective:** Prevent the staff from acting on an unearned improvement.
  <br>**Key Result:** AP-5 (Results-Process Divergence, `woba − xwobacon` by month) is reported for
  every month in scope with an explicit in-band / out-of-band call. *Divergence band to be
  established from the `pos` population distribution of monthly `woba − xwobacon`* — the band is not
  known in advance and is an explicit, trackable assumption, not a silent gap.

- **Objective:** Establish a reusable in-season turnaround diagnostic pattern for pos-side hitters.
  <br>**Key Result:** AP-1, AP-2, AP-3 are delivered as `(level, df)`-contract functions with a
  passing verification script, and enter the Baseball Functions Intake Register as ratification
  candidates within one review cycle of delivery.

### Additional Context

- **Requester framing carries an embedded assumption.** "His batting results have grown steadily"
  is a hypothesis supplied with the request, not an established fact. Phase 1 exists specifically to
  test it. If the month-to-month series is not monotonic, the data product reports that plainly
  rather than fitting the narrative. This is the same discipline applied in the Turner down-year
  case (uc-pos-006) in the opposite direction.
- **"Over the last 4 months" and "month-to-month this season" are different windows.** As of
  2026-08-15 the last four months are May, June, July, and a partial August. April is the *anchor*,
  not a member of the window — but it must be present in the dataset for RC-5 to be satisfiable.
  The delivered dataset therefore covers April → current month inclusive.
- **August is incomplete.** The request lands mid-month. Every August figure is a partial-month
  figure and must be labeled as such.
- **Stott is a left-handed batter facing an unbalanced platoon diet.** Handedness of opposing
  pitcher is a known confound for any swing-decision metric and is called out in Assumptions &
  Constraints, not silently absorbed.
- **This is a self-scout use case.** The subject is a Phillies player and the consumers are Phillies
  staff. It inherits the self-scout variant pattern established by uc-pps-023 (Painter return),
  including the deliberate descoping of opponent-facing framing.
- **Provisional identifiers.** `uc-pos-010` and `dp_uc33` are assigned per the last recorded ledger
  state (UC #33 / `uc-pos-009` / `dp_uc32`, delivered 2026-08-08). The ledger is known to lag
  delivered UCs. **Verify with `ls dp_uc*` in the MLB repo before treating these as final.**

---

## Data Specification

> **Guardrail.** This section is the single source of truth for KPI calculation logic, grain, CDEs,
> and semantic mappings. It takes direction from Business Context; it does not restate or re-decide
> business intent.

### Analytical Scope

**Primary analytical focus:** Trend analysis over a within-season time dimension, with a
process-versus-outcome decomposition. Secondary focus: entity comparison against a declared
in-series anchor (April) rather than against a peer population.

**Analytical questions addressed:** BQ-1 through BQ-6 (Business Context).

**Referenced KPIs:** the four panels named in Business Context > Key Metrics, plus AP-4 and AP-5.

### Analytical Grain (Level of Granularity)

**Declared Grain:** *One row represents one batter's aggregated batting performance within one
calendar month of one season.*

**Grain Attributes:** `player_name` · `game_year` · `month`

> `level = ['player_name','game_year','month']` — this is the `(level, df)` contract key passed to
> every KPI function in this use case and is the join key for every merge.

**Non-Grain Attributes** (may be included without increasing grain, because they are constant
within a row given the filter):
`stand` (batter handedness — constant for Stott) · `month_label` · `month_is_partial` ·
`games_played` · `first_game_date` · `last_game_date`

**Other Optional Grain** (would change granularity; reserved for drill-down and future use cases —
**explicitly out of scope for this delivery**):
`p_throws` (platoon split) · `pitch_type` / `pitch_group` · `balls`/`strikes` (count state) ·
`home_away` · `batting_order_slot` · `times_faced`

> **Grain hygiene note for the Join Validator.** `stand` appears in the requester's
> `data_dictionary` object but not in `level` or `kpis`. It is classified here as a **non-grain
> attribute**, not a grain attribute. If it is ever promoted to `level`, every rate denominator in
> this document changes and every KPI must be recomputed. It is not a free addition.

### Canonical Analytical Dataset(s)

**Primary Analytical Dataset — `z` (the curated monthly frame)**

- **Description:** One row per `player_name` × `game_year` × `month` for the subject batter,
  carrying every KPI in the four panels plus reliability denominators. This is the curated dataset
  that drives the data product — the visual layer and any downstream consumption read from `z`, not
  from the pitch log.
- **Required entities:** Batter identity; pitch-level event and description; count and sequence
  state; batted-ball measurement; calendar date.
- **Inclusion criteria:** `player_name == 'Stott, Bryson'`; `game_year == 2026`; regular-season
  games; all pitch rows belonging to plate appearances charged to the subject batter.
- **Exclusion criteria:** Spring training and postseason; any month bucket falling below the
  reliability floor is *reported but flagged*, never silently dropped.

**Derived frame — `zfig` (the presentation projection)**

- **Description:** `z` projected to `level + kpis`, rounded to 3 decimal places, ordered by
  `game_year, month`. Feeds the visual layer.
- **Purpose:** Presentation only. `zfig` must never be the object a downstream consumer joins
  against — rounding to 3 makes it unsuitable as an analytical input.

> ⚠ **Specification defect inherited from the requester's draft, surfaced not fixed.** The draft
> defines `kpis` *before* `swing_rate`, `swing_rate_first_pitch`, and `fpsr` are merged in, then
> builds `zfig = z[level+kpis]`. Under that ordering the three new columns are **silently dropped
> from the presentation frame** — the data product's headline approach metrics never reach the
> visual. Either `kpis` is extended after the merges, or `zfig` is built from an explicit
> presentation column list. This is recorded as a blocking item for the Use Case Validator.

**Secondary / Supporting Datasets**

| Dataset | Purpose |
| --- | --- |
| First-pitch pitch-log subset (`pitch_number == 1`) | Denominator population for AP-1 (`fpsr`) and AP-3 (`srfp`). A filtered view of the same source, aggregated to `level` and left-merged onto `z`. |
| `pos` population monthly distribution | Establishes the AP-5 divergence band and the monthly-noise reference for the Key Results. Not a per-row join — a calibration input. |
| wOBA / FIP constants (`wOBA and FIP Constants.csv`) | Required by `runs_created` (`wrc`). External file dependency — see Assumptions & Constraints. |

### Data Domains and Critical Data Elements

| Data Domain | CDE Name | Purpose in Analysis |
| ----------- | -------- | -------------------- |
| Player Identity & Season Aggregates | `batter_name` | Grain attribute; subject filter. |
| Player Identity & Season Aggregates | `batter_handedness` | Non-grain attribute; platoon-confound context. |
| Calendar / Season Time | `season_year` | Grain attribute. |
| Calendar / Season Time | `game_month` | Grain attribute — the time dimension the entire diagnostic rests on. |
| Calendar / Season Time | `game_date` | Derivation source for `game_month`; partial-month determination; game counting. |
| Pitch-Level Event & Description | `plate_appearance_key` | The unit `plate_apps` counts and every PA-denominated rate divides by. |
| Pitch-Level Event & Description | `pa_result_event` | Terminal PA outcome — drives BA/OBP/SLG/OPS/wOBA/BB%/K%/runs created. |
| Pitch-Level Event & Description | `pitch_result_description` | Per-pitch outcome — drives swing, whiff, chase, and strike classification. |
| Count & Sequence State | `pitch_number_in_pa` | Isolates the first pitch of each PA for AP-1 and AP-3. |
| Count & Sequence State | `balls_before_pitch` / `strikes_before_pitch` | Count-state context; reserved for optional-grain drill-down. |
| Plate Discipline / Swing Decision | `pitch_in_zone_flag` | Chase denominator (out-of-zone pitches). |
| Plate Discipline / Swing Decision | `pitch_location_x` / `pitch_location_z` | Zone determination where `pitch_in_zone_flag` is derived rather than native. |
| Batted-Ball Contact Quality | `exit_velocity` | Hard-hit rate; EV90. |
| Batted-Ball Contact Quality | `launch_angle` | Barrel classification. |
| Batted-Ball Contact Quality | `batted_ball_event_flag` | Balls-in-play denominator for contact-quality rates. |
| Batted-Ball Contact Quality | `expected_woba_on_contact` | AP-5 process comparator (`xwobacon`). **Reference-field provenance rules apply — see Business Glossary.** |
| Run Creation Constants | `woba_scale_constants` | External constants required by `runs_created`. |

> **Physical names are sourced, not fabricated.** The CDE table above stays deliberately logical.
> The Semantic Mapping table below now carries physical names **recovered from shipped repo
> artifacts**, each traceable to a named source — `uc-pos-stott-qab-001` (`events`, `pitch_number`,
> `launch_speed`, `launch_angle`, `game_pk`, `at_bat_number`), `uc-cat-001`'s
> `03_technical_lineage.json` (`description`, `zone`), and `dp_uc17` (`fpsr` internals). Nothing in
> that table is inferred from naming convention. `metadata-mapper` should **confirm** these against
> the live `pos` schema rather than re-derive them.

### Derived Metrics and Data Functions

**Legend — Status:** `INHERITED-RATIFIED` (in the notebook, ratified) · `INHERITED-PROVISIONAL`
(in circulation, not yet ratified per Intake Register v2) · `NEW-CANDIDATE` (first defined here;
must enter Intake Register v3).

| KPI | ID | Input Grain | Output Grain | Required CDEs | Reusable | Status | Notes |
| --- | --- | --- | --- | --- | :-: | --- | --- |
| Plate Appearances | — | pitch | month | `plate_appearance_key` | Y | INHERITED-RATIFIED | Reliability denominator. Emitted by `nresults`. |
| Batting Average | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | |
| On-Base Percentage | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | |
| Slugging | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | |
| OPS | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | OBP + SLG. |
| wOBA | — | PA | month | `pa_result_event`, `woba_scale_constants` | Y | INHERITED-RATIFIED | Primary results metric. |
| Walk Rate | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | Approach-adjacent outcome, not an approach metric. |
| Strikeout Rate | — | PA | month | `pa_result_event` | Y | INHERITED-RATIFIED | Same. |
| Runs Created | — | PA | month | `pa_result_event`, `woba_scale_constants` | Y | INHERITED-PROVISIONAL | `wrc(level, df, constants)` — Intake Register B6, disposition **B**, blocked on a documented constants loader. **Never label `wRC+`.** In-season 2026 constants carry a ±2% label. |
| Hard-Hit Rate | — | BIP | month | `exit_velocity`, `batted_ball_event_flag` | Y | INHERITED-RATIFIED | |
| Barrel Rate | — | BIP | month | `exit_velocity`, `launch_angle`, `batted_ball_event_flag` | Y | INHERITED-RATIFIED | |
| EV90 | — | BIP | month | `exit_velocity`, `batted_ball_event_flag` | Y | INHERITED-RATIFIED | **Quantile at monthly grain — see DQ floors. A 90th percentile over ~25 BIP is not the same estimator as over ~400.** |
| Whiff Rate | — | pitch (swings) | month | `pitch_result_description` | Y | INHERITED-RATIFIED | Contact-execution, not swing-decision. |
| Chase Rate | — | pitch (out-of-zone) | month | `pitch_result_description`, `pitch_in_zone_flag` | Y | INHERITED-RATIFIED | Emitted by `discipline(level, df)` (Register B1). **Collision risk with AP-2 — see below.** |
| **First-Pitch Strike Rate** | **AP-1** | pitch (`pitch_number_in_pa == 1`) | month | `pitch_result_description`, `pitch_number_in_pa`, `plate_appearance_key` | Y | **INHERITED-APPROVED** ⚠ | **DO NOT BUILD A NEW FUNCTION.** `fpsr(level, df)` already exists (`dp_uc17`, inherited from `dp_uc11`/`dp_uc8`/Baseball Functions) and `cde.fpsr` is **status: approved** in `contract/uc-pps-rangel-scouting-001.contract.yaml`. Consume as-is. This UC's only new work is a **cross-value-stream reuse note** — see below. |
| **Swing Rate** | **AP-2** | pitch | month | `pitch_result_description` | Y | **NEW-CANDIDATE** | Function `swing_rate(level, df)`. Swings ÷ total pitches seen. |
| **First-Pitch Swing Rate** | **AP-3** | pitch (`pitch_number_in_pa == 1`) | month | `pitch_result_description`, `pitch_number_in_pa` | Y | **NEW-CANDIDATE** | **Not a separate function.** `swing_rate(level, df[df.pitch_number == 1])` — same function, filtered input, left-merged onto `z` with an explicit suffix. Output column `swing_rate_first_pitch`, alias `srfp`. |
| **Approach Delta Panel** | **AP-4** | month | month | AP-2, AP-3, `chase_rate`, `whiff_rate`, `bbrate`, `krate` | Y | **NEW-CANDIDATE** | Each approach metric expressed as a signed delta from the April anchor. **Composite-vs-independent is an open DPO decision.** |
| **Results-Process Divergence** | **AP-5** | month | month | `woba`, `expected_woba_on_contact` | Y | **NEW-CANDIDATE** | `woba − xwobacon` by month. Answers BQ-6. **Provenance labeling is mandatory — see Business Glossary.** |

#### AP-2 / AP-3 — the `swing_rate` function contract

```
swing_rate(level, df) -> DataFrame

  Signature      (level, df)  — conforms to the repo-standard KPI contract.
                 Positional order is (level, df), matching the §5 ruling that
                 flipped `pulled_air`. Do not define it as (df, level).

  Denominator    Count of pitch rows in df, grouped by level.
  Numerator      Count of pitch rows in df whose pitch_result_description
                 indicates the batter offered at the pitch, grouped by level.
  Output         level + ['swings', 'pitches_seen', 'swing_rate']
                 Denominator columns ship WITH the rate. A rate that arrives
                 without its denominator cannot satisfy RC-3.
  Null handling  A level group with zero pitch rows does not appear in the
                 output (it is not a zero-rate row). Left-merge onto z
                 therefore yields NULL, not 0.0 — and NULL is correct.
  AP-3 usage     swing_rate(level, df[df.pitch_number == 1])
                 Identical logic, filtered input. One definition, two
                 populations — never two functions.
```

#### AP-1 — `fpsr` is an existing approved term. Consume, do not redefine.

```
fpsr(level, df) -> DataFrame        # EXISTING — dp_uc17 line 211, inherited from dp_uc11 / dp_uc8

  Signature      (level, df)        — already conforms to the repo contract.
  Population     df filtered to pitch_number == 1.
  Denominator    m.pitches   (count of first-pitch rows == count of PAs)
  Numerator      m.pitches - m.balls
  Formula        first_pitch_strike_rate = (pitches - balls) / pitches
  Output column  first_pitch_strike_rate
```

**The numerator question is already settled by the shipped implementation.** `(pitches − balls)`
is the *complement of a ball* — which is option (a), the received broadcast/scouting definition:
called strike, swinging strike, foul, **and ball in play** all count as a first-pitch strike. This
matches Intake Register §8 Principle 2 (*the library implements the received definition*) and it
has been in continuous use across `dp_uc8` → `dp_uc11` → `dp_uc17` → `dp_uc19`, with
`cde.fpsr` carrying **status: approved** in the Rangel contract and reconciling to ±.004 in
`dp_uc17_verification.py`.

> **Correction to an earlier draft of this document.** AP-1 was initially specified as a new
> candidate function with an open numerator decision. **That was wrong**, and it was wrong in the
> specific way Intake Register §8 Principle 1 exists to prevent: it would have created a second
> implementation of an already-approved term. The error was caught by a repo-wide search, not by
> reasoning. *Search the repo before declaring a KPI new.*

**What genuinely is new here — and it is not a function.** Every prior `fpsr` use is **pitcher-side
(`pps`)**, measuring a pitcher's own first-pitch execution. `uc-pos-004` states this explicitly:
*"pps UCs' FPSR/CSW are pitcher-side."* This UC is the **first batter-side (`pos`) consumption** of
the term. The arithmetic is identical; the **subject of the sentence inverts** — here it describes
what pitchers did *to* Stott, not what Stott did.

That inversion is the entire reason for RC-4 (visual separation of the pitcher-intent panel). It
requires a **glossary annotation, not a new term**: `business-glossary-agent` should add a
value-stream-context note to the existing `cde.fpsr` entry, and `version-controller` should classify
the cross-stream reuse as **non-breaking** (no formula change, no consumer impact).

Residual edge cases the existing implementation resolves implicitly by taking the complement of
`balls`, and which should be *confirmed rather than re-litigated*: HBP on 0-0, pitchout, and
pitch-clock automatic ball all fall on the ball side; foul bunt with zero strikes falls on the
strike side.

#### Open DPO decisions in this section

> These are surfaced, not resolved. Per the Use Case Validator's charter, downstream agents must
> not silently pick a convention.

1. **AP-2 — which canonical swing list?** A swing classifier already exists in this repo, but in
   **two variants that disagree**, and both are in shipped code:
   - `dp_uc7_wheeler_mets.py` L191/L200 (`chase_rate`, `whiff_rate`) and `uc-cat-001`'s
     `03_technical_lineage.json` both use the **8-value** list:
     `['foul','foul_bunt','foul_tip','hit_into_play','missed_bunt','swinging_pitchout','swinging_strike','swinging_strike_blocked']`
   - `dp_uc7_wheeler_mets.py` L437 (`SWINGS`) uses the **7-value** list — identical except
     **`swinging_pitchout` is absent**.
   - `uc-pos-002`'s `_SWING_DESCS` is a third declaration of the same concept.

   `uc-cat-001` cites *"`Baseball Functions.ipynb` cell 21 canonical lists"* as the authority, so a
   canonical list exists in the notebook — but two files in this repo diverge from each other, which
   means at least one is stale. **This is a live Intake Register §8 Principle 1 violation already
   present in the codebase, not a new risk introduced by this UC.** The DPO must ratify one list;
   `swing_rate` (AP-2) must then consume it rather than declare a fourth.

   Practical note: `swinging_pitchout` is vanishingly rare, so the two lists will almost always
   produce identical numbers — which is exactly what makes the drift dangerous. It will not be
   caught by a value comparison.

2. **AP-2 relationship to `discipline()`.** Given a ratified list, `swing_rate` should be an
   **additional output column of the existing discipline family**, not a parallel function.
   `discipline(level, df)` (Register B1, disposition A) already computes swing membership to derive
   `chase_rate` and `whiff_rate`; it simply does not currently expose the unconditioned rate. If
   `swing_rate` is built standalone, `swing_rate` and `whiff_rate` can contradict each other inside
   the same delivered row of `z` — a swing count that fails to reconcile with the denominator of
   the hitter's own whiff rate. *The `discipline()` body could not be read from this folder; the
   notebook lives in the MLB repo.*

3. **AP-4 composite vs. independent.** Does the Approach Delta Panel roll into a single index, or
   report as independent per-metric deltas? Precedent: UC-POS-002 flagged exactly this for the
   Approach Degradation Index and retained the decision at DPO level rather than letting
   `kpi-calculator` silently combine. **Recommendation: report independently for this delivery.**
   A composite hides sign-cancellation — a hitter who chases less but also swings less in the zone
   nets to "no change" under a composite while having changed a great deal.

4. **`month` definition.** Is `month` a native column in `pos`, or derived from `game_date`? If
   derived, is it calendar month or month-of-season? And is the conventional March/April merge
   applied? The 2026 season's late-March games, if any exist in `pos`, will either form a
   two-game "month 3" bucket that destroys the visual's axis or silently fold into April. Both are
   defensible; only one can be true, and it must be declared.

5. **AP-5 band calibration.** The divergence band is stated in Expected Outcomes as
   "to be established from the `pos` population." Whether that population is all pos-side hitters,
   all qualified hitters, or Stott's own prior seasons is undetermined and changes the verdict.

### Semantic Mapping (Data Dictionary)

The requester supplied a partial `data_dictionary` object. It is reproduced here as the **display
label** layer and reconciled against CDEs. Unmapped rows are the `metadata-mapper`'s work queue.

| CDE Name | Physical Field | Business Term (display label) | Required |
| -------- | --------------- | -------------- | :-: |
| `batter_name` | `player_name` | Batter Name | Y |
| `season_year` | `game_year` | Season | Y |
| `game_month` | `month` | Month | Y |
| `batter_handedness` | `stand` | Batter Handedness | N |
| `plate_appearance_key` | `game_pk` + `at_bat_number` (composite) | Plate Apps → `plate_apps` | Y |
| `pa_result_event` | `events` | — (input, not displayed) | Y |
| `pitch_result_description` | `description` | — (input, not displayed) | Y |
| `pitch_number_in_pa` | `pitch_number` | — (input, not displayed) | Y |
| `pitch_in_zone_flag` | `zone` (in-zone = `zone <= 9`; out-of-zone = `zone > 9`) | — (input, not displayed) | Y |
| `exit_velocity` | `launch_speed` | — (input, not displayed) | Y |
| `launch_angle` | `launch_angle` | — (input, not displayed) | Y |
| `expected_woba_on_contact` | `estimated_woba_using_speedangle` (restricted to `type == 'X'`) | xwOBA on Contact (Statcast model estimate) | Y |
| — (KPI output) | `woba` | wOBA | Y |
| — (KPI output) | `ops` | OPS | Y |
| — (KPI output) | `chase_rate` | Chase Rate | Y |
| — (KPI output) | `fpsr` | First Pitch Strike Rate | Y |
| — (KPI output) | `swing_rate` | Swing Rate | Y |
| — (KPI output) | `swing_rate_first_pitch` | First Pitch Swing% | Y |

> **Reconciliation findings against the supplied `data_dictionary`:**
> - `stand` is labeled but is not in `level` or `kpis` — it will not appear in `zfig` and its label
>   is currently inert. Classified above as a non-grain attribute; keep the label, note it is unused
>   until `stand` is explicitly selected.
> - `ba`, `obp`, `slg`, `runs_created`, `hard_hit_rate`, `whiff_rate`, `barrel_rate`, `ev90`,
>   `bbrate`, `krate` are in `kpis` but have **no display label**. They will render as raw column
>   names on any axis or tooltip. The dictionary is incomplete relative to the KPI list.
> - `month` has no label and no formatter. A numeric month axis (4, 5, 6, 7, 8) is a legibility
>   defect for the Manager and Player personas.

### Business Glossary

| CDE Name | Business Term | Business Definition | Notes |
| -------- | -------------- | -------------------- | ----- |
| `game_month` | Month | The calendar month in which a game was played, within a single season. The time bucket the entire diagnostic is grouped by. | Definition open — see DPO decision 4. |
| — | Plate Appearance | A completed turn at bat by the batter, terminating in a recorded PA outcome. | The reliability denominator for this use case. |
| — | Swing | A pitch whose `description` is a member of the canonical SWINGS list. | **NOT a new term — but the repo holds two conflicting canonical lists** (8-value incl. `swinging_pitchout`, and 7-value without it), plus a third declaration in `uc-pos-002`'s `_SWING_DESCS`. `uc-cat-001` cites `Baseball Functions.ipynb` cell 21 as the authority. **Ratify one; consume it. Do not declare a fourth.** See DPO decision 1. |
| — | Swing Rate | The share of all pitches seen at which the batter offered. A measure of aggression, independent of pitch quality or location. | **New — AP-2.** Distinct from Chase Rate (which conditions on location) and from Whiff Rate (which conditions on having swung). |
| — | First-Pitch Swing Rate | The share of first pitches of a plate appearance at which the batter offered. | **New — AP-3.** The sharpest single read on early-count intent available from the pitch log. |
| — | First-Pitch Strike Rate | The share of plate appearances in which the first pitch is not a ball — `(pitches − balls) / pitches` over `pitch_number == 1`. Called strikes, swinging strikes, fouls, and balls in play all count. | **EXISTING APPROVED TERM — `cde.fpsr`, status approved** (Rangel contract). Implementation in `dp_uc17` L211, inherited from `dp_uc11`/`dp_uc8`. **This describes the pitcher's execution against the batter, not the batter's behavior** — hence the separate panel (RC-4). **New in this UC only:** first batter-side (`pos`) consumption of a term used exclusively pitcher-side until now. Needs a value-stream context annotation, **not** a new term. |
| `expected_woba_on_contact` | xwOBA on Contact (`xwobacon`) | Mean expected wOBA over batted-ball events, computed from the Statcast expected-wOBA-by-speed-and-angle field restricted to balls in play. | **Ratified governed KPI** per Intake Register §4.3. Reproducible from CDEs by a stated formula. |
| `expected_woba_on_contact` | *(the underlying field)* | Statcast model output — published result, unpublished method. | **REFERENCE FIELD, NOT A KPI.** Must be labeled as a vendor model estimate wherever displayed; never presented as a locally computed metric. Pitch-level `get_stats.xwoba` is **DEPRECATED — do not cite.** |
| — | Runs Created | Batting run production expressed on the wOBA scale using published seasonal constants. | Per Intake Register: **never label this `wRC+`**; in-season 2026 constants carry a ±2% label. |
| — | April Anchor | The April 2026 monthly bucket, used as the fixed comparison baseline for every AP-4 delta. | New term specific to turnaround-diagnostic use cases. Generalizable as *"anchor month."* |
| — | Partial Month | A month bucket whose games do not span the full calendar month because the season is in progress, began mid-month, or the player was unavailable. | Must be flagged, never silently compared as equal to a complete month. |

### Data Quality Expectations

**CDE-Level Expectations** — primary input to the DQ Rule Definer and Data Quality Engineer.
Specifiable now; no dependency on KPI Calculator output.

| CDE Name | Quality Dimension | Threshold or Expectation |
| -------- | ------------------ | -------------------------- |
| `batter_name` | Completeness | 100% non-null across all rows in scope. |
| `batter_name` | Validity | Exactly one distinct value (`'Stott, Bryson'`) after the subject filter. Any second value is a filter defect. |
| `season_year` | Validity | Exactly one distinct value (2026) in the delivered frame. |
| `game_month` | Completeness | 100% non-null. |
| `game_month` | Validity | Values within the season's playing months. Any bucket outside April–current is a March/April-merge defect — see DPO decision 4. |
| `game_date` | Consistency | `game_month` must equal the month derived from `game_date` for every row. This is the rule that catches a bad `month` derivation. |
| `plate_appearance_key` | Uniqueness | One terminal PA row per key. Duplicate terminal rows inflate every PA-denominated rate. |
| `plate_appearance_key` | Completeness | 100% non-null on terminal-event rows. |
| `pitch_number_in_pa` | Validity | Minimum value is 1 within every PA; the count of `pitch_number == 1` rows must equal the PA count for that month. **This is the join-integrity rule for AP-1 and AP-3.** |
| `pitch_result_description` | Completeness | 100% non-null on all pitch rows. A null here silently deflates swing, whiff, and chase rates by shrinking the numerator while the denominator holds. |
| `pitch_result_description` | Validity | Every distinct value must map to exactly one of {swing, take} and one of {strike, ball, in-play, other} under the ratified classifier. **An unmapped description value is a blocking DQ failure, not a warning.** |
| `pitch_in_zone_flag` | Completeness | Non-null on all pitch rows used as a chase denominator. |
| `exit_velocity` | Completeness | Expected non-null on batted-ball rows; **sensor gaps are NULL, never imputed** (uc-pos-009 sensor-boundary standard). |
| `exit_velocity` | Validity | Physically plausible range; values outside it are flagged, not clipped. |
| `expected_woba_on_contact` | Completeness | Non-null on batted-ball rows. Null rate reported per month — a month with elevated nulls has an unreliable AP-5. |
| `woba_scale_constants` | Completeness | Constants row present for 2026. Absent → `runs_created` is not computed and is emitted NULL, not silently zero. |

**KPI-Level Plausibility Checks** — business-facing sanity bounds, secondary to CDE rules.

| KPI | Expected Distribution / Range | Notes |
| --- | ------------------------------- | ----- |
| `plate_apps` | Roughly 70–120 per complete month for an everyday player; materially lower for the partial August bucket. | A complete month far below this range indicates missed games — check before interpreting any rate in that row. |
| `ba` / `obp` / `slg` | Within league-plausible bounds; `obp ≥ ba` must hold in every row. | `obp < ba` is an arithmetic impossibility and a hard failure. |
| `ops` | Must equal `obp + slg` to rounding tolerance in every row. | Cheapest available internal-consistency assertion. |
| `woba` | Within league-plausible bounds for a monthly bucket. | Monthly variance is wide; do not tighten this into a false alarm. |
| `swing_rate` (AP-2) | Bounded [0, 1]; league-typical band for a contact-oriented LHH. | A value outside [0,1] means the swing classifier and the denominator disagree. |
| `swing_rate_first_pitch` (AP-3) | Bounded [0, 1]. First-pitch swing rate is conventionally *below* overall swing rate for most hitters. | Not an assertion — a directional expectation worth flagging if violated. |
| `fpsr` (AP-1) | Bounded [0, 1]; league-typical first-pitch strike band. | Compare against a league reference before drawing a conclusion for BQ-5. |
| `chase_rate`, `whiff_rate` | Bounded [0, 1]. | |
| `ev90` | Must fall between the month's median and maximum exit velocity. | **Requires a batted-ball floor to be meaningful — see below.** |
| AP-5 (`woba − xwobacon`) | Centered near zero over a full season; monthly values disperse widely. | The band is uncalibrated — see DPO decision 5. |

**Reliability floors** (guardrails, not thresholds — a row below floor is reported and flagged,
never dropped):

> **Floors are inherited from the standing repo standard, not invented here.** The
> `phillies-data-analyst` data-quality standard is a **50-PA minimum for batter rate stats**
> (wOBA, xwOBA, barrel%). It is applied as 50 PA in `uc-pos-004` (*"July is soft: .336 wOBA, 2 HR
> in 48 PA — below the 50-PA floor, directional only"*) and in `uc-pos-006`. `uc-pos-002`'s 20-PA
> floor is an **explicit DPO-set exception** for situational RISP/2-out buckets, documented as such
> in its own gap report, and does **not** govern calendar-month buckets. This UC therefore inherits
> **50 PA** and introduces no new PA floor.

| Metric family | Floor | Source | Rationale |
| --- | --- | --- | --- |
| PA-denominated rates (BA/OBP/SLG/OPS/wOBA/BB%/K%/runs created) | **50 PA** per month bucket | **Inherited** — standing batter rate-stat standard | Below this, month-to-month movement is dominated by sampling. Applied identically in uc-pos-004 and uc-pos-006. |
| First-pitch rates (AP-1 `fpsr`, AP-3 `srfp`) | **50 first pitches** per month bucket | **Derived** — equals the PA floor by construction | One first pitch per PA, so this is the PA floor restated, not a second decision. |
| Pitch-denominated rates (AP-2 swing rate, chase rate, whiff rate) | **190 pitches** per month bucket | **NEW — requires ratification** | ~3.8 pitches per PA, so 50 PA ≈ 190 pitches. Derived from the PA floor rather than chosen independently, but the multiplier is an assertion and should be re-derived from Stott's actual P/PA (`ppa`, Register B7, disposition A) rather than assumed. |
| BIP-denominated rates (hard-hit, barrel) | **25 batted-ball events** per month bucket | **NEW — requires ratification** | No repo precedent found for a BIP floor at monthly grain. |
| **EV90** | **40 batted-ball events** per month bucket | **NEW — requires ratification** | A 90th-percentile estimator is far more sample-sensitive than a mean. At 25 BIP, EV90 is effectively the 3rd-hardest ball hit. **The higher floor relative to the other BIP metrics is deliberate, not an inconsistency.** |
| AP-5 divergence | Both `woba` and `xwobacon` above their respective floors | Derived | |

> **Three of these six floors are new to the repo and none should be treated as settled by this
> document.** Ratifying a general *"minimum denominator by metric family at a bucketed grain"*
> standard — rather than a per-UC choice — is the durable fix, and would close the same class of
> gap that `uc-pos-003` flagged as OD-4 and left to a DPO call.

**Partial-month rule:** the current (in-progress) month is flagged `month_is_partial = True` and
carries its own denominator disclosure on every rendered surface. It is never suppressed and never
compared as an equal.

### Assumptions & Constraints

- **A-1.** `pos` covers the player's Phillies tenure. Stott is a Phillies player throughout 2026, so
  the `roster_support` guard established in the Marsh build is not expected to bind — but it should
  still be asserted rather than assumed.
- **A-2.** `month` is available at the pitch-log grain, either natively or derivably from
  `game_date`. If neither holds, the declared grain is unbuildable and this is blocking.
- **A-3.** `pitch_number` resets within each PA. **Corroborated** — `uc-pos-stott-qab-001` uses
  `max(pitch_number) >= 7` per at-bat to identify a battled at-bat, and the shipped `fpsr`
  implementation filters on `pitch_number == 1`; both depend on the same reset behaviour and both
  reconcile in verification. Residual risk is confined to true edge cases (substitution mid-PA,
  ejected batter, PA inherited after a pitching change), which the DQ rule
  *"count of `pitch_number == 1` rows equals the PA count"* is written to catch.
- **A-4.** `runs_created` depends on an external constants file outside the pitch log. Per Intake
  Register §5 this loader is an open item. If the file is unavailable, `runs_created` is emitted
  NULL and its absence is disclosed — it is not approximated.
- **A-5. Opponent quality and platoon mix are uncontrolled.** A hitter's monthly line moves with the
  quality and handedness of the pitchers he faced. This diagnostic does **not** adjust for it. Any
  approach change identified here is *associated with* the period, not *caused by* the player,
  until a controlled comparison is run. This is the single largest interpretive limitation in the
  document and must survive into the delivered narrative.
- **A-6.** Park factors are uncontrolled. Home/away mix varies by month.
- **A-7.** Injury, illness, and rest days are not modeled. A month with depressed `plate_apps` may
  reflect availability rather than performance.
- **A-8.** Regression to the mean is the null hypothesis. An April that is atrocious by chance will
  be followed by better months with no behavioral change whatsoever. The data product must make
  this explanation *visible and defeasible*, not assume it away.
- **A-9.** The season is in progress as of 2026-08-15. Every figure is as-of, and the diagnostic is
  expected to be re-run.

### Out of Scope

- Platoon splits (`p_throws`), pitch-type splits, count-state splits, home/away, and batting-order
  slot. All are listed as optional grain and are deliberately deferred — adding any of them changes
  the declared grain and every denominator in this document.
- Bat-tracking measurables (swing speed, attack angle). Available in principle; escalation path A-5
  covers them. Per Intake Register B8 they are a **reference-field passthrough, not a KPI**.
- Zone/region damage profiling (the OZ family from uc-pos-005).
- Any other hitter. This is a single-subject diagnostic; roster-wide extension is a separate UC.
- Defense, baserunning, and positional value.
- Predictive modeling or rest-of-season projection. This is descriptive and diagnostic only.
- Any causal claim. See A-5.

---

## Implementation

> **Guardrail.** All dataset definitions, grain, KPI logic, and semantic mappings are referenced
> from Data Specification and are not redefined here.

### System Architecture

- **Ingestion Layer:** Existing local parquet/CSV Statcast layer in the MLB repo, accessed through
  the established `get_phillies_data()` API. No new ingestion is introduced by this use case.
- **Processing / Transformation Layer:** Python / pandas in the MLB repo, using the Baseball
  Functions library. All KPI functions conform to the `(level, df)` contract.
- **Storage Layer(s):** Source parquet (read-only) → in-memory `z` frame → CSV receipts written to
  the use-case output directory.
- **Serving / Consumption Layer:** Plotly figure(s) built from `zfig`, plus the CSV receipts.
  Delivered as a report artifact under `data-products/uc-pos-010-stott-approach-change-001/`.

### Data Flow & Pipeline Design

- **Source → Target Mappings:**
  1. Load pitch-level source → filter to subject batter and season → `df`.
  2. `z = nresults(level, df)` — the results and inherited-KPI spine at the declared grain.
  3. `z = z.merge(swing_rate(level, df), on=level, how='left', suffixes=('', '_sr'))` — AP-2.
  4. `z = z.merge(swing_rate(level, df[df.pitch_number == 1]), on=level, how='left',
     suffixes=('', '_first_pitch'))` — AP-3.
  5. `z = z.merge(fpsr(level, df), on=level, how='left', suffixes=('', '_fpsr'))` — AP-1.
  6. Attach `month_is_partial`, `month_label`, reliability-floor flags, and AP-4 / AP-5 derivations.
  7. `zfig = z[presentation_columns].round(3)` — presentation projection.

> ⚠ **Three defects in the requester's draft pipeline, surfaced not fixed.** These are recorded for
> the Use Case Validator and are not silently corrected here.
>
> 1. **Merge suffix collision.** Step 4 in the draft reuses `swing_rate` as the merge source
>    against a frame that already has a `swing_rate` column from step 3. With
>    `suffixes=('', '_first_pitch')`, the *incoming* column is renamed and the resulting column is
>    `swing_rate_first_pitch` — which is the intended name. **But `swings` and `pitches_seen`
>    collide identically**, producing `swings_first_pitch` / `pitches_seen_first_pitch`. That is
>    fine and in fact desirable — but it is accidental rather than specified, and it only works
>    because the left frame is built first. Reordering the merges silently renames the wrong side.
>    **Specify the output column names explicitly rather than relying on suffix mechanics.**
> 2. **Syntax errors in the draft.** The draft merge line has unbalanced parentheses and passes
>    `suffixes='','_first_pitch'` (two positional strings) rather than a tuple. The `px.scatter`
>    call likewise closes `sort_values(...` before `x=`. These will not execute.
> 3. **`zfig = z[level+kpis]` drops the new columns** — already flagged under Canonical Analytical
>    Datasets. `fpsr`, `swing_rate`, and `swing_rate_first_pitch` are not members of `kpis`.
>
> Additionally: the draft's `px.scatter` title reads **"Bryson Stott wOBA by Season"** while the
> x-axis is `month` and the frame is filtered to one season. The title contradicts the encoding.

- **Intermediate Stages:** First-pitch subset (`pitch_number == 1`) is a filtered view, not a
  persisted stage.
- **Persistence Strategy:** raw (parquet, untouched) → curated (`z`, the governed data product) →
  presentation (`zfig`, rounded, non-analytical).
- **Interface Types:** in-memory dataframe; CSV receipts; static/interactive figure.

### Processing & Execution Model

- **Execution Type:** Batch, single-shot.
- **Trigger Mechanism:** Manual, on DPO request. Expected re-run cadence: monthly while the season
  is in progress (A-9), and once at season end.
- **Orchestration Approach:** Single build script (`dp_uc33_stott_approach_change.py`, provisional
  numbering) plus an independent verification script (`dp_uc33_verification.py`) per house pattern.
- **Dependency Structure:** Upstream — the parquet layer and the constants CSV. Downstream — none
  at delivery; the report and CSV receipts are terminal artifacts.

### Environment & Infrastructure

- **Environment Strategy:** Local single-environment (the MLB repo). No dev/test/prod separation.
- **Compute Considerations:** Trivial. Single-player, single-season slice.
- **Storage Considerations:** Receipts measured in kilobytes.
- **Access & Security Boundaries:** Local filesystem only. No external publication.

### Exposure Mechanisms

- **Exposed Artifacts:** the `z` curated monthly dataset (CSV receipt); `zfig` presentation frame;
  the monthly results panel, approach panel, and divergence read; a report artifact.
- **Access Interfaces:** Local file paths under
  `data-products/uc-pos-010-stott-approach-change-001/`.
- **Data Freshness Characteristics:** As-of the last game date present in the source parquet. **The
  as-of date must be printed on every delivered surface** — a mid-season diagnostic without a
  visible as-of date is a misinformation risk the moment it is re-opened.
- **Latency Expectations:** None. Not an operational product.

### Observability & Traceability

- **Key Monitoring Points:** row count of `z` (expected: one row per month played); PA sum across
  months reconciling to the season total; every reliability floor evaluated and its result recorded.
- **Logging / Audit Surfaces:** the verification script's PASS/FAIL ledger.
- **Lineage Anchors:** `uc-pos-010-stott-approach-change-001`; `dp_uc33` artifact prefix; CDE names
  as the join key across the CDE, Semantic Mapping, and Business Glossary tables.

### Implementation Assumptions & Open Questions

- **Assumptions:** the MLB repo is the data plane and this repo is the governance plane; the
  `(level, df)` contract holds for every function used; verification is written independently of the
  build and does not import the build's KPI kernel.
- **Known Gaps:** the three pipeline defects above; the `discipline()` swing-classifier collision
  check (DPO decision 2) cannot be performed from this repo.
- **Deferred Decisions:** output format beyond the CSV receipts (PDF report, interactive HTML, or
  both) — the requester's phrasing implies a Plotly figure at minimum.

### Out of Scope

- Any change to the source parquet layer or the ingestion path.
- Promotion of `swing_rate` / `fpsr` into the Baseball Functions notebook — that is a ratification
  action gated on the Intake Register, not a build step.

---

## Governance

### Ownership & Stewardship

- **Data Owner:** Kellen Short (Data Product Owner) — accountable for business definition, KPI
  ratification, and every open decision in this document.
- **Data Steward:** Data Product Owner agent, with `domain-steward-proxy` standing in for baseball
  domain rules where no human steward is available.
- **Technical Owner:** Kellen Short — the MLB repo is a personal data plane.

| Activity | Owner | Steward | Technical | Consumers |
| --- | --- | --- | --- | --- |
| KPI definition (AP-1…AP-5) | DPO | business-glossary-agent | — | Analyst |
| Open-decision resolution | **DPO only** | use-case-validator (surfaces) | — | — |
| Build & verification | — | — | data-engineer | — |
| Interpretation & action | Hitting Coach / Manager | — | — | All personas |

### Access & Usage Controls

- **Data Sensitivity Classification:** **Internal.** The subject is a public figure and every
  underlying measurement derives from publicly published tracking data. No PII beyond a
  publicly-known player name and publicly-observable on-field performance. **No health, injury,
  contract, or personnel-evaluation data is in scope**, and none may be joined in without a fresh
  privacy review.
- **Authorized Personas / Roles:** Hitting Coach, Manager, Performance Analyst, Player (Bryson
  Stott), Data Product Owner — as named in Business Context > Personas.
- **Permitted Use Cases:** in-season approach diagnosis; coaching-cue formulation; lineup and
  platoon deployment decisions; template development for future turnaround diagnostics.
- **Restricted Uses:** contract or arbitration valuation; public or media distribution; any
  representation of the diagnostic as establishing causation (see A-5); any use of `xwobacon` or
  the underlying expected-wOBA field as a locally-computed metric rather than a labeled vendor
  model estimate.
- **Access Approval Process:** DPO discretion; local artifact.

### Data Lifecycle

- **Retention Policy:** Retained indefinitely as a governed use-case artifact under
  `data-products/`, consistent with every prior UC in this repo.
- **Archival Strategy:** Superseded re-runs are retained alongside, not overwritten — the as-of
  date distinguishes them.
- **Deletion / Purging Rules:** None.
- **Versioning Strategy:** Per-UC directory; `dp_uc33` artifact prefix; re-runs versioned by as-of
  date.

### Data Quality Management

- **Referenced Quality Rules:** Data Specification > Data Quality Expectations (CDE-level rules,
  KPI plausibility checks, reliability floors, partial-month rule).
- **Monitoring Approach and Ownership:** the verification script is the monitoring surface;
  `data-quality-engineer` executes; DPO reviews.
- **Issue Management Process:** Detection (verification FAIL) → Triage (DPO classifies as
  correctness defect vs. conformance work) → Resolution → Communication (recorded in the Validator
  Log below).
- **Escalation Paths:** Any unmapped `pitch_result_description` value, any `obp < ba` row, or any
  `pitch_number == 1` count that disagrees with the PA count **halts delivery** and escalates to
  DPO. These are correctness failures, not warnings.
- **SLA / SLO Ownership:** None — not an operational product.

### Change & Version Management

- **Change Triggers:** ratification of a single canonical SWINGS list; resolution of whether
  `swing_rate` extends `discipline()` or stands alone; any change to the `month` derivation;
  promotion of `swing_rate` into the notebook; ratification of the three new reliability floors;
  any addition to the declared grain.
- **Approval Process:** DPO ratification via the Baseball Functions Intake Register.
- **Versioning Strategy:** `version-controller` classifies. **Pre-classification:**
  - Ratifying one SWINGS list over the other is **breaking** for `chase_rate` and `whiff_rate`
    across **every UC that has ever consumed them** — not just this one. The value impact is
    near-zero (`swinging_pitchout` is vanishingly rare), which makes it *silently* breaking and
    therefore more dangerous, not less.
  - A change to the `month` derivation is **breaking** for every row in `z`.
  - Batter-side reuse of `fpsr` is **non-breaking** — no formula change, no consumer impact.
- **Backward Compatibility Expectations:** AP-2 and AP-3 are new and unratified with no consumers,
  so breaking changes are cheap *now* and expensive after promotion — **this is the correct moment
  to settle them.** AP-1 is the opposite case: `fpsr` already has consumers across four pitcher-side
  UCs, so it must be consumed unchanged.
- **Change Communication Requirements:** recorded in the Validator Log and in the Intake Register.

### Compliance & Risk Controls

- **Regulatory Considerations:** None. Public sports performance data, internal use.
- **Privacy Constraints:** No PII beyond a public player name. `privacy-watchdog` review expected
  to return low risk; the review is still required rather than assumed.
- **Other Policy Constraints:** **Intake Register §8 Principle 3 governs this use case directly** —
  a vendor-modelled field whose computation is not reproducible from the CDEs cannot be a governed
  KPI. `xwobacon` qualifies (stated formula over stated CDEs); the underlying
  expected-wOBA-by-speed-and-angle field does not and must be labeled as a vendor model estimate.
  Pitch-level `get_stats.xwoba` is deprecated and must not be cited.
- **Data Retention & Deletion:** see Data Lifecycle.
- **Audit Requirements:** every headline number in the delivered report must be independently
  reproducible by the verification script without importing the build's KPI kernel.
- **Risk Classification:** **Low technical risk, moderate interpretive risk.** The dominant risk is
  not a wrong number — it is a correct number read as causal. A-5 and A-8 exist to mitigate that
  and must survive into the delivered narrative rather than being confined to this document.

### Lineage & Traceability

- **Lineage References:** Data Specification > Data Domains and CDEs; Implementation > Data Flow.
- **Required Lineage Depth:** **Column level.** Every KPI in `z` traces to its source columns
  through each named transformation hop. `technical-lineage-builder` owns this.
- **Audit Anchors:** UC id; `dp_uc33` prefix; CDE names as the cross-table join key; the as-of date.
- **Reproducibility Expectations:** the build script re-run against the same parquet snapshot
  reproduces every receipt byte-identically; the verification script reproduces every headline by an
  independent path.

### Governance Artifacts, Assumptions, and Open Questions

- **Artifacts:** `Use Case Template.md`; `BASEBALL_FUNCTIONS_INTAKE_REGISTER_v2_2026-07-24.md`;
  the `use-case-validator` gap report accompanying this document; `CLAUDE.md`; `ORG.md`.
- **Assumptions:** the DPO resolves all five open decisions before build; the ledger numbers are
  verified before claiming.
- **Known Gaps:** AP-1 numerator undefined; `discipline()` collision unchecked; AP-4 form undecided;
  `month` derivation undeclared; AP-5 band uncalibrated.
- **Deferred Decisions:** whether AP-1/AP-2/AP-3 go to Round 1 or Round 2 of the next ratification
  sequence.

### Out of Scope

- Redefining datasets, schema, or KPI logic (Data Specification owns these).
- Transformation logic or execution (Implementation owns these).
- Re-stating business definitions already captured in Data Specification.

---

## Delivery & Consumption

### Consumption Context

- **Primary Personas:** Hitting Coach, Manager, Performance Analyst, Player.
- **Decision Points / Workflows:** pre-series hitting meeting; individual player review; lineup card
  construction; off-season / stretch-run development planning.
- **Trigger Moments:** on delivery; on each monthly re-run; whenever the improvement narrative is
  raised in a staff setting and someone needs the factual record.

### Consumption Interfaces

- **Primary Interface Type:** a report artifact combining the monthly panel tables with the figures.
- **Secondary Interfaces:** CSV receipts for the Analyst; the `z` frame directly for ad-hoc follow-up.
- **Interaction Mode:** self-service read; analyst-mediated for the Player and Coach personas.

### Consumption Patterns

- **Usage Type:** Analytical (decision support) and Monitoring (re-run monthly through season end).
- **Frequency of Use:** monthly during the season; episodic thereafter.
- **Depth of Interaction:** aggregate monthly panel → per-metric monthly series → (escalation only)
  pitch-level drill-down, which is out of scope for this delivery.

### Delivered Artifacts

- **User-Facing Assets:**
  - **Results panel** — monthly table: `plate_apps`, `ba`, `obp`, `slg`, `ops`, `woba`,
    `runs_created`, with partial-month and floor flags.
  - **Approach panel** — monthly table: `swing_rate`, `swing_rate_first_pitch`, `chase_rate`,
    `whiff_rate`, `bbrate`, `krate`, with denominators.
  - **Pitcher-intent panel** — `fpsr` monthly, **visually separated** from the approach panel per
    RC-4, so the Player and Coach personas cannot read it as a hitter behavior.
  - **Contact-quality panel** — `hard_hit_rate`, `barrel_rate`, `ev90`, with BIP counts.
  - **Divergence read** — AP-5 monthly, with the band and its calibration source stated.
  - **AP-4 delta view** — each approach metric as a signed delta from the April anchor.
  - At least one figure: monthly `woba` with `plate_apps` encoded as size, per the requester's
    intent. **Title must match the encoding** — it plots month within a season, not season.
- **System-Facing Assets:** the `z` CSV receipt as a potential input to a future roster-wide
  turnaround diagnostic.

### Experience Expectations

- **Timeliness Expectations:** as-of the latest game in the source snapshot; as-of date visible on
  every surface.
- **Performance Expectations:** none meaningful at this scale.
- **Usability Requirements:**
  - **Discoverability:** artifacts under the standard `data-products/<uc-id>/` layout.
  - **Interpretability:** every displayed column carries a business label from the Semantic Mapping
    table — **including the ten KPIs the requester's `data_dictionary` currently omits**. `month`
    renders as a month name, not an integer. Every rate is adjacent to its denominator (RC-3).
    The pitcher-intent panel is labeled as such (RC-4). The uncontrolled-confound caveat (A-5) and
    the regression null (A-8) appear in the narrative, not only in this specification.

### Delivery Cadence

- **Update Pattern:** Batch, on request; expected monthly while the season is live.
- **Delivery Mechanism:** Pull — artifacts written to the repo.
- **Availability Windows:** N/A.

### Feedback & Adoption Signals

- **Usage Monitoring:** none automated; DPO observation.
- **Consumer Feedback Channels:** direct to DPO.
- **Adoption Indicators:** the diagnostic is re-run in a later month; the AP-1/AP-2/AP-3 functions
  are reused by a second hitter UC — which is also the Round-3 ratification trigger, per the
  precedent set for RF-1 / RF-2.
- **Known Friction Points:** monthly grain is small-sample by construction; the temptation to read
  a monotone series as causal is the central adoption risk.

### Downstream Dependencies

- **Critical Consumer Processes:** none at delivery.
- **Downstream Systems or Use Cases:** a prospective roster-wide in-season turnaround diagnostic
  would inherit AP-1…AP-5 and the anchor-month pattern.
- **Breakage Sensitivity:** low now, rising after ratification — see Backward Compatibility.

### Assumptions & Gaps

- **Assumptions:** monthly grain is the right resolution for the coaching decision (the alternative
  — rolling PA windows per RF-2 from uc-pos-006 — is deliberately not chosen here because the
  requester asked the question in months).
- **Known Gaps:** ten KPIs lack display labels; `month` lacks a formatter; the AP-5 band is
  uncalibrated.
- **Deferred Decisions:** final output format (PDF / HTML / both).

### Out of Scope

- System architecture, pipelines, or exposure mechanisms (see Implementation).
- Data definitions, grain, or KPI logic (see Data Specification).
- Access control policies or enforcement (see Governance).

---

## Process Tracking

### Agent Workflow Status

**Layer Status**

| Layer | Status |
| ----- | ------ |
| Layer 1 — Intake & Discovery | in progress — validator pass complete, awaiting DPO resolution |
| Layer 2 — Design | blocked |
| Layer 3 — Build | pending |
| Layer 4 — Certify & Publish | pending |

**Agent Assignments**

| Agent | Task | Status | Blocker |
| ----- | ---- | ------ | ------- |
| use-case-validator | Stress-test this document | **complete** | — |
| data-product-owner | Resolve 5 open decisions; sequence delivery | **awaiting human DPO** | Open decisions 1–5 |
| source-system-profiler | Fitness-for-purpose on the 16 CDEs against `pos` | pending | Layer 1 gate |
| domain-steward-proxy | Read `discipline()` in the MLB notebook; report on swing-classifier collision | **pending — required to clear a blocking issue** | Notebook is outside this repo |
| business-glossary-agent | Ratify the 5 new terms; detect collision with existing swing terminology | blocked | Open decisions 1, 2 |
| metadata-mapper | Map the 11 unmapped CDEs to physical `pos` columns | pending | source-system-profiler |
| data-architect | `z` model blueprint incl. merge strategy and explicit output naming | blocked | metadata-mapper |
| join-validator | Test the two left-merges for fan-out and suffix collision | pending | data-architect |
| kpi-calculator | Calculation specs for AP-1…AP-5 | blocked | Open decisions 1, 3, 5 |
| dq-rule-definer | Convert the CDE expectations table into rule specs | pending | metadata-mapper |
| technical-lineage-builder | Column-level lineage for all KPIs | blocked | data-architect |
| data-engineer | Build `dp_uc33_stott_approach_change.py` | blocked | Layer 2 |
| data-quality-engineer | Execute rules; DQ scorecard; run verification | blocked | Layer 3 |
| dashboard-specifier | Panel layout enforcing RC-3 and RC-4 | pending | kpi-calculator |
| data-dictionary | Fill the 10 missing display labels + `month` formatter | pending | metadata-mapper |
| privacy-watchdog | Confirm Internal classification | pending | — |
| version-controller | Pre-classify AP-1 numerator and `month` derivation as breaking | pending | Open decisions 1, 4 |
| certification-agent | Assemble the certification package | pending | Layer 3 |
| consumer-onboarding-agent | Persona guides — esp. the Player-facing simplified read | pending | Layer 3 |

**Open Items**

| Issue | Source Agent | Requires Human | Status |
| ----- | ------------ | --------------- | ------ |
| ~~O-1 AP-1 numerator membership undefined~~ | use-case-validator | — | **CLOSED 2026-08-15** — `fpsr` is an existing approved term (`cde.fpsr`); numerator is `(pitches − balls)/pitches`, settled by the shipped `dp_uc17` implementation. Superseded by O-1b. |
| **O-1b** AP-1 is the first **batter-side** use of a pitcher-side approved term — needs a value-stream context annotation on `cde.fpsr` | use-case-validator | Yes — glossary | open |
| **O-2 (restated)** Two conflicting canonical SWINGS lists exist in shipped repo code (8-value with `swinging_pitchout` vs. 7-value without), plus a third in `uc-pos-002`. Pre-existing Principle 1 violation. `swing_rate` must consume a ratified list, not declare a fourth. | use-case-validator | **Yes — DPO** | open |
| **O-2b** `swing_rate` should be an added output of `discipline()`, not a parallel function — otherwise `swing_rate` and `whiff_rate` can contradict within one row of `z` | use-case-validator | **Yes — DPO** | open |
| O-3 AP-4 composite vs. independent | use-case-validator | **Yes — DPO** | open |
| O-4 `month` derivation and March/April merge convention undeclared | use-case-validator | **Yes — DPO** | open |
| O-5 AP-5 divergence band population uncalibrated | use-case-validator | **Yes — DPO** | open |
| O-6 `zfig = z[level+kpis]` drops the three new KPI columns | use-case-validator | No — spec fix | open |
| O-7 Merge suffix behavior is accidental, not specified | use-case-validator | No — spec fix | open |
| O-8 Draft code has syntax errors (merge parens, `suffixes` not a tuple, `px.scatter` parens) | use-case-validator | No — build fix | open |
| O-9 Figure title contradicts its encoding ("by Season" over a month axis) | use-case-validator | No — build fix | open |
| O-10 Ten KPIs have no display label; `month` has no formatter | use-case-validator | No — data-dictionary | open |
| ~~O-11 UC ledger number and `dp_uc` prefix are provisional~~ | use-case-validator | — | **PARTIALLY CLOSED 2026-08-15** — `data-products/` listing confirms `uc-pos-009-schwarber-swing-decay-001` is the highest `pos` slug, so **`uc-pos-010` is correct and free**. The `dp_uc33` build prefix still requires `ls dp_uc*` in the MLB repo. |
| **O-12** A prior UC on this subject player exists (`uc-pos-stott-qab-001`, QAB Rate, Draft) and was not referenced at intake. QAB Rate is a plausible additional results-panel metric, and that UC's open items may bear on this one. | use-case-validator | **Yes — DPO** | open |
| **O-13** Three of six reliability floors (190 pitches, 25 BIP, 40 BIP for EV90) are new to the repo. The PA floor is now correctly inherited at 50. | use-case-validator | **Yes — DPO** | open |

**Certification Recommendation:** pending
<br>**Publish Approved By:** pending

### Validator Log

| Date | Issue | Field / Section | Suggested Assumption | Resolution | Resolved By |
| ---- | ----- | ----------------- | ----------------------- | ---------- | ----------- |
| 2026-08-15 | O-1 … O-11 opened | see Open Items | see accompanying gap report | pending | pending |
