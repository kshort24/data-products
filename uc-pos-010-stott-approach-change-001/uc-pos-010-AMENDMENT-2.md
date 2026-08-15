```yml
# Amendment Identity
amends: uc-pos-010-stott-approach-change-001
amendment: 2
title: AP-8 — pitch-level plate-location drilldown (series / month view)
date: 2026-08-15
status: Draft — pending Use Case Validator pass 2
scope_change: MATERIAL — third grain, first pitch-level artifact, first QAB consumption
```

# UC-POS-010 · Amendment 2

**What changed.** The DPO has drilled one layer further — from game grain (AP-7) to **pitch grain**,
plotting individual pitch locations (`plate_x` × `plate_z`) faceted by game date and platoon, with a
strike-zone overlay and a Quality At-Bat Rate headline. The submitted code is commented out, which
is the right instinct: **it does not currently produce a correct number.**

Two framing notes from the submission carry governance weight:

> *"we could more easily filter to the month of August using that trusted column"*

`month` is the **one attribute this use case has flagged as having no declared derivation** — pass-1
blocking item **B-3**. It is being described as trusted at exactly the moment its definition is
still open. Note also that **August is the partial month**: as of 2026-08-15 a `month == 8` filter
returns roughly half a month, which is fine for a series view and misleading for anything compared
against a complete month.

> *"I drilled down next into a series view"*

That makes three grains in one use case — month (base), game (AP-7), pitch (AP-8). That is a
coherent and well-formed drill path, and it is worth saying so: `month → game_pk → at_bat_number →
pitch_number` is a clean hierarchy with no grain skipping. The problem is not the path. It is that
**PA-level and pitch-level metrics are being computed at the same level.**

---

## 1 · B-11 — The QAB headline cannot produce a correct value at this grain. **BLOCKING.**

```python
level = ['game_date','game_pk','at_bat_number','inning','outs_when_up',
         'p_throws','stand','player_name','pitch_number','pitch_type','pitch_name']

z = nresults(level, df).merge(qab(level, df), on=level, how='left', suffixes=('','_qab'))
...
subtitle = "... Quality At-Bat Rate was {}.".format(round(z.quality_at_bat_rate.unique()[0]*100, 1))
```

`qab_rate.py` states its own contract explicitly:

> *"Denominator = plate appearances (count of distinct `(game_pk, at_bat_number)`).
> Grain = whatever `level` is passed."*

**The declared `level` includes `pitch_number`.** Every group therefore contains exactly one pitch,
which belongs to exactly one at-bat, so the denominator is **1** in every group. QAB Rate collapses
to a **boolean**: `1.0` if that pitch's at-bat was a quality at-bat, `0.0` if not.

`.unique()` on that column returns `[0.0, 1.0]` or `[1.0, 0.0]` — **order determined by whichever
value appears first in the frame**, which is whichever pitch happens to sort first. `[0]` then takes
one of them.

**The subtitle will render either "Quality At-Bat Rate was 0.0." or "was 100.0." — never the actual
rate for the window.** Which of the two appears depends on the first row's outcome and is stable
across runs only because the sort is stable. It is not a rounding problem or a precision problem; it
is a headline number that is structurally incapable of being right.

**Remedy — two grains, one artifact.** This is the same finding as Amendment 1 §3.3 (AP-7), one
level deeper, and it has the same shape of answer:

| Object | Grain | Carries |
|---|---|---|
| **Window summary** | `player_name` × window | QAB Rate, PA count, and every PA-level rate. Computed **once**, at the window level. |
| **Pitch scatter** | `game_pk` × `at_bat_number` × `pitch_number` | Locations, pitch attributes, and the **per-pitch decision**. No rates. |

```python
# window-level headline — computed at the grain the metric is defined for
window_qab = qab_rate(['player_name'], df)          # or (df, level=...) — see B-12
qab_pct = round(window_qab.quality_at_bat_rate.iat[0] * 100, 1)

# pitch-level plot frame — no aggregation, no rates
plot_df = df  # already at pitch grain
```

**Do not use `.unique()[0]` to extract a scalar from an aggregate.** It is a silent failure mode:
it returns a value of the right type and plausible magnitude regardless of whether the aggregation
was correct. `.iat[0]` on a frame you have asserted is single-row fails loudly instead — which is
what you want. Recommend a DQ rule: *any scalar lifted into a title, subtitle, or annotation must
come from a frame asserted to have exactly one row.*

