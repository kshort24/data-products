```yml
# Amendment Identity
amends: uc-pos-010-stott-approach-change-001
amendment: 1
title: Rolling wOBA hero visual + At-Bat Approach game-grain drilldown
date: 2026-08-15
status: Draft — pending Use Case Validator pass 2
author: Data Product Owner (Kellen Short), via working-notebook submission
scope_change: MATERIAL — adds two deliverables, one new grain, six function specs
```

# UC-POS-010 · Amendment 1

**What changed.** The original submission asked for a monthly results-and-approach panel. The DPO
has since supplied working notebook code and two further asks that extend the use case
substantially:

1. **AP-6 — replace the discrete monthly wOBA facet grid with a rolling wOBA line**, plotted
   against **cumulative plate appearance**, prior seasons rendered as greyed context and 2026 in
   the primary color.
2. **AP-7 — an at-bat-approach drilldown at game grain**, targeting a specific 11-game stretch
   (14 BB, 0 K), with `facet_col` moving from `game_year` to `game_date` / `game_pk`.

The working code also reveals **six functions** not present in the original spec, three of which
already exist in the repo under other names or signatures.

> **This amendment does not restate the original document.** Sections not mentioned here are
> unchanged. The five open DPO decisions and six blocking items from validator pass 1 remain live
> except where explicitly closed below.

---

## 1 · Findings from the working code

### 1.1 Closed by evidence

| Pass-1 item | Status | Evidence |
|---|---|---|
| **B-4** — `swing_rate` may declare a swing classifier parallel to `discipline()` | **CLOSED** | The DPO's implementation takes `swings` **directly from `whiff_rate(level, df)`** and `pitches` from `nresults(level, df)`. It declares no classifier of its own. Reconciliation between `swing_rate` and `whiff_rate` is therefore guaranteed **by construction**, not by assertion — which is the structural remedy pass 1 recommended, already implemented. |
| **B-1** — narrowed | **NARROWED, not closed** | Because `swing_rate` inherits `whiff_rate`'s swing list, this UC introduces **no new fork**. But it does mean the repo's three-way SWINGS drift now silently determines `swing_rate` as well as `chase_rate` and `whiff_rate`. The ratification is still owed; the blast radius just grew by one metric. |

### 1.2 The DPO's `swing_rate` — and the root cause of the suffix problem

Two definitions appear in the submitted notebook:

```python
# Variant A — returns the projection
def swing_rate(level, df):
    data = nresults(level, df).merge(whiff_rate(level, df), on=level, how='left', suffixes=('','_wr'))
    data['swing_rate'] = data.swings / data.pitches
    return data[level + ['swing_rate']].round(3)      # ← narrow return

# Variant B — returns everything
def swing_rate(level, df):
    z = nresults(level, df).merge(whiff_rate(level, df), on=level, how='left', suffixes=('','_wr'))
    z['swing_rate'] = z.swings / z.pitches
    return z                                           # ← wide return
```

**Variant B is the cause of the merge-suffix mess in the original submission.** Merging a wide
return into `z` re-imports every `nresults` column — `pitches`, `plate_apps`, `swings`, `woba`, and
the rest — forcing suffix disambiguation on ten-plus columns that were never wanted. Variant A
merges cleanly because it returns only the key and the metric.

**Recommendation:** ratify **Variant A** as the contract. Amend it only to ship the denominators
alongside, which RC-3 requires:

```python
return data[level + ['swings', 'pitches', 'swing_rate']].round(3)
```

**Do not round inside a function whose output feeds further arithmetic.** `.round(3)` inside
`swing_rate` means AP-6's cumulative series and any AP-4 delta inherit a rounded input. Rounding
belongs in `zfig`, the presentation projection — never in `z`, the curated dataset. *(The original
spec already states this rule for `zfig`; the function-level `.round(3)` contradicts it.)*

### 1.3 Three functions the repo already has

