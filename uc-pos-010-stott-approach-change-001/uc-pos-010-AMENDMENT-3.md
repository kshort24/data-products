```yml
amends: uc-pos-010-stott-approach-change-001
amendment: 3
title: AP-9 Plate-Discipline Ratio family + AP-10 Walks-Between-Strikeouts streak
date: 2026-08-15
status: Draft — pending Use Case Validator pass 2
artifact: discipline_ratio.py (Layer-3 DRAFT, carries the NOT-AUTHORIZED banner)
```

# UC-POS-010 · Amendment 3

---

## 0 · I could not run it

> *"So let's run that for context and see how Bryson Stott is currently standing up?"*

**The MLB repo is not reachable from this session.** Only `Agents for Data Products` is mounted;
`Python Scripts\MLB` — where `pos`, the parquet layer, and the Baseball Functions notebook live —
is outside it. This is the same limitation recorded in Intake Register §0, and it is why
`dp_uc17_verification.py` and `dp_uc18_verification.py` were written here but had to be executed
locally.

So **the 3:2 claim is unverified.** It is currently an assertion in a video title's supporting
narrative, and it needs to be computed before it is published. §5 gives you a paste-ready snippet
that produces it and the surrounding percentile in one cell.

Everything below is grounded in repo artifacts I *could* read — the governed event sets, the PA
definition, the streak precedent — not in the data.

---

## 1 · The title and the KPI measure different things

> **Video title:** *"Bryson Stott drawing 14 walks between strikeouts"*
> **Proposed KPI:** `bb:k` = `bbrate / krate`

These are not the same statistic, and the gap between them is the most important thing in this
amendment.

| | `bb_per_k` (AP-9) | `walks_between_ks` (AP-10) |
|---|---|---|
| Kind | **Rate ratio** over an unordered window | **Run length** over an ordered PA sequence |
| Needs sort order | No | **Yes — and it fails silently without one** |
| What it says | "For every punchout, he draws N walks" | "He went N walks without a punchout" |
| The title's claim | ✗ | **✓** |

They can disagree in both directions. A hitter with a 2.0 BB/K whose walks and strikeouts perfectly
interleave has a longest run of **1**. A hitter with a mediocre BB/K can still own one long K-free
stretch. **Neither is a proxy for the other.**