---

## 2 · B-12 — `qab` has three names, an inverted signature, and an unauthorized implementation. **BLOCKING.**

The DPO's code calls `qab(level, df)`. The repo contains:

| Name | Signature | Location | Status |
|---|---|---|---|
| `qab_rate(df, level=('player_name',))` | **`(df, level)` — inverted**, level defaulted | `data-products/uc-pos-stott-qab-001/qab_rate.py` L96 | **⛔ carries a DO-NOT-USE banner** |
| `qab_rate(level, df)` | `(level, df)` — conforming | `uc-pps-022-keller-lhv-2026-001/SR-M1_ratification_packet.md` L138 | in a ratification packet |
| `quality_at_bat_rate` **v3** | — | `Baseball Functions.ipynb` (governed) | the authority `qab_rate.py` mirrors |
| `qab(level, df)` | `(level, df)` | **the DPO's notebook** | fourth name |

**Three problems, in ascending order of seriousness.**

**(a) Signature.** `qab_rate(df, level=...)` is the same inversion Register §5 already ruled against
for `pulled_air` — *"flip to `(level, df)`."* That ruling was scoped to `pulled_air` and evidently
did not sweep. This is the **second** inverted-signature function found in this use case, after
`pulled_air` in Amendment 1 §1.3. **The flip should be applied as a repo-wide rule, not per
function.**

**(b) Naming.** `qab` / `qab_rate` / `quality_at_bat_rate` is the same three-name pattern as
`pull_air_rate` / `pulled_air` / `pulled_air_rate`. That is now twice in one use case, which makes
it a **pattern rather than an incident**: short aliases get invented at the notebook prompt and
never reconcile with the governed name.

**(c) Authorization — the serious one.** `qab_rate.py` opens with:

> ```
> ⛔ DRAFT — NOT AUTHORIZED — pending human DPO sign-off
> This Layer-3 (Build) pipeline was produced PREMATURELY, in breach of the hard Layer-1 stop.
> It has NOT been authorized. Do not run, import, or rely on it.
> Retained (not deleted) only for human DPO review or disposal.
> ```

If the notebook's `qab` resolves to that module, **an explicitly unauthorized artifact is producing
a headline number in a delivered visual.** If it resolves to the governed `quality_at_bat_rate` v3
in Baseball Functions, there is no breach — but *the code as written does not say which*, and that
ambiguity is itself the finding. **Establish which implementation `qab` binds to before it is run
again.**

**(d) And the underlying KPI is unreconciled.** `uc-pos-stott-qab-001`'s **OI-1** is open:

> *"the funnel's own arithmetic does not close — its three named components sum to 810 but it states
> 1500 Quality At-Bats. Until the human confirms the QAB component set, the headline number cannot
> be validated or reproduced."*

So the metric being promoted into a subtitle is, at present: **Draft status, unreconciled headline,
unauthorized implementation, non-conforming signature, fourth alias.** Every one of those is
individually clearable and none is fatal — but QAB should not appear in a delivered artifact until
at least OI-1 and (c) are closed.

> **Credit where due:** reaching for QAB here is the right instinct and closes pass-1 item **N-15**,
> which flagged that the prior Stott UC had been missed at intake. QAB is the aptest available
> single answer to *"did the at-bats get better."* The problem is entirely its readiness, not its
> relevance.

---

## 3 · B-13 — Three strike zones now exist in the repo. **BLOCKING (display consistency).**

```python
fig.add_shape(type='rect', x0=-0.83, x1=0.83, y0=df.sz_bot.mean(), y1=df.sz_top.mean(),
              row='all', col='all')
```

| Artifact | Half-width | Vertical bounds |
|---|---|---|
| **This submission** | **0.83 ft** | `df.sz_bot.mean()` / `df.sz_top.mean()` — **window mean** |
| `uc-pos-005` (Harper OZ) | **0.83 ft** (`HALF_X`, Statcast plate convention) | **per-pitch** `sz_top` / `sz_bot` |
| `dp_uc7` L103, L533 | **`17.0/12.0/2.0 = 0.708 ft`** — physical plate half-width | **fixed** 1.5 / 3.4 |

**Two distinct conflicts, and the Intake Register caught neither.**