| DPO code | Repo reality | Action |
|---|---|---|
| `def ppa(level, df)` | **Already exists** — `dp_uc24` L191 and `dp_uc31` L244, identical `(level, df)` signature. Intake Register **B7, disposition A — ready for sign-off.** | **Do not redefine.** Import. Second duplication of an existing function in this UC, after `fpsr`. |
| `pull_air_rate(level, df)` | **Third name for one concept.** `pulled_air(df, level)` ships in `dp_uc24` L154, `dp_uc31` L208, and `marsh_breakout_analysis.py` L151 — with the **inverted** signature that Register §5 already **ruled must be flipped** to `(level, df)`. A `pulled_air_rate` also exists in the notebook and is Register §5's still-open comparison item. | **Blocking.** Pick one name and one signature. `pull_air_rate` vs `pulled_air` vs `pulled_air_rate` is Principle 1 with three claimants. The §5 flip ruling should land here rather than being deferred again. |
| `fpsr(level, df)` | Already covered in the amended spec — approved term, `dp_uc17` L211. | Import. |

### 1.4 `foul_ball_rate` is built on an open, undocumented data quirk

```python
def foul_ball_rate(level, df):
    fbs  = df[(df.launch_speed.isna() == False) & (df.type != 'X')]   # "fouls"
    bips = df[df.type == 'X']                                          # denominator
    ...
    data['foul_ball_rate'] = data.foul_balls / data.balls_in_play
```

**Three separate defects, one of them a direct hit on an open governance item.**

1. **The numerator is not "foul balls."** It is *non-in-play pitches that happen to carry a tracked
   exit velocity.* That population exists only because of Intake Register **O3** — the open finding
   from `uc-pps-024` (Kilian) that *"`launch_speed` is populated on foul balls, not only balls in
   play; 114 of 736 rows in the 2026 tier."* O3 is documented as a **trap to filter out**
   (`05_quality_certification.md`: an EV mean read 80.8 mph instead of 86.8 because of it). This
   function instead uses the trap as a **definition**. It will therefore count only *tracked* fouls,
   silently excluding untracked ones, and its coverage will drift with tracking quality rather than
   with Stott's approach.

2. **The denominator is the wrong population.** Fouls are pitch events; balls in play are a
   different population. `fouls / balls_in_play` is not bounded by 1 and is not a rate in any
   ordinary sense. `uc-pps-024`'s own consumer guidance states the governing rule:
   *"Population must match metric class — usage/zone/location metrics → tracked pop; PA outcomes →
   full pop; contact metrics → BIP. Mixing produces the O2/O3 defect class."* This mixes.

3. **It contradicts the business claim it exists to support.** The DPO's narrative is *"his foul
   ball rate was trending above average"* — a statement about **how often he fouls pitches off**,
   which is a per-pitch or per-swing rate. Neither is what this computes.

**Recommendation — define it against the population the claim implies:**

```
foul_ball_rate = fouls / swings          # "when he offers, how often does he stay alive"
        or       fouls / pitches         # "how often does a pitch to him end in a foul"
```
where `fouls` is derived from the ratified **`description`** classifier (`foul`, `foul_tip`,
`foul_bunt`), **never** from `launch_speed` non-nullity. Which denominator is a DPO call —
`fouls / swings` is the better read of *battling*, and pairs directly with `whiff_rate` since both
condition on a swing.

### 1.5 `line_drive_rate`

Genuinely new — no repo definition found. Logic is sound: `bb_type == 'line_drive'` over
`type == 'X'`, correctly BIP-denominated. Two notes:

- The `how='right'` merge is deliberate and correct — it retains BIP groups with zero line drives.
  But those rows emit **NaN, not 0**, and the distinction matters (see 1.6).
- Register B2's `batted_ball(level, df)` (disposition **A**) already emits GB/FB/LD/PU rates.
  **Check whether `line_drive_rate` is already a column there** before ratifying a second function.
  Same search discipline that caught `fpsr` and `ppa`.

### 1.6 `.fillna(0)` on `z` violates the sensor-boundary NULL standard

```python
z = nresults(level, df).merge(...).merge(...).fillna(0)
```