The title is making the *streak* claim. If the supporting visual shows the *ratio*, the video shows
a number that does not substantiate its own headline. Ship both — the ratio is the context ("this
is who he is"), the streak is the event ("this is what just happened"). That is in fact the exact
structure of the stated intent: *"offer deeper context for the performance during this stretch."*

> **AP-10 carries a precedent problem the DPO should rule on rather than inherit.**
> `scoreless_streak(df)` (SL-1, `dp_uc21` L323) is Intake Register disposition **D — do not
> promote**, recorded as *"receipt-class, explicitly not for reuse without caveats."* A
> walks-between-Ks streak is the same class of statistic. It may well be right to **ship** as a
> receipt for this use case and wrong to **promote** to the library — but that should be a ruling,
> not an inheritance by analogy or an exemption by silence.

---

## 2 · `bbrate / krate` is exactly BB/K — and that is good news

BB% and K% share the same PA denominator, so:

```
(BB / PA) / (K / PA)  ==  BB / K
```

The DPO's `z.bbrate / z.krate` is therefore **algebraically identical to the received baseball
statistic BB/K**. That satisfies Intake Register §8 Principle 2 — *the library implements the
received definition, not the better one* — with no local invention at all. No repo precedent for
BB/K was found, so AP-9 is **genuinely new**, unlike `fpsr`, `ppa`, and `qab_rate` before it.

**One caveat that matters at three decimals.** The cancellation is exact only if neither input has
been rounded. `nresults` rounds to 3 dp; at a K% near .150, a half-unit rounding error in the
denominator is roughly **0.33% relative**, and it lands directly in the headline. The drafted
function therefore computes from **counts**, not from a ratio of rounded rates. Same rule as
Amendment 1 §1.2: **round in `zfig`, never in `z`.**

### The zero-strikeout problem is not a corner case — it is *this* case

`krate == 0` makes `bbrate / krate` return `inf`. The subject window has **zero strikeouts by
construction** — that is the entire premise of the video. So the headline computation is
`14 / 0` and the metric is undefined precisely where the story is.

`discipline_ratio` handles this three ways at once, which is why it returns eight columns rather
than one:

- `bb_per_k` → **NaN** (honest — the ratio genuinely does not exist), not `inf` (which breaks a
  plotly axis and reads as a real value in a table)
- `k_free` → **True**, so the state is queryable rather than inferred from a null
- `walks` / `strikeouts` shipped raw, so a consumer can render **"14 BB / 0 K"** — which is more
  informative than any number could be
- `bb_minus_k` (BB% − K%) → **always defined**, and the metric that still carries meaning when the
  ratio cannot

---

## 3 · `obp:k` should not be promoted

`bb:k` and `obp:k` look like siblings. They are not, and only one of them is defensible.

| | `bb_per_k` | `obp_per_k` |
|---|---|---|
| Received statistic? | **Yes** — BB/K is standard | **No** — not in general use |
| Numerator & denominator disjoint? | **Yes** — a PA is a walk or a strikeout, never both | **No** |
| Reduces to a unit? | **Yes** — "walks per strikeout" | **No** |

**The disjointness failure is the substantive objection.** A strikeout is an out, so it sits in
OBP's denominator *and* suppresses OBP's numerator. `obp / krate` therefore divides a quantity by
something that partly determines it. The ratio moves for two reasons at once and you cannot tell
them apart: a hitter can raise it by reaching base more, or by striking out less — and striking out
less *also* raises OBP. **The metric double-counts its own denominator.**

It will still correlate with "good hitter," which is exactly what makes it dangerous — it will look
like it works.

**What to use instead, depending on which claim you actually want:**

| Claim | Metric |
|---|---|
| "He earns his way on rather than being handed it" | `bb_per_k` (AP-9) |
| "He gets on base a lot *and* doesn't strike out" | Report **OBP and K% as two axes** — which the scatter already does. The scatter is the better artifact; a ratio collapses it and loses information. |
| "He went a long time without a punchout" | `walks_between_ks` (AP-10) |

**The scatter already encodes the ratio geometrically.** With x = `krate` and y = `obp`, each point's
ratio *is its slope from the origin*. The ratio does not need to be a column at all — see §4.

If the DPO wants `obp_per_k` shipped anyway, it should be labeled a **derived index, not a governed
KPI** — the same treatment Register §4.3 Principle 3 gives vendor-modelled fields: reportable,
labeled, not governed.

---

## 4 · The dangling `#fig.add_hline(` — you want a ray, not a line

The commented-out annotation is where the 3:2 claim belongs, and a horizontal line will not express
it. On a plot of `obp` (y) against `krate` (x), a **constant ratio is a straight line through the
origin with slope equal to that ratio.** A 3:2 OBP:K ratio is `obp = 1.5 × krate`.

```python
xmax = z[z.plate_apps > 49].krate.max()
fig.add_shape(type='line', x0=0, y0=0, x1=xmax, y1=1.5 * xmax,
              line=dict(dash='dot'))
fig.add_annotation(x=xmax, y=1.5 * xmax, text="OBP:K = 3:2",
                   showarrow=False, xanchor='right', yanchor='bottom')
```

Every point **above** the ray beats 3:2; every point below it does not. One shape, and the claim in
the subtitle becomes visually checkable — which is the whole job of a context chart.

> This is also the clearest argument for §3: once the ray is drawn, `obp_per_k` as a *column* is
> redundant. The geometry already carries it, without asking anyone to interpret a ratio whose
> parts overlap.

**Two smaller notes on the same figure.**

- **`'bs_color'` is in `kpis`.** It is a display encoding, not a KPI. This is the third instance of
  the same taxonomy slip — `'First Pitch Strike Rate'` (a label) in `kpis` at pass 1, `kpis`
  declared-and-unused in Amendment 2 §4 N-33. Recommend a standing rule: **`kpis` holds column
  names of measures; encodings and labels live elsewhere.**
- **Colon-named columns.** `'bb:k'` and `'obp:k'` are legal pandas columns but break attribute
  access (`z.bb:k`) and `df.query()`. Use `bb_per_k` / `obp_per_k` as **column names** and keep
  `'BB% : K%'` as the **display label** — which the `data_dictionary` already does correctly.

---

## 5 · Run this to get the 3:2 number

Paste-ready. Answers "how is Stott standing up" and produces the percentile the narrative needs.

```python
from discipline_ratio import discipline_ratio      # or paste into Baseball Functions.ipynb

level = ['player_name', 'game_year']
ctx   = discipline_ratio(level, pos)
ctx   = ctx[ctx.plate_apps > 49].copy()            # ratified 50-PA floor

# OBP is not in discipline_ratio's output — join it from nresults
ctx = ctx.merge(nresults(level, pos)[level + ['obp']], on=level, how='left')
ctx['obp_per_k'] = ctx.obp / ctx.krate             # derived index, NOT a governed KPI (§3)

stott = ctx[ctx.player_name == 'Stott, Bryson'].sort_values('game_year')
print(stott[['game_year','plate_apps','walks','strikeouts',
             'bbrate','krate','bb_per_k','bb_minus_k','obp','obp_per_k']].round(3))

# the claim: is he above the Phillies-since-2015 average, and by how much?
for m in ['bb_per_k', 'obp_per_k', 'bb_minus_k']:
    pool = ctx[m].dropna()
    print(f"{m:12s} pool mean {pool.mean():.3f} | median {pool.median():.3f} | "
          f"Stott career-seasons mean {stott[m].mean():.3f} | "
          f"pctile {(pool < stott[m].mean()).mean()*100:.0f}")
```

**Read the output with three cautions.**

1. **`pos` is Phillies-tenure only.** "Phillies hitters since 2015" is the right framing for a
   *Phillies* comparison, but a player's non-Phillies seasons are absent — so a mid-career
   acquisition contributes only his Phillies years. That is the `roster_support` pattern from the
   Marsh build and it is fine here; it just means the pool is *Phillies seasons*, not *players*.
2. **Season-level rows, unequal weight.** A 50-PA September call-up and a 650-PA everyday season
   are one row each in an unweighted mean. Consider a PA-weighted mean, or say "average qualified
   season" rather than "average hitter."
3. **`(pool < value).mean()` is a percentile of the season pool, not of hitters.** Say which.

---

## 6 · The drafted function

`discipline_ratio.py` accompanies this amendment. Conformance summary:

| Standard | How it is met |
|---|---|
| `(level, df)` signature | ✅ — and the docstring names `qab_rate(df, level=...)` as the shape not to copy |
| Governed sets inherited, not redeclared | ✅ — `K_EV` / `BB_EV` cited to `dp_uc7` L439 |
| PA definition inherited | ✅ — cited to `dp_uc24` L219 / `dp_uc22` L80 (non-null `events`, excluding `pickoff_1b`) |
| Denominators ship with rates (RC-3) | ✅ — `plate_apps`, `walks`, `strikeouts` all returned |
| No rounding in the curated frame | ✅ — rounding is the caller's job in `zfig` |
| Sensor-boundary NULL standard | ✅ — **named count columns** filled to 0; no blanket `.fillna(0)` |
| Open decisions explicit and greppable | ✅ — `DR-1`, `DR-2`, `DR-3` as module constants with rationale |
| Layer-1 stop disclosed | ✅ — carries the `qab_rate.py` NOT-AUTHORIZED banner |

### Three open decisions the function surfaces rather than settles

**DR-1 — does an intentional walk count as plate discipline?** The repo already holds both
conventions, each defensible: `dp_uc7` L439's `BB_EV` **includes** `intent_walk`; `dp_uc24` L222's
wOBA weight map keys **only** `'walk'`, following the wOBA convention that an IBB is not a batter
achievement. For an *approach* metric the wOBA reasoning is stronger — an intentional walk measures
what the opposing manager thinks of the hitter, not how the hitter controlled the at-bat. Exposed as
`UNINTENTIONAL_ONLY`, defaulted to current `dp_uc7` behaviour. **The validator does not pick.**

**DR-2 — zero-strikeout behaviour.** `'null'` recommended, as §2. `'inf'` is what the current
snippet produces.

**DR-3 — streak KPIs and the SL-1 precedent.** As §1.

---

## 7 · Amended totals

**New this amendment:** AP-9 (`discipline_ratio`), AP-10 (`walks_between_ks`), open decisions
DR-1 / DR-2 / DR-3.

| ID | Item | Severity |
|---|---|---|
| **B-14** | The video title claims a **streak**; the proposed KPI measures a **rate ratio**. Publishing the ratio as support for the title's claim would misrepresent it. | **BLOCKING** — narrative correctness |
| **B-15** | `bb_per_k` is undefined (`inf`) in the exact window the use case is about. DR-2 must be ruled before AP-9 ships. | **BLOCKING** |
| **N-35** | `obp_per_k` numerator and denominator are not disjoint — a strikeout both sits in OBP's denominator and suppresses its numerator. Ship as a labeled derived index or not at all. | non-blocking |
| **N-36** | The 3:2 claim is **unverified** — MLB repo unreachable from this session. Compute before publishing. §5. | non-blocking |
| **N-37** | DR-1 IBB treatment — both conventions already live in the repo. | non-blocking |
| **N-38** | DR-3 — AP-10 vs. the SL-1 do-not-promote precedent. | non-blocking |
| **N-39** | `'bs_color'` in `kpis`; third instance of encodings/labels leaking into the measure list. Standing rule recommended. | non-blocking |
| **N-40** | Colon-named columns (`bb:k`, `obp:k`) break attribute access and `.query()`. Use `bb_per_k` / `obp_per_k`; keep colons for labels. | non-blocking |
| **N-41** | Context-pool caveats — Phillies-tenure only; unweighted season rows; percentile is over seasons not hitters. §5. | non-blocking |
| ✅ | **50-PA floor correctly applied** (`plate_apps > 49`) — matches the standing standard identified in pass 1 B-5. First clean floor application in the use case. | credit |
| ✅ | **AP-9 is genuinely new** — no BB/K precedent found in the repo. First proposed function in this UC that is not a duplication. | credit |

**Running total: 14 blocking, 41 non-blocking.**

> Worth noting against the pattern of the last two amendments: this one searched first, found no
> duplication, and inherits three governed definitions rather than declaring any. That is what the
> mandatory-search step is supposed to produce.