Register v2 §4.1 states: *"`PLATE_HALF = HALF_X = 0.83 ft` was already common to both and is
unaffected."* That comparison covered Harper and the UC8 trio. **It did not cover `dp_uc7`, which
uses 0.708.** The difference is real and physical: 0.83 ft is the Statcast convention (plate
half-width **plus** a ball radius); 0.708 ft is the bare plate. A pitch at `plate_x = 0.75` is
**inside** the zone in one rendering and **outside** it in the other.

Separately, the vertical bounds have three conventions — per-pitch, window-mean, and hard-coded.

**Why this is blocking for AP-8 specifically.** AP-8's entire purpose is to let a coach look at
*where pitches were relative to the zone* and judge whether Stott's takes were disciplined. **The
zone is not decoration here — it is the measuring instrument.** A rendering whose boundary disagrees
with `uc-pos-005`'s by 1.5 inches will disagree with the OZ shadow-band analysis about which pitches
were takeable, and the two artifacts will be read side by side by the same Hitting Coach.

**Recommendation:** ratify **`HALF_X = 0.83`** (majority convention, matches Statcast, matches the
Register's own §4.1 language) and **per-pitch `sz_top`/`sz_bot`** (matches `uc-pos-005`, and the
strike zone genuinely is per-pitch). Retire `dp_uc7`'s 0.708 and its fixed 1.5/3.4.

**Caveat on the mean.** With `row='all', col='all'` a single averaged rectangle is drawn on every
facet — including across the `p_throws` facet rows. For a single batter the vertical variation is
modest, so the approximation is defensible **as a display**, but it must be **labeled an
approximation** and must never be the geometry any *metric* is computed from. Per-pitch is cheap
here; prefer it.

> **Note:** this rectangle is the **rulebook zone**, not the OZ shadow band. It correctly omits
> `BALL_FT = 2.94/12`. Label it so, or a reader familiar with `uc-pos-005` will assume shadow
> geometry and misread every edge pitch.

---

## 4 · Non-blocking findings

| # | Finding | Recommendation |
|---|---|---|
| **N-25** | **Self-referential filter bug.** `df = po26[(po26.player_name == 'Stott, Bryson') & (df.month == 8)]` masks `po26` using **`df`** — the previous, differently-indexed frame. Raises on length mismatch, or silently misaligns if lengths happen to match. | `po26.month == 8`. Also decide `po26` vs `pos` as the source of record for this UC — both appear; only one should. |
| **N-26** | **The approach study does not encode the approach.** Marks encode `pitch_group` (color), `pitch_type` (text), `release_speed` (size) — three encodings of *what was thrown*, **none of what Stott did about it.** For a use case whose question is "did he change his approach," the most informative channel is unused. | Add `symbol` = take / swing-miss / swing-foul / in-play, derived from the ratified `description` classifier (B-1). One channel, and the plot answers H1 vs. H2 from Amendment 1 §3.1 visually. |
| **N-27** | **Redundant and misleading encodings.** `pitch_type` (text) and `pitch_group` (color) are the same hierarchy twice. `size='release_speed'` maps a ~70–100 mph range onto marker area, producing visible size differences that read as importance rather than velocity — on a plot where **position is the meaningful channel**. | Drop `text='pitch_type'` (redundant with color); free `size` for something with a meaningful zero, or drop it entirely. Reserve `text` for the small number of pitches worth annotating. |
| **N-28** ✅ | **`pitch_group` is conforming reuse.** The canonical `PITCH_GROUP` map (`dp_uc18_marsh_breakout.py`: FF/SI/FC→fastball, SL/ST/CU/KC/SV/CS→breaking, CH/FS/FO/SC/KN→offspeed, else→other) is already reused across `uc-pos-004`, `uc-pos-005`, and `uc-cat-001`. | No action — cite the map as the source. Follow `uc-pos-005`'s convention of excluding `other` from group receipts, or state why not. |
| **N-29** ✅ | **`facet_row='p_throws'` partially closes N-13.** Pass 1 flagged that A-5's platoon-confound caveat *"cannot be evidenced or inspected from the delivered dataset."* Faceting by pitcher handedness makes it directly visible. | **Scope change to record**: `p_throws` was declared *optional grain, out of scope* in the base spec. It is now in a delivered artifact. Move it from Out of Scope to declared grain for AP-8. |
| **N-30** | **Hard-coded narrative in the subtitle.** *"In the St. Louis mess, he managed to put together good ABs"* is not derivable from the pitch log. | Apply the `uc-pos-006` manual-carry-in disclosure pattern: *"Manual carry-ins (not derivable from the pitch log): …"*. Also parameterize — a subtitle naming one specific series will be wrong on the next re-run. |
| **N-31** | **Date filter fragility.** `from_date`/`to_date` are strings compared against `game_date`. Works for ISO strings and for datetimes via coercion; fails silently on mixed dtypes. | Coerce explicitly. And prefer the date-range form over `month == 8` for a **series** view — a series is a date range, not a calendar month. The two are being offered as interchangeable and are not. |
| **N-32** | **Unlabeled columns, again.** `at_bat_number`, `inning`, `outs_when_up`, `p_throws`, `sz_bot`, `sz_top`, `release_spin_rate`, `pfx_x`, `pfx_z` have no `data_dictionary` entries. The `data_dictionary \| {...}` union pattern is good — the dictionary is just incomplete. | Extend the base dictionary once, centrally, rather than per-figure. This is the third amendment to raise missing labels (pass-1 N-10, here). |
| **N-33** | **`kpis` declared but unused.** `kpis = ['release_speed','release_spin_rate','pfx_x','pfx_z']` is defined and never referenced — the figure plots `plate_x`/`plate_z`. | Either drop it or state its purpose. A declared-and-unused KPI list in a governed spec reads as an omission rather than a leftover. |
| **N-34** | **Pin the player ID.** `qab_rate.py` records `STOTT_MLBAM_ID = 681082`, *"pinned (resolves the fuzzy `player_name` mapping)."* This UC filters on `player_name` string equality throughout. | Adopt the pinned ID as the subject filter, consistent with the repo's practice for other subjects. Add `681082` to the base spec's Identity block. |