`uc-pos-009` (Schwarber swing decay) established the standard: **never impute a missing measurement
as zero.** `.fillna(0)` applied to the whole frame erases the distinction between two very different
facts:

| Situation | Correct value | What `.fillna(0)` produces |
|---|---|---|
| Stott had batted balls, none were barrels | `barrel_rate = 0.0` ✅ | `0.0` ✅ |
| Stott had **no tracked batted balls** that month | `barrel_rate = NULL` | **`0.0`** ❌ |
| A month has no first pitches in the filtered frame | `srfp = NULL` | **`0.0`** ❌ |

The second and third rows manufacture a *measured zero* out of an *absence of measurement* — and a
zero barrel rate is a coaching signal while a null is a sample warning. On a monthly grain with a
partial August, this is a live risk, not a hypothetical.

**Recommendation:** remove the blanket `.fillna(0)`. Fill only count columns that are genuinely
zero-valid (`swings`, `barrels`, `line_drives`), explicitly and by name. Leave every **rate** NULL
when its denominator is absent. This is the same rule the original spec already states for
`swing_rate`'s left-merge behaviour — the `.fillna(0)` silently overrides it.

### 1.7 Two mechanical defects in the KPI projection

- `kpis` contains **`'First Pitch Strike Rate'`** — a *display label*, not a column. `z[level+kpis]`
  raises `KeyError`. The `fpsr()` function returns **`first_pitch_strike_rate`**. Use the column
  name in `kpis`; keep the label in `data_dictionary`.
- `suffixes=('','sr')` on the `swing_rate` merge is **missing the underscore**, yielding `swingssr`
  / `pitchessr`. Every neighbouring merge uses `'_xx'`. Cosmetic until something reads the column by
  name, then not cosmetic.

---

## 2 · AP-6 — Rolling wOBA by cumulative plate appearance

### 2.1 Business intent

Replace the discrete monthly wOBA points with a **continuous within-season trajectory**. Monthly
buckets impose an arbitrary boundary on a process that has none: a hitter who turned a corner on
May 20 shows up as "a good May and a better June," which is an artifact of the calendar rather than
a finding. A rolling line indexed by cumulative PA shows **where the turn actually happened**, and
whether it was a turn or a drift.

This directly serves **BQ-2** — *is the improvement monotonic, or an endpoint artifact?* — which
validator pass 1 flagged (N-5) as a business question with **no KPI able to answer it**. AP-6
answers it. **N-5 is closed by this amendment.**

### 2.2 This is RF-1, with one grain change

`running_line(df)` already exists — `dp_uc24_turner_2026_review.py` L215:

> *"Cumulative OBP/SLG/OPS and wOBA-to-date by game index, per season. RF-1 hero data. One row per
> (season, game_date)."*

It is Intake Register **B12, disposition C** — *hold, promote after one more hitter reuse.*
**This UC is that reuse.** But it is not a clean one:

| | RF-1 as shipped | AP-6 as requested |
|---|---|---|
| x-axis | `game_date` (one row per game) | **cumulative plate appearance** |
| Output grain | (season, game_date) | (season, cumulative_pa) |
| Signature | `running_line(df)` — **no `level` argument** | should be `(level, df)` |

**Two governance consequences:**

1. **A cumulative-PA index is the better x-axis and should be argued for, not assumed.** Games are
   not equal units — a 5-PA doubleheader game and a 1-PA pinch-hit appearance both advance
   `game_date` by one step. Cumulative PA makes the x-axis proportional to opportunity, which is
   what a rate-stat trajectory needs. It also makes seasons directly comparable at equal PA, which
   is exactly what the greyed prior-year context is for.

2. **`running_line(df)` is a no-grain function** — Register §5's open *"review the no-grain
   functions at ratification"* item. Changing its index is the natural moment to bring it onto the
   `(level, df)` contract. **Do not fork it.** Either extend `running_line` with a
   `index_by='pa'|'game'` parameter, or promote a single `running_line(level, df, index_by=...)`.
   A second cumulative-wOBA function would be the third duplication in one use case.

