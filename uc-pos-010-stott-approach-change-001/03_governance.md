# 03 · Governance
**business-glossary-agent · metadata-mapper · data-tagger · privacy-watchdog · version-controller**

## Glossary — terms consumed and introduced

| Term | Status | Definition | Note |
|---|---|---|---|
| First-Pitch Strike Rate (`fpsr`) | **APPROVED — consumed** | `(first_pitches − first_pitch_balls) / first_pitches` | `cde.fpsr` approved in the Rangel contract. **First `pos`-side use of a `pps`-side term** — value-stream annotation required, not a new term |
| Swing | **RATIFIED THIS BUILD** | `description` in the 8-value governed SWINGS list **including `swinging_pitchout`** | Resolves B-1. Notebook is the authority; `dp_uc7` L437 is stale |
| Swing Rate (AP-2) | NEW — provisional | swings ÷ pitches | Inherits the swing classifier; declares none |
| First-Pitch Swing Rate (AP-3) | NEW — provisional | AP-2 on `pitch_number == 1` | Measures "he takes the first pitch" |
| Out-of-Zone Whiff Rate | NEW — provisional | `(ooz & swing & whiff) / (ooz & swing)` | Same filter both sides, per `uc-cat-001` |
| Walks per Strikeout (AP-9) | NEW — provisional | BB ÷ K from **counts** | Received stat (BB/K). K==0 → NULL + `k_free` |
| Walks Between Strikeouts (AP-10) | NEW — provisional | longest run of BB between consecutive K | **Run length, not a rate.** SL-1 precedent is disposition D |
| Anchor Month | NEW | April 2026, fixed across re-runs | |
| Partial Month | NEW | month not spanning its full calendar range | August 2026 |
| Month | **DECLARED** | `game_date.dt.month`, calendar | **No March/April merge.** March 2026 = 2 games, 13 PA, retained + flagged |

## Metadata mapping
All 16 CDEs mapped **exact** against the live `pos` schema. Zero unmapped, zero inferred —
each confirmed by reading the column, not by naming convention.

## Tagging
Domain `pos` · subject area *Batting / Plate Discipline* · sensitivity **Internal** ·
product `uc-pos-010`.

## Privacy — **LOW**
Public player name, publicly-tracked on-field performance. No PII beyond a public figure's name.
No health, injury, contract or personnel-evaluation data joined, and none may be without a fresh review.

**Access asymmetry noted.** Stott is both a named persona and the subject of a product whose
actions include lineup-slot and platoon decisions about him. Recommendation: staff receive the
full artifact; the player-facing surface is the persona guide in `06`, scoped to his own approach
metrics and excluding deployment framing.

## Restricted uses
Contract or arbitration valuation · public/media distribution · any causal claim (see `05` §caveats).

## Version control

| Change | Class |
|---|---|
| `fpsr` cross-value-stream reuse | **non-breaking** — no formula change |
| Ratifying the 8-value SWINGS list | **breaking to values** for any consumer that used the 7-value list — near-zero magnitude, therefore *silently* breaking |
| `_fix` variants for whiff/hard-hit/fpsr | **non-breaking** — additive; originals untouched |
| AP-2/3/6/9/10 | new, no consumers, **cheap to change now** |