---

## 5 · AP-8 spec

| Field | Value |
|---|---|
| **KPI ID** | AP-8 — Pitch-Location Approach View |
| **Status** | **NEW — presentation artifact, not a KPI.** Computes no rate; it displays located events. |
| **Declared grain** | `game_pk` × `at_bat_number` × `pitch_number` (the pitch key, per `qab_rate.py`'s `PITCH_KEY`) |
| **Facets** | `game_date` (col, wrap 3) × `p_throws` (row) |
| **Encodings** | position = `plate_x`/`plate_z`; color = `pitch_group` (canonical map); **symbol = swing/take decision (N-26, required)** |
| **Overlay** | Rulebook zone — `HALF_X = 0.83`, per-pitch `sz_bot`/`sz_top`. **Labeled rulebook, not shadow band.** |
| **Companion object** | Window-level summary row carrying QAB Rate and PA count, computed at window grain (B-11) |
| **Floors** | **None apply** — this is an event display, not a rate. Its honesty comes from showing every pitch, so **no filtering to "interesting" pitches.** |
| **Population rule** | Location metrics require the **tracked** population. Per `uc-pps-024`: *"usage/zone/location metrics → tracked pop; PA outcomes → full pop; contact metrics → BIP."* Pitches with null `plate_x`/`plate_z` are **excluded and counted** — `uc-pos-005` excluded 10 such rows and disclosed it. Do the same. |

---

## 6 · Amended totals

**Blocking: 12** — B-1, B-2, B-3, B-5, B-6 (pass 1) · B-7, B-8, B-9, B-10 (Amendment 1) ·
**B-11, B-12, B-13 (new)**. B-4 closed.
**Non-blocking: 34.**

### The pattern worth ruling on once

Four separate findings across two amendments are the same defect class:

| | Governed name | Aliases found | Signature |
|---|---|---|---|
| First-pitch strike | `fpsr` | — | conforming |
| Pulled air | `pulled_air` | `pull_air_rate`, `pulled_air_rate` | **inverted `(df, level)`** |
| Quality at-bat | `quality_at_bat_rate` | `qab`, `qab_rate` | **inverted `(df, level)`** |
| Pitches per PA | `ppa` | — | conforming |

Two rulings close all of it and prevent the next instance:

1. **Signature: `(level, df)` is repo-wide and non-optional.** Register §5 ruled this for
   `pulled_air` alone; the ruling did not sweep, and `qab_rate` proves it. Make it a lint rule.
2. **Notebook aliases are not names.** A short alias at the prompt is fine for exploration and must
   be reconciled to the governed name before any spec, receipt, or figure references it.

Together with the mandatory repo-search step recommended in pass 1, these are the three process
changes this engagement has actually earned — and they will do more for the organization than any
individual KPI ruling in the queue.