**Reuse the wOBA-numerator logic verbatim.** RF-1 already implements the per-row seasonal weight
map (`wBB`/`wHBP`/`w1B`/`w2B`/`w3B`/`wHR`), the regular-season filter (`game_type == 'R'`), and the
PA definition (excludes `NA` and `pickoff_1b` events). That PA definition should be **lifted as the
canonical one** for this UC rather than re-derived — it is the same `plate_appearance_key` the CDE
table describes.

### 2.3 Visual grammar — inherited, not invented

The requested treatment (prior seasons greyed, current season in primary color) is the **ghost-line
pattern already established** by `marsh_xbh_animated.py`: *prior seasons render as distinct
self-referential ghost lines, with a two-phase reveal and a `roster_support` guard so mid-season
acquisitions do not fabricate pre-acquisition zero games.*

| Marsh precedent | AP-6 application |
|---|---|
| Ghost lines for prior seasons, primary for current | ✅ direct reuse |
| Self-referential comparison (player vs. own history) | ✅ direct reuse — and it is also the AP-5 band recommendation |
| `roster_support` guard for partial seasons | **Applies.** Stott's rookie/partial seasons must not render as a full-length line. A season with fewer PA ends its line where its data ends — it does not extend flat to the right. |

**Layout.** The requested arrangement — four prior seasons across the top row, 2026 alone on the
bottom — is `facet_col='game_year', facet_col_wrap=4`. Note that with five seasons this yields 4+1
naturally. **If Stott has a sixth season in `pos`, the layout silently becomes 4+2 and the "current
year gets its own row" property is lost.** Pin 2026 to its own row explicitly rather than relying on
the wrap arithmetic.

**Open question for the DPO:** on a single-axis overlay (all seasons on one panel, which the
cumulative-PA index now makes meaningful), the ghost/primary treatment reads more directly than a
facet grid — the whole point of a common PA index is that the lines are comparable *on top of each
other*. Faceting separates what the index was chosen to bring together. Recommend **both**: overlay
as the hero, facet grid as the appendix.

### 2.4 AP-6 spec

| Field | Value |
|---|---|
| **KPI ID** | AP-6 — Rolling wOBA Trajectory |
| **Status** | **INHERITED-VARIANT** — RF-1 `running_line`, re-indexed. Not a new function. |
| **Input grain** | PA (pitch log, terminal PA rows only) |
| **Output grain** | `player_name` × `game_year` × `cumulative_pa` |
| **Required CDEs** | `pa_result_event`, `season_year`, `game_date`, `plate_appearance_key`, `woba_scale_constants` |
| **Null handling** | Line terminates at each season's final PA. **No forward-fill, no extension to a common right edge.** |
| **Floor** | The **left tail is unstable by construction** — cumulative wOBA at PA 5 is meaningless. Suppress or visually de-emphasize the first **50 PA** of every line, consistent with the inherited 50-PA floor. This is the floor's most visible application in the whole UC. |
| **Dependency** | `wOBA and FIP Constants.csv` (Register §5 open loader item) — same dependency as `runs_created`. |

> **The left-tail rule is not cosmetic.** An unsuppressed rolling line starts at wOBA 0.000 or
> 4.000 depending on whether PA 1 was an out or a home run, and then converges. A reader's eye is
> drawn to the dramatic early swing, which is pure sampling. Every season's line will show it, in
> the greyed context lines too.

---

## 3 · AP-7 — At-Bat Approach drilldown (game grain)

### 3.1 Business intent, stated as a falsifiable hypothesis

The DPO's framing is unusually precise and should be preserved verbatim in the spec, because it is
already a testable proposition:

> *"He chased, but he did not whiff. Or did he just not chase anymore?"*

That is a **two-branch hypothesis with a discriminating measurement**, which is rare enough at
intake to be worth naming as a strength:

| Branch | `chase_rate` | `whiff_rate` on chases | Reading |
|---|---|---|---|
| **H1 — better contact on the same aggression** | flat | ↓ | He still expands, but he fouls them off / puts them in play. *Skill/timing change.* |
| **H2 — genuine discipline gain** | ↓ | flat | He stopped offering at balls. *Decision change.* |
| **H3 — both** | ↓ | ↓ | Approach and execution moved together. |
| **H4 — neither** | flat | flat | The walks came from pitchers missing, not from Stott changing. **This is the null, and it must be reachable.** |

**H4 is the branch the data product exists to be able to reach.** It is also where `fpsr` (AP-1)
does its work: if first-pitch strike rate *fell* during the stretch, pitchers changed, not Stott.
The narrative claim *"He takes the first pitch all the time"* is measured by `srfp` (AP-3), and the
two together separate his intent from their execution.

### 3.2 The window-selection problem — **BLOCKING**

> The requested population is *"the 11 game stretch where he walked 14 times without striking out
> once."*

**The window is defined by its own outcome.** Selecting a stretch *because* it contains 14 walks and
zero strikeouts, then reporting walk rate and strikeout rate over that stretch, is circular: those
two numbers are guaranteed to be extraordinary because they are the selection criterion. Any
supporting metric correlated with them — chase rate, first-pitch take rate, pitches per PA —
inherits the same bias to an unknown degree.

This is a sharper instance of the anchor problem flagged as N-7 in pass 1 (April was chosen because
it was extreme). There, one endpoint was outcome-selected. Here, **the entire analysis population
is.**

**This does not make the stretch uninteresting — it makes it un-generalizable without a control.**
Three remedies, any of which clears the block; the DPO picks:

| Remedy | What it gives you |
|---|---|
| **A — Pre-declare the window by date, not by outcome.** "The last 15 games" or "since the All-Star break." | Cleanest. The 14-BB/0-K fact then becomes a *finding within* the window rather than its definition. **Recommended.** |
| **B — Keep the outcome-selected window, but report BB% and K% as `descriptive — selection-defined, not inferential`** and draw conclusions only from metrics *not* used in the selection (chase, foul, whiff, `srfp`, `ppa`). | Honest and preserves the DPO's actual interest. Requires discipline in the narrative. |
| **C — Ship both windows side by side** — the outcome-selected 11 games and a date-defined comparator of similar length. | Most informative; the gap between them *is* the selection-bias magnitude, measured rather than argued. |

**Whichever is chosen must be recorded**, because the delivered artifact will otherwise read as
"here is what Stott does now" when it actually says "here is what Stott did during a stretch we
picked because it was his best."

### 3.3 Grain change and its consequences

`facet_col` moving to `game_date` / `game_pk` is **a change of declared grain**, not a display
choice. Governance consequences:

| Consequence | Detail |
|---|---|
| **New grain** | `player_name` × `game_year` × `game_date` × `game_pk`. `game_pk` is the reliable key (doubleheaders share a `game_date`); `game_date` is the display attribute. **Ship both — they are not interchangeable.** |
| **Every floor is breached** | An 11-game stretch is roughly **40–50 PA total** — i.e. the *whole window* sits at about one monthly bucket's worth, and a *single game* is 3–5 PA. Per-game rate stats are not interpretable. |
| **Therefore: no per-game rates** | At game grain, report **counts and events**, not rates. `bbrate` and `krate` over 4 PA are noise with a decimal point. The rates belong at the **stretch level** (one row for all 11 games), with the per-game panel showing the *sequence of events* that composes them. |
| **Two grains, one artifact** | The drilldown is legitimately two objects: a **stretch-level rate row** (above floor if 40+ PA, flagged if not) and a **game-level event sequence** (counts, no rates). Specifying it as one grain forces one of the two to be wrong. |

### 3.4 AP-7 component KPIs

| KPI | Status | Note |
|---|---|---|
| `line_drive_rate` | **NEW-CANDIDATE** | Check against Register B2 `batted_ball()` first (§1.5). |
| `foul_ball_rate` | **NEW — SPEC REJECTED AS WRITTEN** | Rebuild on `description`, not `launch_speed`. See §1.4. |
| `ppa` (pitches per PA) | **INHERITED — do not redefine** | Register B7, disposition A. `dp_uc24` L191. |
| `pull_air_rate` | **BLOCKED — three competing names** | See §1.3. |
| `chase_rate`, `whiff_rate` | INHERITED | Discriminators for H1–H4. |
| `swing_rate`, `srfp` | NEW-CANDIDATE (from base spec) | `srfp` measures *"he takes the first pitch all the time."* |
| `fpsr` | INHERITED-APPROVED | Measures whether **pitchers** changed. The H4 test. |

**Missing from the DPO's list and needed for H1 vs. H2:** whiff rate *conditioned on out-of-zone
swings* — "did he make contact on the pitches he chased." `chase_rate` and `whiff_rate` as currently
defined are computed over different populations (out-of-zone pitches; all swings), so neither alone
distinguishes H1 from H2. `uc-cat-001` already implements the pattern —
`count(is_ooz AND is_swing AND is_whiff) / count(is_ooz AND is_swing)` — with the explicit note that
*"both sides of the fraction use the same zone filter — this was a blocking issue in the original
intake."* **Inherit that correction rather than rediscovering it.**

---

## 4 · Amended open items

| ID | Item | Requires | Status |
|---|---|---|---|
| ~~B-4~~ | `swing_rate` classifier collision | — | **CLOSED** — inherits `whiff_rate`'s swings by construction |
| ~~N-5~~ | BQ-2 has no trend-shape KPI | — | **CLOSED** — AP-6 answers it |
| **B-7** | Window selection for AP-7 is defined by its own outcome | **DPO** | **NEW — BLOCKING** |
| **B-8** | `pull_air_rate` / `pulled_air` / `pulled_air_rate` — three names, two signatures, one concept; Register §5 flip ruling still unapplied | **DPO** | **NEW — BLOCKING** |
| **B-9** | `foul_ball_rate` numerator is built on open item O3 (`launch_speed` populated on fouls) and its denominator is the wrong population | **DPO** | **NEW — BLOCKING** |
| **B-10** | `.fillna(0)` on `z` violates the uc-pos-009 sensor-boundary NULL standard | Spec/build fix | **NEW — BLOCKING** |
| **N-16** | `ppa` redefined though it exists (Register B7, disposition A) | Import, don't rebuild | new |
| **N-17** | AP-6 re-indexes RF-1 from `game_date` to cumulative PA — extend, do not fork; bring onto `(level, df)` | DPO | new |
| **N-18** | `'First Pitch Strike Rate'` (a label) is in `kpis`; will `KeyError`. Column is `first_pitch_strike_rate` | Build fix | new |
| **N-19** | `suffixes=('','sr')` missing underscore | Build fix | new |
| **N-20** | `swing_rate` Variant B (wide return) causes the suffix cascade; ratify Variant A + denominators, and drop the in-function `.round(3)` | DPO | new |
| **N-21** | AP-7 needs two grains (stretch-level rates, game-level counts); one grain forces one to be wrong | DPO | new |
| **N-22** | AP-6 left tail unstable below 50 PA — suppress or de-emphasize | Build | new |
| **N-23** | Out-of-zone-conditioned whiff rate is missing and is required to separate H1 from H2; inherit the `uc-cat-001` same-filter-both-sides correction | DPO | new |
| **N-24** | AP-6 facet 4+1 layout breaks silently if a sixth season exists; pin 2026 to its own row | Build | new |

**Running total: 9 blocking** (B-1, B-2, B-3, B-5, B-6 carried; B-7…B-10 new — B-4 closed),
**24 non-blocking.**

> **The direction of travel is worth noting.** Every new blocking item in this amendment came from
> the *working code*, not from the prose — and three of the four are duplications or population
> mismatches that a repo search would have caught before a line was written. That is now twice in
> one use case. The mandatory-search step recommended in pass 1 should be treated as the primary
> finding of this engagement, ahead of any individual metric ruling.
